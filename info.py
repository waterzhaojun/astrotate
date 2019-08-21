from . import utils
import os

def getInfoList(rootPath):
    folders = os.listdir(rootPath)
    folders = [os.path.join(rootPath, x) for x in folders]
    folders = [x for x in folders if os.path.isdir(x)]
    animalfolders = []
    for f in folders:
        tmp = [os.path.join(f, x, 'info.json') for x in os.listdir(f)]
        animalfolders = animalfolders + tmp
    
    animalfolders = [x for x in animalfolders if os.path.exists(x)]
    return(animalfolders)

def getListWithExpType(rootPath, expType):
    infoList = getInfoList(rootPath)
    finalList = []
    for i in infoList:
        try:
            tmp = utils.readjson(i)
            if expType in tmp.keys():
                finalList.append(i)
        except:
            print('%s has problem, fail to load' % i)
    return(finalList)

def getInfoContent(rootPath, keyarray):
        
    animalfolders = getInfoList(rootPath)
    result = []
    for f in animalfolders:
        info = utils.readjson(f)
        try:
            finalc=info
            for k in keyarray:
                finalc = finalc[k]
            result.append([f, finalc])
        except:
            pass
        
    return(result)

def checkTreatmentDrug(treatArrayList):
    finalList = []
    for treat in treatArrayList:
        for t in treat[1].keys():
            try:
                if 'drug apply' == treat[1][t]['method']:
                    finalList.append([treat[0], treat[1][t]['activate_drug']])
            except:
                pass
    return(finalList)


def treatmentMethod(info, method):
    treatment = info['treatment']
    thekey = []
    thedict = []
    for key, value in treatment.items():
        if value['method'] == method:
            thekey.append(key)
            thedict.append(value)
    if len(thekey) == 0:
        thekey = [None]
        thedict = [{}]
    elif len(thekey) > 1:
        raise Exception('No or more than 1 this method treatment')
    return(thekey[0], thedict[0])

