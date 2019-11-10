# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:17:59 2019

@author: jzhao1
"""
import os

import pandas as pd
import numpy as np
from astrotate import array, utils, treatment, surgery, config
import json


class Exp(config.Experiment):
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
    def __init__(self, type):
        self.type = utils.select('=== antibody type ===', ['primary', 'secondary'])
        if self.type == 'primary':
            self.antibody = utils.select('=== which antibody ===', ['define', 'define'])
            tmp = utils.input('=== how long did it treat ===/nPress ENTER for overnight, or input a value like 4h')
        elif self.type == 'secondary':
            self.antibody = utils.select('=== which antibody ===', ['define', 'define'])
        
        self.concentration = '1:'+input('=== antibody concentration ===/n1:xxx, just input the second number by int: ')
