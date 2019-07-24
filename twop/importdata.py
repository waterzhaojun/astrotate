# from scipy.io import loadmat
import os
import pandas as pd
import argparse
import numpy as np
from datetime import datetime
# import shutil
import psycopg2
import json
from util import *


parser = argparse.ArgumentParser(description='import')
parser.add_argument('--exp', type=str, required=True,
                    help='exp folder')

args = parser.parse_args()



if __name__ == "__main__":

    config = readjson('config.json')
    root = config['root']

    # This is the place to save system data. Don't need to change if use in the same computer.
    saveroot = config['data_folder']

    # This is the connection to the database. Don't need to change if use the same database.
    conn_comment = 'host='+config['host']+' dbname='+config['dbname']+' user='+config['username']
    conn = psycopg2.connect(conn_comment)

    # exp defines which folder we will process.
    # the format should be date_animalid
    exp = args.exp   

    # for each experiment, we need 9 different parts information:
    # researcher, date, project, animal, data, treatment, result, object, note

    # In each experiment folder, the structure is:
    # info.json to provide main information.
    # for each kind of data, there are two files, one is xx_data, another is xx_treatment_log which is 
    # to record the time point of treatment.

    # The result part is more likely to update after analysis.
    animal = info['animal']   # <======================== need to change and confirm
    date = datetime.strptime(exp.split['_'][0], '%y%m%d')   # <================ need to change and confirm
    expobject = info['object']    # <================== need to change and confirm the last sub folder is bv_1


    files = os.listdir(os.path.join(root, animal))
    files = [x for x in files if x[0] != '.']
    files.sort()
    print(files)

    diameter = []
    running = []
    running_rate = config['running_rate']

    for ifolder in files:
        folder = os.path.join(root, animal, ifolder, bv)
        data = loadmat(os.path.join(root, folder, 'result.mat'))
        print(np.shape(data['diameter_value']))
        diameter = np.append(diameter, data['diameter_value'])
        
        tmp = read_running(os.path.join(root, animal, ifolder), fq = running_rate)
        running = np.append(running, tmp)
        print(np.shape(tmp))
        print('=============')
    diameter = np.reshape(diameter, [1, -1])
    running = np.reshape(running, [1, -1])

    # At here we suppose running rate will always be saved as 15 hz. 
    # And diameter vessel data will always the same length as running.
    # So the scanning rate of diameter can be calculated.
    diameter_rate = round(running_rate * np.shape(diameter)[1] / np.shape(running)[1])
    print('running rate: %s' % running_rate)
    print('diameter rate: %s' % diameter_rate)

    file_basename = animal + '_' + date.strftime('%y%m%d')+'_' + 'a'

    wheel_file_id = upload_data_and_return_id(data = running, file_basename = file_basename, 
                                            data_type = 'WHEEL', save_folder = saveroot, 
                                            data_rate = running_rate, conn = conn)

    bv_file_id = upload_data_and_return_id(data = diameter, file_basename = file_basename, 
                                            data_type = 'DIAMETER', save_folder = saveroot, 
                                            data_rate = diameter_rate, conn = conn)

    expdata = []
    expdata = np.append(expdata, {'type':'vessel diameter', 
                                'fileid': bv_file_id,
                                'treat_point': {'0': 0, '1': 5580} #<===== need to change and confirm ======
                                })

    expdata = np.append(expdata, {'type':'wheel running',
                                'fileid': wheel_file_id,
                                'treat_point': {'0': 0, '1': 27900} #<===== need to change and confirm =====
                                })


    treatment = {'pre':{'method': 'label blood vessel', 'dye': 'dextran texas red', 'concentration': '25mg/cc',
                        'dose': '100ul', 'apply_method': 'ip', 'pre_time':'30 min before setup'
                    },
                '0': {'method': 'baseline'},
                '1': {'method': 'csd', 'csd_method': 'pinprick'}
    }
    project = info['project']