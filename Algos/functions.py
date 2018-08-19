import pandas as pd
import numpy as np




def fourier(df, K, p):
    df['t'] = range(df.shape[0])
    
    for k in range(1,K+1):
        df['Cos{k}'.format(k=k)] = df['t'].apply(
                lambda t: np.cos(2*np.pi*k*t/p))
        df['Sin{k}'.format(k=k)] = df['t'].apply(
                lambda t: np.sin(2*np.pi*k*t/p))
        
    return df.drop(columns='t')
    
        
    
    