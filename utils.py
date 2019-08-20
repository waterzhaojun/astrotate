# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:27:39 2019

@author: jzhao1
"""

import json


def readjson(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return(data)


def writejson(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
