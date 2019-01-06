import pandas as pd
import numpy as np

from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from scipy.stats import gmean, boxcox_normmax
from scipy.special import boxcox, inv_boxcox


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
  


    
    
def columns_to_onehot(df, oh_cols):
    df[oh_cols] = df[oh_cols].astype(str)

    int_labels = dict(zip(oh_cols, list(map(lambda x: le.fit_transform(df[x]),
                                        oh_cols))))
    
    onehot_labels = dict(zip(oh_cols, list(map(lambda x: ohe.fit_transform(
        int_labels[x].reshape(-1,1)), oh_cols))))

    temp = [pd.DataFrame(onehot_labels[key].toarray()).rename(
                columns = lambda x: key + str(x)) for key in onehot_labels.keys()]
    
    temp = reduce(lambda x, y: pd.concat((x, y), axis=1), temp)
    
    return pd.concat((df.drop(columns=onehot_labels), temp), axis=1) 
