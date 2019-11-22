import os
import pandas as pd
import numpy as np
# from . import array, utils, treatment, config as cg
from astrotate import array, utils, treatment, config as cg, analysis, server
import json
from datetime import datetime
# import h5py
from pathlib import Path
import math


objective = {'Nikon': ['16X']}
magnitude_list = [0.8, 1, 2.0, 2.4, 4.0, 4.8, 5.7]


def folder_format(animalid, date, run):
    out = str(date) + '_' + animalid + '_run' + str(run)
    return(out)

# aqua analysis part ========================================================
def readAquaData(path):
    # This path is the folder path when output from AQuA.
    # Now I will use the excel file as the source of the result.
    # the result is a pandas dataframe
    
    tmp = pd.read_excel(path, 'Sheet1', header = None, index_col=None)
    df = pd.DataFrame(columns = tmp.loc[:,0].values)
    nrow = len(tmp.columns)
    for i in range(nrow-1):
        df.loc[i, :] = tmp.loc[:,i+1].values
    return(df)

def groupAquaData(pathlist):
    kickout_columns = ['Index'] # this list need manully change based on AQuA features.
    res = {'n_of_events':{'array':np.array([])}}

    if isinstance(pathlist, list):
        for i in range(len(pathlist)):
            if i == 0:
                df = readAquaData(pathlist[i])
                res['n_of_events']['array'] = np.append(res['n_of_events']['array'], len(df))
            else:
                tmp = readAquaData(pathlist[i])
                df = pd.concat([df, tmp])
                res['n_of_events']['array'] = np.append(res['n_of_events']['array'], len(tmp))
    elif isinstance(pathlist, str):
        df = readAquaData(pathlist)
        res['n_of_events']['array'] = np.append(res['n_of_events']['array'], len(df))
            
    res['n_of_events'] = analysis.group_value_to_dict_element(res['n_of_events']['array'])
    res['n_of_events']['analysis_method'] = ['box']
    
    res['event_character'] = {'character_columns': ['Basic - Area', 'Curve - Duration 50% to 50%', 'Curve - Max Dff']}
    res['event_character']['array'] = df[res['event_character']['character_columns']].values.tolist()
    res['event_character']['analysis_method'] = ['scatter']

    cname = df.columns
    cname = [x for x in cname if x not in kickout_columns]
    for i in cname:
        try:
            res[i] = analysis.group_value_to_dict_element(df.loc[:,i].values)
            res[i]['analysis_method'] = ['box']
        except:
            pass
    return(res)


def aquaStruct(foldername):
    res = dict()
    res['excel'] = os.path.join(foldername, 'FeatureTable.xlsx') 
    res['mov'] = os.path.join(foldername, 'Movie.tif')
    res['paras'] = os.path.join(foldername, 'aqua_parameters.yml')
    return(res)

# ===================================================================
# query part 
def get_twop_animals(cgobj):
    # This function is to return a list of animals that had two photon experiment.
    twoproot = os.path.join(cgobj.system_path['root'], cgobj.system_path['twophoton'])
    animals = os.listdir(twoproot)
    # animals = [os.path.join(twoproot, x) for x in animals]
    animals = [x for x in animals if os.path.isdir(os.path.join(twoproot, x))]
    animals_path = [os.path.join(twoproot, x) for x in animals]
    return(animals, animals_path)

def get_animal_twop_explist(animallist, cgobj):
    animallist = utils.confirm_array_input(animallist)
    twoproot = os.path.join(cgobj.system_path['root'], cgobj.system_path['twophoton'])
    explist = []
    for animal in animallist:
        path = os.path.join(twoproot, animal)
        dates = os.listdir(path)
        dates = [os.path.join(path, x, 'info.json') for x in dates if os.path.isdir(os.path.join(path, x))]
        explist = explist + dates
    return(explist)

def situation_data_path(infolist, situation, time = None, analysis_method = 'AQuA', *args):
    """
    When you get a list of animal info files in the group, you can use
    this function to get a list of folder path for certain situation of this animal.
    If you have more restrain condition, give a two element array arg as ['magnitude', 5.7].
    So far the condition only support one level query.
    """
    infolist = utils.confirm_array_input(infolist)
    datafolders = []
    for i in infolist:
        info = utils.readjson(i)
        data = info['data']
        data = [x for x in data if (x['situation'] == situation) and (x['analysis_method'] == analysis_method)]
        if time != None:
            data = [x for x in data if x['time_after_treatment'] == time]

        for arg in args:
            data = [x for x in data if x[arg[0]] == arg[1]]
        data = [os.path.join(os.path.dirname(i), x['analysis_result_path']) for x in data]
        datafolders = datafolders + data
    return(datafolders)
