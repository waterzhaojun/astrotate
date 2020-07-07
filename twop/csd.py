import os
import pandas as pd
from .event import readAquaData
from scipy.io import loadmat
from .. import analysis

# csd analysis part =========================================================
def readCsdData(path):
    # The path refers to a folder named runx_CSD
    # csd analysis data is supposed to save in a mat file.
    resultpath = os.path.join(path,'result.mat')
    run = os.path.basename(path).split('_')[0]
    tmp = loadmat(resultpath)
    df = pd.DataFrame(columns = ['csd_speed', 'A1_duration', 'C_duration', 'A2_duration'])
    df.loc[0, 'csd_speed'] = tmp['speed'][0][0]
    df.loc[0, 'A1_duration'] = tmp['A1_duration'][0][0]
    df.loc[0, 'C_duration'] = tmp['C_duration'][0][0]
    df.loc[0, 'A2_duration'] = tmp['A2_duration'][0][0]

    a1resultpath = os.path.join(path,run+'_csdA1_AQuA', 'FeatureTable.xlsx')
    a1result = readAquaData(a1resultpath)
    a1result.columns = ['A1_'+x for x in a1result.columns]
    
    a2resultpath = os.path.join(path,run+'_csdA2_AQuA', 'FeatureTable.xlsx')
    a2result = readAquaData(a2resultpath)
    a2result.columns = ['A2_'+x for x in a2result.columns]
    
    cresultpath = os.path.join(path,run+'_csdC_AQuA', 'FeatureTable.xlsx')
    cresult = readAquaData(cresultpath)
    cresult.columns = ['C_'+x for x in cresult.columns]
    return(df, a1result, a2result, cresult)

def groupCsdData(pathlist):
    res = {}
    for i in range(len(pathlist)):
        if i == 0:
            df, a1, a2, c = readCsdData(pathlist[i])
        else:
            tmp = readCsdData(pathlist[i])
            df = pd.concat([df, tmp[0]])
            a1 = pd.concat([a1, tmp[1]])
            a2 = pd.concat([a2, tmp[2]])
            c = pd.concat([c, tmp[3]])
    for k in df.columns:
        try:
            res[k] = analysis.group_value_to_dict_element(df.loc[:,k].values)
            res[k]['analysis_method'] = ['box']
            res[k]['dataType'] = 'avgStd'
        except:
            pass
    for k in a1.columns:
        try:
            res[k] = analysis.group_value_to_dict_element(a1.loc[:,k].values)
            res[k]['analysis_method'] = ['box']
            res[k]['dataType'] = 'avgStd'
        except:
            pass
    for k in a2.columns:
        try:
            res[k] = analysis.group_value_to_dict_element(a2.loc[:,k].values)
            res[k]['analysis_method'] = ['box']
            res[k]['dataType'] = 'avgStd'
        except:
            pass
    for k in c.columns:
        try:
            res[k] = analysis.group_value_to_dict_element(c.loc[:,k].values)
            res[k]['analysis_method'] = ['box']
            res[k]['dataType'] = 'avgStd'
        except:
            pass
    return(res)  
