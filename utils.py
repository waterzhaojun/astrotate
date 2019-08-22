# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:27:39 2019

@author: jzhao1
"""

import json
from datetime import datetime
import numpy as np


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