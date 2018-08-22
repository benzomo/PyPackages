import pandas as pd
import numpy as np

from sklearn.preprocessing import OneHotEncoder, LabelEncoder

from functools import reduce

ohe = OneHotEncoder()
le = LabelEncoder()

def fourier(df, K, p):
    df['t'] = range(df.shape[0])
    
    for k in range(1,K+1):
        df['Cos{k}'.format(k=k)] = df['t'].apply(
                lambda t: np.cos(2*np.pi*k*t/p))
        df['Sin{k}'.format(k=k)] = df['t'].apply(
                lambda t: np.sin(2*np.pi*k*t/p))
        
    return df.drop(columns='t')
    
        
    
def columns_to_onehot(df, cols):
    df[cols] = df[cols].astype(str)

    int_labels = dict(zip(cols, list(map(lambda x: le.fit_transform(df[x]),
                                        cols))))
    
    onehot_labels = dict(zip(cols, list(map(lambda x: ohe.fit_transform(
        int_labels[x].reshape(-1,1)), cols))))

    temp = [pd.DataFrame(onehot_labels[key].toarray()).rename(
                columns = lambda x: key + str(x)) for key in onehot_labels.keys()]
    
    temp = reduce(lambda x, y: pd.concat((x, y), axis=1), temp)
    
    return pd.concat((df, temp), axis=1) 
