"""
This file contains all functions to create a dictionary about one treatment method.
I put them in one indepent file is because the treatment can be used in different types of experiment, even how they structure the treatments is different.
So far I set them by different function but finally I may need to put them all in one class.

"""
from datetime import datetime
import inspect
from astrotate import utils, config
import copy



primary_antibody_list = ['rabbit anti c-Fos']
secondary_antibody_list = ['goat anti rabbit']



# ================================================================================================================================
# ==== This part includes all kinds of treatment. It will return a dict containing all parameters ================================
# ================================================================================================================================

# aavinject is to create a dictionary 



def ihcstain():
    # deprecated
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
        value = utils.format_date(tmp)
    return(value)

def create_treatment_with_timepoint():
    flag = True
    i = 0
    treatment = {}
    treat_list = ['Baseline', 'CSD', 'Drug', 'OptoStimulation']
    while flag:
        treat_type = utils.select('Choose the treatment type you want to enter: ', treat_list)
        treatment[str(i)] = eval(treat_type+'()').toDict()
        i = i+1
        flag = utils.select('More treatment?', [False, True], 1)
    return(treatment)

def choose_treatment():
    treatlist = ['baseline', 'CSD', 'drug application', 'setup window', 'IHC', 'AAV inject', 
    'purfusion', 'opto stimulation']
    newt = utils.select('Which treatment you want to choose: ', treatlist)
    if newt == 'baseline':
        t = Baseline()
    elif newt == 'CSD':
        t = CSD()
    elif newt == 'opto stimulation':
        t = OptoStimulation()
    
    return(t.toDict())

    
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
        self.operator = utils.select('Treatment operator: ', cg.operator, 0)
        self.parameters = {}
        self.note = input('input your note for %s treatment: ' % self.method)

    def properties(self):
        props = [x for x in self.__dir__ if (not callable(x)) and x[0:2] != '__']
        return(props)

    def show(self):
        pass

    def toDict(self):
        a= copy.copy(self.__dict__)
        del a['__title__']
        return(a)

class OptoStimulation(Treatment):
    def __init__(self):
        super().__init__('opto stimulation')
        self.parameters['duration'] = input('Stimulation duration (sec, input an int): ')+'sec'
        self.parameters['power percentage'] = int(input('opto stimulation power. (input an int number for percentage int part):' ))
        self.parameters['stimulation_type'] = utils.select('Choose stimulation type: ', ['continue', 'discrete'])
        if self.parameters['stimulation_type'] == 'discrete':
            self.parameters['freq']= input('stimulation frequency. unit is Hz. input a float number: ')+'Hz'
            self.parameters['width']= input('Width of the stimulation, unit is sec. input a float number: ')+'sec'
    

class CSD(Treatment):
    def __init__(self):
        csd_method_list = ['pinprick', 'KCl']
        super().__init__('CSD')
        self.parameters['apply_method'] = utils.select('Choose CSD method: ', csd_method_list)
        if self.parameters['apply_method'] == 'KCl':
            self.parameters['concentration'] = input('KCl concentration (unit is mM, input int part) ')
 
class Baseline(Treatment):
    def __init__(self):
        super().__init__('baseline')

class Purfusion(Treatment):
    def __init__(self):
        super().__init__('PFA purfusion')

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


class Setupwindow(Treatment):

    def __init__(self):
        # csd_method_list = ['pinprick', 'KCl']
        super().__init__('window setup')
        self.parameters['window_type'] = utils.select('Choose window type: ', ['glass', 'thin bone'])
        self.parameters['layers'] = utils.select('glass layers: ', ['5-3-3-3', '5-3-3'], defaultChoose = 0)
        self.parameters['with_agar']= utils.select('Put agar under?: ', ['Y', 'N'], defaultChoose = 1)
        self.parameters['remove_dura'] = utils.select('Removed dura?: ', ['Y', 'N'], defaultChoose = 1)
        self.parameters['location'] = utils.select('location of the window: ', ['visual cortex', 'transverse sinus'])

class Drug(Treatment):
    
    def __init__(self):
        drug_list = ['ACSF', 'AL8810', 'L-NAME', 'oxamate', 'L-AA', 'GAP19', 
                     'TTX', 'BIBN', 'HET', 'DAB', 'Napro', 'FLCT', 'PPADS', 
                     'Ozagrel', 'Levcro', 'soup', 'A10606120', 'Prob', 'TNP-ATP', 
                     'saline', 'CBN4', 'SNP', 'GAP26', 'SC560', 'AL8810', 'CNO', 
                     'anti CGRP', 'Tamoxipen']
        apply_method_list = ['ip', 'topic', 'subcutaneous', 'iv', 'cortex', 'ic', 'icv']
        super().__init__('drug apply')
        self.parameters['activate_drug'] = utils.select('Choose treated drug: ', drug_list)

        tmp = input('Drug concentration (If you input a number, unit is mM, If you input like 1mg/cc, it will store what you input): ')
        try:
            tmp2 = float(tmp)
            self.parameters['concentration'] = tmp + 'mM'
        except:
            self.parameters['concentration'] = tmp
            
        tmp = input('Drug soluted in. Press ENTER for default SIF and ignore this input. Input string for specific solution. ')
        if tmp != '':
            self.parameters['activate_drug_solution'] = tmp

        self.parameters['apply_method'] = utils.select('Choose drug apply method: ', apply_method_list)
        tmp = input('How long it treated (unit is min, input int, Press ENTER to ignore): ')
        if tmp != '':
            self.parameters['duration'] = tmp + 'min'

        if self.parameters['apply_method'] == 'topic': # set parameters for topic treatment
            tmp = input('How long it recover after wash the drug (unit is min, input int, Press ENTER for 0): ')
            if tmp == '':
                tmp = '0'
            self.parameters['recovery'] = tmp+'min'
            tmp = input('Wash solution. Press ENTER to consider it as normal SIF wash and ignore this input. Input 0 for same solution as activate drug solution. Input the specific name if it is a special wash method.')
            if tmp == '':
                pass
            elif tmp == '0':
                self.parameters['wash_method'] = self.parameters['activate_drug_solution']
            else:
                self.parameters['wash_method'] = tmp

        if self.parameters['apply_method'] == 'iv': # set parameters for iv treatment
            self.parameters['apply_speed'] = input('iv drug injection speed (unit is ml/min, input number): ') + 'ml/min'
        
        if self.parameters['apply_method'] in ['iv', 'ip']:
            self.parameters['dose'] = input('inject dose (unit is cc. just input number)') + 'ml'
