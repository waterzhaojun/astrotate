import os

import pandas as pd
import numpy as np
import array, utils, treatment
import json

objective = {'Nikon': ['16X']}


def init_exp(animalid, date, run = None):
    exp = {}
    exp['project'] = utils.projectArrayInput()

    exp['treatment'] = {}
    exp['data'] = []
    return(exp)

def add_treatment(exp, newtreatment):
    keys = exp['treatment'].keys()
    newkey = str(len(keys))
    exp['treatment'][newkey] = newtreatment
    return(exp)

def add_data(exp, newdata):
    exp['data'].append(newdata)
    return(exp)

def select_objective():
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

def input_coords():
    ref = utils.select('Please choose the ref direction: ', ['N', 'S', 'E', 'W'])
    coords = input('Please input the coordinates value, seperated by ",": ').replace(' ', '').split(',')
    coords = [int(x) for x in coords]
    return({'coords': coords, 'ref': ref})
