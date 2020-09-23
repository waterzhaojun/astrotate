import matplotlib.pyplot as plt
from matplotlib.markers import TICKDOWN
from matplotlib.ticker import PercentFormatter
import seaborn as sns


def heatmap(mx):
    pass

#============================================================================================================
# plot methods (This is from old analysis file) =============================================================
#============================================================================================================
def analysis_singleKey_between_groups(result_array, key, group_titles, savepath = None):
    """
    This function is to analyse the key between result array element
    """
    # deprecated
    def __intersection__(lists): 
        lst1 = lists[0]
        for i in range(1, len(lists)):
            tmplst = lists[i]
            lst1 = list(set(lst1) & set(tmplst))
        return(lst1)
    
    fig = plt.figure()
    
    ax = fig.add_subplot(n_rows, n_fig_of_each_row, i+1)
    
    dictarray = [x[key] for x in result_array]
    analysis = __intersection__([x[key]['analysis_method'] for x in result_array])
    if 'box' in analysis:
        ax_barplot(ax, dictarray, key, group_titles)
    elif 'scatter' in analysis:
        ax_scatter(ax, dictarray, key, group_titles)
    #fig.tight_layout()
    fig.subplots_adjust(hspace = 0.5, wspace = 0.7)
    if savepath != None:
        plt.savefig(savepath)
    plt.show()

def analysis_between_groups(result_array, group_titles, n_fig_of_each_row = 3, savepath = None):
    """
    When we analyse a group of data, we will get a dict containing series
    of analysis feature. If the analysis method is the same, different group
    will get a dict with same key words. This function is to plot along
    the keys to show different between groups. Right now it only tested two groups.
    """
    # deprecated
    def __intersection__(lists): 
        lst1 = lists[0]
        for i in range(1, len(lists)):
            tmplst = lists[i]
            lst1 = list(set(lst1) & set(tmplst))
        return(lst1)
    
    keys = list(result_array[0].keys())
    n_rows = math.ceil(len(keys)/n_fig_of_each_row)
    plt.rcParams["figure.figsize"] = [6 * n_fig_of_each_row, 6 * n_rows] 
    #plt.subplots_adjust(wspace = 1)
    #fig, axs = plt.subplots(n_rows, n_fig_of_each_row)
    fig = plt.figure()
    
    for i in range(len(keys)):
        axrow = int(i / n_fig_of_each_row)
        axcol = i % n_fig_of_each_row
        
        ax = fig.add_subplot(n_rows, n_fig_of_each_row, i+1)
        key = keys[i]
        dictarray = [x[key] for x in result_array]
        analysis = __intersection__([x[key]['analysis_method'] for x in result_array])
        if 'box' in analysis:
            try:
                ax_barplot(ax, dictarray, key, group_titles)
            except:
                pass
        elif 'scatter' in analysis:
            try:
                ax_scatter(ax, dictarray, key, group_titles)
            except:
                pass
    #fig.tight_layout()
    fig.subplots_adjust(hspace = 0.5, wspace = 0.7)
    if savepath != None:
        plt.savefig(savepath)
    plt.show()

def ax_barplot(ax, result_array, title, group_titles):
    # result_array is an array containing dict results from different groups.
    # This function will use bar plot to show the figure.
    # ax is the subplot from plt.subplot(n,m)
    
    def label_diff(ax,pair,text,X,ylevel):
        x = (X[pair[0]]+X[pair[1]])/2
        y = ylevel
        ax.annotate(text, xy=(x,y), zorder=10, ha = 'center', va = 'center', backgroundcolor='w')
        ax.plot([X[pair[0]], X[pair[1]]], [y, y],'-',lw=1,color = 'grey', marker = TICKDOWN,markersize = 3)

    def pvalue_text(p):
        if p > 0.05:
            text = ''# % p
        elif p <= 0.05 and p > 0.01:
            text = '*'# % p
        elif p<=0.01 and p > 0.005:
            text = '**'# % p
        else:
            text = '***'# % p
        return(text)
    
    # This code should set before make subplot. It is the fundmental.
    # It works for jupyter notebook. But I'm not sure if it works to output.
    width = 3/(4*len(result_array)-1)

    colors = plt.cm.Pastel2(np.linspace(0,1,8)) # Fist get cmap Pastel2. Then define set to how many pieces.
    
    xlocation = 4*np.arange(len(result_array))*width/3 + 0.5*width
    ax.set_xticks(xlocation)
    ax.set_xticklabels(group_titles, rotation=45)

    yvalue = [x['mean'] for x in result_array]
    errvalue = [x['sterr'] for x in result_array]

    ax.bar(xlocation, yvalue, width, 
            yerr = errvalue,
            color=colors)
        
    ax.set_title(title)
    
    standardy = max([x['mean']+x['sterr'] for x in result_array])
    plist, level = paired_analysis_idx(len(result_array))
    levelempty = [0]*len(plist)
    
    for i in range(len(plist)):
        p = stats.mannwhitneyu(np.array(result_array[plist[i][0]]['array']).astype(float), 
                                np.array(result_array[plist[i][1]]['array']).astype(float))[1]
        
        if p < 0.05:
            levelempty[level[i]-1] = 1
            label_diff(ax, plist[i], pvalue_text(p), xlocation, standardy + standardy * 0.12 * sum(levelempty[0:level[i]]))
    
    ax.set_ylim(0.0, standardy + standardy * 0.12 * sum(levelempty) +0.1 * standardy)


