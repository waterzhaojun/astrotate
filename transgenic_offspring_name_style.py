import pandas as pd



style_list = pd.DataFrame(columns=['parents_title', 'offspring_title'])
# style_list.loc[len(style_list), :] = []

def name_title(fullname):
    tmp = fullname.split('-')
    if len(tmp) > 1:
        tmp = tmp[0:-1]
    title = '-'.join(tmp)
    return(title)

def offspring_title(title_list):

    title_list = [x for x in title_list if x is not None]

    if len(title_list) == 1:
        offspring_title = title_list[0]
    
    elif len(title_list) == 2:
        if title_list[0] == title_list[1]:
            offspring_title = title_list[0]
        else:
            pass
            # itmp = np.array_equal(style_list.loc[:, 'parents_title'], title_list)
            # offspring_title = style_list.loc[itmp, 'offspring_title']

    return(offspring_title)
