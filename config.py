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
    def __init__(self, config):
        self.root = config.system_path['root']

    def show(self):
        # Check your config file
        tmp = dir(self)
        tmp = [x for x in tmp if x[0] != '_' and type(inspect.getattr_static(self, x)) != types.FunctionType]
        for t in tmp:
            print('===================================================')
            print(t)
            print(inspect.getattr_static(self, t))
        

def load_config(path):
    # load config file. The config file can be used for setting up.
    with open(path, 'r') as f:
        tmp = yaml.safe_load(f)
    return(tmp)

