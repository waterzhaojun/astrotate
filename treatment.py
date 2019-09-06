"""
This file contains all functions to create a dictionary about one treatment method.
I put them in one indepent file is because the treatment can be used in different types of experiment, even how they structure the treatments is different.
So far I set them by different function but finally I may need to put them all in one class.

"""
from datetime import datetime
# from . import utils
import astrotate.utils as utils

aav_list = [
    'AAV5.CAG.GCaMP6s.WPRE.SV40',
    'AAV1.CAG.GCaMP6s.WPRE',
    'AAV5.GfaABC1D.cyto.GCaMP6f.SV40',
    'AAV-PHP.S CA6.6PP',
    'AAV2/5.GFAP.hM3D(Gq).mCherry',
    'pGP.AAV.syn.JGCaMP7s.WPRE'
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



# ================================================================================================================================
# ==== This part includes all kinds of treatment. It will return a dict containing all parameters ================================
# ================================================================================================================================

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

def csd():
    treat = {'method': 'CSD'}
    csd_method_list = ['pinprick', 'KCl']

    tmp = input('CSD time, format as xx:xx (Press ENTER to ignore this step): ')
    if tmp != '':
        treat['time'] = tmp
    
    treat['apply_method'] = utils.select('Choose CSD method: ', csd_method_list)

    return(treat)
        
def baseline():
    return({"method": "baseline"})
    
def drug(config):
    treat = {'method': 'drug apply'}

    apply_method = ['ip', 'topic', 'subcutaneous', 'iv', 'cortex', 'ic', 'icv']
    # config = utils.load_config()
    treat['activate_drug'] = utils.select('Choose treated drug: ', config.drug_list)
    treat['concentration'] = input('Drug concentration (unit is mM, input a number): ')+'mM'
    treat['apply_method'] = utils.select('Choose drug apply method: ', apply_method)
    treat['duration'] = input('How long it treated (unit is min, input int): ')+'min'

    if treat['apply_method'] == 'topic': # set parameters for topic treatment
        tmp = input('How long it recover after wash the drug (unit is min, input int, Press ENTER for 0): ')+'min'
        if tmp == '':
            tmp = '0'
        treat['recovery'] = tmp+'min'

    if treat['apply_method'] == 'iv': # set parameters for iv treatment
        treat['apply_speed'] = input('iv drug injection speed (unit is ml/min, input number): ') + 'ml/min'

    return(treat)

def optoStimulation():
    treat = {'method': 'opto stimulation'}
    opto_calibration = 5
    treat['duration']: input('Stimulation duration (sec, input an int): ')+'sec'
    treat['power']: input('opto stimulation power. (input a fraction number):' ) * opto_calibration
    treat['stimulation_type']: utils.select('Choose stimulation type: ', ['continue', 'discrete'])
    if treat['stimulation_type'] == 'discrete':
        treat['freq']: input('stimulation frequency. unit is Hz. input a float number: ')+'Hz'
        treat['on_duration']: input('In each loop, stimulation on duration, unit is sec. input a float number: ')+'sec'
    return(treat)