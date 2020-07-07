import os
import pandas as pd
import numpy as np
from .. import array, utils, treatment, config as cg, analysis, server
import json
from datetime import datetime
import h5py
from pathlib import Path
import math
from scipy.io import loadmat
#from oasis.functions import deconvolve


objective = {'Nikon': ['X16']}
magnitude_list = [0.8, 1, 2.0, 2.4, 4.0, 4.8, 5.7]

"""
So far the idea to organize the two photon data is:

-- twop_info: contains almost all information of an experiment. The path refers to the animal on certain day. 
it may contains a lot each run data, including wheel running, astrocyte signal, vessel diameter, etc.
These are tidy data from raw data. 

-- twop_data: These data are analysis data, not just signal. It may contains signal but not necessary.
Right now I have two analysis method finished building code: AQuA, CSD.

-- twop_run_para: These table records all parameters like coordinates, power etc information.

"""


def folder_format(animalid, date, run):
    out = str(date) + '_' + animalid + '_run' + str(run)
    return(out)



# ===================================================================
# query part 
def get_data_list(datatype, analysis_method, **kwargs):
    conn = server.connect_server()
    cur = conn.cursor()
    cur.execute(
    """
    SELECT animalid, filepath FROM twop_data
    WHERE data_type = '{}' and analysis_method = '{}';
    """.format(datatype, analysis_method)
    )
    record = cur.fetchall()
    conn.commit()
    conn.close()
    
    if 'filename_ext' in kwargs.keys():
        record = [x for x in record if kwargs['filename_ext'] in x[-1]]

    return(record)

def get_runpath(root, animalid, **kwargs):
    """
    This function is to get the folder path of certain data.
    Provide only root, animalid, date will return the date path
    You can set run=x to get folders have 'runx'.
    You can set datatype = 'x' to get folders have x.
    """
    path = os.path.join(root, animalid)
    if len(kwargs.keys()) > 0:
        if 'date' in kwargs.keys():
            path = os.path.join(path, date)
        else:
            path = [os.path.join(path,x) for x in os.listdir(path) if x[0] != '.'][0]
        
        files = [x for x in os.listdir(path) if x[0] != '.']
        if 'run' in kwargs.keys():
            run='run'+str(kwargs['run'])
            files = [x for x in files if run in x]
        if 'datatype' in kwargs.keys():
            files = [x for x in files if kwargs['datatype'] in x]
        path = [os.path.join(path, x) for x in files]
    return(path)

