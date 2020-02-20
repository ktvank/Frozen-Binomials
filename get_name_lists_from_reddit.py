#!/usr/bin/env python
# coding: utf-8

# In[22]:


import pandas as pd
import re
import os
import json
import multiprocessing as mp
import copy
from pathlib import Path

# In[25]:

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

# In[26]:

#This will process Reddit comments. In this case, that just means a list of dictionaries.
#'text' referes to the text, 'id' refers to the comment id.
#Here, we are splitting lists based on several splitters - and, or, vs, v.s. and /. The vast
#majority of lists contain 'and', with about 10% containing 'or'. The other cases are usually
#negligible.
def process_comments(lists, name_re):
    filter_lists = {}
    splitters = re.compile(r'(?:and |or |vs |v\.s\. |\/|,)', re.IGNORECASE)
    for l in lists:
        text = l['text']
        matches = name_re.findall(text)
        matches = [m for m in matches if splitters.search(m)]
        if len(matches)>0:
            l['matches'] = matches
            filter_lists[l['id']] = l

    orders = {}
    for tid, lst in filter_lists.items():
        order = []
        matches = lst['matches']
        for l in matches:
            listing = copy.deepcopy(lst)
            listing['order'] = [n.strip().lower() for n in splitters.split(l) if len(n.strip()) > 0]
            listing['matches'] = l
            order.append(listing)
        orders[tid] = order

    all_lists = []
    for k, v in orders.items():
        for l in v:
            all_lists.append(l)
    return all_lists


# In[27]:

#This will process a single reddit comment or post. The metadata here is in the format
#that Reddit downloads usually present it in. Not all metadata is recorded. Note
#that there is a difference in the metadata for some Reddit data between posts and comments.
def process_line(line, name_re):  
    entry = line
    metadata = {'Author': entry.get('author', None),
        'URL': entry.get('permalink', None),
        'id': entry.get('id', entry.get('name', None)),
        'Subreddit': entry['subreddit'],
        'Time': entry['created_utc'],
        'link_id': entry.get('link_id', None),
        'parent_id': entry.get('parent_id', None),
        'is_post': 'selftext' in entry,
        'text': entry.get('selftext', entry.get('body', '')),
        'author_flair_text': entry.get('author_flair_text', None),
        'retrieved_on': entry.get('retrieved_on', None),
        'author_flair_css_class': entry.get('author_flair_css_class', None)}
    text = entry.get('selftext', entry.get('body', ''))
    finds = name_re.search(text)
    if finds:
        return metadata

#%%
#Please place the Reddit post data in a json file as a jsonlist. The comments are often
#too big to fit in one file, so instead place a series of jsonlists in a folder
#called 'comments'. This also aids in parallelization.
def get_paths():
     return ['comments/', 'posts.json']
#%%
def get_lists_callback(result):
    #list_result.extend(result)
    print('done')

#%%
    
#This processes one comment file, and dumps the resulting lists and metadata in an output folder.
def get_lists_from_file(file, name_re):
    lists=[]
    if '.json' in file:
        with open(get_paths()[0] + file, 'r') as f:
            print(file)
            for line in f:
                l = json.loads(line)
                p = process_line(l, name_re)
                if(p):
                    lists.append(p)
        with open('partial_list/list_partial_comments_full_metadata_' + file, 'w') as fp:
            json.dump(lists, fp)
    return

# In[28]:


def get_all_lists():
    names = get_names()
    name_regex = r'(?:' + '|'.join([re.escape(n) for n in names]) + ')'
    regex = r'(?:\A|\W)(?:{}(?:,|\/)? )+(?:and |or |vs |v\.s\. |\/)?{}(?=\Z|\W)'.format(name_regex, name_regex)
    name_re = re.compile(regex, re.IGNORECASE)
    #Change this as necessary
    pool = mp.Pool(5)
    for file in os.listdir(get_paths()[0]):
        if not '.json' in file:
            continue
        pool.apply_async(get_lists_from_file, args=(file, name_re), callback=get_lists_callback)
    pool.close()
    pool.join()
    print('mp success')
    
    full_lists = []
    for file in os.listdir('partial_list/'):
        with open('partial_list/' + file, 'r') as f:
            l = json.load(f)
            full_lists.extend(l)
    with open('full_metadata_name_lists_comments.json', 'w') as f:
        json.dump(full_lists, f)
    
    
    lists = []        
    count = 0    
    with open(get_paths()[1], 'r') as f:
        print(get_paths()[1])
        for line in f:
            count += 1
            if (count % 1000 == 0):
                print(count)
            l = json.loads(line)
            p = process_line(l, name_re)
            if(p):
                lists.append(p)
                    
    print(len(lists))
    return lists, full_lists, name_re



# In[29]:

# In[30]:


def get_season_lists():
    lists, full_lists, name_re = get_all_lists()
    with open('full_metadata_name_lists_posts.json', 'w') as fp:
        json.dump(lists, fp)
    all_lists = full_lists
    all_lists.extend(lists)
    all_lists = process_comments(all_lists, name_re)
    with open('full_metadata_name_lists_all.json', 'w') as fp:
        json.dump(all_lists, fp)
    print('done')
    

    


# In[31]:
if __name__ == '__main__':
    
    Path("partial_list/").mkdir(parents=True, exist_ok=True)
    get_season_lists()
    


# In[ ]:




