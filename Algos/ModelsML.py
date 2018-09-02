# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

import numpy as np, pandas as pd
from .functions import *


import sklearn


from sklearn.model_selection import train_test_split

from keras.models import load_model, Model, Sequential
from keras.layers import Dense, Activation, Dropout, Input 
from keras.layers import LSTM, Reshape, Lambda, RepeatVector
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.utils import to_categorical
from keras.optimizers import Adam
from keras import backend as K


from keras.wrappers.scikit_learn import KerasClassifier, KerasRegressor

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor


from functools import reduce, partial


def laglead(df,lag, lead):
    newDict = {}
    df.dropna(inplace=True)
    for col in iter(df.columns):
        newDict[col] = pd.DataFrame([])
        for i in range(-lag,lead + 1):
            newDict[col][str(i)] = df[col].shift(-i)
        newDict[col].dropna(inplace=True)
    return newDict




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
        
        
        self.__name__ = 'ts_LSTM'
         
    
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


class DecisionTree():    
    def __init__(self, ttype='aboost',random_state=0,max_depth=4,n_estimators=300): 
        self.max_depth = max_depth
        self.random_state=random_state
        self.n_estimators=n_estimators 
        
        self.__name__ = 'DecisionTree'
        
        if ttype == 'aboost':
            self.regressor = AdaBoostRegressor(DecisionTreeRegressor(max_depth=self.max_depth),
                              n_estimators=self.n_estimators, 
                              random_state=self.random_state)
        
        else:
            self.regressor = DecisionTreeRegressor(max_depth=self.max_depth, 
                                                   random_state=self.random_state)
        
        def fit(X_train, y_train):
            return self.regressor.fit(X_train, y_train)
        
        def predict(df):
            return self.regressor.predict(df)
        
        
        self.fit = fit
        self.predict = predict
        
        
class NN():    
    def __init__(self, data, random_state=0, nn_type='regressor'): 
        self.random_state=random_state
        self.type = nn_type
        self.data = data
        self.ncols = self.data.shape[1]
        
        self.__name__ = 'NN'
        
        
        if self.type == 'regressor':
            self.NN_skl = KerasRegressor(build_fn=self.create_model,ncols=self.ncols,hidden_layers=1)
    
    def create_model(self, ncols=5,optimizer='adam', act = ['sigmoid'], act_op='sigmoid', 
                     neurons=None, hidden_layers=1, loss='mean_squared_error', 
                     metrics=['mae', 'logcosh','mean_absolute_percentage_error']):

        if neurons == None:
            neurons = [self.ncols]*(hidden_layers + 1)
        
        if len(act) == 1:
            act.extend([act[0]]*hidden_layers)
        
        model = Sequential()
    
        model.add(Dense(neurons[0], activation=act[0], input_shape=(self.ncols,)))
    
        for i in range(hidden_layers):
            model.add(Dense(neurons[i + 1], activation=act[i]))
      
        model.add(Dense(1, activation=act_op))
      
        model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
        
        return model      
       
    
    
      