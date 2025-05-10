from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass
import re
from urllib import request
import io  
import xlrd
import networkx as nx
import community
import math
import urllib 
# from xlutils.copy import copy
from openpyxl import load_workbook
import socket
import sys 
import json
import requests
import time
import random
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# import psutil

def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.
    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:
        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}
    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__
 
    def sizeof(o):
        #print(o)
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)
 
        if verbose:
            print(s, type(o), repr(o), file=stderr)
 
        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s
 
    return sizeof(o)
def construct_tree(filename):

    cnt2child={}
    cnt2fa={}
    cnt2and={}
    cnt2seq={}
    cnt2condition={}
    cnt2interval={}
    cnt2combinations={}
    num=1
    with open(filename,'r',encoding='utf8') as f:
        for line in f:
            line=line.strip('\n')
            if num%2==1:
                a=int(line.split(' ')[0])
                b=int(line.split(' ')[1])
                cnt2fa[a]=b
                if a not in cnt2child.keys():
                    cnt2child[a]=[]
                if b not in cnt2child.keys():
                    cnt2child[b]=[a]
                else:
                    cnt2child[b].append(a)
                cnt2interval[a]=60
                And=line.split(' ')[3]
                and_list=And.split('|')
                seq=line.split(' ')[4]
                if seq=="":
                    seq_list=[]
                else:
                    seq_list=seq.split('|')
                
                cnt2and[a]=and_list
                cnt2seq[a]=seq_list
                cnt2combinations[a]={}
            else:
                condition=json.loads(line)
                cnt2condition[a]=condition
            num+=1
    return cnt2child,cnt2fa,cnt2and,cnt2seq,cnt2condition,cnt2interval,cnt2combinations
def update_ready():
    global ready
    tem_list=[]
    for item in ready:
        if cnt2fa[item] not in success:
            tem_list.append(item)
    for item in tem_list:
        ready.remove(item)
        delete_extra_memory(item)
def add_ready(node,cur_time): #node从ready变成success后更新它的子节点
    global ready,cnt2combinations
    for child in cnt2child[node]:
        ready.append(child)
        for item in all_events:
            if item[0] in cnt2and[child] and cur_time-item[3]<=cnt2interval[child]:
                if item[0] not in cnt2combinations[child].keys():
                    cnt2combinations[child][item[0]]=[(item[1],item[2],item[3])]
                else:
                    cnt2combinations[child][item[0]].append((item[1],item[2],item[3]))
        add_extra_memory(child)
def delete_all_events(cur_time):
    global all_events
    tem_list=[]
    for item in all_events:
        if cur_time-item[3]>60:
            tem_list.append(item)
    for item in tem_list:
        all_events.remove(item)
def delete_success(cur_time):#去除过时的事件，更新success和ready状态
    global success,cnt2combinations,ready
    delete_list=[]
    for node in success:
        if node==0:
            continue
        for key in cnt2combinations[node].keys():
            tem_list=[]
            for item in cnt2combinations[node][key]:
                if cur_time-item[2]>cnt2interval[node]:
                    tem_list.append(item)
            for item in tem_list:
                cnt2combinations[node][key].remove(item)
        if judge_success(node)==False:
            delete_list.append(node)
    for node in delete_list:
        success.remove(node)
    tem_list=[]
    for item in ready:
        if cnt2fa[item] not in success:
            tem_list.append(item)
    for item in tem_list:
        ready.remove(item)
        delete_extra_memory(item)
    for item in success:
        for node in cnt2child[item]:
            if node not in ready and node not in success:
                ready.append(node)
                add_extra_memory(node)
    for node in ready:
        for key in cnt2combinations[node].keys():
            tem_list=[]
            for item in cnt2combinations[node][key]:
                if cur_time-item[2]>cnt2interval[node]:
                   tem_list.append(item)
            for item in tem_list:
                cnt2combinations[node][key].remove(item)
def judge_success(node):
    
    for id in cnt2and[node]:
        if id not in cnt2combinations[node].keys() or len(cnt2combinations[node][id])==0:
            return False
    #print("!!!")
    for key in cnt2condition[node].keys():
        flag=False
        for type in cnt2condition[node][key]:
            for item in cnt2combinations[node][key]:
                if type==0:
                    if item[0]<5:
                        flag=True
                elif type==1:
                    if item[0]>40:
                        flag=True
                elif type==2:
                    if item[1]<20:
                        flag=True
                elif type==3:
                    if item[1]>120:
                        flag=True
        if flag==False:
            return False
    #print("???")
    flag=False
    all_seq=[]
    for key in cnt2condition[node].keys():
        for item in cnt2combinations[node][key]:
            all_seq.append((key,item[2]))
    all_seq=sorted(all_seq,key=lambda x:x[1])
    pos=0
    if len(cnt2seq[node])==0:
        return True
    for item in all_seq:
        if cnt2seq[node][pos]==item[0]:
            pos+=1
        if pos==len(cnt2seq[node]):
            break
    if pos==len(cnt2seq[node]):
        return True
    else:
        return False
