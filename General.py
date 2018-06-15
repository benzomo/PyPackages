# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 22:45:00 2018

@author: benmo
"""

import pandas as pd, numpy as np, dask.dataframe as ddf
import quandl
import sys, os, socket
import pickle
from dask import delayed
from difflib import SequenceMatcher
from matplotlib.dates import bytespdate2num, num2date
from matplotlib.ticker import Formatter
import re
from itertools import permutations, product, chain
from functools import reduce


similar = lambda a, b: SequenceMatcher(None, a, b).ratio()

crs4326 = {'init': 'epsg:4326'}


def print_lines(fn, N, out=None):
    fout=open(out, 'w+') if out == None else None
    f=open(fn)
    for i in range(N):
        line=f.readline()
        print(line) if out == None else fout.write(line)
    f.close()
    fout.close() if out == None else print('no file written')
    


tuple2str = lambda name: name if isinstance(name, tuple) ==False else reduce(lambda x, y:  str(x)
        .replace('.0','') + '_' + str(y).replace('.0',''), list(map(lambda xi: str(xi), name)))

def search_str(regx, string):
    return True if re.search(regx, string) else False

def returnFiltered(term, data):
        temp = list(filter(lambda x: term
                           in x.lower(), data['item']))
        return data[data.isin(temp).item==True]


def egen(data, f, applyto, groupby, column_filt, newcol):
    tmp = data[column_filt]
    tmp[newcol] = tmp.groupby(groupby).apply(f)
    tmp['index'] = tmp.index
    
    return pd.merge(data, tmp, how='inner', left_on=column_filt, right_on =applyto + ['index'])
    


class MyComp():
    cName = socket.gethostname()
    if sys.platform == 'linux':
        ffProfilePath = "/home/benmo/.mozilla/firefox/w55ako72.dev-edition-default"
        picklePath = "/home/benmo/Data/PyObjects"
    else:
        if cName == 'DESKTOP-HOKP1GT':
            ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/it0uu1ch.default"
            uofcPath = "D:/OneDrive - University of Calgary"
            financePath = "C:/users/benmo/OneDrive/2016& 2017Classes/Financial Econ"
            picklePath = "D:/data/pyobjects"
            classesPath = "C:/users/benmo/OneDrive/2016& 2017Classes"

        else:
            ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/vpv78y9i.default"
            uofcPath = "D:/benmo/OneDrive - University of Calgary"
            financePath = "D:/benmo/OneDrive/2016& 2017Classes/Financial Econ"
            picklePath = "D:/data/pyobjects"
            classesPath = "D:/benmo/OneDrive/2016& 2017Classes"
        

def mySAS():
    bob = pd.read_sas("D:/data/Personal Research/pcg15Public/pcg15Public/epcg15.sas7bdat")
    return bob


def collect_csv(path, na_val='NA',skiprows=0, dtype_map=None):
    try:
        return list(map(lambda x: [x, x.compute()], ddf.read_csv(
                path, skiprows=skiprows, dtype=dtype_map)))
    except:
        try:
            return list(map(lambda x: [x, x.compute()], ddf.read_csv(
                    path, low_memory=False, skiprows=skiprows, dtype=dtype_map)))           
        except:
            try:
                return list(map(lambda x: [x, x.compute()], ddf.read_csv(
                        path, low_memory=False, dtype=str,
                        skiprows=skiprows)))          
            except:
                return list(map(lambda x: [x, x.compute()], ddf.read_csv(
                        path, low_memory=False, dtype=str,
                                    na_values=na_val, skiprows=skiprows)))

'''example:
    bob = ddf.read_csv('Z:/Electricity/*.csv',skiprows=2,dtype={'Date': str,
        'HE': str,
       'Import/Export': str,
       'Asset Id': str,
       'Block Number': str,
       'Price': 'float64',
        'From': 'int64', 
        'To': 'int64',
        'Size': 'int64', 
        'Available': 'int64',
        'Dispatched': str, 
        'Dispatched MW': 'int64',
       'Flexible': str,
       'Offer Control': str})
    bob=bob.drop('Effective Date/Time',axis=1)
    bob.compute().to_csv('Z:/Electricity/Combined.csv',index=False)
    
    
'''

def nestmap(outer, outerf, innerf, mapping=list):
    return map(lambda x: outerf(mapping(map(lambda inner: innerf(inner), x))), outer)



def test():
    bob = pd.read_csv("C:/users/benmo/desktop/fedReserve.csv")
    list(filter(lambda x: 'utl' in x.lower(), bob['item']))


    data = quandl.get('FED/DTCOLRHTS_N_M', authtoken="FLjC56RgKyq7-zAcTJ_x")
    
    
class pickleLib:
    
    picklePath = MyComp.picklePath

    pathStates = picklePath + '/usaStates.pkl'
    pathCensus = "D:/Data/Personal Research/usadata.dta"
    
    states = lambda pth=pathStates: pd.read_pickle(pth)
    priceData = lambda pth=picklePath + "/priceData.pkl": pd.read_pickle(pth)
    fedData = lambda pth=picklePath + "/fedData.pkl": pd.read_pickle(pth)
    futuresData = lambda pth=picklePath + "/futuresData.pkl": pd.read_pickle(pth)
    treasuryData = lambda pth=picklePath + "/treasuryData.pkl": pd.read_pickle(pth)
    globalYieldData = lambda pth=picklePath + "/globalYield.pkl": pd.read_pickle(pth)
    pwt9 = lambda pth=picklePath + "/pwt9.pkl": pd.read_pickle(pth)
    aesoMO = lambda pth=picklePath + "/aesoMeritOrder.pkl": pd.read_pickle(pth)
    aesoPool = lambda pth=picklePath + "/aesoPool.pkl": pd.read_pickle(pth)
    aesodata = lambda pth=picklePath + "/aesodata.pkl": pd.read_pickle(pth)
    aesoforecast = lambda pth=picklePath + "/aesoforecast.pkl": pd.read_pickle(pth)
    ioTable = lambda pth1=picklePath + "/worldIO_index.pkl", pth2=picklePath + "/worldIO.pkl": [pd.read_pickle(pth1),
                                                                                                pd.read_pickle(pth2)]
    ioTable2013 = lambda pth=picklePath + "/worldIO_2013.pkl": pd.read_pickle(pth)
    can_occ_forecast = lambda pth=picklePath + "/can_occ_forecast.pkl": pd.read_pickle(pth)
    
    def getCensus(cntry, state, picklePath=picklePath):
        if cntry in ['USA', 'usa']:
            censusList = list(filter(lambda x: 'Census.pkl' in x[-10:], 
                                     os.listdir(picklePath)))
            file = list(filter(lambda x, s=state: state in x, censusList))[0]
            
            return pd.read_pickle(picklePath + '/' + file)
    
    
    def createStates(pathStates=pathStates):
        import us
        states = us.states.STATES_AND_TERRITORIES
        states = np.vstack(list(map(lambda x: 
            [x.__dict__[tempMethod] for tempMethod in ['fips', 'abbr','ap_abbr', 
             'capital', 'capital_tz', 'name']], states)))
        
        states = pd.DataFrame(states,columns=['fips', 'abbr','ap_abbr', 
             'capital', 'capital_tz', 'name'])

        states.to_pickle(pathStates)
    
class dates_noWkd(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M:%S'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(np.round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''

        return num2date(self.dates[ind]).strftime(self.fmt)

#formatter = dates_noWkd(x)