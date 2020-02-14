import numpy as np
import pandas as pd
import os
from scipy.io import loadmat
# import matplotlib.pyplot as plt
# import math
from astrotate import array as ay, analysis, utils, config as cg, server, treatment
import copy
import shutil
import json

recording_types = ['WHEELRUNNING', 'FACEVIDEO']

def running_array(matpath, binsize):
    # This function is to read the array data from mat file by giving the path.
    
    array = loadmat(matpath)['speed_array'][0].astype(np.float)
    array = array[1:] - array[0:-1]
    
    # remove shake. =======================
    # shake happens when animal almost don't move but the bar edge up and down on the IR probe.
    # So the number can't be more than 2. 
    # Our stragety is to seperate the whole array to pieces by 2 as threshold.
    def __removeshake__(array):
        array_shake = (abs(array) == 1) * array
        shake_idx = np.where(array_shake != 0)[0]
        
        if len(shake_idx) > 1:
            for i in range(len(shake_idx)-1):
                array_shake[shake_idx[i]] = array_shake[shake_idx[i]] - array_shake[shake_idx[i+1]]
            array_shake[shake_idx[-1]] = array_shake[shake_idx[-1]] - array_shake[shake_idx[-2]]
            array = array* (array_shake == 0)
        return(array)
    
    pieceidx = np.where(abs(array) > 1)[0]
    pieceidx = np.concatenate(([0], pieceidx, [len(array)]))
    for i in range(len(pieceidx)-1):
        if len(array[pieceidx[i]:pieceidx[i+1]]) > 2:
            tmppiece = array[pieceidx[i]:pieceidx[i+1]]
            array[pieceidx[i]:pieceidx[i+1]] = __removeshake__(tmppiece)
    
    # bint the array
    array = abs(array)
    array2 = ay.bint1D(array, binsize) * binsize
    
    return(array2)

def get_bout(array, gap=2, duration=2, threshold=0):
    # The stragety is first fill the gap, then remove short bout by duration.
    
    array_01 = ((array>threshold)*1).astype(str)
    array_01 = ''.join(array_01)
    
    for i in range(1,gap):
        array_01 = array_01.replace('1'+'0'*i+'1', '1'+'1'*i+'1')
    array_01 = np.array(list(array_01)).astype(int)
        
    df = pd.DataFrame(columns = ['start', 'end', 'length', 'average', 'peak'])
    flag = 0
    
    for i in range(len(array_01)):
        if i != len(array_01)-1:
            if flag == 0 and array_01[i] == 1:
                flag = 1
                df.loc[len(df), 'start'] = i
            elif flag == 1 and array_01[i] == 0:
                flag = 0
                df.loc[len(df)-1, 'end'] = i-1
        else:
            if flag == 1:
                df.loc[len(df)-1, 'end'] = i-1+array_01[i]
                
    for i in range(len(df)):
        if df.loc[i,'end'] - df.loc[i, 'start'] < duration-1:
            df.drop(i, inplace = True)
            
    df.reset_index(inplace = True, drop = True)
    
    for i in range(len(df)):
        df.loc[i,'length'] = df.loc[i,'end']-df.loc[i,'start']+1
        tmp = array[df.loc[i,'start']:df.loc[i,'end']+1]
        df.loc[i,'average'] = np.mean(tmp)
        df.loc[i,'peak'] = np.max(tmp)
    #df.astype(int)
    return(df)



def label_running_array(array, pretreatdict, characters):
    # This function is the label each bout we got from the array by treatdict
    # characters is a dict should containing array frequency, time after last treatment with unit min
    # 
    df = get_bout(array)
    for i in range(len(df)):
        df.loc[i,'group'] = pretreatdict['method']
        df.loc[i,'time'] = int(characters['time_after_pretreat'] + df.loc[i,'start']/characters['freq']/60)
                
    return(df)

def build_result_wheelrunning(file,savefolder,pretreatdict,characters):
    # This function is to analyse an array and build a folder to put all related files in.
    # The result will by typed in database as wheelrunning.
    # The file should be a mat file.
    
    savefolder = os.path.join(savefolder,'wheelrunning')
    if not os.path.exists(savefolder):
        os.mkdir(savefolder)
    
    
    clean_array = running_array(file, characters['bint_size'])
    tmp = label_running_array(clean_array, pretreatdict, characters)
    tmp.loc[:,'trial'] = os.path.basename(file).split('.')[0]
    
    result_df_path = os.path.join(savefolder, 'result.csv')
    if os.path.exists(result_df_path):
        df = pd.read_csv(result_df_path,index_col = False)
        df = pd.concat([df,tmp])
    else:
        df = tmp
    df.to_csv(result_df_path, index = False)
    # shutil.move(file, savefolder)



# ==================================================================
# Analysis part ====================================================
# ==================================================================
def analyse_wheelrunning_df(df):
    """
    This function is to analysis behavior's WHEELRUNNING type df result.
    """
    res = {}
    res['running length'] = analysis.build_ttest_character(df['length'].values)
    res['average speed'] = analysis.build_ttest_character(df['average'].values)
    res['peak speed'] = analysis.build_ttest_character(df['peak'].values)
    
    return(res)


# ==================================================================
# Classes ==========================================================
# ==================================================================
class Parameter:

    def __init__(self, type = None):
        if type == None:
            self.type = utils.select('Which experiment: ', recording_types)
        else:
            self.type = type

        self.parameter = {}
        if self.type == 'WHEELRUNNING':
            self.parameter['freq'] = int(input('freqency of wheel running scanning rate like xxx hz. just input int part.'))

    def to_dict(self):
        return({self.type: self.parameter})

class Experiment(cg.Experiment):
    def __init__(self):
        super().__init__()
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT recording_types, path, parameters, treatment FROM bh_info
        WHERE animalid = %s and date = %s;
        """, (self.animalid, self.date)
        )
        exp = cur.fetchone()
        conn.commit()
        
        if exp == None:
            self.recording_types = utils.multi_select('Which experiment type: ', recording_types)
            self.path = os.path.join(self.animalid, self.date.strftime('%y%m%d'))
            self.parameters = {}
            for i in self.recording_types:
                self.parameters[i] = Parameter(i).parameter
            self.treatment = treatment.create_treatment_with_timepoint()

            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO bh_info 
            (animalid, date,parameters,path,recording_types,treatment,note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, 
            (self.animalid, self.date, json.dumps(self.parameters), self.path, 
            self.recording_types, json.dumps(self.treatment), self.note)
            )
            conn.commit()
        
        else:
            self.recording_types = exp[0]
            self.path = exp[1]
            self.parameters = exp[2]
            self.treatment = exp[3]

        conn.close()