import os
import pandas as pd
import numpy as np
from . import twop
from .. import array, utils, treatment, config as cg, analysis, server
import json
from datetime import datetime
import h5py
from pathlib import Path
import math
from scipy.io import loadmat
import copy
from .signal_treatment import *

# ROI analysis part =========================================================
def analyze_neuron_deconvolve_signal(array):
    # At the very beginning I wrote it to analyze astrocyte signal but didn't work. 
    # I will save it for neuron in the future.
    tmpa = array
    a = np.r_[False, tmpa[:-1] < tmpa[1:]] & np.r_[tmpa[:-1] > tmpa[1:], False]*1
    a_idx = np.where(a == 1)[0]
    a_max = np.array([])
    a_tao = np.array([])
    a_rising = np.array([])
    for k in a_idx:
        tmpmax = tmpa[k]
        a_max = np.append(a_max,tmpmax)
        j = 1
        while True:
            if tmpa[k+j]<tmpmax*0.37:
                a_tao = np.append(a_tao, j)
                break
            else:
                j = j+1
        j = 1
        while True:
            if tmpa[k-j]<tmpmax*0.37:
                a_rising = np.append(a_rising, j)
                break
            else:
                j = j+1
    return([a,a_idx,a_max,a_tao,a_rising])

def resultDic_roi(df, scanrate):
    # scanrate is how many frames per sec
    res = {}
    
    tmpmax = np.array([])
    tmpduration = np.array([])
    tmpfeq = np.array([])
    
    for i in range(len(df)):
        tmpmax = np.append(tmpmax, df.loc[i,'max'])
        tmpduration = np.append(tmpduration, df.loc[i,'duration'])
        tmpfeq = np.append(tmpfeq, df.loc[i, 'count']*scanrate/len(df.loc[i,'raw']))
    res['amplitude'] = analysis.build_ttest_character(tmpmax)
    res['duration'] = analysis.build_ttest_character(tmpduration)
    res['frequency'] = analysis.build_ttest_character(tmpfeq)
    
    return(res)

def readRoiData(path, standard, window_size, **kwargs):
    """
    align_baseline: Sometimes like CSD I need to align the baseline timecourse based on the peak. This is not
    a best way but can temperally solve the problem. Set it to true for CSD trial.
    
    align_range: if you do align the baseline by rising peak, you need to set this parameter to tell the range
    to search the peak around background rising peak. The default value is 60 as I think definitly csd will 
    cross the whole area in 4sec.
    
    """

    f = h5py.File(path)
    n = f['roivalues'].__getitem__('id').shape[0]
    df = pd.DataFrame(
        columns=[
            'id','type','raw','baseline','dff','deconvolve','count',
            'activation_idx_start','activation_idx_end','top_idx','max','duration'
        ]
    )
    res = {}
    background = f['background'][()].flatten()
    if kwargs.get('align_baseline', False):
        print('%s need baseline alignment' % path)
        background_risingpeak_idx = np.argmax(background[1:]-background[:-1])+1
        res['background_risingpeak_idx'] = background_risingpeak_idx
    for i in range(n):
        # It is such a headache that set array value to pd cell. So far I can only do build a new df then concat.
        tmp = pd.DataFrame(columns = df.columns).astype(np.object)
        tmp.loc[0,'id'] = f[f['roivalues'].__getitem__('id')[()][i,0]][()].tobytes()[::2].decode()
        tmp.loc[0,'type'] = f[f['roivalues'].__getitem__('type')[()][i,0]][()].tobytes()[::2].decode()
        if kwargs.get('align_baseline', False):
            tmparray = np.transpose(f[f['roivalues'].__getitem__('rawsignal')[()][i,0]]).flatten()
            tmp_peak_range = kwargs.get('align_range', 60) 
            tmparray_risingpeak = tmparray[background_risingpeak_idx-tmp_peak_range:background_risingpeak_idx+tmp_peak_range]
            tmpgap = np.argmax(tmparray_risingpeak[1:]-tmparray_risingpeak[:-1]) + 1 - tmp_peak_range
            print('No.%d roi adjusted %d timepoints' % (i,tmpgap))
            if tmpgap > 0:
                background_align = np.append(np.repeat([np.median(background[:10])], tmpgap), background[:-tmpgap])
            elif tmpgap < 0:
                background_align = np.append(background[-tmpgap:], np.repeat([np.median(background[-10:])], -tmpgap))
            else:
                background_align = background
            tmp.loc[0,'raw'] = tmparray - background_align
        else:
            tmp.loc[0,'raw'] = np.transpose(f[f['roivalues'].__getitem__('rawsignal')[()][i,0]]).flatten() - background
        (tmp.loc[0,'dff'],tmp.loc[0,'deconvolve'],tmp.loc[0,'baseline']) = deconvolve_astrocyte_signal(tmp.loc[0,'raw'], window_size, 0.3, **kwargs)
        tmptmp = analyze_astrocyte_deconvolve_signal(tmp.loc[0,'deconvolve'], standard)
        tmp.loc[0,'count'] = len(tmptmp[0])
        tmp.loc[0,'activation_idx_start'] = tmptmp[0]
        tmp.loc[0,'activation_idx_end'] = tmptmp[1]
        tmp.loc[0,'top_idx'] = tmptmp[3]
        tmp.loc[0,'max'] = tmptmp[2]
        tmp.loc[0,'duration'] = tmptmp[4]
        #df.loc[i,'tao'] = a_tao
        #df.loc[i,'rising_time'] = a_rising
        df = pd.concat([df, tmp],ignore_index = True)
        
    df.sort_values(by='id',inplace=True,ignore_index=True)
    res['background'] = background
    res['df'] = df
    return(res)

