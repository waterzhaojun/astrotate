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


def readjson(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return(data)


def writejson(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

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
def load_config():
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    return(config)

def check_config():
    print(load_config())

def download_config(path):
    copyfile('config.yml', path)

def upload_config(path):
    copyfile(path, 'config.yml')