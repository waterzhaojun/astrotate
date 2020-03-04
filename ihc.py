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

tissue_list = ['dura', 'TG', 'brain', 'nerve', 'DRG', 'SpinalCord', 'muscle', 'skin']

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
    def __init__(self, configpath = 'config.yml', primary = None, secondary = None):
        configobj = config.Config(configpath)
        super().__init__(configobj)
        self.animalid = input('=== animal id ===/nIf it has surgery id, better use it instead of transgenic id/nInput animal id: ')
        
        tmp = input('=== Date ===/nThis date is when you make the slide/ndate: ')
        self.date = utils.format_date(datetime.strptime(tmp, '%y%m%d').strftime('%m/%d/%Y'))

        self.microscope = utils.select('=== Which microscope are you using for these slides ===', ['8th floor', 'own lab'])
        
        if primary !=  None:
            self.primary = primary.properties()
        if secondary != None:
            self.secondary = secondary.properties()

        self.animalfolder = os.path.join(self.mainfolder, animalid)
        if not os.path.exists(self.animalfolder):
            os.mkdir(self.animalfolder)

        self.expfile = os.path.join(self.animalfolder, str(dateid)+'.json')
        if not os.path.exists(self.expfile):
            exp = {}
            exp['project'] = utils.projectArrayInput(configobj)
            exp['treatment'] = {}
            exp['data'] = []
            utils.writejson(self.expfile, exp)
        self.loadExp()

class Antibody():
    def __init__(self):
        self.type = utils.select('=== antibody type ===', ['primary', 'secondary'])
        if self.type == 'primary':
            primary_list = ['GFAP from mouse', 'DsRed from rabbit']
            self.antibody = utils.select('=== which antibody ===', primary_list)
            
        elif self.type == 'secondary':
            secondary_list = ['488 Goat anti Mouse', '594 Goat anti Rabbit']
            self.antibody = utils.select('=== which antibody ===', secondary_list)
        
        self.concentration = '1:'+input('=== antibody concentration ===/n1:xxx, just input the second number by int: ')
        tmp = input('=== how long did it treat ===/nPress ENTER for overnight, or input a value like 4h')
        if tmp == '':
            self.duration = 'overnight'
        else:
            self.duration = tmp

    def to_dict(self):
        return({'type':self.type, 'antibody':self.antibody, 'concentration':self.concentration, 'duration': self.duration})