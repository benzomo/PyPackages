# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

import numpy as np, pandas as pd

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split

from keras.models import load_model, Model, Sequential
from keras.layers import Dense, Activation, Dropout, Input 
from keras.layers import LSTM, Reshape, Lambda, RepeatVector
from keras.utils import to_categorical
from keras.optimizers import Adam
from keras import backend as K


def laglead(df,lag, lead):
    newDict = {}
    df.dropna(inplace=True)
    for col in iter(df.columns):
        newDict[col] = pd.DataFrame([])
        for i in range(-lag,lead + 1):
            newDict[col][str(i)] = df[col].shift(i)
        newDict[col].dropna(inplace=True)
    return newDict


class ts_LSTM():
    lag=20 
    lead=3 
    split=0.8 
    h_layers=2
    neurons=120
    lr=0.01 
    scale='std' 
    epochs=500
    batch_size=500
    

    def __init__(self, df, pred_key): 
        self.df = df
        self.pred_key = pred_key
    
        class stats:
            mu = self.df.mean()
            sigma = self.df.std()
        
        self.stats = stats()
        
        def reshape(self, lag=self.lag, lead=self.lead):
            xcols = list(filter(lambda x: x != pred_key, self.df.columns))   
            ycols = list(filter(lambda x: x == pred_key, self.df.columns))
        
            seqData = laglead(self.df, lag, lead)
            N = seqData[pred_key].shape[0]
            xtN = lag
            ytN = lead + 1
            xfN = len(xcols)
            yfN = len(ycols)
            
            xData = np.array([[[None]*(xfN + 1)]*xtN]*N)
            yData = np.array([[None]*ytN]*N)
            
            for (i, key) in enumerate(xcols):
                xData[:,:,i] = seqData[key].iloc(axis=1)[:xtN].values
            xData[:,:,xfN] = seqData[self.pred_key].iloc(axis=1)[:xtN].values  
        
            for (i, key) in enumerate(ycols):
                yData[:,:] = seqData[key].iloc(axis=1)[xtN:].values
            
            return xData, yData
    
        
        def ttsplit(df=self.df, pred_key=self.pred_key, shuffle=False, 
                    train_size=self.split, lag=self.lag, lead=self.lead):
            
            self.lag = lag
            self.lead = lead
            
            xData, yData = reshape(self,lag,lead)
            X_train, X_test, y_train, y_test = train_test_split(xData, 
                                                            yData,
                                                            shuffle=False,
                                                            train_size=0.8)
            return X_train, X_test, y_train, y_test
        
        self.ttsplit = ttsplit
       
        def setup(n_neur=self.neurons,h_layers=self.h_layers, lr=self.lr):
          
            self.X_train, self.X_test, self.y_train, self.y_test = self.ttsplit()
            self.model = Sequential()
            self.model.add(LSTM(n_neur, input_shape=(self.X_train.shape[1], 
                                        self.X_train.shape[2]),
                                        return_sequences=True if h_layers  > 1 else False))
            
            if h_layers > 2:
                for hlayer in range(h_layers - 2):
                    self.model.add(LSTM(n_neur, return_sequences=True))
                self.model.add(LSTM(n_neur))
            elif h_layers  ==2:
                self.model.add(LSTM(n_neur))
                
            self.model.add(Dense(self.lead + 1))
    
            self.opt = Adam(lr=lr, beta_1=0.9, beta_2=0.999, decay=0.01)
            self.model.compile(loss='mae', optimizer=self.opt)
            
        
        self.setup = setup
            
        def run(epochs=self.epochs, batch_size=self.batch_size):
            try:
                self.history = self.model.fit(self.X_train, self.y_train, epochs=epochs, 
                        validation_data=(self.X_test, self.y_test), 
                        verbose=2, shuffle=False, batch_size=batch_size)
        
                self.yhat = self.model.predict(self.X_test)
            except:
                print("TRY SETTING UP MODEL!!! model.setup()")
        
        self.run = run
        
        def data():
            return self.X_train, self.X_test, self.y_train, self.y_test
        
        self.data = data
        

        