class Result_roi(analysis.Result):
    # This class analyze roi calcium signal. The roi should be in one trial that under same treatment.
    # If you want to analyze roi cross trial changes, please use RoiCrossTrialResult.
    # I suppose the df related trials have same scanrate, if not, I need to edit the code.
    def __init__(self, folderpath, group_title, scanrate, standard, window_size, **kwargs):
        self.scanrate = scanrate
        df = readRoiData(os.path.join(folderpath, 'result.mat'), standard, window_size, **kwargs)
        super().__init__(df,group_title)
        self.analyze()
        
    def label_signal(self,ax,i):
        value = self.df.loc[i,'raw']
        dev = self.df.loc[i,'deconvolve']
        ax.plot(value/np.median(value))
        ax.plot(dev,c='red')
        
        
    def analyze(self):
        # scanrate is how many frames per sec
        self.res = {}

        tmpmax = np.array([])
        tmpduration = np.array([])
        tmpfeq = np.array([])

        for i in range(len(self.df)):
            tmpmax = np.append(tmpmax, self.df.loc[i,'max'])
            tmpduration = np.append(tmpduration, self.df.loc[i,'duration'])
            tmpfeq = np.append(tmpfeq, self.df.loc[i, 'count']*self.scanrate/len(self.df.loc[i,'raw']))
        self.res['amplitude'] = analysis.build_ttest_character(tmpmax)
        self.res['duration'] = analysis.build_ttest_character(tmpduration)
        self.res['frequency'] = analysis.build_ttest_character(tmpfeq)
    
    def label_astrocyte_activation(self, ax):
        for i in range(len(self.df)):
            array = self.df.loc[i,'dff']
            ax.plot(array, color = 'gray', alpha = 0.5)

            for j in range(len(self.df.loc[i,'activation_idx'])):
                actx = np.arange(self.df.loc[i,'activation_idx'][j][0]-1, 
                                 self.df.loc[i,'activation_idx'][j][1]+1)
                actx = actx.astype(int)
                acty = array[actx]
                ax.plot(actx, acty, color = 'red')

