import pandas as pd
import numpy as np



style_list = pd.DataFrame(columns=['parents_title', 'offspring_title'])
style_list.loc[len(style_list), :] = [['IP3R2', 'B6.Cg-Edil3'], 'IP3R2.B6CE']
style_list.loc[len(style_list), :] = [['Pirt-Cre', 'R26tdTomato'], 'Pirt-Cre-R26tdTomato']
style_list.loc[len(style_list), :] = [['R26tdTomato', 'CGRP.Cre'], 'CGRP.Cre-R26tdTomato']
# print(style_list)

def name_title(fullname):
    tmp = fullname.split('-')
    if len(tmp) >1:
        num_length = len(tmp[-1])
        title = fullname[0:int(len(fullname)-num_length-1)]
    else:
        title=fullname
    return(title)

def name_serialnum(fullname):
    tmp = fullname.split('-')
    return(tmp[-1])

def different_strain_title(a, b):
    title = np.array([])
    for i in range(len(style_list)):

        if (a in style_list.loc[i, 'parents_title']) & (b in style_list.loc[i, 'parents_title']):
            title = np.append(title, style_list.loc[i, 'offspring_title'])

    print(title)
    if len(title)>1:
        raise ValueError('You have multi rows fit your parents title. Please check the style_list.')
    else:
        return(title[0])
    


def offspring_title(title_list):

    title_list = [x for x in title_list if x is not None]

    if len(title_list) == 1:
        offspring_title = title_list[0]
    
    elif len(title_list) == 2:
        if title_list[0] == title_list[1]:
            offspring_title = title_list[0]
        else:
            offspring_title = different_strain_title(title_list[0], title_list[1])
            # itmp = np.array_equal(style_list.loc[:, 'parents_title'], title_list)
            # offspring_title = style_list.loc[itmp, 'offspring_title']

    return(offspring_title)