# =======================================================================================================================================================
# =======================================================================================================================================================
# Data class is an object for two photon data. It contains the information how the data was recorded, under which situation when the animal experiencing 
# test, the setting of scanbox.
#
# Runpara class is an object contains all information about the recording system
# =======================================================================================================================================================
# =======================================================================================================================================================
class Runpara:
    def __init__(self, exp, run):
        self.folder = exp.date.strftime('%y%m%d') + '_' + exp.animalid +'_run' + str(run)
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT * FROM twop_run_para
        WHERE folder = '{}';
        """.format(self.folder)
        )
        run = cur.fetchall()
        conn.commit()

        if len(run) == 0: # need to build new animal info
            self.coordinates = self.input_coords()
            self.depth = int(input('Depth to the surface. Value is based on knobby. The surface refers to the area at the edge of changing from light to dark.'))
            self.objective_lens = self.select_objective()
            self.input_scanbox()
            self.input_situation(exp)

            # add the new animal in database
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO twop_run_para
                (folder, coords_ref, coords_x, coords_y, depth, objective_lens_brand, objective_lens_mag, pmt0, pmt1, scanrate, volume, magnitude, startpoint_situation, time_after_treatment) 
                VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s)
                """, 
                (self.folder, self.coordinates['ref'], self.coordinates['coords'][0], self.coordinates['coords'][1], 
                self.depth, self.objective_lens['brand'], self.objective_lens['mag'], 
                self.pmt0, self.pmt1,self.scanrate,self.volume, self.magnitude,
                self.situation, self.time_after_treatment)
            )
            conn.commit()
            

        elif len(run) == 1: # load run parameters
            self.coordinates = {'ref':run[0][1], 'coords':[run[0][2], run[0][3]]}
            self.depth = run[0][4]
            self.objective_lens = {'brand':run[0][5], 'mag':run[0][6]}
            self.pmt0 = run[0][7]
            self.pmt1 = run[0][8]
            self.scanrate = run[0][9]
            self.volume = run[0][10]
            self.magnitude = run[0][11]
            self.situation = run[0][12]
            self.time_after_treatment = run[0][13]

        conn.close()

    def input_coords(self):
        ref = utils.select('Please choose the ref direction: ', ['N', 'S', 'E', 'W'])
        coords = input('Please input the coordinates value (x,y), seperated by ",": ').replace(' ', '').split(',')
        coords = [int(x) for x in coords]
        return({'coords': coords, 'ref': ref})

    def select_objective(self):
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

    

    def input_scanbox(self):
        self.laser_power = int(input('Laser power (just int part, no %): '))
        self.pmt0 = float(input('PMT 0 value: '))
        self.pmt1 = float(input('PMT 1 value: '))
        self.duration = str(int(input('Record duration (how many minutes, no unit, int): ')))+'min'
        
        tmp = input('Scan rate (Press Enter for default 15.5): ')
        if tmp == '':
            self.scanrate = 15.5
        else:
            self.scanrate = float(tmp)
            
        tmp = input('opto scanning volumn number (int, Press ENTER for 1): ')
        if tmp == '':
            self.volume = 1
        else:
            self.volume = int(tmp)
            
        self.magnitude = float(utils.select('magnitude: ', magnitude_list))
        
    def input_situation(self, exp):
        t = []
        for key, value in exp.treatment.items():
            t.append([key, value])
        tarr = [str(x[0])+': '+x[1]['method'] for x in t]
        #self.situation = {}
        #self.situation['treatment'] = utils.select('Select the situation which this data is experiencing: ', tarr).split(':')[0]
        #self.situation['time_after_treatment'] = input('How long under this situation (consider the beginning of the trial. unit is min. int): ')+'min'
        self.situation = utils.select('Select the situation which this data is experiencing: ', tarr).split(':')[0]
        self.time_after_treatment = input('How long under this situation (consider the beginning of the trial. unit is min. int): ')

    def __date_format__(self, datestr):
        return(datetime.strptime(datestr, '%m-%d-%Y').strftime('%y%m%d'))

    def update(self):
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE twop_run_para
            set coords_ref=%s, coords_x=%s, coords_y=%s, depth=%s, objective_lens_brand=%s, objective_lens_mag=%s, pmt0=%s, pmt1=%s, scanrate=%s, volume=%s, magnitude=%s, startpoint_situation=%s, time_after_treatment=%s
            WHERE folder = %s
            """, 
            (self.coordinates['ref'], self.coordinates['coords'][0], self.coordinates['coords'][1], 
            self.depth, self.objective_lens['brand'], self.objective_lens['mag'], 
            self.pmt0, self.pmt1,self.scanrate,self.volume, self.magnitude,
            self.situation, self.time_after_treatment, self.folder)
        )
        conn.commit()
        conn.close()


class Data:
    def __init__(self, exp, data_type):
        self.data_type = data_type #utils.select('Data type: ', ['astrocyte_event', 'GCaMP_afferent', 'bloodvessel_dilation'])
        self.animalid = exp.animalid
        self.datafolder = os.path.join(exp.animalid, exp.date.strftime('%y%m%d'))# self.__date_format__(exp.date) + '_' + exp.animalid +'_run' + str(run)
        self.channel = []#utils.select('Data from channel: ', [[0], [1], [0,1]])
        self.filepath = ''

    def load_records(self):
        # This function is to load the record from database. It only contain the path of the data, not data itself.
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM twop_data
            WHERE animalid = %s and data_type = %s and filepath = %s
            """, 
            (self.animalid, self.data_type, self.filepath)
        )
        records = cur.fetchall()
        conn.commit()
        conn.close()

        return(records)
    
    def upload(self):
        # I am still hesitating where to put it, parent or child class?
        # Looks like I can use filepath as pk
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * from twop_data
            WHERE filepath = %s
            """,
            (self.filepath)
        )
        record = cur.fetchall()
        conn.commit()
        if len(record) > 0:
            flag = utils.select('this filepath already exist, you want to update? ', ['Y', 'N'], 0)
            if flag == 'Y':
                print('Note: animalid wont change')
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE twop_data
                    SET rawfolder = %s, analysis_method = %s, data_type = %s, pmt = %s
                    WHERE filepath = %s
                    """, 
                    (
                        self.rawfolder, self.analysis_method, self.data_type,
                        self.pmt, self.filepath
                    )
                )
                conn.commit()
        else:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO twop_data
                (animalid, data_type, pmt, rawfolder, analysis_method, filepath)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, 
                (
                    self.animalid, self.data_type, self.pmt, self.rawfolder, 
                    self.analysis_method, self.filepath
                )
            )
            conn.commit()
        conn.close()
        

    def show(self):
        ot = self.__dict__
        for key, value in ot.items:
            print(key, value)
        return(ot)

