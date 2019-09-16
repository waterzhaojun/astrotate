import os
import pandas as pd
import numpy as np
# from . import array, utils, treatment, config as cg
from astrotate import array, utils, treatment, config as cg
import json
import scipy.stats as stats
from datetime import datetime
import h5py
from pathlib import Path
import math
import matplotlib.pyplot as plt

objective = {'Nikon': ['16X']}
magnitude_list = [0.8, 1, 2.0, 2.4, 4.0, 4.8, 5.7]
datatype = ['astrocyte_event', 'GCaMP_afferent']


def folder_format(animalid, date, run):
    out = animalid + '_' + str(date) + '_run' + str(run)
    return(out)


def readAquaData(path):
    # This path is the folder path when output from AQuA.
    # Now I will use the excel file as the source of the result.
    # the result is a pandas dataframe
    #mfile = pd.h5py.File(path, 'r')['res']['featureTable']
    path = Path(path)
    foldername = os.path.basename(path)
    filename = foldername + '_AQuA.xlsx'
    filepath = os.path.join(path, filename)
    tmp = pd.read_excel(filepath, 'Sheet1', header = None)
    df = pd.DataFrame(columns = tmp.loc[:,0].values)
    nrow = len(tmp.columns)
    for i in range(nrow-1):
        df.loc[i, :] = tmp.loc[:,i+1].values
    return(df)

def astrocyte_event_aqua_ana(df):
    # the input df suppose come from aqua
    def __meanStdeArray__(df, colname):
        tmp = {}
        tmp['mean'] = np.mean(df.loc[:, colname])
        tmp['stdev'] = np.std(df.loc[:, colname])/math.sqrt(len(df.loc[:, colname].values))
        tmp['array'] = df.loc[:, colname].values
        return(tmp)

    result = {}
    result['nEvent'] = len(df)
    result['area'] = __meanStdeArray__(df, 'Basic - Area')
    result['perimeter'] = __meanStdeArray__(df, 'Basic - Perimeter')
    result['max dff'] = __meanStdeArray__(df, 'Curve - Max Dff')
    result['duration_50_to_50'] = __meanStdeArray__(df, 'Curve - Duration 50% to 50%')
    result['duration_10_to_10'] = __meanStdeArray__(df, 'Curve - Duration 10% to 10%')
    result['rising_duration_10_to_90'] = __meanStdeArray__(df, 'Curve - Rising duration 10% to 90%')
    result['decaying_duration_90_to_10'] = __meanStdeArray__(df, 'Curve - Decaying duration 90% to 10%')
    result['decay_tau'] = __meanStdeArray__(df, 'Curve - Decay tau')
    result['propagation_onset_overall'] = __meanStdeArray__(df, 'Propagation - onset - overall')
    result['propagation_onset_anterior'] = __meanStdeArray__(df, 'Propagation - onset - one direction - Anterior')
    result['propagation_onset_posterior'] = __meanStdeArray__(df, 'Propagation - onset - one direction - Posterior')
    result['propagation_onset_left'] = __meanStdeArray__(df, 'Propagation - onset - one direction - Left')
    result['propagation_onset_right'] = __meanStdeArray__(df, 'Propagation - onset - one direction - Right')
    result['propagation_offset_overall'] = __meanStdeArray__(df, 'Propagation - offset - overall')
    result['propagation_offset_anterior'] = __meanStdeArray__(df, 'Propagation - offset - one direction - Anterior')
    result['propagation_offset_posterior'] = __meanStdeArray__(df, 'Propagation - offset - one direction - Posterior')
    result['propagation_offset_left'] = __meanStdeArray__(df, 'Propagation - offset - one direction - Left')
    result['propagation_offset_right'] = __meanStdeArray__(df, 'Propagation - offset - one direction - Right')
    result['network_temporal_density'] = __meanStdeArray__(df, 'Network - Temporal density')
    result['network_temporal_density_similar_size'] = __meanStdeArray__(df, 'Network - Temporal density with similar size only')
    result['network_spatial_density'] = __meanStdeArray__(df, 'Network - Spatial density')
    
    return(result)

def astrocyte_event_aqua_ana_between_groups(result_array, group_titles):
    # the result input is the output from astrocyte_event_aqua_ana function
    keys = list(result_array[0].keys())
    # group1 = []
    # group1_err = []
    # group2 = []
    # group2_err = []
    # xlabel = []
    for key in keys[1:]:
        print(key)
        p = stats.mannwhitneyu(np.array(result1[key]['array']).astype(float), np.array(result2[key]['array']).astype(float))
        # group1.append(result1[key]['mean'])
        # group1_err.append(result1[key]['stdev'])
        # group2.append(result2[key]['mean'])
        # group2_err.append(result2[key]['stdev'])
        # xlabel.append(key)
        fig, ax = plt.subplots()
        width = 0.2
        for ra in result_array:
            ax.bar(0.5 - width/2, ra[key]['mean'], width, yerr = ra[key]['stdev'])
            
        ax.set_title(key)
        ax.legend(group_titles)
        plt.show()
        print(p)
        print('=======================================================')
        
    

