import os
import pandas as pd
import numpy as np
from . import array, utils, treatment
import json

objective = {'Nikon': ['16X']}
magnitude_list = [0.8, 1, 2.0, 2.4, 4.0, 4.8, 5.7]
datatype = ['astrocyte_event', 'GCaMP_afferent']


def folder_format(animalid, date, run):
    out = animalid + '_' + str(date) + '_run' + str(run)
    return(out)

def init_exp(animalid, date, run = None):
    exp = {}
    exp['project'] = utils.projectArrayInput()

    exp['treatment'] = {}
    exp['data'] = []
    return(exp)

def add_treatment(animalid, date, newtreatment):
    config = utils.load_config()
    path = os.path.join(config['system_path']['root'], config['system_path']['twophoton'], animalid, str(date)+'.json')
    exp = utils.readjson(path)
    keys = exp['treatment'].keys()
    newkey = str(len(keys))
    exp['treatment'][newkey] = newtreatment
    utils.writejson(path, exp)

def add_data(animalid, date, newdata):
    config = utils.load_config()
    path = os.path.join(config['system_path']['root'], config['system_path']['twophoton'], animalid, str(date)+'.json')
    exp = utils.readjson(path)
    exp['data'].append(newdata)
    utils.writejson(path, exp)

def select_objective():
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

def input_coords():
    ref = utils.select('Please choose the ref direction: ', ['N', 'S', 'E', 'W'])
    coords = input('Please input the coordinates value, seperated by ",": ').replace(' ', '').split(',')
    coords = [int(x) for x in coords]
    return({'coords': coords, 'ref': ref})

def input_scanbox():
    fin = {}
    fin['laser_power'] = int(input('Laser power (just int part, no %): '))
    fin['pmt0'] = float(input('PMT 0 value: '))
    fin['pmt1'] = float(input('PMT 1 value: '))
    fin['duration'] = str(int(input('Record duration (how many minutes, no unit, int): ')))+'min'
    
    tmp = input('Scan rate (Press Enter for default 15.5): ')
    if tmp == '':
        fin['scanrate'] = 15.5
    else:
        fin['scanrate'] = float(tmp)
        
    tmp = input('opto scanning volumn number (int, Press ENTER for 1): ')
    if tmp == '':
        fin['volumn'] = 1
    else:
        fin['volumn'] = int(tmp)
        
    fin['magnitude'] = float(utils.select('magnitude: ', magnitude_list))
    
    return(fin)
    
def input_situation(animal, date):
    config = utils.load_config()
    twop = os.path.join(config['system_path']['root'], config['system_path']['twophoton'], animal, str(date)+'.json')
    record = utils.readjson(twop)
    tmp = record['treatment']
    t = []
    for key, value in tmp.items():
        t.append([key, value])
    tarr = [str(x[0])+': '+x[1]['method'] for x in t]
    s = {}
    s['treatment'] = utils.select('Select the situation which this data is experiencing: ', tarr).split(':')[0]
    s['time_after_treatment'] = input('How long under this situation (consider the beginning of the trial. unit is min. int): ')+'min'
    return(s)
    
def input_data(animalid, date, run, datatype):
    data = {}
    datatype = utils.select('Choose data type: ', datatype)
    if datatype == 'astrocyte_event':
        data['path'] = folder_format(animalid, date, run)+'_AstrocyteEvent.mat'
        
    