def ax_scatter(ax, result_arrays, title, group_titles):
    markerlist = ['s', '^']
    colors = plt.cm.tab10(np.linspace(0,1,10))
    
    for i in range(len(result_arrays)):
        array = result_arrays[i]
        X = np.array([x[0] for x in array['array']])
        Y = np.array([x[1] for x in array['array']])
        #C = np.array([x[2] for x in array['array']])
        
        ax.scatter(X, Y, c=colors[i], s=2, marker = ',', alpha = 0.3)
    ax.set_xlabel(result_arrays[0]['character_columns'][0])
    ax.set_ylabel(result_arrays[0]['character_columns'][1])
    ax.legend(group_titles)
    ax.set_title(title)

def ax_3dscatter(ax, result_arrays, title, group_titles):
    markerlist = ['s', '^']
    for i in range(len(result_arrays)):
        array = result_arrays[i]
        X = np.array([x[0] for x in array['array']])
        Y = np.array([x[1] for x in array['array']])
        Z = np.array([x[2] for x in array['array']])
        ax.scatter(X, Y, Z, marker=markerlist[i], alpha = 0.3)
        #ax.plot_wireframe(X,Y,Z, marker = markerlist[i], alpha = 0.2)
    ax.set_xlabel(result_arrays[0]['character_columns'][0])
    ax.set_ylabel(result_arrays[0]['character_columns'][1])
    ax.set_ylabel(result_arrays[0]['character_columns'][2])
    ax.legend(group_titles)
    ax.set_title(title)

def ax_boxplot(ax, result_arrays, title, group_title, show_marker = True, **kwargs):
    """
    This function is used to plot boxplot and scatter plot. It use matplotlib functions to do this
    instead of seaborn function.
    """
    N = len(result_arrays)
    width = 0.8
    h = np.max([np.max(x) for x in result_arrays])
    #markers = ['o','s','^']
    marker_size = kwargs.get('marker_size', 120)
    fontsize = kwargs.get('fontsize',20)

    for i in range(N):
        b = ax.boxplot(result_arrays[i],positions = [i],widths=width,showfliers=False)
        b = [item.get_ydata()[1] for item in b['whiskers']]
        
        if show_marker:
            x = np.random.normal(i, width/8, len(result_arrays[i]))
            plt.scatter(x,result_arrays[i], 
                        #marker=markers[i], 
                        alpha = 0.5, s = marker_size)
        if i > 0:
            aou, p = stats.mannwhitneyu(result_arrays[0], result_arrays[i])
            ax.text(i,b[1]+h*0.05,'p=%.03f'%p,horizontalalignment='center',fontsize=int(fontsize*0.8))
        
        
    ax.set_xticklabels(group_title)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(length=0)
    ax.tick_params(axis='x', labelsize=fontsize)
    ax.tick_params(axis='y', labelsize=fontsize)
    if 'ylabel' in kwargs.keys():
        ax.set_ylabel(kwargs['ylabel'], fontsize = fontsize)

