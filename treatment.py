"""
This file contains all functions to create a dictionary about one treatment method.
I put them in one indepent file is because the treatment can be used in different types of experiment, even how they structure the treatments is different.
So far I set them by different function but finally I may need to put them all in one class.

"""
from datetime import datetime
import inspect
from astrotate import utils, config



primary_antibody_list = ['rabbit anti c-Fos']
secondary_antibody_list = ['goat anti rabbit']



# ================================================================================================================================
# ==== This part includes all kinds of treatment. It will return a dict containing all parameters ================================
# ================================================================================================================================

# aavinject is to create a dictionary 


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

    tmp = input('Drug concentration (If you input a number, unit is mM, If you input like 1mg/cc, it will store what you input): ')
    try:
        tmp2 = float(tmp)
        treat['concentration'] = tmp + 'mM'
    except:
        treat['concentration'] = tmp
        
    tmp = input('Drug soluted in. Press ENTER for default SIF and ignore this input. Input string for specific solution. ')
    if tmp != '':
        treat['activate_drug_solution'] = tmp

    treat['apply_method'] = utils.select('Choose drug apply method: ', apply_method)
    treat['duration'] = input('How long it treated (unit is min, input int): ')+'min'

    if treat['apply_method'] == 'topic': # set parameters for topic treatment
        tmp = input('How long it recover after wash the drug (unit is min, input int, Press ENTER for 0): ')
        if tmp == '':
            tmp = '0'
        treat['recovery'] = tmp+'min'
        tmp = input('Wash solution. Press ENTER to consider it as normal SIF wash and ignore this input. Input 0 for same solution as activate drug solution. ')
        if tmp == '':
            pass
        elif tmp == '0':
            treat['wash_method'] = treat['activate_drug_solution']
        else:
            treat['wash_method'] = tmp

    if treat['apply_method'] == 'iv': # set parameters for iv treatment
        treat['apply_speed'] = input('iv drug injection speed (unit is ml/min, input number): ') + 'ml/min'
    
    if treat['apply_method'] in ['iv', 'ip']:
        treat['dose'] = input('inject dose (unit is cc. just input number)') + 'ml'

    utils.input_time(treat, 'apply_time', 'Treatment start time', allow_none = False)
    utils.input_date(treat, 'date', 'Treat date', allow_none = False)

    return(treat)

def setupWindow():
    treat = {'method': 'window setup'}
    treat['window_type'] = utils.select('Choose window type: ', ['glass', 'thin bone'])
    if treat['window_type'] == 'glass':
        treat['layers'] = utils.select('glass layers: ', ['5-3-3-3', '5-3-3'])
        treat['with_agar']  =utils.select('Put agar under?: ', ['Y', 'N'])
        treat['remove_dura'] = utils.select('Removed dura?: ', ['Y', 'N'])
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

def input_time(title, allow_none = True):
    
    if allow_none:
        note = '=== %s treatment start time.===\nPress Enter to leave it blank. Input 1 for present time. Input HH:MM for certain time: ' % title
    else:
        note = '=== %s treatment start time.===\nInput 1 for now. Input HH:MM for certain time: ' % title
    tmp = input(note)
    
    if tmp == '1':
        value = datetime.now().strftime('%H:%M')
    elif tmp == '':
        if not allow_none:
            raise Exception('need a valid time.')
        else:
            value = tmp
    else:
        value = tmp
    return(value)

def input_date(title, allow_none = True):

    if allow_none:
        note = '=== %s treatment start date.===\nPress Enter to ignore this.\nInput 1 for today.\nInput mm-dd-yyyy for detail date: ' % title
    else:
        note = '=== %s treatment start date.===\nInput 1 for today.\nInput mm-dd-yyyy for detail date: ' % title
    
    tmp = input(note)
    if tmp == '1':
        value = utils.format_date(datetime.now().strftime('%m-%d-%Y'))
    elif tmp == '':
        if not allow_none:
            raise Exception('Need a valid date.')
        else:
            value = tmp
    else:
        value = utils.format_date(datetime.now().strftime('%m-%d-%Y'))
    return(value)
    
#========================================================

class Treatment():
    def __init__(self, method, title = None, cgpath = 'config.yml'):
        cg = config.Config(cgpath)
        self.method = method

        if title == None:
            self.__title__ = method
        else:
            self.__title__ = title

        self.time = input_time(self.__title__)
        self.date = input_date(self.__title__)
        self.operator = utils.select('Treatment operator: ', cg.operator)
        self.parameters = {}
        self.note = input('input your note: ')

    def properties(self):
        props = [x for x in self.__dir__ if (not callable(x)) and x[0:2] != '__']
        return(props)

    def show(self):
        pass


class CSD(Treatment):
    def __init__(self):
        csd_method_list = ['pinprick', 'KCl']
        super().__init__('CSD')
        self.apply_method = utils.select('Choose CSD method: ', csd_method_list)
 
class Baseline(Treatment):
    def __init__(self):
        super().__init__('baseline')

class Purfusion(Treatment):
    def __init__(self):
        super().__init('PFA purfusion')

class Aavinject(Treatment):
    __aav_list__ = [
        'AAV5.CAG.GCaMP6s.WPRE.SV40', 
        'AAV1.CAG.GCaMP6s.WPRE',
        'AAV5.GfaABC1D.cyto.GCaMP6f.SV40',
        'AAV-PHP.S CA6.6PP',
        'AAV2/5.GFAP.hM3D(Gq).mCherry (do not use this one)',
        'AAV5.GFAP.hM3D(Gq).mCherry',
        'pGP.AAV.syn.JGCaMP7s.WPRE'
    ]

    __inject_method_list__ = [
        'superficial cortical injection', 
        'TG injection from contra lateral cortex', 
        'TG injection from ipsi lateral cortex', 
        'TG injection from nasal',
        'retro orbital injection', 
        'apply topically'
    ]

    __inject_tool_list__ = [
        'glass pipette', 
        'needle', 
        'insolin syringe'
    ]
    def __init__(self):
        super().__init__('virus inject')
        self.parameters['virus_id'] = utils.select('Choose virus: ', self.__aav_list__)
        self.parameters['inject_method'] = utils.select('Choose inject method: ', self.__inject_method_list__)
        self.parameters['inject_dose'] = input('Input dose (ul). It is the total amount: ')+'ul'
        
        tmp = input('Input spot number. Press ENTER for default 1. Intput an integer: ')
        if tmp == '':
            self.parameters['inject_spots'] = 1
        else:
            self.parameters['inject_spots'] = int(tmp)
        
        tmp = input('inject depth of each spot. Press ENTER for default 1. Input an integer: ')
        if tmp == '':
            self.parameters['depth_num_of_each_spot'] = 1
        else:
            self.parameters['depth_num_of_each_spot'] = int(tmp)
        
        self.parameters['inject_tool'] = utils.select('Choose inject tool: ', self.__inject_tool_list__)
        self.parameters['inject_speed'] = input('Inject speed (ul/min): ') + 'ul/min'
        self.parameters['inject_depth'] = input('Inject depth (mm): ') + 'mm'
        self.parameters['result'] = input('Result: ')
