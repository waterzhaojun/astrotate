import os
import pandas as pd
import argparse
import numpy as np
from datetime import datetime
# import shutil
import psycopg2
import json

def list2array(array):
    array = str(array)
    array = array.replace('(', '{').replace(')', '}')
    array = array.replace('[', '{').replace(']', '}').replace('\'', '\"')
    return array

def bint_1d(array, size):
    remain = len(array)%size
    array = array[0: (len(array)-remain)]
    array = np.reshape(array, [-1, size])
    array = np.mean(array, axis = 1)
    array = list(array)
    return(array)
           

def read_running(folder_path, absolute = True, fq = 15):
    files = os.listdir(folder_path)
    file = [x for x in files if 'quadrature.mat' in x]
    file = file[0]
    data = loadmat(os.path.join(folder_path, file))
    data = data['quad_data'][0]
    data = np.append(data[0], data[1:] - data[0:-1])
    if absolute:
        data = abs(data)
        
    data = bint_1d(data, size = int(15/fq))
    return(data, )

def read_vessel_diameter(folder_path):
    pass
           
def readjson(path):
    with open(path, "r") as read_file:
        x = json.load(read_file)
    return(x)

    
def upload_data_and_return_id(data, file_basename, data_type, save_folder, data_rate, conn = conn):
    filename = file_basename + '_' + data_type.lower()
    savepath = os.path.join(data_type, filename+'.npy')
    np.save(os.path.join(save_folder, savepath), data)
    
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO data_2p (id, shape, path, type, rate) 
        VALUES (DEFAULT, '{}', '{}', '{}', '{}')
        RETURNING id;
        """.format(list2array(np.shape(data)), savepath, data_type, data_rate) 
    )
    diaid = cur.fetchall()
    conn.commit()
    diaid = diaid[0][0]
    
    return(diaid)

def createExpObj(info):
    checklist = ['neuron', 'bf_location']
    exp = {}
    for li in checklist:
        if li in info:
            exp[li] = info[li]

    return(exp)