def input_data_info(animalid, date, run, datatype):
    data = {}
    datatype = utils.select('Choose data type: ', datatype)
    
    if datatype == 'astrocyte_event':
        data['path'] = folder_format(animalid, date, run)+'_AstrocyteEvent.mat'


# =======================================================================================================================================================
# =======================================================================================================================================================
# Data class is an object for two photon data. It contains the information how the data was recorded, under which situation when the animal experiencing 
# test, the setting of scanbox.
# =======================================================================================================================================================
# =======================================================================================================================================================
class Data:
    def __init__(self, exp, run):
        self.rawfolder = self.__date_format__(exp.date) + '_' + exp.animalid +'_run' + str(run)
        self.coordinates = self.input_coords()
        self.objective_lens = self.select_objective()
        self.input_scanbox()
        self.input_situation(exp)

    def __date_format__(self, datestr):
        return(datetime.strptime(datestr, '%m-%d-%Y').strftime('%y%m%d'))

    def select_objective(self):
        oblist = list(objective.keys())
        if len(oblist) > 1:
            ob = utils.select('Select the objective you are using: ', oblist)
        else:
            ob = oblist[0]

        maglist = objective[ob]
        if  len(maglist) > 1:
            mag = utils.select('Select your %s magnitude: ' % ob, maglist)
        else:
            mag = maglist[0]

        return({'brand': ob, 'mag': mag})

    def input_coords(self):
        ref = utils.select('Please choose the ref direction: ', ['N', 'S', 'E', 'W'])
        coords = input('Please input the coordinates value, seperated by ",": ').replace(' ', '').split(',')
        coords = [int(x) for x in coords]
        return({'coords': coords, 'ref': ref})

    def input_scanbox(self):
        self.laser_power = int(input('Laser power (just int part, no %): '))
        self.pmt0 = float(input('PMT 0 value: '))
        self.pmt1 = float(input('PMT 1 value: '))
        self.duration = str(int(input('Record duration (how many minutes, no unit, int): ')))+'min'
        
        tmp = input('Scan rate (Press Enter for default 15.5): ')
        if tmp == '':
            self.scanrate = 15.5
        else:
            self.scanrate = float(tmp)
            
        tmp = input('opto scanning volumn number (int, Press ENTER for 1): ')
        if tmp == '':
            self.volumn = 1
        else:
            self.volumn = int(tmp)
            
        self.magnitude = float(utils.select('magnitude: ', magnitude_list))
        
    def input_situation(self, exp):
        t = []
        for key, value in exp.treatment.items():
            t.append([key, value])
        tarr = [str(x[0])+': '+x[1]['method'] for x in t]
        self.situation = {}
        self.situation['treatment'] = utils.select('Select the situation which this data is experiencing: ', tarr).split(':')[0]
        self.situation['time_after_treatment'] = input('How long under this situation (consider the beginning of the trial. unit is min. int): ')+'min'

    def output(self):
        ot = self.__dict__
        return(ot)

# ========================================================================================================================================
# ========================================================================================================================================
# Exp2P class build a clas for a two photon experiment. It should include information like animal id, date, path where save the data, 
# animal treatment, and the experiment data 
# ========================================================================================================================================
# ========================================================================================================================================        
class Exp2P(cg.Experiment):

    def __init__(self, config, animalid, dateid):
        super().__init__(config)
        self.animalid = animalid
        self.date = utils.format_date(datetime.strptime(dateid, '%y%m%d').strftime('%m/%d/%Y'))
        self.mainfolder = os.path.join(self.root, config.system_path['twophoton'])

        self.animalfolder = os.path.join(self.mainfolder, animalid)
        if not os.path.exists(self.animalfolder):
            os.mkdir(self.animalfolder)

        self.expfile = os.path.join(self.animalfolder, str(dateid)+'.json')
        if not os.path.exists(self.expfile):
            exp = {}
            exp['project'] = utils.projectArrayInput(config)
            exp['treatment'] = {}
            exp['data'] = []
            utils.writejson(self.expfile, exp)
        self.loadExp()

    def loadExp(self):
        tmp = utils.readjson(self.expfile)
        self.project = tmp['project']
        self.treatment = tmp['treatment']
        self.data = tmp['data']
    
    def writeExp(self):
        tmp = {'project': self.project, 'treatment':self.treatment, 'data':self.data}
        utils.writejson(self.expfile, tmp)

    
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

