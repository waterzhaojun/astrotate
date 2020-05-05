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
from astrotate import array as ay, utils, treatment, config, analysis, server
import json
from datetime import datetime
import tkinter
from tkinter import filedialog

root = os.path.join(config.Config().system_path['root'], config.Config().system_path['electrophysiology'])

def trialnum(path):
    # Each file saved in the EP system has a name format.
    # This function is to get the path's trial num. 
    path = os.path.basename(path)
    trial = path.split('.')[0].split('-')[-1]
    return(trial)

def check_channel_name(exp_folder, trialNum = None):
    # you can provide a folder path or a file path.
    if os.path.isfile(exp_folder):
        file = exp_folder
    else:
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
        values = ay.bint1D(values, int(scanRate/outputRate), setint = intvalue)
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

def get_array_from_file(file, channel, **kwargs):
    # Different to get_array function, this function is a simple version.
    # Just give path, channel name, scanrate to extract data.
    # kickout_period is an option. it is a list, each element is a list containing 2 value (start sec, end sec).
    # I think this is a better way to code. I will depricate get_array in the future.
    # scanRate means how many value in one sec. it is Hz.
    # output_bin means each value represent how many seconds. it is opposite to scanRate.
    df = pd.read_csv(file, sep = '\t')
    values = df.loc[:, channel].values
    values = values[~np.isnan(values)]
    if 'kickout_period' in kwargs.keys():
        scanRate = kwargs['scanRate']
        period = np.array(kwargs['kickout_period'])
        kickrange = np.array([])
        for i in range(len(period)):
            start = period[i,0]
            end = period[i,1]
            kickrange = np.append(kickrange, np.arange(start*scanRate,end*scanRate))
        kickrange = np.unique(kickrange).astype(int)
        values = np.delete(values, kickrange)
    if 'output_bin' in kwargs.keys():
        values = ay.bint1D(values, kwargs['scanRate']*kwargs['output_bin'])
    return(values)
    
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
    
    data = np.loadtxt(path, delimiter = ',')
    if len(np.shape(data)) == 1:
        x = np.array(data[startpoint:endpoint])
        baseline = np.mean(x[0:prepoints])
        x_norm = x/baseline
    elif len(np.shape(data)) == 2:
        x = np.array(data[startpoint:endpoint,:])
        baseline = np.mean(x[0:prepoints], axis = 0)
        x_norm = x/baseline
    
    if prepoints == 0:
        return({'array_ori':x})
    else:
        return({'array_ori':x, 'array_norm':x_norm, 'baseline':baseline})

    
# ===========================================================================================
# ====== polt part ==========================================================================
# ===========================================================================================
def timecourse(array, ax, **kwargs):
        
    mean_array = np.mean(array, axis = 0)  
    error_array = np.std(array, axis = 0)/np.shape(array)[0]
    
    marker = kwargs.get('marker', '.')
    alpha = kwargs.get('alpha', 0.5)
    color = kwargs.get('color', 'gray')
    timecourse_xlabels = kwargs.get('xticks', np.arange(np.shape(array)[1]))

    ax.errorbar(
        timecourse_xlabels, mean_array, yerr=error_array, alpha = alpha, color = color,
        marker = marker, ms=1
    )#, fmt='|')
    


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
            tmp = list(ay.bint1D(pd.read_csv(trials[i][2], sep='\t').loc[:,channelname].values, int(output_freq/scanrate)))
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
    def __init__(self, type, querydf):
        self.type = type
        self.querydf = querydf.reset_index(drop=True)
        self.animalid = self.querydf.animalid.values
        tmp = list(set(self.querydf.group.values))
        if len(tmp) != 1:
            raise Exception('This class suppose the querydf contains only one group data. Please check it.')
        else:
            self.group = tmp[0]
        #self.feq = feq
        #self.result = None

    def create_result(self):
        return(1)
    
    def extract_array_from_infodf(self, fn, paradict = None):
        # infodf may have many columns, but the following columns is necessary: id, group, data
        tmpdf = self.querydf.loc[:,'data'].map(lambda x: fn(x, paradict))
        for i in range(len(tmpdf)):
            tmp = np.reshape(tmpdf[i], [1,-1])
            if i == 0:
                array = tmp
            else:
                array = np.concatenate((array, tmp), axis = 0)
        return(array)