class Data_astrocyte_csd(Data):
    def __init__(self, exp):
        super().__init__(exp, 'astrocyte_csd')
        self.filepath = os.path.join(self.datafolder, 'CSD')
        self.analysis_method = 'csd_analysis'

    def load_records(self):
        # This function is to load the record from database. 
        # It only contain the path of the data, not data itself.
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM twop_data
            WHERE animalid = %s and data_type = %s and filepath = %s
            """, 
            (self.animalid, self.data_type, self.filepath)
        )
        records = cur.fetchall()
        conn.commit()
        conn.close()

        return(records)

    def load_data(self, database_root):
        # This function is to use data folder path to load the detail data.
        path = os.path.join(database_root, '2P', self.filepath)
        data = {}
        # add the load data code here.
        return(data)

class Data_astrocyte_event(Data):
    def __init__(self, exp):
        super().__init__(exp, 'astrocyte_event')
        self.run = int(input('run (input an int): '))
        self.rawfolder = ['run'+str(self.run)+'_AQuA']
        #self.filepath = os.path.join(self.datafolder, 'run'+str(self.run)+'_AQuA')
        self.analysis_method = 'AQuA'

    def load_records(self):
        # This function is to load the record from database. 
        # It only contain the path of the data, not data itself.
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM twop_data
            WHERE animalid = %s and data_type = %s and %s = ANY(rawfolder)
            """, 
            (self.animalid, self.data_type, self.filepath)
        )
        records = cur.fetchall()
        conn.commit()
        conn.close()

        return(records)

    def load_data(self, database_root):
        # This function is to use data folder path to load the detail data.
        path = os.path.join(database_root, '2P', self.filepath)
        data = {}
        # add the load data code here.
        return(data)
    


# ========================================================================================================================================
# ========================================================================================================================================
# Exp2P class build a class for a two photon experiment. It should include information like animal id, date, path where save the data, 
# animal treatment, and the experiment data 
# ========================================================================================================================================
# ========================================================================================================================================        
class Exp2P(cg.Experiment):
    """
    The reason to structure the 2P data based on animal, date, but not run is because each animal
    will only expect receive 1 treatment. Even has multiple treatment, the previous treatment will
    effect the later treatment. So it is hard to seperate treatment in each runs. So it will be better
    understand to give a total treatment list, and add all runs in one info.json, for each run, just need to 
    give a situation value to label it.
    """
    def __init__(self):
        super().__init__()
        #self.date = utils.format_date(datetime.strptime(dateid, '%y%m%d').strftime('%m/%d/%Y'))
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT path,treatment,note FROM twop_info
        WHERE animalid = %s and date = %s;
        """, (self.animalid, self.date)
        )
        exp = cur.fetchone()
        conn.commit()

        if exp == None: # need to build new animal info
            self.treatment = treatment.create_treatment_with_timepoint()
            self.path = os.path.join(self.animalid, self.date.strftime('%y%m%d'))
            # add the new animal in database
            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO twop_info
            (animalid, date, path, treatment, note) 
            VALUES (%s, %s, %s, %s, %s)
            """, (self.animalid, self.date, self.path, json.dumps(self.treatment), self.note)
            )
            conn.commit()
            

        else: # load animal info
            self.path = exp[0]
            self.treatment = exp[1]
            self.note = exp[2]

        conn.close()