# =======================================================================================================================================================
# =======================================================================================================================================================
# Data class is an object for two photon data. It contains the information how the data was recorded, under which situation when the animal experiencing 
# test, the setting of scanbox.
# =======================================================================================================================================================
# =======================================================================================================================================================
class Runpara:
    def __init__(self, animalid, date,run):
        self.rawfolder = self.__date_format__(exp.date) + '_' + exp.animalid +'_run' + str(run)
        self.coordinates = self.input_coords()
        self.depth = int(input('Depth to the surface. Value is based on knobby. The surface refers to the area at the edge of changing from light to dark.'))
        self.objective_lens = self.select_objective()
        self.input_scanbox()
        self.input_situation(exp)

    def input_coords(self):
        ref = utils.select('Please choose the ref direction: ', ['N', 'S', 'E', 'W'])
        coords = input('Please input the coordinates value (x,y), seperated by ",": ').replace(' ', '').split(',')
        coords = [int(x) for x in coords]
        return({'coords': coords, 'ref': ref})

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
        #self.situation = {}
        #self.situation['treatment'] = utils.select('Select the situation which this data is experiencing: ', tarr).split(':')[0]
        #self.situation['time_after_treatment'] = input('How long under this situation (consider the beginning of the trial. unit is min. int): ')+'min'
        self.situation = utils.select('Select the situation which this data is experiencing: ', tarr).split(':')[0]
        self.time_after_treatment = input('How long under this situation (consider the beginning of the trial. unit is min. int): ')+'min'


class Data:
    def __init__(self, exp, run):
        self.data_type = utils.select('Data type: ', ['astrocyte_event', 'GCaMP_afferent', 'bloodvessel_dilation'])
        self.rawfolder = self.__date_format__(exp.date) + '_' + exp.animalid +'_run' + str(run)
        self.channel = utils.select('Data from channel: ', ['pmt0', 'pmt1'])
        

        if self.data_type == 'astrocyte_event':
            self.analysis_method = utils.select('Choose analysis method: ', ['AQuA'])

        self.__analysis_result_path__(exp)

    def __date_format__(self, datestr):
        return(datetime.strptime(datestr, '%m-%d-%Y').strftime('%y%m%d'))

    
    def __analysis_result_path__(self, exp):
        # the analysis result file is suppose to save at the same folder with info.json
        # It will be convienent to be able to upload to google cloud, but right now this 
        # function is not available.
        # This path refer to a folder under the animal folder, in this folder there are at list one data file and at list parameter json file.
        # The structure of this folder based on the analysis method.
        files = os.listdir(exp.animalfolder)
        files = [x for x in files if os.path.isdir(os.path.join(exp.animalfolder, x))]
        self.analysis_result_path = utils.select('Choose the analysis result folder for this run: ', files)


    def output(self):
        ot = self.__dict__
        return(ot)

# ========================================================================================================================================
# ========================================================================================================================================
# Exp2P class build a class for a two photon experiment. It should include information like animal id, date, path where save the data, 
# animal treatment, and the experiment data 
# ========================================================================================================================================
# ========================================================================================================================================        
class Exp2P(cg.Experiment):
    """
    The reason to structure the 2P data based on animal, date, but not run is because each animal
    will only expect receive 1 treatment. Even has multiple treatment, the previous treatment will
    effect the later treatment. So it is hard to seperate treatment in each runs. So it will be better
    understand to give a total treatment list, and add all runs in one info.json, for each run, just need to 
    give a situation value to label it.
    """
    def __init__(self, animalid, dateid):

        self.__keys__ = ['animalid', 'date', 'treatment', 'note']
        self.animalid = animalid
        self.date = utils.format_date(datetime.strptime(dateid, '%y%m%d').strftime('%m/%d/%Y'))
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT * FROM twop_info
        WHERE animalid = %s and date = %s;
        """, (self.animalid, self.date)
        )
        animal = cur.fetchall()
        conn.commit()

        if len(animal) == 0: # need to build new animal info
            self.animalid = animalid
            self.date = utils.format_date(datetime.strptime(dateid, '%y%m%d').strftime('%m/%d/%Y'))
            self.treatment = treatment.create_treatment_with_timepoint()
            tmp = input('Any note?')
            if tmp != '':
                self.note = tmp
            else:
                self.note = None

            # add the new animal in database
            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO twop_info
            (animalid, date, treatment, note) 
            VALUES (%s, %s, %s, %s)
            """, (self.animalid, self.date, json.dumps(self.treatment), self.note)
            )
            conn.commit()
            

        elif len(animal) == 1: # load animal info
            for i in range(len(self.__keys__)):
                setattr(self, self.__keys__[i], animal[0][i])

        conn.close()

    """def __setinfopath__(self, config):
        self.animalfolder = os.path.join(self.catagoryroot, self.animalid)
        # print(self.animalfolder)
        if not os.path.exists(self.animalfolder):
            os.mkdir(self.animalfolder)
        path = os.path.join(self.animalfolder, datetime.strptime(self.date, '%m-%d-%Y').strftime('%y%m%d')+'.json')
        if not os.path.exists(path):
            exp = {}
            exp['project'] = utils.projectArrayInput(config)
            exp['treatment'] = {}
            exp['data'] = []
            utils.writejson(path, exp)
        return(path)


    def add_data(self, dataObj):
        # use this to add a new data to exp and update it to the json file in database
        self.data.append(dataObj.output())
        self.writeExp()"""