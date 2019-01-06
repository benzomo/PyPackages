# -*- coding: utf-8 -*-

import copy

import pandas as pd, numpy as np


def explode_data(dict_data):

    df_data = []
    
    for dk in dict_data.keys():
    
        temp = dict(zip(dict_data[dk].keys(), 
                        map(lambda it: pd.DataFrame(np.array(list(it[1].values())).reshape(1,-1), 
                                                    columns=list(it[1].keys())) if isinstance(
                                                            it[1], dict) else {it[0]: it[1]}, dict_data[dk].items()
                            )
                        )
                    )
            
        _prices = temp.pop('ListingPrice')
        
        dfi = pd.concat([temp[k] for k in ['PropertySummary', 'listingDetailsBuildingCon', 
                         'propertyDetailsLandSection', 'RoomDetails'] if k in temp.keys()], axis=1)
            
        for k in ['MLSNum', 'Neighborhood', 'Address', 'Description']:
            dfi[k] = temp[k]
            
        for i, pi in enumerate(_prices.items()):
            dfi.loc[i, [col for col in dfi.columns if col not in [
                    'Date', 'ListingPrice']]] = dfi.loc[0, [col for col in dfi.columns if col not in [
                                                        'Date', 'ListingPrice']]].values
            dfi.loc[i,'Date'] = pi[0]
            dfi['ListingPrice'] = pi[1]
            
        dfi['MLSNum'] = copy.copy(dk)
            
                
        df_data.append(dfi)
        
        for i in range(len(df_data)):
            df_data[i] = df_data[i].loc[:,~df_data[i].columns.duplicated()]
        
    return pd.concat(df_data, axis=0)