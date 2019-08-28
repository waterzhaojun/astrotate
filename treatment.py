"""
This file contains all functions to create a dictionary about one treatment method.
I put them in one indepent file is because the treatment can be used in different types of experiment, even how they structure the treatments is different.
So far I set them by different function but finally I may need to put them all in one class.

"""
from datetime import datetime
import utils

aav_list = [
    'AAV5.GfaABC1D.cytoGCaMP6f.SV40',
    'AAV2/5-GFAP-hM3D(Gq)-m-cherry'
]

inject_method_list = [
    'superficial cortical injection', 
    'TG injection from contra lateral cortex', 
    'TG injection from ipsi lateral cortex', 
    'TG injection from nasal',
    'retro orbital injection', 
    'apply topically'
]

inject_tool_list = [
    'glass pipette', 
    'needle', 
    'insolin syringe'
]

# aavinject is to create a dictionary 
def aavinject(*args, **kwargs):

    treatment = {'method': 'virus inject'}
    treatment['virus_id'] = utils.select('Choose virus: ', aav_list)
    treatment['inject_method'] = utils.select('Choose inject method: ', inject_method_list)
    treatment['inject_dose'] = input('Input dose (ul): ')+'ul'
    treatment['inject_tool'] = utils.select('Choose inject tool: ', inject_tool_list, **kwargs)

    # date ===============================
    tmp = input('Inject date (format: month-date-year, Press ENTER for today): ')
    if tmp == '':
        treatment['inject_date'] = utils.format_date(datetime.today().strftime('%m-%d-%Y'))
    else:
        treatment['inject_date'] = utils.format_date(tmp)

    # speed ===============================
    treatment['inject_speed'] = input('Inject speed (ul/min): ') + 'ul/min'

    # depth ===============================
    tmp = input('Inject depth (um): ')
    if tmp != '':
        treatment['inject_depth'] = tmp + 'um'
    
    treatment['result'] = input('Result: ')

    return(treatment)

