# -*- coding: utf-8 -*-


datapath = "/home/benmo/OneDrive/GitHub/Kaggle/HousePrices/data"
X_raw = pd.read_csv(datapath + '/train.csv')
y_raw = X_raw.SalePrice

X_raw.drop(columns='SalePrice',inplace=True)
X_raw = X_raw.fillna(X_raw.mean())


rc = RegressorCollection(X_raw, y_raw)

from sklearn.model_selection import GridSearchCV


parameters = {'epochs' : [50], 'batch_size' : [50], 'hidden_layers' : [2,3], 
              'neurons' : [[90, 40, 20, 5, 5], [75, 35, 35, 10, 2], [55, 45, 40, 5, 2]], 
              'act' : [['sigmoid', 'relu', 'relu','sigmoid', 'relu']], 
              'act_op' : ['sigmoid']}


nn1 = NN(rc.X.scaled)

clf = GridSearchCV(nn1.NN_skl, parameters)
fitted = clf.fit(rc.X.scaled, rc.y.scaled.iloc(axis=1)[0])
