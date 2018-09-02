#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 15:32:42 2018

@author: benmo
"""
import pandas as pd, numpy as np
from .functions import *


class MLDataFrame(pd.DataFrame):
    _attributes_ = "raw, oh_features, add_oh, add_scaled"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if len(args) == 1 and isinstance(args[0], MLDataFrame):
            args[0]._copy_attrs(self)
        
        self.raw = pd.DataFrame(self._data)

    def _copy_attrs(self, df):
        for attr in self._attributes_.split(","):
            df.__dict__[attr] = getattr(self, attr, None)

    @property
    def _constructor(self):
        def init(*args, **kw):
            mldf = MLDataFrame(*args, **kw)
            self._copy_attrs(mldf)
            return mldf
        return init
    
    def add_oh(self, oh_features):
            self.oh_features = oh_features
            self.oh = columns_to_onehot(self, oh_features) 
            return self
     
    
    
    def add_scaled(self, df, scale_cols=None, scale_types=None):
        
        if scale_cols == None:
             self.scaler = scale(df, how='minmax' if scale_types == None else scale_types)
             self.scaled = self.scaler.tfm((df))
        
        else:
            scalers = pd.Series(scale_cols, index=scale_types)
            scale_types = scalers.index.unique()
               
            self.scaler = {}
            tempcols = scalers[scale_types[0]].tolist()
            self.scaler[scale_types[0]] = scale(df, columns=tempcols, how=scale_types[0])
            self.scaled = scaler.tfm(df)
            
            
            if len(scale_types) > 1: 
                for i in scalers.index.unique():
                    tempcols = scalers[i] if isinstance(scalers[i], str) else scalers[i].tolist()
                    self.scaler[i] = scale(df, columns=tempcols, how=i)
                    temp = self.scaler[i].tfm(df)
                    
                    self.scaled = pd.concat((self.scaled, temp), axis=1)
                    
            self.scaled = pd.concat((self.scaled, df[list(filter(lambda x: x not in scale_cols,
                                                                df.columns))]), axis=1)
                
        
    