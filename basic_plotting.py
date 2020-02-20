
# coding: utf-8

# In[2]:


import numpy as np
import json
from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# In[82]:

#Configure the data for plotting, does not process lists with fewer than cutoff instances
def get_plot_data(lists, k, cutoff=30):
    n_1 = Counter([n[0] for n in lists])
    n_2 = Counter([n for lst in lists for n in lst[1:]])
    lst_names = set(n_1.keys())
    lst_names.update(n_2.keys())
    perc_first = {key: n_1[key]/(n_1[key] + n_2[key]) for key in lst_names if n_1[key] + n_2[key] >= cutoff}
    return perc_first.values()


# In[81]:

#Configure data for plotting ordinalities, does not process lists with fewer than cutoff instances
#Ordinality, in this case, is with respect to alphabetization
def get_plot_data_binomials(lists, cutoff=30):
    counter = Counter([tuple(l) for l in lists if len(l)==2])
    percs = {}
    counts = {}
    for t, c in counter.items():
        t2 = tuple([t[1], t[0]])
        c2 = counter[t2]
        if t > t2 and c+c2 >= cutoff:
            percs[t] = c/(c+c2)
            counts[t] = c+c2
        elif c2 == 0 and c+c2 >= cutoff:
            percs[t2] = 0
            counts[t2] = c+c2
    counts = Counter(counts)
    tot_percs = [percs[t[0]] for t in counts.most_common()]
    return tot_percs


# In[6]:

#Create the percentage histogram plots for lists of length 2-6, 30 bins
def get_plots(lists, title, pp=None):
    for k in range(2,6):
        lsts = [l for l in lists if len(l) == k]
        print(len(lsts))
        dat = get_plot_data(lsts, k, cutoff=30)
        plt.hist(dat, bins=30)
        plt.title(title + ', list length=' + str(k))
        plt.xlabel('Percent First')
        plt.ylabel('Number of Names')
        if(pp):
            pp.savefig()
        plt.show()


# In[78]:

#Gives a histogram of oridinality, where ordinality is alphabetical
#Plots are large for detail
def get_plots_binomials(lists, title, pp=None):
    
    
    fs=35
    
    data = get_plot_data_binomials(lists, cutoff=30)
    fig, ax = plt.subplots(1,1, figsize=(20, 10))
    #print(len(data))
    y,binEdges=np.histogram(data,bins=30)
    bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
    plt.plot(bincenters,y,'-')
        
    plt.title(title, fontsize=fs)
    plt.xlabel('Ordinality', fontsize=fs)
    plt.ylabel('Number of Lists', fontsize=fs)
    plt.rcParams['xtick.labelsize']=fs
    plt.rcParams['ytick.labelsize']=fs
    plt.show()


# In[5]:
if __name__ == '__main__':
    
    lists = []
    #We only collected lists of various sizes for the names lists
    with open('full_metadata_name_lists_all.json', 'r') as fp:
        all_lists = json.load(fp)
        lists.extend([l['order'] for l in all_lists])
         
    get_plots(lists, 'Name Lists, Percentage First')
    
    #We can run the ordinailty histogram on the all words lists (which should
    #contain the name lists of length=2)
    with open('all_words_filtered.json', 'r') as fp:
        all_lists = json.load(fp)
        get_plots_binomials(all_lists, 'All Words, Ordinality Histogram')
    
    #We can also run the ordinailty histogram on the names lists
    get_plots_binomials(lists, 'Name Lists, Ordinality Histogram')

