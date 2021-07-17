# This module is to analyze open field experiment. The data is recorded by camera and initially analyzed by DLC

# Importing the toolbox (takes several seconds)
import pandas as pd
from pathlib import Path
import numpy as np
import os
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from IPython.display import Video


def sortCorner(corners):
    # This function is to sort the input corners to let it start from upper left corner and go clockwise.
    center = np.mean(corners, axis = 0)
    c = corners - center
    cup = c[(c[:,0] <= 0)]
    cup_angle = np.arcsin(cup[:,1] / np.sqrt(cup[:,0]**2 + cup[:,1]**2))
    cup_angle_idx = np.argsort(cup_angle)

    cdown = c[(c[:,0] > 0)]
    cdown_angle = np.arcsin(cdown[:,1] / np.sqrt(cdown[:,0]**2 + cdown[:,1]**2))
    cdown_angle_idx = np.flip(np.argsort(cdown_angle))

    res = np.concatenate([cup[cup_angle_idx], cdown[cdown_angle_idx]])

    return(res, center)


def box_identify(corners):
    # This function is to identify a rectangle box's characters by giving the corner coordinates.
    # The rectangle's longer axis will be put horizontal.
    # Negtive angle means the original rectangle anti-clockwised. This angle is exactly the angle we need for angle_translate function.
    # The corner coordinates should be [r,c], in another words: [y,x]
    res = dict()

    res['corners'],res['center'] = sortCorner(corners)
    print(res['corners'])

    point1 = np.mean(res['corners'][0:2, :], axis = 0)
    point2 = np.mean(res['corners'][2:4, :], axis = 0)
    d = point1 - point2

    # point1_backup = np.mean(res['corners'][1:3, :], axis = 0)
    # point2_backup = np.mean(res['corners'][[0,3], :], axis = 0)
    # d_backup = point1_backup - point2_backup

    # if d[0]**2 + d[1]**2 < d_backup[0]**2 + d_backup[1]**2:
    #     theangle = math.asin(d[1] / math.sqrt(d[0]**2 + d[1]**2))
    # else:
    #     theangle = math.acos(d[1] / math.sqrt(d[0]**2 + d[1]**2))
    theangle = math.asin(d[1] / math.sqrt(d[0]**2 + d[1]**2))

    res['angle'] = theangle
    res['angle_degree'] = theangle/math.pi*180
    res['translated_corners'] = [angle_translate(x, res['angle']) for x in res['corners']]
    
    return(res)

def angle_translate(coord, angle):
    # The coord is the old coord [x,y].
    # the angle is the value that trun axis clockwise. this value is not degree but real value.
    res = [
        coord[0] * math.cos(angle) - coord[1] * math.sin(angle),
        coord[0] * math.sin(angle) + coord[1] * math.cos(angle)
    ]
    return(res)

def relative_dlc_coord(data, boxdata):
    newdata = np.zeros(np.shape(data))
    parts = int(np.shape(data)[1] / 2)
    for i in range(parts):
        tmpdata = np.fliplr(data[:,i*2:i*2+2])
        for j in range(np.shape(tmpdata)[0]):
            newdata[j,i*2:i*2+2] = angle_translate(tmpdata[j,:] - boxdata['center'], boxdata['angle']) *np.array([-1,1])
    return(newdata)
        




# def relative_coordinates(coord, corners):
#     sorted_corners = sortCorner(corners)
#     box_angle = box_identify(sorted_corners)
#     relative_coord = angle_translate(coord)



class OpenField():
    def __init__(self, dlcresultpath):
        self.rawdata = pd.read_hdf(dlcresultpath)
        self.partnames = np.unique([x[1] for x in self.rawdata.columns])
        dataidx = np.sort(np.append(3 * np.arange(len(self.partnames)), 3 * np.arange(len(self.partnames))+1))
        self.r = len(self.partnames)
        self.c = 2
        self.f = np.shape(self.rawdata)[0]
        self.data = np.reshape(self.rawdata.iloc[:,dataidx].to_numpy(), (self.f, self.r, self.c))
        
    def set_corners(self,corners):
        # You could use a 4x2 as corners, which means the corners are constant along the video.
        # Or you could use Nx4x2 as corners, which means along the video, each frame has independent corners (even it is the same).
        # In this function if the corners is the 1st option, we will transform it to Nx4x2.
        
        if not (np.shape(corners)[-2] == 4 and np.shape(corners)[-1] == 2):
            raise Exception('corners shape should be Nx4x2')

        if len(np.shape(corners)) == 2:
            self.corners = np.repeat(np.reshape(sortCorner(corners),[1,4,2]), self.f, axis = 0)
        elif len(np.shape(corners)) == 3:
            for i in range(len(np.shape(corners)[0])):
                self.corners[i,:,:] = sortCorner(corners[i,:,:])
        else:
            raise Exception('The corners shape should be Nx4x2')
        
    def get_relative_coord(self):
        res = dict()

        res['corners'],res['center'] = sortCorner(corners)
        print(res['corners'])

        point1 = np.mean(res['corners'][0:2, :], axis = 0)
        point2 = np.mean(res['corners'][2:4, :], axis = 0)
        d = point1 - point2

        # point1_backup = np.mean(res['corners'][1:3, :], axis = 0)
        # point2_backup = np.mean(res['corners'][[0,3], :], axis = 0)
        # d_backup = point1_backup - point2_backup

        # if d[0]**2 + d[1]**2 < d_backup[0]**2 + d_backup[1]**2:
        #     theangle = math.asin(d[1] / math.sqrt(d[0]**2 + d[1]**2))
        # else:
        #     theangle = math.acos(d[1] / math.sqrt(d[0]**2 + d[1]**2))
        theangle = math.asin(d[1] / math.sqrt(d[0]**2 + d[1]**2))

        res['angle'] = theangle
        res['angle_degree'] = theangle/math.pi*180
        res['translated_corners'] = [angle_translate(x, res['angle']) for x in res['corners']]
        
        return(res)


    def to_relative_mov(self):
        pass
