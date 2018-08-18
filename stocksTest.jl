using PyCall
using DataFrames
using Pandas: query, read_csv, read_excel, read_pickle
using RCall
using Pipe
#using Winston
using MLDataUtils
using Gadfly
using TSne
using Clustering
using Plots
using StatsBase

plotlyjs()

@pyimport re
@pyimport pandas as pd
@pyimport numpy as np


@pyimport scipy.stats as sps


unshift!(PyVector(pyimport("sys")["path"]),
            "/home/benmo/OneDrive/GitHub/PyPackages/Algos")
@pyimport ModelsML

include("./juliaAlgo.jl")



stocks_df = pd.read_pickle("/home/benmo/Data/PyObjects/stocks_df.gz",
                            compression="gzip")

stocks_df = pd.pivot_table(stocks_df, values=collect(stocks_df[:columns])[1:end-1],
                       index=stocks_df[:index], columns="Ticker")

stocksPrice = stocks_df[:Adj_Close]
stocksVol = stocks_df[:Volume]

sp500 = pd.read_pickle("/home/benmo/Data/PyObjects/SP500.pkl")
sp500long = pd.read_pickle("/home/benmo/Data/PyObjects/SP500long.pkl")


sp500[:DATE] = pd.to_datetime(sp500[:DATE])
sp500 = sp500[:set_index]("DATE")
sp500[:SP500] = sp500[:SP500][:apply](pd.to_numeric, errors="coerce")



stocksRtn = stocksPrice[:apply](np.log)[:diff]()
sp500 = sp500[:apply](np.log)[:diff]()

sp500μ = sp500[:mean]()
sp500σ = sp500[:std](ddof=0)

stocksRtnσ = stocksRtn[:std](ddof=0)



βⱼ = pd.read_pickle("/home/benmo/Data/PyObjects/stocks_betaj1.pkl")
βⱼ = py"$βⱼ.drop(columns='T').drop('T')"
#βⱼ = βⱼ[:dropna](axis=1,how="all")[:dropna](how="all")

stocksRtn, stocksVol, sVol_pd, mVol_pd, lVol_pd = clean_Vol(
                                                    βⱼ, stocksRtn, stocksVol;
                                                    startY=2013
                                                    )

stockcols = py"list(filter(lambda x: x in $βⱼ.columns.tolist(), $stocksRtn.columns.tolist()))"

βⱼ = py"$βⱼ[$stockcols].loc[$stockcols]" |> pandas2julia


#stocksRtn = stocksRtn[:join](sp500[:apply](
        #np.log)[:diff](), how="inner")
#stocksRtn[:SP500] = stocksRtn[:SP500][:fillna](method="ffill")
#stocksRtn[:SP500] = stocksRtn[:SP500][:fillna](method="bfill")

Rσ = stocksRtn[:std](ddof=0)

for stock in stocksRtn[:columns] stocksRtn[stock] =
    stocksRtn[stock] ./ Rσ[stock] end


stockCats, dims, km1 = classifyRⱼ(βⱼ; perplx=50, nclust=30)
Gadfly.plot(x=dims[:,1], y=dims[:,2], color = km1.assignments, Geom.point)


tech_idx = stockCats[stockCats[:,2] .== "AAPL",1][1]
namesTech = stockCats[stockCats[:,1] .== tech_idx,2]
techVol = py"$stocksVol[$namesTech]['2013':]"
techPrice = py"$stocksPrice[$namesTech]['2013':]"

techRtn = techPrice[:apply](np.log)[:diff]()[:fillna](0)

techRtnσ, techRtnμ = techRtn[:std](ddof=0), techRtn[:mean]()
techRtn_max, techRtn_min = techRtn[:max](), techRtn[:min]()


scaler = ModelsML.scale(py"$techRtn")

techRtn = scaler[:tfm](py"$techRtn")

techRtn_bxcx = techPrice[:apply](np.log)[:diff]()[:fillna](0)
scaler_bxcx = ModelsML.scale(py"$techRtn_bxcx", how="boxcox")
techRtn_bxcx = scaler_bxcx[:tfm](py"$techRtn_bxcx")

techRtnJ = techRtn |> pandas2julia
techRtnJ_bxcx = techRtn_bxcx |> pandas2julia

dates = techRtn[:index][:tolist]()


#histogram(techRtnJ[3], opacity=0.45)
#histogram!(techRtnJ_bxcx[3], opacity=0.45)

stockᵢ = try sample(filter((x) -> x ∈ sVol_pd[:columns][:tolist](), namesTech))
            catch sample(filter((x) -> x ∈ mVol_pd[:columns][:tolist](), namesTech)) end

stocksⱼ = sampleStocks(namesTech[namesTech .!= stockᵢ], sVol_pd, mVol_pd, lVol_pd, 0.1, 0.4, 0.5; N=10)



#mdl = ModelsML.ts_LSTM(techRtn, stockᵢ)
#ŷ, y_test = py"$mdl.yhat.astype('float64'), $mdl.y_test.astype('float64')"

#ŷ , y_test = (ŷ, y_test) .|> ((x) -> x * techRtnσ[stockᵢ][:tolist]() +
                                                        #techRtnμ[stockᵢ][:tolist]()) .|>
                                                        #transpose .|> DataFrame

yᵣ = DataFrame([])
yᵣ[:time] = 1:4

yᵣ = hcat(yᵣ, ŷ[1], y_test[1]; makeunique=true)

Gadfly.plot( ŷ, x=:time, y=Col.value(:x1,:x1_1),
            color=Col.index(:x1,:x1_1), Geom.line)

y₁ = DataFrame([])
y₁[:time] = 1:251
y₁ = hcat(y₁, reduce(vcat, DataFrames.columns( ŷ[1,:])),
                    reduce(vcat, DataFrames.columns( y_test[1,:])))

Gadfly.plot( y₁, x=:time, y=Col.value(:x1,:x1_1),
            color=Col.index(:x1,:x1_1), Geom.line)
