import numpy as np, pandas as pd

from Viz import *
from ModelsML import ts_LSTM, DecisionTree, scale
from functions import *
from base import *

from functools import reduce, partial
from sklearn.model_selection import RepeatedKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn import tree



class RegressorCollection():
    """Regressor Types:
        RandomForestRegressor(bootstrap=True, criterion='mse', max_depth=2,
           max_features='auto', max_leaf_nodes=None,
           min_impurity_decrease=0.0, min_impurity_split=None,
           min_samples_leaf=1, min_samples_split=2,
           min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
           oob_score=False, random_state=0, verbose=0, warm_start=False)
        RandomForestRegressor(bootstrap=True, criterion='mse', max_depth=2,
           max_features='auto', max_leaf_nodes=None,
           min_impurity_decrease=0.0, min_impurity_split=None,
           min_samples_leaf=1, min_samples_split=2,
           min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
           oob_score=False, random_state=0, verbose=0, warm_start=False)
        RandomForestRegressor(bootstrap=True, criterion='mse', max_depth=2,
           max_features='auto', max_leaf_nodes=None,
           min_impurity_decrease=0.0, min_impurity_split=None,
           min_samples_leaf=1, min_samples_split=2,
           min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
           oob_score=False, random_state=0, verbose=0, warm_start=False)
        RandomForestRegressor(bootstrap=True, criterion='mse', max_depth=2,
           max_features='auto', max_leaf_nodes=None,
           min_impurity_decrease=0.0, min_impurity_split=None,
           min_samples_leaf=1, min_samples_split=2,
           min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
           oob_score=False, random_state=0, verbose=0, warm_start=False)"""
        
    
    def __init__(self, X=None, y=None, 
                 ireg=DecisionTree(ttype='generic',max_depth=8), *args, **kwargs):
        
        self.corr = X.corr()
        self.ireg = ireg
        
        if 'oh_features' in list(kwargs.keys()):
            self.oh_features = kwargs['oh_features']
            
        else:
            self.oh_features = list(filter(
                    lambda x: x not in self.corr.columns.tolist(), X.columns))
            
        
        self.X = MLDataFrame(X)
        self.y = MLDataFrame(y)
        
        self.X.add_oh(self.oh_features)
        
        if 'scale_cols' in list(kwargs.keys()):
            self.scale_cols = kwargs['scale_cols']
            if 'scale_types' in list(kwargs.keys()):
                self.scale_types = kwargs['scale_types']
            else:
                self.scale_types = ['minmax']*len(self.scale_cols)
                
            self.X.add_scaled(self.X.oh, scale_cols=self.scale_cols, 
                              scale_types=self.scale_types)
            self.y.add_scaled(self.y)
        
        else:
             self.X.add_scaled(self.X.oh)
             self.y.add_scaled(self.y)
        
        
        
        self.models = dict(zip([arg.__name__ for arg in args], args))
        self.fitted = {}
        
        
    def rank_importance(self, out_file='tree.dot',show=True):
        self.initial_tree = self.ireg.fit(self.X.oh, self.y)
        tree.export_graphviz(self.initial_tree, out_file=out_file)
        self.feature_importances_ = pd.DataFrame(self.initial_tree.feature_importances_, 
                                                 index=self.X.oh.columns,
                                                 columns=['Features']).sort_values(
                                                         'Features',ascending=False).to_dict()
    
    def fit(self, X, y):
        for key in self.models.keys():
            self.fitted[key] = self.models[key].fit()
        

    
