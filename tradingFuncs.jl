using PyCall
using DataFrames
using Pandas: query, read_csv, read_excel, read_pickle
using RCall
using Pipe
#using Winston

using TSne
using Clustering
using StatsBase


@pyimport re
@pyimport pandas as pd
@pyimport numpy as np
@pyimport pyspark.sql as sparksql

@pyimport scipy.stats as sps

@pyimport sklearn.preprocessing as sklpp

unshift!(PyVector(pyimport("sys")["path"]),
            "/home/benmo/OneDrive/GitHub/PyPackages/Algos")
@pyimport ModelsML

include("./myPandasIO.jl")


function fw_theorem(RᵢRₘ,i="AAPL",m="SP500";q=0.005)

    for stock in RᵢRₘ[:columns][:tolist]()
        qᵤ = py"$RᵢRₘ[$stock].quantile(1-$q)"
        qₗ = py"$RᵢRₘ[$stock].quantile($q)"
        RᵢRₘ[stock] = py"$RᵢRₘ[$stock].mask($RᵢRₘ[$stock] > $qᵤ, $qᵤ)"
        RᵢRₘ[stock] = py"$RᵢRₘ[$stock].mask($RᵢRₘ[$stock] < $qₗ, $qₗ)"
    end


    X = [ones(RᵢRₘ[m][:shape][1]) RᵢRₘ[m][:values]]
    Mᵢ = I - X*inv(X'*X)*X'


    stocks = py"list(filter(lambda x: x != $m, $RᵢRₘ.columns))"

    R̃ᵢ = RᵢRₘ[:copy]()

    for stock in stocks
        R̃ᵢ[stock] = Mᵢ * py"$RᵢRₘ[$stock].values"
    end
        R̃ᵢ = py"$R̃ᵢ[$stocks]"
end


function laglead(df; lag=15, lead=5)
    df = df[:dropna]()
    newDict = Dict()
    for col in df[:columns]
        newDict[col] = pd.DataFrame([])
        for i in -lag:lead
            newDict[col] = pd.concat((newDict[col],
                                        df[col][:shift](-i)),axis=1)
        end
        newDict[col] = newDict[col][:dropna]()
    end
    return newDict
end

function classifyRⱼ(βⱼ; perplx=50, nclust=16)
    dims = tsne(Matrix(βⱼ), 2, perplx)
    km1 = kmeans(transpose(dims), nclust; maxiter=100000, display=:iter)

    dimsT = dims'
    coeffs = [dimsT[:,i] for i in 1:length(dimsT[1,1:end])]
    tsneDF = DataFrame(Dict(zip(names(βⱼ), coeffs)))
    classesRow  = DataFrame(Dict(zip(names(βⱼ), km1.assignments')))

    classes = [tsneDF; classesRow]

    stockCats = hcat(
            DataFrames.columns(
            classes[3,:]) .|> (x) -> x[1],
            string.(names(classes))
            )
    return stockCats, dims, km1
end

function clean_Vol(βⱼ,rtns, stocksVol; startY=2013)
    dates = rtns[:index][:tolist]()

    #histogram(sample(techRtnJ[!isnan(techRtnJ[2]),2],500), opacity=0.45)
    #histogram!(sample(techRtnJ[!isnan(techRtnJ[1]),1],500), opacity=0.45)
    startY = string(startY)
    stocksVol = py"""$stocksVol[$startY:][$βⱼ.columns]"""
    isNa = stocksVol[:isna]()[:sum]()

    stocksVol = py"$stocksVol[$isNa[($isNa < 30)].index]"
    stocksVol = stocksVol[:dropna]()

    stocksVolμ = hcat(stocksVol[:mean]()[:tolist](),
                    stocksVol[:mean]()[:index][:tolist]())

    #histogram(techVolμ[:,1])


    sVol = stocksVolμ[stocksVolμ[:,1] .< 2.5e5,:]
    mVol = stocksVolμ[2.5e5 .< stocksVolμ[:,1] .< 1e7,:]
    lVol =  stocksVolμ[stocksVolμ[:,1] .> 1e7,:]

    nacols = py"$βⱼ.dropna(axis=1,how='all').columns.tolist()"
    βⱼ = py"$βⱼ[$nacols].loc[$nacols]"

    sVol_pd = py"$βⱼ[$(sVol[:,2])].loc[$(sVol[:,2])].dropna()"
    mVol_pd = py"$βⱼ[$(mVol[:,2])].loc[$(mVol[:,2])].dropna()"
    lVol_pd =  py"$βⱼ[$(lVol[:,2])].loc[$(lVol[:,2])].dropna()"

    dupcols = sVol_pd[:drop_duplicates]()[:index][:tolist]()
    sVol_pd = py"$sVol_pd[$dupcols].loc[$dupcols]"

    dupcols = mVol_pd[:drop_duplicates]()[:index][:tolist]()
    mVol_pd = py"$mVol_pd[$dupcols].loc[$dupcols]"

    dupcols = lVol_pd[:drop_duplicates]()[:index][:tolist]()
    lVol_pd = py"$lVol_pd[$dupcols].loc[$dupcols]"

    allstocks = []
    for x in [sVol_pd, mVol_pd, lVol_pd]
        allstocks = vcat(allstocks, x[:columns][:tolist]())
    end

    stocksRtn = py"$rtns[$allstocks]"
    βⱼ = py"$βⱼ[$allstocks]"

    return stocksRtn, stocksVol, sVol_pd, mVol_pd, lVol_pd

end


function sampleStocks(stockNames, sVol_pd, mVol_pd, lVol_pd, ωₛ, ωₘ, ωₗ; N=10)
    namesₛ, namesₘ, namesₗ =  (sVol_pd, mVol_pd, lVol_pd) .|> (x) ->
                        x[:columns][:tolist]()
    namesₛ, namesₘ, namesₗ = (namesₛ, namesₘ, namesₗ) .|>
                                        (x -> filter((z) -> z ∈ stockNames, x))

    ωₛ, ωₘ, ωₗ = (namesₛ, namesₘ, namesₗ) |> (x) ->  (ωₛ/length(x[1]), ωₘ/length(x[2]), ωₗ/length(x[3]))

    ωₛ = fill(ωₛ, length(namesₛ))
    ωₘ = fill(ωₘ, length(namesₘ))
    ωₗ = fill(ωₗ, length(namesₗ))

    samplex = [sample([namesₛ; namesₘ; namesₗ],Weights([ωₛ; ωₘ; ωₗ])) for i in 1:N]

end
