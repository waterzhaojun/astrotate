# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:17:59 2019

@author: jzhao1
"""

# last update is 1/14/2020, I copy all function from google cloud.
# The steps to analyse is: query an infodf, .....(to be continue)

import os

import pandas as pd
import numpy as np
from astrotate import array, utils, treatment, config, analysis, server
import json
from datetime import datetime
import tkinter
from tkinter import filedialog

root = os.path.join(config.Config().system_path['root'], config.Config().system_path['electrophysiology'])


def check_channel_name(exp_folder, trialNum = None):
    files = os.listdir(exp_folder)
    files = [x for x in files if ((x[-4:] == '.txt') & (len(x.split('-'))>1))]
    if trialNum == None:
        file = os.path.join(exp_folder, files[-1])
    else:
        tmp = [x for x in files if x.split('-')[-1][:-4] == str(trialNum)]
        if len(tmp) == 1:
            file = os.path.join(exp_folder, tmp[0])
        else:
            raise Exception('There are %d files named %s' % (len(tmp), str(trialNum)))

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
    
def treatmentList(treatlist):
    treat = {}
    for i in range(len(treatlist)):
        treat[str(i)] = treatlist[i]
    return(treat)


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

# ===================================================================================== 
# query part ==========================================================================
# =====================================================================================
def get_exp_animal_list(tb_name):
    # This function is to extract a df containing exp info
    engine = server.server_engine()

    neurondf = pd.read_sql('SELECT * FROM %s' % tb_name, engine)
    animaldf = pd.read_sql('SELECT * FROM ep_info', engine)
    df = pd.merge(neurondf, animaldf, how='left', left_on='animalid', right_on='animalid')
    engine.dispose()
    return(df)

def extract_array_from_infodf(infodf, fn, paradict = None):
    # infodf may have many columns, but the following columns is necessary: id, group, data
    tmpdf = infodf.loc[:,'data'].map(lambda x: fn(x, paradict))
    for i in range(len(tmpdf)):
        tmp = np.reshape(tmpdf[i], [1,-1])
        if i == 0:
            array = tmp
        else:
            array = np.concatenate((array, tmp), axis = 0)
    
    return(array)


def get_method_key(treatdic, method, nth_key=0, **kwargs):
    """
    This function is to query the key for specific method you want to check by giving treatment dict.
    It might return multiple items. So you need to give the nth of the key, usually it is the first one.
    You may set nth_key to -1 to get the last one.
    For example, if you want the key when did CSD, write: get_method_key(treatdic, 'CSD')
    If you want the key when treated drug right before CSD, write: get_method_key(treatdic, 'drug apply', nth_key=-1, key_limit = csdkey)
    """
    csdkey = []
    for key, value in treatdic.items():
        if value['method'] == method:
            csdkey.append(key)
    
    csdkey = np.array(sorted([int(x) for x in csdkey]))

    if len(csdkey)>0:
        if kwargs.get('key_limit', False):
            csdkey = csdkey[csdkey < int(kwargs['key_limit'])]
        csdkey = str(csdkey[nth_key])
    else:
        csdkey = None

    return(csdkey)


def load_ep_data(path, treatpoint_dict, key, prepoints, postpoints):
    """
    This function is to read the ep data based on the path, treat point in the array, prepoints, postpoints
    """
    #print(path)
    treatpoint = treatpoint_dict[key]
    startpoint = treatpoint-prepoints
    endpoint = treatpoint+postpoints
    #print(treatpoint, startpoint, endpoint)

    if treatpoint < prepoints:
        raise Exception('not enough points before treatpoint')
    
    nextkey = str(int(key) + 1)
    if nextkey in treatpoint_dict.keys():
        if endpoint > treatpoint_dict[nextkey]:
            raise Exception('not enough points after treatpoint')

    x = np.array(np.loadtxt(path)[startpoint:endpoint])
    baseline = np.mean(x[0:prepoints])
    #print(len(x))
    #print(baseline)
    x_norm = x/baseline
    return({'array_ori':x, 'array_norm':x_norm, 'baseline':baseline})


# ================================================================================
# analyse part ========================================================================
# ================================================================================

# To analyse single neuron ep data extracted from database, a good sequence is as below:
# 1. use decode_singleneuron_xxxx function to analyse the data you extracted from database.
# 2. use singleneuron_analysis function to transfer the df to a dict containing all comparisons.

def singleneuron_array_analysis(array, baseline, ci, **kwargs):
    """
    This function is used to analyse whether the response period have increased activity by 
    giving the response array.

    The array should be only response period. No baseline required. 
    The length of the array should be what you want to analyse.
    baseline and ci are for baseline period.
    If you need to define the activation/sensitization should happen in some range like 1h, 
    you can use kwargs basic_range, set a number like 4 to test if it happen in first 4 numbers.
    the activation / sensitization standard is baseline + ci
    """
    
    array = np.array(array)
    array1 = array > (baseline + ci)
    array2 = np.append([0], array1[:-1])
    array3 = np.append(array1[1:], [array1[-1]*array1[-2]])
    array_final = ((array1 * array2 + array1 * array3) > 0) *1
    
    result = {'immediate': array[0]>baseline+ci,
              'longterm_activation': np.sum(array_final) > 0
             }
    
    if 'basic_range' in kwargs.keys():
        test_period = array_final[0:kwargs['basic_range']]
        result['longterm_activation'] = np.sum(test_period) > 0
        
    if result['longterm_activation']:
        result['delay'] = np.where(array_final == 1)[0][0]
        result['duration'] = np.sum(array_final)
        if baseline != 0:
            result['magnification'] = np.sum((array * array_final) / baseline)/result['duration']
        else:
            result['magnification'] = np.sum((array * array_final) / kwargs['alter_baseline'])/result['duration']
    else:
        result['delay'] = np.nan#None
        result['duration'] = np.nan#None
        result['magnification'] = np.nan#None
    
    return(result)
    
    

def decode_singleneuron_mech(data, key, rootpath, response_points = 8):
    # This function is to help you build data df based on the data extracted from database
    # data is a dict extract from database.
    # key is the treatment key.
    # response_points defines how many response points you want to analyze.
    result = {}
    result['filepath'] = os.path.join(rootpath, data['file_path'])
    result['data'] = np.loadtxt(result['filepath'], delimiter = ',')
    treatpoint = data['treat_point'][key]
    
    result['th_data'] = result['data'][treatpoint:treatpoint+response_points,0] 
    result['th_baseline'] = data['result'][key]['th_baseline']
    result['th_ci'] = data['result'][key]['th_ci']
    
    result['th_sensitization'] = data['result'][key]['neuron_sensitization_th_whe']
    if result['th_sensitization'] == 'Y':
        tmp = singleneuron_array_analysis(result['th_data'], result['th_baseline'], result['th_ci'], basic_range = 8)
        result['th_delay'] = tmp['delay']
        result['th_duration'] = tmp['duration']
        result['th_magnification'] = tmp['magnification']
        result['th_area'] = tmp['duration'] * tmp['magnification']
    else:
        result['th_delay'] = np.nan
        result['th_duration'] = np.nan
        result['th_magnification'] = np.nan
        result['th_area'] = np.nan
    
    result['sth_data'] = result['data'][treatpoint:treatpoint+response_points,1] 
    result['sth_baseline'] = data['result'][key]['sth_baseline']
    result['sth_ci'] = data['result'][key]['sth_ci']
    result['sth_sensitization'] = data['result'][key]['neuron_sensitization_sth_whe']
    if result['sth_sensitization'] == 'Y':
        tmp = singleneuron_array_analysis(result['sth_data'], result['sth_baseline'], result['sth_ci'], basic_range = 8)
        result['sth_delay'] = tmp['delay']
        result['sth_duration'] = tmp['duration']
        result['sth_magnification'] = tmp['magnification']
        result['sth_area'] = tmp['duration'] * tmp['magnification']
    else:
        result['sth_delay'] = np.nan
        result['sth_duration'] = np.nan
        result['sth_magnification'] = np.nan
        result['sth_area'] = np.nan
        
    return(result)

def decode_singleneuron_spon(data, key, rootpath, response_points = 18, **kwargs):
    """
    This function is to help you build data df based on the data extracted from database
    data is a dict extract from database.
    key is the treatment key.
    response_points defines how many response points you want to analyze.

    If you want to get a response period activity / sensitivity value, like time point 4 to
    time point 6 activity average value, set spon_activity_name_list which is the output label name list,
    and spon_activity_timepoint_list which is the required time points list (shape is n * 2).
    For sensitivity, you need to set th_value_name_list, th_value_timepoint_list, sth_value_name_list, 
    sth_value_timepoint_list.
    the element in timepoint_list should be [start, end] and count the sequence only in response period.
    """
    result = {}
    result['filepath'] = os.path.join(rootpath, data['file_path'])
    result['data'] = np.loadtxt(result['filepath'], delimiter = ',')
    treatpoint = data['treat_point'][key]
    
    result['res_data'] = result['data'][treatpoint:treatpoint+response_points] 
    result['baseline'] = data['result'][key]['neuron_activation_baseline_average']
    result['ci'] = data['result'][key]['neuron_activation_baseline_CI']

    if 'spon_activity_name_list' in kwargs.keys():
        if len(kwargs['spon_activity_name_list']) > 0:
            for i in len(kwargs['spon_activity_name_list']):
                result[kwargs['spon_activity_name_list'][i]] = result['res_data'][kwargs['spon_activity_timepoint_list'][i,0] : kwargs['spon_activity_timepoint_list'][i,1]] / result['baseline']
    
    try:
        result['immed_activation'] = data['result'][key]['neuron_immediate_activation']
    except:
        if result['res_data'][0] > (result['baseline'] + result['ci']):
            result['immed_activation'] = 'Y'
        else:
            result['immed_activation'] = 'N'
           
    result['activation'] = data['result'][key]['neuron_delay_activation']
    if result['activation'] == 'Y':
        tmp = singleneuron_array_analysis(result['res_data'], result['baseline'], result['ci'], basic_range = 12)
        result['act_delay'] = tmp['delay']
        result['act_duration'] = tmp['duration']
        result['act_magnification'] = tmp['magnification']
        result['act_area'] = tmp['duration'] * tmp['magnification']
    else:
        result['act_delay'] = np.nan
        result['act_duration'] = np.nan
        result['act_magnification'] = np.nan
        result['act_area'] = np.nan
        
    return(result)

def singleneuron_analysis(df):
    res = {}
    res['activation rate'] = analysis.build_chi_character(df['activation'].values)
    if 'immed_activation' in df.columns:
        res['immediate activation rate'] = analysis.build_chi_character(df['immed_activation'].values)

    try:
        res['activation duration'] = analysis.build_ttest_character(df['acti_duration'].values)
    except:
        pass

    try:
        res['activation delay'] = analysis.build_ttest_character(df['acti_delay'].values)
    except:
        pass

    try:
        res['activation magnitude'] = analysis.build_ttest_character(df['acti_magnitude'].values)
    except:
        pass

    res['threshold sensitization rate'] = analysis.build_chi_character(df['th'].values)
    res['threshold sensitization duration'] = analysis.build_ttest_character(df['th_duration'].values)
    res['threshold sensitization delay'] = analysis.build_ttest_character(df['th_delay'].values)
    res['threshold sensitization magnitude'] = analysis.build_ttest_character(df['th_magnitude'].values)
    res['super threshold sensitization rate'] = analysis.build_chi_character(df['sth'].values)
    res['super threshold sensitization duration'] = analysis.build_ttest_character(df['sth_duration'].values)
    res['super threshold sensitization delay'] = analysis.build_ttest_character(df['sth_delay'].values)
    res['super threshold sensitization magnitude'] = analysis.build_ttest_character(df['sth_magnitude'].values)
    
    try:
        res['activation AUC'] = analysis.build_ttest_character(df['area_activated'].values)
    except:
        pass
    
    res['threshold sensitization AUC'] = analysis.build_ttest_character(df['th_area_activated'].values)
    res['super threshold sensitization AUC'] = analysis.build_ttest_character(df['sth_area_activated'].values)

    tmp = [['N', 'Y'][(((x=='Y') + (y=='Y')) > 0)*1] for (x,y) in zip(df['th'].values, df['sth'].values) if x in ['Y', 'N'] and y in ['Y', 'N']]
    res['sensitization rate of any force'] = analysis.build_chi_character(np.array(tmp))

    tmp = [['N', 'Y'][(x=='Y') * (y=='Y')] for (x,y) in zip(df['th'].values, df['sth'].values) if x in ['Y', 'N'] and y in ['Y', 'N']]
    res['sensitization rate of both force'] = analysis.build_chi_character(np.array(tmp))

    tmp = [(x=='Y') + (y=='Y') for (x,y) in zip(df['th'].values, df['sth'].values) if x in ['Y', 'N'] and y in ['Y', 'N']]
    res['sensitization score'] = analysis.build_ttest_character(np.array(tmp))

    tmp = [x for x in df['th'].values if x in ['Y', 'N']] + [x for x in df['sth'].values if x in ['Y', 'N']]
    res['sensitization rate of each force'] = analysis.build_chi_character(np.array(tmp))
    return(res)
    
# ========================================================================================================================================
# ========================================================================================================================================
# Exp class build a class for a electrophysiology experiment. It should include information like animal, date, path where save the data, 
# animal treatment, and the experiment data 
# Different to Result class, Exp class is mainly to input the exp info. but Result class is to analyse the data.
# ========================================================================================================================================
# ========================================================================================================================================        
class Experiment():
    def __init__(self, animalid):

        self.animalid = animalid

        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT animalinfo, transgenic_id, date, note, weight, gender, species, strain, pilot, treatment FROM ep_info
        WHERE animalid = '{}';
        """.format(animalid)
        )
        animal = cur.fetchall()
        conn.commit()

        if len(animal) <1:
            self.gender = None

            self.transgenic_id = input('transgenic id: ')
            if self.transgenic_id != '':
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT gender from transgenic_animal_log
                    WHERE animalid = '{}'
                    """.format(self.transgenic_id)
                )
                tinfo = cur.fetchall()
                conn.commit()
                if len(tinfo) == 1:
                    self.gender = tinfo[0][0]
            
            if self.gender is None:
                self.gender = utils.select('Animal gender: ', ['M', 'F'])
            
            self.animalinfo = {}
            self.animalinfo['brain_bloom'] = utils.select('brain bloom? ', ['Y', 'N'], defaultChoose = 1)
            self.animalinfo['give_oxygen'] = utils.select('gave oxygen? ', ['Y', 'N'], defaultChoose = 0)
            self.animalinfo['sub_bleeding'] = utils.select('sub_bleeding? ', ['Y', 'N'], defaultChoose = 1)
            self.date = utils.format_date(datetime.strptime(animalid[-10:-2], '%Y%m%d').strftime('%m-%d-%Y'))
            self.weight = int(input('weight, input an integar (unit is g, jus integar like 330): '))
            self.species = utils.select('species: ', ['rat', 'mouse'])
            if self.species == 'rat':
                self.strain = utils.select('Strain: ', ['SD'])
            else:
                self.strain = utils.select('Strain: ', ['C57BL/6J'])
            self.pilot = utils.select('Is it a pilot experiment? ', ['Y', 'N'])
            self.pilot = self.pilot == 'Y'
            self.note = input('Any note? ')
            self.treatment = {}

            cur = conn.cursor()
            cur.execute(
                """
                INSERT into ep_info (animalid, animalinfo, transgenic_id, date, note, weight, gender, species, strain, pilot, treatment)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                """.format(self.animalid, json.dumps(self.animalinfo), self.transgenic_id, self.date,
                self.note, self.weight, self.gender, self.species, self.strain, self.pilot, json.dumps(self.treatment)
                )
            )
            conn.commit()
        elif len(animal) == 1:
            self.animalinfo = animal[0][0]
            self.transgenic_id = animal[0][1]
            self.date = utils.format_date(animal[0][2].strftime('%m-%d-%Y'))
            self.note = animal[0][3]
            self.weight = animal[0][4]
            self.gender = animal[0][5]
            self.species = animal[0][6]
            self.strain = animal[0][7]
            self.pilot = animal[0][8]
            self.treatment = animal[0][9]

        conn.close()

    def add_treatment(self):
        treatlen = len(self.treatment.keys())
        self.treatment[str(treatlen)] = treatment.choose_treatment()
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE ep_info
            SET treatment = '{}'
            WHERE animalid = '{}'
            """.format(json.dumps(self.treatment), self.animalid)
        )
        conn.commit()
        conn.close()

    def reset_treatment(self):
        self.treatment = {}
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE ep_info
            SET treatment = '{}'
            WHERE animalid = '{}'
            """.format(json.dumps(self.treatment), self.animalid)
        )
        conn.commit()
        conn.close()

    def delete_last_treatment(self):
        tlen = len(self.treatment.keys())
        del self.treatment[str(tlen-1)]
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE ep_info
            SET treatment = '{}'
            WHERE animalid = '{}'
            """.format(json.dumps(self.treatment), self.animalid)
        )
        conn.commit()
        conn.close()

    def add_data(self):
        # If need to add another data type in this function, two part (if/elif) need to update

        tkroot = tkinter.Tk()
        tkroot.withdraw()
        #root.update()
        folder_path = filedialog.askdirectory()
        tkroot.destroy()
        date_template = utils.format_date(self.date, '%b-%d-%y')
        filelist = os.listdir(folder_path)
        filelist = [os.path.join(folder_path, x) for x in filelist if date_template in x]
        filelist.sort()
        trials =[]
        channelnames = []
        for i in range(len(filelist)):
            tmp = [filelist[i].split('-')[-1]]#.split('.')[0]]
            contenttmp = pd.read_csv(filelist[i], sep = '\t', nrows = 1)
            tmp.append(list(contenttmp.columns))
            tmp.append(filelist[i])
            trials.append(tmp)
            channelnames = channelnames + list(contenttmp.columns)
        channelnames = list(set(channelnames))

        datatype = utils.select('Choose your data type: ', ['single neuron', 'multi unit', 'LFP', 'BF', 'ECoG', 'DC'])
        if datatype == 'multi unit':
            scanrate = 1
            savepath = os.path.join(root, 'MULTIUNIT', 'multi'+self.animalid[1:]+'.csv')
        elif datatype == 'BF':
            scanrate = 0.2
            savepath = os.path.join(root, 'BF', 'bf'+self.animalid[1:]+'.csv')
        elif datatype == 'DC':
            scanrate = 10
            savepath = os.path.join(root, 'DC', 'dc'+self.animalid[1:]+'.csv')

        channelname = utils.select('Choose the channel where your data come from: ', channelnames)
        output_freq = int(input('Your spike2 file output freq? (input an int): '))

        trials = [x for x in trials if channelname in x[1]]
        print(trials)
        data = []
        for i in range(len(trials)):
            tmp = list(array.bint1D(pd.read_csv(trials[i][2], sep='\t').loc[:,channelname].values, int(output_freq/scanrate)))
            data = data + tmp
            trials[i].append(len(tmp))

        # Each trials element is a list containing trial name, channel names, path, data length
        lengthlist = [x[3] for x in trials]
        treat_point = {}
        for key, value in self.treatment.items():
            tmptrial = utils.select('which trial for %s: %s' % (key, value['method']), [x[0] for x in trials])
            tmpsec = int(input('When did this treatment happen in trial %s (input the time by sec): ' % tmptrial))
            tmp = [x[0] for x in trials].index(tmptrial)
            #tmp = tmp
            treat_point[key] = int(sum(lengthlist[0:tmp])+tmpsec * scanrate)

        np.savetxt(savepath, data)

        conn = server.connect_server()
        if datatype == 'multi unit':
            cur = conn.cursor()
            cur.execute(
                """
                INSERT into ep_data_multiunit (animalid, treat_point, filepath, scanrate)
                VALUES ('{}', '{}', '{}', '{}')
                """.format(self.animalid, json.dumps(treat_point), os.path.basename(savepath), scanrate
                )
            )
            conn.commit()
        elif datatype == 'BF':
            cur = conn.cursor()
            cur.execute(
                """
                INSERT into ep_data_bf (animalid, treat_point, filepath)
                VALUES ('{}', '{}', '{}')
                """.format(self.animalid, json.dumps(treat_point), os.path.basename(savepath)
                )
            )
            conn.commit()
        elif datatype == 'DC':
            cur = conn.cursor()
            cur.execute(
                """
                INSERT into ep_data_dc (animalid, treat_point, filepath, scanrate)
                VALUES ('{}', '{}', '{}', '{}')
                """.format(self.animalid, json.dumps(treat_point), os.path.basename(savepath), scanrate
                )
            )
            conn.commit()

        conn.close()
        print(treat_point)

    
