import numpy as np
import pandas as pd
from .. import analysis
import os

"""
This module is to analysis astrocyte event calcium signal changes. The data folder come from Matlab module AQuA.
"""

# aqua analysis part ========================================================
def readAquaData(path, drop_cols = ['Index']):
    # This path is the folder path when output from AQuA.
    # Now I will use the excel file as the source of the result.
    # the result is a pandas dataframe
    
    tmp = pd.read_excel(path, 'Sheet1', header = None, index_col=None)
    df = pd.DataFrame(columns = tmp.loc[:,0].values)
    nrow = len(tmp.columns)
    for i in range(nrow-1):
        df.loc[i, :] = tmp.loc[:,i+1].values
    if len(drop_cols) > 0:
        df.drop(columns = drop_cols, inplace = True)
    return(df)

def groupAquaData(pathlist, **kwargs):
    """
    This function read a series of path to df, and analyse each columns, also each trial's event number.

    If you don't want to analyze based on all events, you can set analyze_event_num to a number you want, like 500.
    And set sort_columns to a list of column name like: sort_columns = ['Curve - Max Dff', 'Curve - Duration 50% to 50%', 'Basic - Area']
    I think the sorting method based on mag first, then duration, then size is a good stragety, so I set it as default.

    If you want to give a costumize trial id, use kwargs trialid=['xxx', 'xxx', 'xxx', ...]
    """
    def __formatid__(path, **kwargs):
        l1 = os.path.basename(os.path.dirname(path)).split('_')[0]
        l2 = os.path.basename(os.path.dirname(os.path.dirname(path)))
        l3 = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path))))
        return(l3 + '-' + l2 + '-' + l1)


    kickout_columns = ['Index', 'trial', 'Curve - P Value on max Dff (-log10)', 'Curve - Decay tau'] # this list need manully change based on AQuA features.
    res = {'n_of_events':{'array':np.array([])}}

    if type(pathlist) in [str]:
        pathlist = np.array([pathlist])

    # if type(pathlist) in [list, np.ndarray]:
    for i in range(len(pathlist)):
        if 'trialid' in kwargs.keys():
            tmpid = kwargs['trialid'][i]
        else:
            tmpid = __formatid__(pathlist[i])
        
        if i == 0:
            df = readAquaData(pathlist[i])
            df['trial'] = tmpid
            res['n_of_events']['array'] = np.append(res['n_of_events']['array'], len(df))
        else:
            tmp = readAquaData(pathlist[i])
            tmp['trial'] = tmpid
            df = pd.concat([df, tmp])
            res['n_of_events']['array'] = np.append(res['n_of_events']['array'], len(tmp))
    df.reset_index(drop = True, inplace = True)
    res['n_of_events'] = analysis.group_value_to_dict_element(res['n_of_events']['array'])
    res['n_of_events']['analysis_method'] = ['box']
    res['n_of_events']['dataType'] = 'avgStd'

    if kwargs.get('analyze_event_num', False):
        num = kwargs['analyze_event_num']
        sorting_columns = kwargs.get('sort_columns', 
            ['Curve - Max Dff', 'Curve - Duration 50% to 50%', 'Basic - Area']
        )
        tmp = np.zeros(len(df))
        for c in sorting_columns:
            tmp = tmp + df[c].rank()
        df['rank'] = tmp
        df.sort_values(by = 'rank', ascending = False, inplace = True)
        df.reset_index(drop = True, inplace = True)
        df = df.loc[:num-1, :]


    cname = df.columns
    cname = [x for x in cname if x not in kickout_columns]
    for i in cname:
        try:
            res[i] = analysis.group_value_to_dict_element(df.loc[:,i].values)
            res[i]['analysis_method'] = ['box']
            res[i]['dataType'] = 'avgStd'
        except:
            pass
    return(res, df)


def aquaStruct(foldername):
    res = dict()
    res['excel'] = os.path.join(foldername, 'FeatureTable.xlsx') 
    res['mov'] = os.path.join(foldername, 'Movie.tif')
    res['paras'] = os.path.join(foldername, 'aqua_parameters.yml')
    return(res)