import os
import pandas as pd
import argparse
import numpy as np
from datetime import datetime
# import shutil
# import psycopg2
import json

def bint1d(array, size, *args):
    l = len(array)
    rem = len(array)%size
    array1 = array[l-rem:l]
    array = array[0:l-rem]
    array = np.reshape(array, [len(array)/size, size])
    data = np.mean(array, axis = 1)
    if rem > (size/2):
        data = np.append(data, np.mean(array1))
    return(data)


def list2array(array):
    array = str(array)
    array = array.replace('(', '{').replace(')', '}')
    array = array.replace('[', '{').replace(']', '}').replace('\'', '\"')
    return array
           
def readjson(path):
    with open(path, "r") as read_file:
        x = json.load(read_file)
    return(x)

def updateInfo(path, data):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
    else:
        with open(path, 'r') as f:
            info = json.load(f)
        for k,a in data.items():
            info[k] = a
        with open(path, 'w') as f:
            json.dump(info, f, indent=4, sort_keys=True)

def tidyDict(dic):
    keys = dic.keys()
    negkeys = [x for x in keys if x[0] == '_']
    for n in negkeys:
        dic.pop(n, None)
    return(dic)

    

def ep_checklist():
    return(['bf', 'lfp', 'spon', 'mech', 'multi'])

def checkexp(root, folder_path):
    files = os.listdir(os.path.join(root, folder_path))
    files = [x for x in files if x[0] != '.']
    
    checklist = ep_checklist()
    exp_catalog = {}
    for i in checklist:
        this_cag_files = [x for x in files if x.startswith(i)]
        if len(this_cag_files) > 0:
            tmp1 = [os.path.join(root, folder_path, x) for x in this_cag_files if 'npy' in x]
            tmp2 = [os.path.join(root, folder_path, x) for x in this_cag_files if '_treatment_log.json' in x]
            exp_catalog[i] = {'datafile':tmp1[0], 'treatfile':tmp2[0]}
            
    # each exp should have a treatment.json. This is out of the test catalog.
    exp_catalog['treatment'] = os.path.join(root, folder_path, 'treatment.json')
    return exp_catalog

def data_type(datapath):
    filename = os.path.basename(datapath)
    checklist = ep_checklist()
    
    tmp = [x for x in checklist if filename.startswith(x)]

    # it is a risk if there are more than one type match.
    filetype = tmp[0].upper()
    
    return(filetype)

def data_rate(datatype):
    
    if datatype == 'BF':
        rate = 0.2
    elif datatype == 'MECH':
        rate = 0.001111
    elif datatype == 'SPON':
        rate = 0.003333
    elif datatype == 'LFP':
        rate = 100
    elif datatype == 'MULTI':
        rate = 1
    else:
        print('can not recognize this type')
              
    return(rate)
    
def input_data_and_return_id(datapath, targetFolder, para, conn):

    savepath = os.path.join(targetFolder, os.path.basename(datapath))
    
    data = np.load(datapath)
    shape = np.shape(data)
    if len(shape) == 1:
        data = np.reshape(data, [1,-1])
        shape = np.shape(data)
    print('file shape: %s' % str(shape))
        
    filetype = data_type(datapath)
    print('file type: %s' % filetype)
    
    filerate = data_rate(filetype)
    try:
        filerate = para['rate']
    except:
        pass
    print('file rate: %f' % filerate)
    
    np.save(savepath, data)
    
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO data_ep (id, shape, path, type, rate) 
        VALUES (DEFAULT, '{}', '{}', '{}', '{}')
        RETURNING id;
        """.format(list2array(shape), os.path.basename(savepath), filetype, filerate) 
    )
    diaid = cur.fetchone()
    conn.commit()
    
    print('==============')
    return(diaid)

def createExpObj(info):
    checklist = ['neuron', 'bf_location']
    exp = {}
    for li in checklist:
        if li in info:
            exp[li] = info[li]

    return(exp)
