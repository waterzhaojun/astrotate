# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:17:59 2019

@author: jzhao1
"""
import os

import pandas as pd
import numpy as np
from astrotate import array, utils, treatment, config as cg
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

    
# ========================================================================================================================================
# ========================================================================================================================================
# Exp class build a class for a electrophysiology experiment. It should include information like animal, date, path where save the data, 
# animal treatment, and the experiment data 
# ========================================================================================================================================
# ========================================================================================================================================        
class Exp(cg.Experiment):
    """
    The reason to structure the 2P data based on animal, date, but not run is because each animal
    will only expect receive 1 treatment. Even has multiple treatment, the previous treatment will
    effect the later treatment. So it is hard to seperate treatment in each runs. So it will be better
    understand to give a total treatment list, and add all runs in one info.json, for each run, just need to 
    give a situation value to label it.
    """
    def __init__(self, config):
        super().__init__(config, 'electrophysiology')
        self.keys = ['animal', 'project', 'treatment']
        self.__date__()
        self.__setup_animal__()
        self.infopath = self.__setinfopath__(config)
        self.loadExp()

    def __setinfopath__(self, config):
        path = os.path.join(self.animalfolder, 'info.json')
        if not os.path.exists(path):
            exp = {}
            exp['animal'] = self.animal
            exp['project'] = utils.projectArrayInput(config)
            exp['treatment'] = {}
            utils.writejson(path, exp)
        return(path)

    def __date__(self):
        tmp = input('Exp date. Press ENTER for today. Otherwise, input mm/dd/yyyy: ')
        self.date = utils.format_date(tmp)

    def __setup_animal__(self):
        animaldict = {}
        datefolder = os.path.join(self.catagoryroot, datetime.strptime(self.date, '%m-%d-%Y').strftime('%y%m%d'))
        if not os.path.exists(datefolder):
            os.mkdir(datefolder)
        folders = os.listdir(datefolder)
        folders = [x for x in folders if '.' not in x]
        nanimal = len(folders)
        self.animalfolder = os.path.join(datefolder, 'animal_'+str(nanimal+1))
        if not os.path.exists(self.animalfolder):
            os.mkdir(self.animalfolder)
        animaldict['id'] = input('Input Animal id. Press ENTER for generate id by date: ')
        if animaldict['id'] == '':
            animaldict['id'] = datetime.strptime(self.date, '%m-%d-%Y').strftime('%Y%m%d') + '%02d' % (nanimal+1)
        animaldict['gender'] = utils.select('Animal gender: ', ['M', 'F'])
        animaldict['weight'] = int(input('Animal weight. unit is g. input an int: '))
        
        animaldict['brain_bloom'] = utils.select('Brain bloom? : ', ['N', 'Y'])
        animaldict['sub_bleeding'] = utils.select('Sub bleeding? : ', ['N', 'Y'])
        animaldict['ever_search_neuron'] = utils.select('Ever search neuron? : ', ['N', 'Y'])
        animaldict['give_oxygen'] = utils.select('Give oxygen? : ', ['N', 'Y'])
        
        animaldict['strain'] = utils.select('Strain : ', ['SD', 'C57'])
        if animaldict['strain'] in ['SD']:
            animaldict['species'] = 'rat'
        elif animaldict['strain'] in ['C57']:
            animaldict['species'] = 'mouse'
        
        self.animal = animaldict
    
    def add_treatment(self, newtreatment, allowRepeatTreat = False):
        # use this to add a new treatment to exp and update it to the json file in database. 
        # This should be done before you start to add data
        keys = self.treatment.keys()
        methods = [self.treatment[x]['method'] for x in keys]

        if (newtreatment['method'] in methods) and (not allowRepeatTreat):
            print('You sure you want to add this treatment? If yes, run this function again and set allowRepeatTreat = True')
        else:
            newkey = str(len(keys))
            self.treatment[newkey] = newtreatment
            self.writeExp()

    def add_data(self, dataObj):
        # use this to add a new data to exp and update it to the json file in database
        self.data.append(dataObj.output())
        self.writeExp()