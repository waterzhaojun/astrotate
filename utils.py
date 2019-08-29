# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:27:39 2019

@author: Jun Zhao

This file contains functions that are commonly used in different place.
"""

import json
from datetime import datetime
import numpy as np
import yaml
from shutil import copyfile
import importlib


def readjson(path):
    # read a json file
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return(data)


def writejson(path, data):
    # write a dict to a json file
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def update():
    # As this module is frequently updated, this function helps you update the module
    # This function is still under development. Not usable.
    # importlib.reload(astrotate)
    pass

def format_date(string, outputformat = '%m-%d-%Y'):
    # the correct sequence should be month/day/year, otherwise there might be some error
    separray = ['/', '-', '_']
    seplist = []
    for i in separray:
        seplist.append(len(string.split(i)))
    sep = separray[np.argmax(seplist)]
    dateformat = '%m'+sep+'%d'+sep
    if len(string.split(sep)[2]) == 4:
        dateformat = dateformat + '%Y'
    elif len(string.split(sep)[2]) == 2:
        dateformat = dateformat + '%y'
    else:
        raise Exception('the format is not correct')
    
    strdate = datetime.strptime(string, dateformat).strftime(outputformat)
    return(strdate)

def select(hellowords, array, **kwargs):
    # This function helps you use input function to select a key value from an array.
    # It list the elements and use choose the element by idx. Based on the idx, the 
    # function return the value. if you want to add some extra words, use extra_note = 'xxx'.
    print(hellowords)
    for i in range(len(array)):
        print('%d ---> %s' % (i, array[i]))
    x = input('Select by idx: ')
    final = array[int(x)]
    try:
        final = final + ' (' + kwargs['extra_note'] + ')'
    except:
        pass
    return(final)

def select_from_dict(hellowords, dict, **kwargs):
    # This function helps you use input function to select a key value from a dict.
    # The input should be a dict. The function list all the 'key: value' out. 
    # If you want to return the key instead of value, use return_key = True.
    # If you want multiple choice and return an array, use allow_array = True.
    print(hellowords)
    for key, value in dict.items():
        print('%s ---> %s' % (str(key), str(value)))
    y = input('Select by key: ')

    if 'allow_array' in kwargs:
        final = y.replace(' ', '').split(',')
    else:
        final = [y]

    if 'return_key' not in kwargs:
        try:
            final = [dict[x] for x in final]
        except:
            final = [dict[int(x)] for x in final]

    if 'extra_note' in kwargs:
        final = [x + ' (' + kwargs['extra_note'] + ')' for x in y]

    if 'allow_array' not in kwargs:
        final = final[0]

    return(final)

def projectArrayInput():
    config = load_config()
    projects = config['projects']
    result = select_from_dict('Choose involved projects', projects, allow_array=True, return_key=True)
    result = [int(x) for x in result]
    result.sort()
    return(result)


# ====================================================================================================
# ===== config of the system =========================================================================
# ====================================================================================================
# config file is important for the database setup. This file exist in the root folder of the module.
# To update the config file, you can download the config file by using download_config function.
# After revise, use upload_config file to overwrite the old one. Keep the one you used for update as 
# every time after update the module, you have to upload the config again.
def load_config():
    # load config file. The config file can be used for setting up.
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    return(config)

def check_config():
    # Check your config file
    print(load_config())

def download_config(path):
    # Download the config file from the module root folder
    copyfile('config.yml', path)

def upload_config(path):
    # upload the config file to module root folder.
    # the path is where your file locally is.
    copyfile(path, 'config.yml')