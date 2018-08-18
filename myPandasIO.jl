
using PyCall
using DataFrames
using Pandas: query



function pandas2julia(pdf)
    getcols(x) = typeof(x) == Pandas.DataFrame? map(Symbol, Pandas.columns(x)) :
                                            map(Symbol, x[:columns]);
    getdf(df, colnames) = DataFrames.DataFrame(
                            Any[Array(df[c]) for c in colnames], colnames);
    getdf(pdf, getcols(pdf));
end

function pj2pd(df)
    pd.DataFrame(df)
end

function pd2pj(df)
    Pandas.DataFrame(df)
end

function jdf2p(jdf, dftype="pd")
    df = Pandas.DataFrame([])
    for (colname, colvals) in zip(string.(names(jdf)),
        DataFrames.columns(jdf)) eval(:($df[$colname]=$colvals)) end

    if dftype=="pd"
        df = pd.DataFrame(df)
    end

    return df
end


#example expr is :(DispatchedMW == "15")
function query_pd(df, expr)
    @pipe test |> pd2pj |>  query(_, expr) |> pd.DataFrame
end