class Result_csdtrial(analysis.Result):
    """
    The trial path is the single trial that did csd. 
    If you want to analyze csd response cross trials, please use another class.
    """
    def __init__(self,trialpath_array,group_title,standard,window_size,
                 prestart_points,poststart_points,**kwargs):
        tmpdf = pd.DataFrame(columns = [
            'trialid','id', 'type', 'start_idx','end_idx','duration','mag','peak_idx'
        ])

        for path in trialpath_array:
            [trialid,filepath] = self.trialid(path)
            tmpres = readRoiData(filepath,standard,window_size,**kwargs)
            df = tmpres['df']
            background_idx = tmpres['background_risingpeak_idx']
            
            for i in range(len(df)):
                curri = len(tmpdf)
                start_idx_array = np.absolute(df.loc[i,'activation_idx_start'] - background_idx)
                try:
                    csd_idx = np.argmin(start_idx_array)
                    tmpdf.loc[curri,'trialid'] = trialid
                    tmpdf.loc[curri,'id'] = df.loc[i,'id']
                    tmpdf.loc[curri,'type'] = df.loc[i,'type']
                    tmpdf.loc[curri,'start_idx'] = df.loc[i,'activation_idx_start'][csd_idx]
                    tmpdf.loc[curri,'end_idx'] = df.loc[i,'activation_idx_end'][csd_idx]
                    tmpdf.loc[curri,'duration'] = df.loc[i,'duration'][csd_idx]
                    tmpdf.loc[curri,'mag'] = df.loc[i,'max'][csd_idx]
                    tmpdf.loc[curri,'peak_idx'] = df.loc[i,'top_idx'][csd_idx]
                    tmparray = df.loc[i,'dff'][int(tmpdf.loc[curri,'start_idx']-prestart_points):int(tmpdf.loc[curri,'start_idx']+poststart_points)]
                    tmparray = np.reshape(tmparray, [1,-1])
                    if i == 0:
                        self.csd = tmparray
                        self.dff = np.reshape(df.loc[i,'dff'], [1,-1])
                        self.raw = np.reshape(df.loc[i,'raw'], [1,-1])
                    else:
                        self.csd = np.concatenate((self.csd, tmparray), axis = 0)
                        self.dff = np.concatenate((self.dff, np.reshape(df.loc[i,'dff'], [1,-1])), axis = 0)
                        self.raw = np.concatenate((self.raw, np.reshape(df.loc[i,'raw'], [1,-1])), axis = 0)
                except:
                    print('%s %d roi wrong, please check it' % (path, i))
        super().__init__(tmpdf,group_title)
        #self.analyze(['mag','duration'])
        
    def trialid(self,path):
        """
        This path is the folder path of the result.
        Based on the path, this function translate it to trial's id and filepath
        """
        filepath = os.path.join(path, 'result.mat')
        run = os.path.basename(path).split('_')[0]
        date = os.path.basename(os.path.dirname(path))
        animal = os.path.basename(os.path.dirname(os.path.dirname(path)))
        fileid = animal + '_' + date + '_' + run
        return(fileid, filepath)

    def analyze(self, columns):
        self.res = {}
        for c in columns:
            self.res[c] = analysis.build_ttest_character(self.df.loc[:,c])
        

