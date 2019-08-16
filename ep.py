# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:17:59 2019

@author: jzhao1
"""
import os
import pandas as pd
import numpy as np
from . import array
from . import utils
import json

def check_channel_name(exp_folder):
    files = os.listdir(exp_folder)
    files = [x for x in files if ((x[-4:] == '.txt') & (len(x.split('-'))>1))]
    file = os.path.join(exp_folder, files[-1])
    df = pd.read_csv(file, nrows = 1, sep = '\t').columns.values
    print(df)
    
def get_array(folderPath, startTrial, endTrial, channel, scanRate, outputRate, treatment_df, intvalue = False):
    
    treatment_df = treatment_df.astype({'trial': 'str'}) # after load from csv, the trial is int64
    
    trials = list(range(startTrial,endTrial+1,1))
    trials_txt = [str(x)+'.txt' for x in trials]
    files = [x for x in os.listdir(folderPath) if x.split('-')[-1] in trials_txt]
    files.sort()
    data = []
    #timepoint_df = pd.DataFrame(columns = ['trial', 'length'])
    treat_point = {}
    present_length = 0
    for file in files:
        df = pd.read_csv(os.path.join(folderPath, file), sep = '\t')
        values = df.loc[:, channel].values
        values = values[~np.isnan(values)]
        values = array.bint1D(values, int(scanRate/outputRate), setint = intvalue)
        data = np.append(data, values)
        
        tmp_trial = file.split('-')[-1][0:-4]
        #timepoint_df.loc[len(timepoint_df), :] = [tmp_trial, len(values)]
        print('%s done, length is %d' % (file, len(values)))
        if tmp_trial in treatment_df.loc[:, 'trial'].tolist():
            tmp_row = treatment_df.index[treatment_df.loc[:, 'trial'] == tmp_trial].tolist()[0]
            tmp_id = str(treatment_df.loc[tmp_row, 'treatment_id'])
            tmp_sec = treatment_df.loc[tmp_row, 'sec']#.value#astype(float)
            treat_point[tmp_id] = present_length + int(tmp_sec*outputRate)
            
        present_length = present_length + len(values)
    return(data, treat_point)
    
def treatment(treatlist):
    treat = {}
    for i in range(len(treatlist)):
        treat[str(i)] = treatlist[i]
    return(treat)

"""    
def array_timepoints_based_on_treatment(timepoint_df, treatment_tp):
    rows = len(treatment_tp)
    result = {}
    for r in range(rows):
        tid = treatment_tp.loc[r, 'treatment_id']
        idx = timepoint_df.index[timepoint_df['trial'] == treatment_tp.loc[r, 'trial']].tolist()[0]
        totaltime = np.sum(timepoint_df.loc[:, 'length'].values[0:idx]) + treatment_tp.loc[r, 'sec']*output_rate
        result[str(tid)] = int(totaltime)
    return(result)
"""
    
def update_info(infopath, newinfo):
    if os.path.exists(infopath):
        info = utils.readjson(infopath)
    else:
        info = {}
        
    for key, value in newinfo.items():
        info[key] = value
    with open(infopath, 'w') as f:
        json.dump(info, f, indent = 4)
        
def file_format(data_type, **kwargs):
    if data_type == 'multi unit':
        base = 'multiunit'
        if 'extend' in kwargs.keys():
            base = base + '_' + kwargs['extend']
    elif data_type == 'bf':
        base = 'bf'
    elif data_type == 'ECoG':
        base = 'ECoG'
    else:
        raise Exception('Does not have this type of experiment data')
        
    return(base+'.csv')    
    

# define all kinds of treatment in this section =================================================
# ===============================================================================================        
def treatment_csd(time = '', apply_method = 'pinprick'):
    treat = {}
    treat['method'] = 'CSD'
    if time != '':
        treat['time'] = time
        
    if apply_method == 'pinprick':
        treat['apply_method'] = apply_method
    else:
        raise Exception('This CSD method is not in the list')
        
    return(treat)
        
def treatment_baseline():
    return({"method": "baseline"})
    
def treatment_drug(activate_drug, concentration, apply_method):
    treat = {}
    treat['method'] = 'drug apply'
    treat['activate_drug'] = activate_drug
    treat['concentration'] = concentration
    treat['apply_method'] = apply_method

# ===============================================================================================        