def filtered():
    result={}
    for key in cnt2combinations.keys():
        if key in ready or key in success:
            result[key]=cnt2combinations[key]
    return result
def test():
    for node in success:
        for item in cnt2child[node]:
            if item not in success and item not in ready:
                print("!!!",item)

    #update_ready()
    for item in ready:
        if item in success:
            print(tim,item)
        for child in cnt2child[item]:
            if child in ready:
                print("error",child)
    for item in success:
        if item>0 and cnt2fa[item] not in success:
            if cnt2fa[item] in ready:
                print('ready',item,cnt2fa[item])
                        
            else:
                print('null',item,cnt2fa[item])
                #print(judge_success(item))
                #print(judge_success(cnt2fa[item]))
def add_extra_memory(node):
    global extra_combinations
    all_events_base = [x[0] for x in all_events]
    if len(cnt2seq[node]) == 0:
        tem_dic = {x: id2fre[str(x)] for x in cnt2and[node]}
        result_min = min(tem_dic, key=lambda x: tem_dic[x])
        mn_base_event = int(result_min)
    else:
        mn_base_event = cnt2seq[node][-1]
    if mn_base_event not in all_events_base:
        # extra_combinations[node] = {x:cnt2combinations[node][x] for x in cnt2combinations[node].keys()}
        extra_combinations[node] = cnt2combinations[node]
def delete_extra_memory(node):
    global extra_combinations
    if node in extra_combinations.keys():
        del extra_combinations[node]
id2cnt={}
ids=[]
test_num=500
test_type='traffic'
method='ours'
with open(test_type+'_time_input.json','r',encoding='utf8') as f:
    dic=json.load(f)

    id_num=0
    cnt=1
    tim=0
    input=[]
    for key in dic.keys():
        for cross_id in dic[key].keys():
            if 'avgSpeed'not in dic[key][cross_id].keys():
                continue
            count=dic[key][cross_id]['vehCount']
            speed=dic[key][cross_id]['avgSpeed']
            input.append((cross_id,count,speed,tim))
        tim+=5
print("sum_time:",tim)
            
filename='data'+'/'+str(test_type)+'/'+str(test_type)+'_tree_'+str(method)+str(test_num)+'.txt'
cnt2child,cnt2fa,cnt2and,cnt2seq,cnt2condition,cnt2interval,cnt2combinations=construct_tree(filename)
#print('init_child',cnt2child[0])
success=[0]
ready=[]
for item in cnt2child[0]:
    ready.append(item)
num=0
all_events=[]
pre_time=-1
cnt=0
days=-1
sum_time=0
sum_mem=0
mx_mem=0
starttime = time.time()
extra_combinations={}
with open('data'+'/'+test_type+'/'+test_type+'_frequency.json', 'r', encoding='utf8') as f:
    id2fre = json.load(f)
for item in input:
    cross_id=item[0]
    tim=item[3]
    count=item[1]
    speed=item[2]
    cnt+=1
    if tim>pre_time:
                        
        delete_success(tim)
        delete_all_events(tim)
        dic=filtered()
        #print(type(dic),dic)
        siz=total_size(dic)- total_size(extra_combinations)
        mx_mem=max(mx_mem,siz)
        if tim%1440==0:
            sum_mem+=mx_mem
            mx_mem=0
            days+=1
            print('tim:',tim,siz)
            endtime = time.time()
            dtime = endtime - starttime
            print("run_time:",tim,dtime)
            #f.write(str(siz)+'\n')
            if tim//1440==30:
                break
        pre_time=tim
    if count>0 and speed>110 or speed<30:
        #print(cross_id,tim,dif)
        #print(tim,cross_id)
        all_events.append((cross_id,count,speed,tim))
        num+=1
            
        #update_ready()
        tem_list=[]
        for node in success:
            if node>0 and cross_id in cnt2and[node]:
                if cross_id not in cnt2combinations[node].keys():
                    cnt2combinations[node][cross_id]=[(count,speed,tim)]
                else:
                    cnt2combinations[node][cross_id].append((count,speed,tim))
        for node in ready:
            #comb_list=cnt2combinations[node]
            #print(cross_id,cnt2and[node])
            if cross_id in cnt2and[node]:

                if cross_id not in cnt2combinations[node].keys():
                    cnt2combinations[node][cross_id]=[(count,speed,tim)]
                else:
                    cnt2combinations[node][cross_id].append((count,speed,tim))
            if judge_success(node):
                tem_list.append(node)
        for node in tem_list:
            success.append(node)
            ready.remove(node)
            delete_extra_memory(node)
            add_ready(node,tim)
        #print(cnt2combinations)
        #print('ready:',ready)
        #print('success:',success)
        #if len(success)>1:
            #print('success:',success)
            #print(get_current_memory_gb())
        #test()
            
endtime = time.time()
dtime = endtime - starttime
#runtime:5425.43         
print(num)
print('ave_time:',dtime/days)
print('ave_mem:',sum_mem/days)



