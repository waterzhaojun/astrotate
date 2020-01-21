# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:17:59 2019

@author: jzhao1
"""

# last update is 1/14/2020, I copy all function from google cloud.

import os

import pandas as pd
import numpy as np
from astrotate import array, utils, treatment, config, analysis, server
import json
from datetime import datetime

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


# the following part come from info.py. Now as this info is only used in ep, so I merge them in ep.py
# ===============================================================================================
def getInfoList(rootPath):
    folders = os.listdir(rootPath)
    folders = [os.path.join(rootPath, x) for x in folders]
    folders = [x for x in folders if os.path.isdir(x)]
    animalfolders = []
    for f in folders:
        tmp = [os.path.join(f, x, 'info.json') for x in os.listdir(f)]
        animalfolders = animalfolders + tmp
    
    animalfolders = [x for x in animalfolders if os.path.exists(x)]
    return(animalfolders)

def getListWithExpType(rootPath, expType):
    infoList = getInfoList(rootPath)
    finalList = []
    for i in infoList:
        try:
            tmp = utils.readjson(i)
            if expType in tmp.keys():
                finalList.append(i)
        except:
            print('%s has problem, fail to load' % i)
    return(finalList)

def getInfoContent(rootPath, keyarray):
        
    animalfolders = getInfoList(rootPath)
    result = []
    for f in animalfolders:
        info = utils.readjson(f)
        try:
            finalc=info
            for k in keyarray:
                finalc = finalc[k]
            result.append([f, finalc])
        except:
            pass
        
    return(result)

def checkTreatmentDrug(treatArrayList):
    finalList = []
    for treat in treatArrayList:
        for t in treat[1].keys():
            try:
                if 'drug apply' == treat[1][t]['method']:
                    finalList.append([treat[0], treat[1][t]['activate_drug']])
            except:
                pass
    return(finalList)


def treatmentMethod(info, method):
    treatment = info['treatment']
    thekey = []
    thedict = []
    for key, value in treatment.items():
        if value['method'] == method:
            thekey.append(key)
            thedict.append(value)
    if len(thekey) == 0:
        thekey = [None]
        thedict = [{}]
    elif len(thekey) > 1:
        raise Exception('No or more than 1 this method treatment')
    return(thekey[0], thedict[0])

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
            result['magnification'] = (array * array_final) / kwargs['alter_baseline']
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
# ========================================================================================================================================
# ========================================================================================================================================        
class Exp(config.Experiment):
    """
    The reason to structure the 2P data based on animal, date, but not run is because each animal
    will only expect receive 1 treatment. Even has multiple treatment, the previous treatment will
    effect the later treatment. So it is hard to seperate treatment in each runs. So it will be better
    understand to give a total treatment list, and add all runs in one info.json, for each run, just need to 
    give a situation value to label it.
    """
    def __init__(self, animalid, cgobj):
        self.__keys__ = ['animalid', 'animalinfo', 'date', 'project', 'treatment', 'note']
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT {} FROM ep_info
        WHERE animalid = '{}';
        """.format(', '.join(self.__keys__), animalid)
        )
        animal = cur.fetchall()
        conn.commit()

        if len(animal) == 0: # need to build new animal info
            self.animalid = animalid
            self.animalinfo = {}
            self.animalinfo['species'] = utils.select('Choose animal strain: ', ['rat', 'mouse'])
            if self.animalinfo['species'] == 'rat':
                self.animalinfo['strain'] = 'SD'
            elif self.animalinfo['species'] == 'mouse':
                self.animalinfo['strain'] = utils.select('What is the strain: ', ['C57'])

            self.animalinfo['transgenic_id'] = input('transgenic db id. Press ENTER to ignore: ')
            if self.animalinfo['transgenic_id'] != '':
                cur = conn.cursor()
                cur.execute(
                """
                SELECT dob,gender FROM transgenic_animal_log
                WHERE animalid = '{}';
                """.format(self.transgenic_id)
                )
                dob = cur.fetchall()
                conn.commit()
                self.animalinfo['birthday'] = dob[0][0]
                self.animalinfo['gender'] = dob[0][1]
            else:
                tmp = input('Animal birthday (format month-day-year). Press ENTER to ignore: ')
                if tmp != '':
                    self.animalinfo['birthday'] = utils.format_date(tmp)
                else:
                    self.animalinfo['birthday'] = None
                self.animalinfo['gender'] = utils.select('Choose animal gender: ', ['M', 'F'], defaultChoose = 0)

            self.animalinfo['weight'] = int(input('Animal weight. unit is g. input an int: '))
            
            self.animalinfo['brain_bloom'] = utils.select('Brain bloom? : ', ['N', 'Y'], defaultChoose = 0)
            self.animalinfo['sub_bleeding'] = utils.select('Sub bleeding? : ', ['N', 'Y'], defaultChoose = 0)
            self.animalinfo['ever_search_neuron'] = utils.select('Ever search neuron? : ', ['N', 'Y'], defaultChoose = 0)
            self.animalinfo['give_oxygen'] = utils.select('Give oxygen? : ', ['N', 'Y'], defaultChoose = 1)
            
            self.date = utils.format_date(input('Exp date. Press ENTER for today. Otherwise, input mm/dd/yyyy: '))

            self.project = utils.projectArrayInput(cgobj)

            tmp = input('Any note?')
            if tmp != '':
                self.note = tmp
            else:
                self.note = None

            # add the new animal in database
            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO ep_info
            (animalid, animalinfo, date, project, note) 
            VALUES (%s, %s, %s, %s, %s)
            """, (self.animalid, json.dumps(self.animalinfo), self.date, self.project, self.note)
            )
            conn.commit()
            

        elif len(animal) == 1: # load animal info
            for i in range(len(self.__keys__)):
                setattr(self, self.__keys__[i], animal[0][i])

        conn.close()

    

    def add_data(self, dataObj):
        # use this to add a new data to exp and update it to the json file in database
        self.data.append(dataObj.output())
        self.writeExp()