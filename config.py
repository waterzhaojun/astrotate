# ====================================================================================================
# ===== config of the system =========================================================================
# ====================================================================================================
# config file is important for the database setup. This file exist in the root folder of the module.
# To update the config file, you can download the config file by using download_config function.
# After revise, use upload_config file to overwrite the old one. Keep the one you used for update as 
# every time after update the module, you have to upload the config again.
# This module also contains some fundamental classes like experiment.

import yaml
import shutil
import inspect
import types
from pathlib import Path
import os
from astrotate import utils

# ========================================================================================================================================
# ========================================================================================================================================
# Each database has a config yml file. It contains some fundamental setting like the root path, where is each type of experiment stored,
# how many projects involved etc..
# ========================================================================================================================================
# ========================================================================================================================================  
class Config:
    def __init__(self, path):
        tmp = load_config(path)
        self.sourcepath = path
        for key, value in tmp.items():
            exec('self.'+key +'= value')
        for key in self.system_path.keys():
            self.system_path[key] = Path(self.system_path[key])
        

    def show(self):
        # Check your config file
        tmp = dir(self)
        tmp = [x for x in tmp if x[0] != '_' and type(inspect.getattr_static(self, x)) != types.FunctionType]
        for t in tmp:
            print('===================================================')
            print(t)
            print(inspect.getattr_static(self, t))
    
    def check_surgery_animal(self, animalid = None):
        if 'surgery' not in self.system_path.keys():
            raise Exception('This database does not have SURG folder')
        else:
            folder = os.path.join(self.system_path['root'], self.system_path['surgery'])
            files = os.listdir(folder)
            files = [x[0:-5] for x in files if x[-5:] == '.json']
        
        if animalid == None:
            return(files)
        else:
            animal = utils.readjson(os.path.join(folder, animalid+'.json'))
            return(animal)



    # def download(path):
    #     # Download the config file from the module root folder
    #     shutil.copyfile('config.yml', path)

# ========================================================================================================================================
# ========================================================================================================================================
# This is the parent class of all different experiment type like two photon, ep.
# It contains some fundamental field like the root path of whole database system.
# ========================================================================================================================================
# ========================================================================================================================================   
class Experiment:
    def __init__(self, config, catagory):
        self.root = config.system_path['root']
        self.catagoryroot = os.path.join(config.system_path['root'], config.system_path[catagory])
        self.infopath = None
        self.keys = ['animal', 'project', 'treatment', 'data']

    def __setinfopath__(self):
        pass

    def loadExp(self):
        tmp = utils.readjson(self.infopath)
        for key, value in tmp.items():
            setattr(self, key, value)

    def writeExp(self):
        tmp = {}
        for key in self.keys:
            tmp[key] = getattr(self, key)
        utils.writejson(self.infopath, tmp)

    def show(self):
        # Check your config file
        tmp = dir(self)
        tmp = [x for x in tmp if x[0] != '_' and type(inspect.getattr_static(self, x)) != types.FunctionType]
        for t in tmp:
            print('===================================================')
            print(t)
            print(inspect.getattr_static(self, t))

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

        

def load_config(path):
    # load config file. The config file can be used for setting up.
    with open(path, 'r') as f:
        tmp = yaml.safe_load(f)
    return(tmp)

