"""
functions in this file is to build a record for surgery animal.
Steps:
1. use init_animal(folder) to build based animal information in the surgery folder.
2. When we do some treatment, use add_treatment(animalid, folder, treatment) to add a treatment dict to this animal's treatment array.
3. When we want to add some note to this animal, use add_note(animalid, folder) to add note to this animal's note array. Each note in this array should be a list formated by 
   [date, value]. This method is under development.
"""

import numpy as np
import os
from datetime import datetime
from astrotate import utils

def init_animal(config):
    # the folder is where the surgery records stored.
    animal = {}
    animal['id'] = input('input animal id: ')
    outputpath = os.path.join(config.system_path['root'], config.system_path['surgery'], animal['id']+'.json')
    if os.path.exists(outputpath):
        print('This animal already exists, do not need initiate. You may use add_treatment or add_note to update.')
    else:
        animal['info'] = {}
        animal['note'] = ''
        animal['info']['species'] = utils.select('Choose animal strain: ', ['rat', 'mouse'])
        if animal['info']['species'] == 'rat':
            animal['info']['strain'] = 'SD'
        elif animal['info']['species'] == 'mouse':
            animal['info']['strain'] = utils.select('What is the strain: ', ['C57'])
        animal['info']['gender'] = utils.select('Choose animal gender: ', ['M', 'F'])
        tmp = input('Animal birthday (format month-day-year). Press ENTER to ignore: ')
        if tmp != '':
            animal['info']['birthday'] = utils.format_date()
        tmp = input('transgenic db id. Press ENTER to ignore: ')
        if tmp != '':
            animal['info']['transgenic_id'] = tmp
        tmp = utils.select('Ear punch when giving surgery. ', ['L', 'R', 'LR', 'none'])
        if tmp != 'none':
            animal['info']['ear_punch'] = tmp
        print(animal)
        utils.writejson(outputpath, animal)
        
def add_treatment(animalid, treatment, config):
    folder = os.path.join(config.system_path['root'], config.system_path['surgery'])
    path = os.path.join(folder, animalid+'.json')
    record = utils.readjson(path)
    if 'treatment' not in record.keys():
        record['treatment'] = []
    record['treatment'].append(treatment)
    for key, value in record.items():
        print('{}: {}'.format(key, value))
    utils.writejson(path, record)

# add_note is still under development. delete this note when tried
def add_note(animalid, note, config):
    path = os.path.join(config.system_path['root'], config.system_path['surgery'], animalid + '.json')
    record = utils.readjson(path)
    if type(record['note']) != list:
        record['note'] = []
    record['note'].append([utils.format_date(datetime.today().strftime('%m-%d-%Y')), note])
    print(record)
    utils.writejson(path, record)

# get all animal id and path in surgery part.    
def get_surgery_animals(cg):
    surgeryroot = os.path.join(cg.system_path['root'], cg.system_path['surgery'])
    animals = os.listdir(surgeryroot)
    animals = [x for x in animals if x[-5:] == '.json']
    animals_path = [os.path.join(surgeryroot, x) for x in animals]
    return(animals, animals_path)

def animalinfo(animalid, cg):
    path = os.path.join(cg.system_path['root'], cg.system_path['surgery'], animalid + '.json')
    info = utils.readjson(path)
    return(info, path)