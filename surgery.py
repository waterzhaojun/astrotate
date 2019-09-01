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


def init_animal(folder):
    # the folder is where the surgery records stored.
    animal = {}
    animal['id'] = input('input animal id: ')
    outputpath = os.path.join(folder, animal['id']+'.json')
    if os.path.exists(outputpath):
        print('This animal already exists, do not need initiate. You may use add_treatment or add_note to update.')
    else:
        animal['info'] = {}
        animal['note'] = ''
        animal['info']['strain'] = utils.select('Choose animal strain: ', ['rat', 'mouse'])
        animal['info']['gender'] = utils.select('Choose animal gender: ', ['M', 'F'])
        animal['info']['birthday'] = utils.format_date(input('Animal birthday (format month-day-year): '))
        print(animal)
        utils.writejson(outputpath, animal)
        
def add_treatment(animalid, folder, treatment):
    path = os.path.join(folder, animalid+'.json')
    record = utils.readjson(path)
    if 'treament' not in record.keys():
        record['treatment'] = []
    record['treatment'].append(treatment)
    print(record)
    utils.writejson(path, record)

# add_note is still under development. delete this note when tried
def add_note(animalid, folder, note):
    path = os.path.join(folder, animalid + '.json')
    record = utils.readjson(path)
    if type(record['note']) != list:
        record['note'] = []
    record['note'].append([utils.format_date(datetime.today().strftime('%m-%d-%Y')), note])
    print(record)
    utils.writejson(path, record)
    
# available_treatment = ['virus inject', 'chemical treatment', 'window setup', 'CSD']
# def check_available_treatment():
#     for i in range(len(available_treatment)):
#         print('%d ---> %s'% (i, available_treatment[i]))
        

    
