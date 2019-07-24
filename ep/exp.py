import os
import argparse
import util
import pandas as pd
import numpy as np

def getProject():
    info = util.readjson('project.json')
    project = info['project']
    return(project)

def loadSpikeData(files, channel, bint):
    data = []
    for file in files:
        tmp = pd.read_csv(file, sep = '\t')
        tmp = tmp.loc[:, channel].values
        tmp = [x for x in tmp if not pd.isnull(x)]
        if bint > 1:
            tmp = util.bint1d(tmp, bint)
        data = np.append(data, tmp)
    return(data)


parser = argparse.ArgumentParser(description='init a folder for the exp')
parser.add_argument('-e', '--exp', type=str, required=True,
                    help='exp date, will use this as folder name. The format should be 190520')
parser.add_argument('-t', '--type', type=str, required=True,
                    help='the type of data. b represent blood flow. s represent single neuron. l represent lfp. m represent multi unit. o represent oxygen')
parser.add_argument('--bchannel', default = '1 BF', 
                    help='blood flow channel name')
parser.add_argument('--freq', type=int, help='the output spike 2 file frequency.')                    
args = parser.parse_args()


if __name__ == "__main__":
    foldername = args.exp
    if not os.path.exists(foldername):
        os.mkdir(foldername)
    else:
        print('This folder already exist. Stop init the exp.')

    project = getProject()
    if project == 1:
        animal = util.readjson('templates/animal_cno.json')['animal']
    
    treatment = util.readjson('treatment.json')['treatment']

    info = {}
    info['animal'] = animal # update animal info
    info['project'] = [project] # update project info
    info['treatment'] = treatment # update treatment

    # single neuron data ===================================================================
    if 's' in args.type:
        data = pd.read_csv('templates/data_singleneuron.csv')

        # update spontaneous data
        tmp = data.loc[:, 'ongoing'].values
        spon = []
        for i in range(len(tmp)):
            if not pd.isnull(tmp[i]):
                tmpspon = np.array(list(map(float, tmp[i].replace(' ', '').split(','))))
                # print(tmpspon)
                if len(tmpspon) == 3:
                    tmpspon = tmpspon/np.array([300, 300, 150])
                elif len(tmpspon) == 6:
                    tmpspon = tmpspon/300
                spon = np.append(spon, tmpspon)
        print(spon)
        if len(spon) > 0:
            np.save(os.path.join(args.exp, 'single_neuron_spontaneous_1.npy'), spon)

        # update mech data
        mech = []
        for i in range(len(data)):
            tmp = data.loc[i, ['force1', 'force2']].values
            if (not pd.isnull(tmp[0])) and (not pd.isnull(tmp[1])):
                if len(mech) == 0:
                    mech = np.reshape(tmp, [1,2])
                else:
                    mech = np.concatenate((mech, np.reshape(tmp, [1,2])), axis = 0)
        print(mech)
        if len(mech) > 0:
            np.save(os.path.join(args.exp, 'single_neuron_mech_1.npy'), mech)

    # blood flow data ===================================================================
    if 'b' in args.type:
        files = os.listdir('data')
        files = [os.path.join('data', x) for x in files if x[-4:] == '.txt']
        files.sort()
        if 5%args.freq != 0:
            raise Exception('the output spike2 file can not by full devide by 5. try to output at 1hz')
        else:
            tmpb = int(5/args.freq)
        bfdata = loadSpikeData(files, args.bchannel, tmpb)
        np.save(os.path.join(foldername, 'bf.npy'), bfdata)
        print('bf save finished, the length is %d' % len(bfdata))

        info['bf'] = {}
        info['bf']['file_path'] = 'bf.npy'
        info['bf']['treat_point'] = {'1': 360},
        info['bf']['bin_size'] ='5sec'
    

    util.updateInfo(os.path.join(foldername, 'info.json'), info)
    print('finished upload. please check the info carefully. the present treat points and single neuron data is not created well')
    