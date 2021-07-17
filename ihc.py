# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:17:59 2019

@author: jzhao1
"""
import os

import pandas as pd
import numpy as np
from astrotate import array, utils, treatment, surgery, config as cg
import json

tissue_list = ['dura', 'TG', 'brain', 'nerve', 'DRG', 'SpinalCord', 'muscle', 'skin', 'mesentery','stomach', 'duodenum','colon']

class Exp(cg.Experiment):
    def __init__(self):
        super().__init__()
        self.tissue = utils.select('which tissue: ', tissue_list)
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT (primary, secondary, thickness, slice_id) FROM ihc_info
        WHERE animalid = %s and date = %s and tissue = %s;
        """, (self.animalid, self.date, self.tissue)
        )
        exp = cur.fetchall()
        conn.commit()
        
        if len(exp) == 0:
            if utils.select('Did staining? ', [False, True]):
                self.primary = Antibody('primary').to_dict()
                self.secondary = Antibody('primary').to_dict()
            else:
                self.primary = None
                self.secondary = None
            self.thickness = int(input('Thickness, just input int part, unit is um: '))
            self.slice_id = ' '.join(self.animalid, self.tissue, self.date.strftime('%y%m%d'), '%02d'%(len(exp)+1))

            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO ihc_info 
            (animalid, primary, secondary, tissue, date, thickness, note, slice_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (self.animalid, json.dumps(self.primary), json.dumps(self.secondary), self.tissue, self.date, 
            self.thickness, self.note, self.slice_id)
            )
            conn.commit()
        
        else:
            self.recording_types = exp[0]
            self.path = exp[1]
            self.parameters = exp[2]
            self.treatment = exp[3]

        conn.close()
    

class Antibody(): # This class is good to use.
    def __init__(self):
        self.type = utils.select('=== antibody type ===', ['primary', 'secondary'])
        if self.type == 'primary':
            primary_list = [
                'GFAP from mouse', 
                'DsRed from rabbit', 
                'c-fos from rabbit',
                'NeuN from mouse',
                'GFP from chicken',
                'avidin texas red'
            ]
            self.antibody = utils.select('=== which antibody ===', primary_list)
            
        elif self.type == 'secondary':
            secondary_list = [
                '488 Goat anti Mouse', 
                '594 Goat anti Rabbit',
                '594 Goat anti Mouse',
                '488 Goat anti Chicken'
            ]
            self.antibody = utils.select('=== which antibody ===', secondary_list)
        
        self.concentration = '1:'+input('=== antibody concentration ===/n1:xxx, just input the second number by int: ')
        tmp = input('=== how long did it treat ===/nPress ENTER for overnight, or input a value like 4h')
        if tmp == '':
            self.duration = 'overnight'
        else:
            self.duration = tmp
        
        self.temperature = utils.select('temperature: ', ['RT', '-4'])

    # def translate_name(self):
    #     # deprecated
    #     # I wanna simplify the antibody information. The source and anti is already included in antibody name, don't need to add again.
    #     res = {}
    #     if self.type == 'primary':
    #         res['source'] = self.antibody.split('from')[1].replace(' ', '').lower()
    #     elif self.type == 'secondary':
    #         res['source'] = self.antibody.split(' ')[1].lower()
    #         res['anti'] = self.antibody.split(' ')[3].lower()
    #     return(res)

    def to_dict(self):
        res = {}
        res['type'] = self.type
        res['antibody'] = self.antibody
        res['concentration'] = self.concentration
        res['duration'] = self.duration
        res['temperature'] = self.temperature
        # tmp = self.translate_name()
        # for key, value in tmp.items():
        #     res[key] = value
        return(res)
        # return({
        #     'type':self.type, 'antibody':self.antibody, 
        #     'concentration':self.concentration, 'duration': self.duration,
        #     'temperature':self.temperature
        # })