# ================================================================================================
# == Result class ================================================================================
# ================================================================================================# 
# Not ready yet
class Result():
    def __init__(self, type, df, feq):
        self.type=type
        self.df=df
        self.feq = feq
        self.result=None

    def create_result(self):
        return(1)
    

class Multiunit(Result):
    # the whole part of this class is not ready yet.
    def __init__(self, df, character):
        """
        df for Multiunit should be three columns df including: date, group, data.
        The data of each row should be an array.
        character is a dict 
        """
        super().__init__('multiunit', df, 1/character['bint'])
        self.character = character
        self.result=self.create_result()
        
    def create_result(self):
        result = {}
        peak_arrive_duration_array = np.array([])
        
        for i in range(len(self.df)):
            tmp = self.csd_period_analysis(self.df.loc[i, 'data'], self.character)
            # no need to calculate baseline, it's already normed
            peak_arrive_duration_array = np.append(peak_arrive_duration_array, tmp['peakpoint'])
            
        result['peak_arrive_duration'] = build_ttest_character(peak_arrive_duration_array)
        return(result)
        
    def csd_period_analysis(self, array, character_dict):
        # array is the raw data containing baseline and response period

        # character_dict is the dict containing informations including:
        # -- baseline length
        # -- estimated impossible duration after CSD. When measure the peak, this period will be ignored in case some super active noise happened.
        # -- analyse duration after peak. Define how long after peak will be analysed.
        # -- estimated CSD end timepoint after pinprick. The max timepoint of which CSD peak will be sure past the view, like 300 sec after pinprick.
        #array = signal.savgol_filter(array, window_length = 5, polyorder = 3)

        # post_peak_response is from peak point to the duration of we want to analysis
        # whole_timecourse is the whole duration from we wanted prepeak length to the after peak analysis length.

        bint = character_dict.get('bint', 1)

        tmpstart = character_dict['baseline_length'] + character_dict['estimated_impossible_duration']
        tmpend = character_dict['baseline_length'] + character_dict['estimated_csd_end_timepoint']
        peakpoint = np.argmax(array[tmpstart:tmpend]) + tmpstart
        after_peak_array = array[peakpoint+1+character_dict['analyse_duration_after_peak'][0]:peakpoint+1+character_dict['analyse_duration_after_peak'][1]]
        analysis_array = smooth(ay.bint1D(after_peak_array, bint))#, window_length = 5, polyorder = 3)
        result = {}
        result['peakpoint'] = peakpoint
        result['post_peak_response'] = analysis_array

        timecourse_start = peakpoint - character_dict['prepeak_length']
        timecourse_end = peakpoint + character_dict['analyse_duration_after_peak'][1]
        # print(peakpoint, timecourse_start, timecourse_end)
        result['whole_timecourse'] = smooth(ay.bint1D(array[timecourse_start: timecourse_end], bint))
        return(result)