class Result_roiCrossTrials(analysis.Result):
    # This class analyze roi calcium signal from continous trials. 
    # The signal is related with time course.
    # The trials are supoosed to have same scanrate.
    def __init__(self, folderpath_array, timepoint_array, group_title, scanrate, standard, window_size,**kwargs):
        # timepoint_array defines each result related trial's start time point before or after treatment.
        # The default unit for timepoint_array is min. If you want to use sec as unit, set unit='sec'
        # If it is right after treatment, the timepoint is 0, if it is 15 min before treatment, set it to -15.
        # If it is 30 min after treatment, set it to 30.
        # If some trials need to align baseline like the one did CSD, set it in align_baseline_trials.
        unit = kwargs.get('unit', 'min')
        if unit == 'min':
            timepoint_array = np.array(timepoint_array)*60
        elif unit == 'sec':
            timepoint_array = timepoint_array
        else:
            raise exception('Unknown unit. Please set it to min or sec')
        
        # scanrate should be uniqe to all results
        self.scanrate = scanrate
        
        print('Start to load data from MatLab file...')
        subdfs = [readRoiData(os.path.join(x, 'result.mat'), standard, window_size, align_baseline = (x in kwargs.get('align_baseline_trials', []))) for x in folderpath_array]
        print('Loading finished')
        
        # All subdf should have the same length and same id order. I don't consider diffent length and order situation right now.
        passcheck = True
        for i in range(1,len(subdfs)):
            passcheck = np.array_equal(subdfs[0].loc[:,'id'], subdfs[i].loc[:,'id'])
        if not passcheck:
            raise Exception('All subdf should have the same length and same id order.')
        
        df = pd.DataFrame(columns = np.append(subdfs[0].columns, ['start_tp'])) 
        # 'start_tp' is the time point when the activation happens.
        # it refers to the treatment time as 0.
        df.id = subdfs[0].id
        df.type = subdfs[0].type
        length_array = [len(x.loc[0,'raw']) for x in subdfs] # all rois in one df should have same length.
        n_of_df = len(df)
        for i in range(n_of_df):
            print('Start to analyze roi %d/%d' % (i,n_of_df-1))
            for j in range(len(subdfs)):
                if j == 0:
                    df.loc[i,'raw'] = subdfs[j].loc[i,'raw']
                    df.loc[i,'baseline'] = subdfs[j].loc[i,'baseline']
                    df.loc[i,'dff'] = subdfs[j].loc[i,'dff']
                    df.loc[i,'deconvolve'] = subdfs[j].loc[i,'deconvolve']
                    df.loc[i,'count'] = np.array(subdfs[j].loc[i,'count'])
                    df.loc[i,'max'] = subdfs[j].loc[i,'max']
                    df.loc[i,'duration'] = subdfs[j].loc[i,'duration']
                    df.loc[i,'activation_idx_start'] = subdfs[j].loc[i,'activation_idx_start'] + np.sum(length_array[:j])
                    df.loc[i,'activation_idx_end'] = subdfs[j].loc[i,'activation_idx_end'] + np.sum(length_array[:j])
                    df.loc[i,'top_idx'] = subdfs[j].loc[i,'top_idx']
                    df.loc[i,'start_tp'] = subdfs[j].loc[i,'activation_idx_start']/scanrate + timepoint_array[j]

                else:
                    df.loc[i,'raw'] = np.append(df.loc[i,'raw'], subdfs[j].loc[i,'raw'])
                    df.loc[i,'baseline'] = np.append(df.loc[i,'baseline'], subdfs[j].loc[i,'baseline'])
                    df.loc[i,'dff'] = np.append(df.loc[i,'dff'], subdfs[j].loc[i,'dff'])
                    df.loc[i,'deconvolve'] = np.append(df.loc[i,'deconvolve'], subdfs[j].loc[i,'deconvolve'])
                    df.loc[i,'count'] = np.append(np.array(df.loc[i,'count']), np.array(subdfs[j].loc[i,'count']))
                    df.loc[i,'max'] = np.append(df.loc[i,'max'], subdfs[j].loc[i,'max'])
                    df.loc[i,'duration'] = np.append(df.loc[i,'duration'], subdfs[j].loc[i,'duration'])

                    df.loc[i,'activation_idx_start'] = np.append(
                        df.loc[i,'activation_idx_start'], 
                        subdfs[j].loc[i,'activation_idx_start'] + np.sum(length_array[:j])
                    )
                    df.loc[i,'activation_idx_end'] = np.append(
                        df.loc[i,'activation_idx_end'], 
                        subdfs[j].loc[i,'activation_idx_end']+np.sum(length_array[:j])
                    )
                    df.loc[i,'top_idx'] = np.append(
                        df.loc[i,'top_idx'], 
                        subdfs[j].loc[i,'top_idx']+np.sum(length_array[:j])
                    )

                    #tmpstart = np.array([x[0] for x in df.loc[i,'activation_idx_start'].values if len(x)>0]) 
                    df.loc[i,'start_tp'] = np.append(
                        df.loc[i,'start_tp'], 
                        subdfs[j].loc[i,'activation_idx_start']/scanrate + timepoint_array[j]
                    )
            print('analyze done')
        super().__init__(df,group_title)
        #self.create_activity_df()
        #self.analyze()
        
    def create_activity_df(self):
        activity_df = pd.DataFrame(columns= ['start_idx', 'end_idx', 'start_tp', 'duration', 'magnitude'])
        for i in range(len(self.df)):
            for j in range(len(self.df.loc[i,'max'])):
                k = len(activity_df)
                activity_df.loc[k,'start_idx'] = self.df.loc[i,'activation_idx'][j][0]
                activity_df.loc[k,'end_idx'] = self.df.loc[i,'activation_idx'][j][1]
                activity_df.loc[k,'start_tp'] = self.df.loc[i,'start_tp'][j]
                activity_df.loc[k,'duration'] = self.df.loc[i,'duration'][j]
                activity_df.loc[k,'magnitude'] = self.df.loc[i,'max'][j]
        #self.activity_df = activity_df
        return(activity_df)
        
    def analyze(self):
        self.res = {}
        # need to analyze CSD peak magnitude, duration
        # baseline period activity average duration, mag, count
        # A1 period average duration, mag, count
        
        #tmpmax = np.array([])
        #tmpduration = np.array([])
        #tmpfeq = np.array([])

        #for i in range(len(self.df)):
        #    tmpmax = np.append(tmpmax, self.df.loc[i,'max'])
        #    tmpduration = np.append(tmpduration, self.df.loc[i,'duration'])
        #    tmpfeq = np.append(tmpfeq, self.df.loc[i, 'count']*self.scanrate/len(self.df.loc[i,'raw']))
        #self.res['amplitude'] = analysis.build_ttest_character(tmpmax)
        #self.res['duration'] = analysis.build_ttest_character(tmpduration)
        #self.res['frequency'] = analysis.build_ttest_character(tmpfeq)