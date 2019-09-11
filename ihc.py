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


class Exp(cg.Experiment):
    def __init__(self, config):
        super().__init__(config)
        animallist = config.check_surgery_animal()
        self.animalid = input('animal id: ')
        if self.animalid not in animallist:
            raise Exception('The animal id should be in the SURG folder first. Please confirm.')
        
        tmp = input('Staining date. Use the date to start primary staining.')
        self.date = utils.format_date(datetime.strptime(tmp, '%y%m%d').strftime('%m/%d/%Y'))
        self.mainfolder = os.path.join(self.root, config.system_path['twophoton'])

        self.animalfolder = os.path.join(self.mainfolder, animalid)
        if not os.path.exists(self.animalfolder):
            os.mkdir(self.animalfolder)

        self.expfile = os.path.join(self.animalfolder, str(dateid)+'.json')
        if not os.path.exists(self.expfile):
            exp = {}
            exp['project'] = utils.projectArrayInput(config)
            exp['treatment'] = {}
            exp['data'] = []
            utils.writejson(self.expfile, exp)
        self.loadExp()