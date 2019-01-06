using PyCall
using DataFrames

#using Winston


@pyimport re
@pyimport pandas as pd
@pyimport numpy as np
@pyimport os


unshift!(PyVector(pyimport("sys")["path"]),
            "/home/benmo/OneDrive/GitHub/PyPackages/Algos")
@pyimport ModelsML

include("./myPandasIO.jl")
include("./tradingFuncs.jl")

models_loc = "/home/benmo/Data/Databases/Models/LSTM/"



function save_model(mdl, dir)
    pd.Series(stocksⱼ)[:to_csv](dir*"stocksj.csv")
    mdl[:save_weights](dir*"model.h5")

    open(dir*"mdl.json", "w") do f
            write(f, mdl[:to_json]())
    end
end



function LSTM_J(R, stockᵢ, stocksⱼ; sclr="std")
    scaler = ModelsML.scale(py"$R", how=sclr)
    R̃ = scaler[:tfm](py"$R")


    mdl = ModelsML.ts_LSTM(R̃, stockᵢ)
    ŷ, y_test = py"$mdl.yhat.astype('float64'), $mdl.y_test.astype('float64')"

    ŷ , y_test = (ŷ, y_test) .|> ((x) -> x * techRtnσ[stockᵢ][:tolist]() +
                                                            techRtnμ[stockᵢ][:tolist]()) .|>
                                                            transpose .|> DataFrame
    if os.path[:exists](models_loc*"$stockᵢ") == false
        os.mkdir(models_loc*"$stockᵢ")
        save_model(mdl, models_loc*"$stockᵢ/")
    else
        i=1
        while os.path[:exists](models_loc*"$stockᵢ$i") i+=1 end
        os.mkdir(models_loc*"$stockᵢ$i")
        save_model(mdl, models_loc*"$stockᵢ$i/")
    end
end
