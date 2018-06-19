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
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.utils import to_categorical
from keras.optimizers import Adam
from keras import backend as K

from scipy.stats import gmean, boxcox_normmax
from scipy.special import boxcox, inv_boxcox


def laglead(df,lag, lead):
    newDict = {}
    df.dropna(inplace=True)
    for col in iter(df.columns):
        newDict[col] = pd.DataFrame([])
        for i in range(-lag,lead + 1):
            newDict[col][str(i)] = df[col].shift(-i)
        newDict[col].dropna(inplace=True)
    return newDict

def scale(df, how='std'):
        class Transform():
            def __init__(self, tfm, utfm):
                self.tfm = tfm
                self.utfm = utfm
            
        if how == 'std':
            std = df.std(ddof=0)
            mu = df.mean()
            tfm = lambda df: df.set_value(index=df.index, col=df.columns,
                                  value=StandardScaler().fit_transform(df))
            utfm = lambda x: x*std + mu
        
        elif how == 'minmax':
            maxmin = df.max() - df.min() 
            mu = df.mean()
            tfm = lambda df: df.set_value(index=df.index, col=df.columns,
                                  value=MinMaxScaler().fit_transform(df))
            utfm = lambda x: x*maxmin + mindf           
        
        elif how == 'boxcox':
            maxmin = df.max() - df.min() 
            mindf = df.min()
            tempscaler = MinMaxScaler()
            df = df.set_value(index=df.index, col=df.columns,
                                  value=tempscaler.fit_transform(df))
            
            bxcx_lmd = (df + 0.00000001).apply(boxcox_normmax)
           
            for col in df.columns:
                df[col] = boxcox(df[col] + 0.00000001, 
                        bxcx_lmd[col])
            mu = df.mean()
            
            def tfm(df, bxcx_lmd=bxcx_lmd):
                tempscaler = MinMaxScaler()
                df = df.set_value(index=df.index, col=df.columns,
                                  value=tempscaler.fit_transform(df))                
                for col in df.columns:
                    df[col] = boxcox(df[col] + 0.00000001, 
                            bxcx_lmd[col])
                return df - mu
            
            def utfm(df, bxcx_lmd=bxcx_lmd):
                df = df + mu
                for col in df.columns:
                    df[col] = inv_boxcox(df[col], 
                            bxcx_lmd[col]) - 0.00000001
                return df*maxmin + mindf
            
        scaler = Transform(tfm,utfm)
        
        return scaler


class ts_LSTM():
    lag=30 
    lead=3 
    split=0.8 
    h_layers=1
    neurons=120
    rd=0.33
    d=0
    lr=0.01 
    scaler_type='std' 
    epochs=600
    batch_size=300
    

    def __init__(self, df, pred_key, scaler_type=scaler_type): 
        self.scaler = scale(df,how=scaler_type)
        self.df = self.scaler.tfm(df)
        self.pred_key = pred_key
        self.index=df.index
         
    
        class stats:
            mu = self.df.mean()
            sigma = self.df.std()
        
        self.stats = stats()
        
        def reshape(df = self.df, lag=self.lag, lead=self.lead, pred=False):
            xcols = list(filter(lambda x: x != pred_key, df.columns))   
            ycols = list(filter(lambda x: x == pred_key, df.columns))
        
            seqData = laglead(df, lag, lead if pred == False else 0)
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
            
            if pred == False:
                for (i, key) in enumerate(ycols):
                    yData[:,:] = seqData[key].iloc(axis=1)[xtN:].values
                
            return xData, yData
    
        
        def ttsplit(df=self.df, pred_key=self.pred_key, shuffle=False, 
                    train_size=self.split, lag=self.lag, lead=self.lead):
            
            self.lag = lag
            self.lead = lead
            
            xData, yData = reshape(df, lag,lead)
            X_train, X_test, y_train, y_test = train_test_split(xData, 
                                                            yData,
                                                            shuffle=False,
                                                            train_size=0.8)
            return X_train, X_test, y_train, y_test
        
        self.ttsplit = ttsplit
       
        def setup(n_neur=self.neurons,h_layers=self.h_layers, lr=self.lr, 
                  d=self.d, rd=self.rd):
          
            self.X_train, self.X_test, self.y_train, self.y_test = self.ttsplit()
            self.model = Sequential()
            self.model.add(LSTM(n_neur, input_shape=(self.X_train.shape[1], 
                                        self.X_train.shape[2]),
                                        return_sequences=True if h_layers  > 1 else False,
                                        dropout=d, recurrent_dropout=rd))
            
            if h_layers > 2:
                for hlayer in range(h_layers - 2):
                    self.model.add(LSTM(n_neur, return_sequences=True,
                                        recurrent_dropout=rd))
                self.model.add(LSTM(n_neur,recurrent_dropout=rd))
            elif h_layers  ==2:
                self.model.add(LSTM(n_neur,recurrent_dropout=rd))
                
            self.model.add(Dense(self.lead + 1))
    
            self.opt = Adam(lr=lr, beta_1=0.9, beta_2=0.999, decay=0.01)
            self.model.compile(loss='mae', optimizer=self.opt)
            
        
        self.setup = setup
            
        def run(epochs=self.epochs, batch_size=self.batch_size):
            try:
                
                reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.5,
                              patience=5, min_lr=0.0001)
                early_stp = EarlyStopping(monitor='val_loss', 
                                          min_delta=0, patience=80, 
                                          verbose=2, mode='auto')
                
                self.history = self.model.fit(self.X_train, self.y_train, epochs=epochs, 
                        validation_data=(self.X_test, self.y_test), 
                        verbose=2, shuffle=False, batch_size=batch_size,
                        callbacks=[reduce_lr, early_stp])
        
                self.yhat_train = self.model.predict(self.X_train)
                self.yhat = self.model.predict(self.X_test)
            except:
                print("TRY SETTING UP MODEL!!! model.setup()")
        
        self.run = run
        
        def data():
            return self.X_train, self.X_test, self.y_train, self.y_test
        
        self.data = data
        
        def predict(df, pred=True):
            xData, yData = reshape(df, self.lag, self.lead, pred=True)
            return self.model.predict(xData)
        
        self.predict = predict        

        