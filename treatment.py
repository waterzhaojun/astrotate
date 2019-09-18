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

primary_antibody_list = ['rabbit anti c-Fos']
secondary_antibody_list = ['goat anti rabbit']



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
    utils.input_date(treatment, 'inject_date', 'Inject date', allow_none = False)

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

    utils.input_time(treat, 'time', 'CSD time', allow_none = False)
    
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
        tmp = input('How long it recover after wash the drug (unit is min, input int, Press ENTER for 0): ')
        if tmp == '':
            tmp = '0'
        treat['recovery'] = tmp+'min'

    if treat['apply_method'] == 'iv': # set parameters for iv treatment
        treat['apply_speed'] = input('iv drug injection speed (unit is ml/min, input number): ') + 'ml/min'
    
    utils.input_time(treat, 'apply_time', 'Treatment start time', allow_none = False)
    utils.input_date(treat, 'date', 'Treat date', allow_none = False)

    return(treat)

def setupWindow():
    treat = {}
    treat['window_type'] = utils.select('Choose window type: ', ['glass', 'thin bone'])
    if treat['window_type'] == 'glass':
        treat['layers'] = utils.select('glass layers: ', ['5-3-3-3', '5-3-3'])
        treat['with_agar']  =utils.select('Put agar under?: ', ['Y', 'N'])
    utils.input_date(treat, 'date', 'Setup date', allow_none = False)
    return(treat)


def optoStimulation():

    def __power__(value):
        t = {'value': value}
        t['power_measure_device'] = 'EXTECH EasyView 33'
        return(t)

    treat = {'method': 'opto stimulation'}
    treat['duration'] = input('Stimulation duration (sec, input an int): ')+'sec'
    treat['power'] = __power__(int(input('opto stimulation power. (input an int number):' )))

    treat['stimulation_type'] = utils.select('Choose stimulation type: ', ['continue', 'discrete'])
    if treat['stimulation_type'] == 'discrete':
        treat['freq']: input('stimulation frequency. unit is Hz. input a float number: ')+'Hz'
        treat['on_duration']: input('In each loop, stimulation on duration, unit is sec. input a float number: ')+'sec'
    return(treat)

def purfusion():
    treat = {'method': 'PFA purfusion'}
    return(treat)

def ihcstain():
    treat = {'method': 'IHC stain'}

    treat['stain_type'] = utils.select(['fluorescence', 'DAB'])
    
    if treat['stain_type'] in ['fluorescence', 'DAB']:
        treat['primary'] = {}
        treat['primary']['antibody'] = utils.select('Primary antibody: ', primary_antibody_list)
        treat['primary']['concentration'] = input('Primary antibody dilution, input like 1/10000: ')
        tmp = input('How long did the primary antibody treat. unit is hour, input an int. Press ENTER as overnight: ')
        if tmp == '':
            treat['primary']['duration'] = 'overnight'
        else:
            treat['primary']['duration'] = tmp+'h'

        treat['secondary'] = {}
        treat['secondary']['antibody'] = utils.select('Secondary antibody: ', secondary_antibody_list)
        treat['secondary']['concentration'] = input('Secondary antibody dilution, input like 1/200: ')
        treat['secondary']['duration'] = input('How long did the second antibody treat. unit is hour, input an int: ')+'h'

        
    return(treat)