def ax_ratebar(ax,result_arrays,title,group_title,**kwargs):
    # result_arrays is an array, each element is a [pos num, neg num] in each group
    
    N = len(result_arrays)
    pos_array = np.array([x[0]/(x[0]+x[1]) for x in result_arrays])
    neg_array = 1-pos_array
    
    width = 0.75
    fontsize = kwargs.get('fontsize',20)

    ax.bar(np.arange(N), np.ones(N), width=width,color='gray')
    ax.bar(np.arange(N), pos_array, width=width, bottom=neg_array,color='r')
    ax.set_xticks(np.arange(N))
    ax.set_xticklabels(group_title, fontsize=fontsize)
    ax.set_yticks([0,0.5,1])
    #ax.set_ylim([0,1])
    ax.tick_params(axis='x', labelsize=fontsize)
    ax.tick_params(axis='y', labelsize=fontsize)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    
    text_array=[]
    for i in range(len(result_arrays)):
        tmp = '{}/{}\n{:.1%}'.format(
            result_arrays[i,0],
            result_arrays[i,0]+result_arrays[i,1],
            result_arrays[i,0]/(result_arrays[i,0]+result_arrays[i,1])
        )
        ax.text(i,neg_array[i]+pos_array[i]/2,tmp,
            horizontalalignment='center',va='center',
            fontsize=width*20,color='white',fontweight='bold'
        )
        if i>0:
            aou, p = stats.fisher_exact([result_arrays[0,:], result_arrays[i,:]])
            ptext = 'p={:.3f}'.format(p)
            ylevel = 1.03+(i-1)*0.07
            ax.annotate(
                ptext, xy=(i/2,ylevel+0.03), 
                zorder=10, ha = 'center', va = 'center', 
                #backgroundcolor='w',
                fontsize=fontsize*0.7
            )
            ax.plot(
                [0, i], [ylevel, ylevel],'-',
                lw=2,color = 'grey', 
                marker = TICKDOWN,markersize = 2
            )
        

def ax_polarbar(ax, result_arrays, title, group_title):
    arr = [x['percentage'] for x in result_arrays]
    N = len(arr)

    # width of each bin on the plot
    width = (2*np.pi) / N

    ax.bar([0, width, 2*width, 3*width], math.ceil(max(arr)/0.1)*0.1, width=width, alpha = 0.1)
    ax.bar([0, width, 2*width, 3*width], arr, width=0.8*width, alpha = 0.6, edgecolor = 'grey')

    # set the lable go clockwise and start from the top
    ax.set_theta_zero_location("N")
    # clockwise
    #ax.set_theta_direction(-1)
    ytop = math.ceil(max(arr)/0.1)*0.1

    # set the label
    #ticks = ['0:00', '3:00', '6:00', '9:00', '12:00', '15:00', '18:00', '21:00']
    xlocation = [0, width, 2*width, 3*width]#np.arange(N)*width
    ax.set_xticks([0, width, 2*width, 3*width])
    ax.set_xticklabels(group_title)
    ax.set_ylim = [0,ytop]
    ax.set_yticks(np.linspace(0,ytop,N+1)[0:-1])
    ax.set_yticklabels([])
    for i in range(N):
        ax.text(xlocation[i], max(arr[i]/2, 0.3), "{:.1%}".format(arr[i]), 
                horizontalalignment='center',
                verticalalignment='center')

def ax_swarmplot(ax,result_arrays,title,group_titles,**kwargs):
    # result_obj_array is res_dict array.
    df = pd.DataFrame(columns = ['group','value'])
    control_res = result_arrays[0]
    for i in range(len(result_arrays)):
        tmpre = result_arrays[i]
        tmplen = len(tmpre)
        df = pd.concat([df,pd.DataFrame(data={'group':[group_titles[i]]*tmplen,
                                             'value':tmpre
                                            })],axis = 0)
        
    h = np.max(df.value.values)
    df.reset_index(inplace=True,drop=True)
    sns.boxplot(x="group", y="value", data=df,color='white',ax=ax,showfliers=False)
    plt.setp(ax.artists, edgecolor = 'black', facecolor='w')
    plt.setp(ax.lines, color='black')
    for i,artist in enumerate(ax.artists):
        ax.lines[i*5+4].set_color('orange')
        
        if i > 0:
            tmpre = result_arrays[i]
            aou, p = stats.mannwhitneyu(control_res, tmpre)
            b = np.quantile(tmpre,0.75)
            ax.text(i,b + h*0.05,'p=%.03f'%p,horizontalalignment='center')
    
    #marker_size = kwargs.get('marker_size', 10)

    sns.swarmplot(x='group',y='value',data=df,
        s=kwargs.get('marker_size', 10),
        #alpha=kwargs.get('alpha', 0.5),
        ax=ax,
        **kwargs)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_xlabel('')
    if kwargs.get('ylabel', False):
        ax.set_ylabel(kwargs['ylabel'])