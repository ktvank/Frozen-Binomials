# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 11:53:50 2019

@author: Katherine
"""

import json
from collections import Counter
import pandas as pd
import os

import nltk
#nltk.download('averaged_perceptron_tagger')

#Please have your names in a column named 'Name' in a csv file. Depending on how you acquired your names
#you may need to do additional cleaning or change the format. Some basic cleaning is done below to remove initials
#and common addendums. One excellent source of names is Wikipedia, another is sports stats websites.
def get_names():
    names = []
    with open('name_file.csv', 'r') as f:
        df = pd.read_csv(f, header=0)
    names.extend([s.strip('*+') for s in list(df['Name']) if len(s) > 1])
    name_lst = names + list(set([n for ns in names for n in ns.split(" ") if not (len(n) == 2 and n[1] == '.') and len(n) > 1]))
    return name_lst


#This filter allows only lists that come from teh same part of speech. We make sure that all names
#count as proper nouns, and we use nltk pos_tag for the tagging.
def pos_filter(lst, names):
    white_list = {'CD':0, 'FW':9, 'IN':1, 'JJ':2, 'JJR':2, 'JJS':2, 'MD':3, 'NN':4, 'NNS':4, 'NNP':4,''' 'PRP':5, 'PRP$':5,''' 'RB':6, 'RBR':6, 'RBS':6, 'RP':7, 'VV':8, 'VVD': 8, 'VVP': 8, 'VVG': 8, 'VVN': 8, 'VVP': 8, 'VVZ': 8, 'X':10}
    #print(lst)
    pos = [nltk.pos_tag([l])[0][1] for l in lst]
    name_ind = [i for i in range(len(lst)) if lst[i] in names]
    for i in name_ind:
        pos[i] == 'NNP'
    if not all(p in white_list.keys() for p in pos):
        return False
    return all(p in white_list.keys() for p in pos)

#This filter allows only lists where all words are longer than some length.
def length_filter(lst, length=1):
    return all(len(l) > length for l in lst)

#This filter a
def startswith_filter(lst):
    blacklist = set('th')
    return all(not l.startswith(s) for l in lst for s in blacklist)

#This filter removes lists that contain words such as "you're", "you'll" and "won't". These types of 
#contractions usually can only gramatically come at the end of a conjunction and are not 'real' binomials.
def endswith_filter(lst):
    blacklist = set(["'re", "'ll", "'t"])
    return all(not l.endswith(s) for l in lst for s in blacklist)

#This filter removes two common 'words' that are products of Reddits text encoding.
def contains_filter(lst):
    blacklist = set(['u2019', '&gt'])
    return all(not s in l for l in lst for s in blacklist)

#This filter removes words that are commonly captured in our lists, but rarely form 'true' binomials, 
#as they grammatically can only be on one side of the conjunction.
def blacklist_filter(lst):
    blacklist=set(['and', 'was', 'is', 'we', 'what', 'who', 'when', 'why', 'how', 'where', "it's", 'if', "i'm", "i've", "won't", 'in', 'put', "i'd", 'im', 'by', 'something'])
    return all(l not in blacklist for l in lst)

#This runs the filters above for every list in your all_words_lists_unfiltered directory. This directory is created by a 
#bash script, get_all_words_lists.sh.
def filter_lists():
    global filtered
    global totals
    filtered = Counter()
    totals = {}
    names = get_names()
    sea = []
    for file in os.listdir('all_words_lists_unfiltered/'):
        with open('all_words_lists_unfiltered/' + file, 'r') as fp:
            all_words = []
            for cnt, line in enumerate(fp):
                l = line.split()
                all_words.append([l[0], l[2]])
            print('loaded ' + file)
        filters = [length_filter, startswith_filter, endswith_filter, contains_filter, blacklist_filter]
        print(sea)
        for lst in all_words:
            ls = [l.strip('"()[]{}/') for l in lst]
            if all(f(ls) for f in filters) and pos_filter(lst, names):
                sea.append(ls)
    filtered = Counter([tuple(s) for s in sea])
    print(len(totals))
    print(filtered.most_common()[:50])

    return sorted(sea)
    


if __name__ == '__main__':
    

    
    results=filter_lists()
    
    with open('all_words_filtered.json', 'w') as fp:
           json.dump(results, fp)
