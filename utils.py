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
# from shutil import copyfile
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

def select(hellowords, array, defaultChoose = None, **kwargs):
    # This function helps you use input function to select a key value from an array.
    # It list the elements and use choose the element by idx. Based on the idx, the 
    # function return the value. if you want to add some extra words, use extra_note = 'xxx'.
    if (defaultChoose != None):
        hellowords = hellowords + ' Press Enter for %s' % array[defaultChoose]
    print(hellowords)
    
    for i in range(len(array)):
        print('%d ---> %s' % (i, array[i]))
    x = input('Select by idx: ')
    if x == '':
        if defaultChoose != None:
            final = array[defaultChoose]
        else:
            pass
    else:
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

def input_date(dict, newkey, note, allow_none = False):

    if newkey in dict.keys():
        raise Exception('This key already exist. Please confirm.')

    if allow_none:
        note = note + '. Press Enter to ignore this. Input 1 for today. Input mm-dd-yyyy for detail date: '
    else:
        note = note + '. Input 1 for today. Input mm-dd-yyyy for detail date: '
    
    tmp = input(note)
    if tmp=='':
        if allow_none:
            dict[newkey] = None
        else:
            pass
    elif tmp == '1':
        dict[newkey] = format_date(datetime.now().strftime('%m-%d-%Y'))

    else:
        dict[newkey] = format_date(tmp)

def input_time(dict, newkey, note, allow_none = False):
    if newkey in dict.keys():
        raise Exception('This key already exist. Please confirm.')

    if allow_none:
        note = note + '. Press Enter to ignore this. Input 1 for present time. Input HH:MM for certain time: '
    else:
        note = note + '. Input 1 for now. Input HH:MM for certain time: '
    tmp = input(note)
    if tmp=='':
        if allow_none:
            dict[newkey] = None
        else:
            pass
    elif tmp == '1':
        dict[newkey] = datetime.now().strftime('%H:%M')
    else:
        dict[newkey] = tmp

def projectArrayInput(config):
    projects = config.projects
    result = select_from_dict('Choose involved projects', projects, allow_array=True, return_key=True)
    result = [int(x) for x in result]
    result.sort()
    return(result)

def confirm_array_input(val):
    if not isinstance(val, list):
        return([val])
    else:
        return(val)

