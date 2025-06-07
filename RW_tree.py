import re
from urllib import request
import io  
import xlrd
import networkx as nx
import community
import math
import urllib 
from xlutils.copy import copy
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
import psutil

nodes=[]
id2adj={}
id2fa={}
vis={}
pair2and={}
pair2condition={}
pair2seq={}
path='processed_data_feb_june/'
time2data={}

id2and={}
id2condition={}
id2seq={}
id2freq={}#基础事件个数
id2prob={}#每个路口满足属性条件的个数
id2sum={}#基础事件总数量

def cal_cost(id_list,condition_dict):

    
    #id_list=mode_dict[key]['id']
    #interval=mode_dict[key]['interval']
    interval=60
    #condition=mode_dict[key]['condition']
    size=len(id_list)
    #sum_base=0
    result=1
    for id in id_list:
        #sum_base+=id2freq[id]
        result=result*(id2freq[id]/sum_len)
    #result=result*pow(interval/60,size)
    for id in condition_dict.keys():
        tem=0
        for condition in condition_dict[id]:
            tem+=id2prob[id][condition]/id2freq[id]
        if tem>0:
            result=result*tem
        else:
            result=result/(id2freq[id]/sum_len)
    return result
def check(id1,id2):
    for id in id2and[id1]:
        if id in id2and[id2]:
            return False
    return True
starttime = time.time()
for filename in os.listdir(path):
     with open(path+filename,'r',encoding='utf8') as f:
        
        sum_len=0
        #id=filename.split('.')[0][13:19]
        id=filename.split('.')[0][11:17]
        id2sum[id]=0
        dict=json.load(f)
        num=0
        nums={0:0,1:0,2:0,3:0}
        for key in dict:
            sum_len+=5
            if dict[key]["vehCount"]==0 or "avgSpeed" not in dict[key].keys():
                continue
            
            id2sum[id]+=1
            if  (dict[key]["avgSpeed"]>100 or dict[key]["avgSpeed"]<50):
                num+=1
            if dict[key]["vehCount"]<5:
                nums[0]+=1
            elif dict[key]["vehCount"]>40:
                nums[1]+=1
            elif dict[key]["avgSpeed"]<20:
                nums[2]+=1
            elif dict[key]["avgSpeed"]>120:
                nums[3]+=1
        sum_len=sum_len/60
        id2freq[id]=num
        id2prob[id]=nums
test_num=1000
test_type='traffic'
method='RW'
iter=5000//(1000//test_num)
with open(str(test_type)+'_mode_'+str(test_num)+'.json','r',encoding='utf8') as f:
    mode_dict=json.load(f)
    cnt=0
    for key in mode_dict.keys():  
        
        cnt+=1
        id_list=mode_dict[key]['id']
        #interval=mode_dict[key]['interval']
        interval=60
        condition=mode_dict[key]['condition']
        id2and[key]=mode_dict[key]['id']
        id2condition[key]={}
        for id in mode_dict[key]['property']:
            id2condition[key][id]=[mode_dict[key]['condition']]
        if mode_dict[key]['logic']['seq']==1:
            id2seq[key]=mode_dict[key]['property']
        else:
            id2seq[key]=[]
with open('baseline3/graph'+str(test_num)+'.txt','r',encoding='utf8') as f:
    num=1
    for line in f:
        line=line.strip()
        if num%2==1:
            words=line.split(' ')
            a=words[0]
            b=words[1]
            if a not in nodes:
                id2fa[a]=[]
                nodes.append(a)
            if b not in nodes:
                id2fa[b]=[]
                nodes.append(b)
            if a not in id2adj.keys():
                id2adj[a]=[b]
            else:
                id2adj[a].append(b)
            if b not in id2adj.keys():
                id2adj[b]=[a]
            else:
                id2adj[b].append(a)
            and_list=words[2].split('|')
            pair2and[(a,b)]=and_list
            pair2and[(b,a)]=and_list
            num_seq=int(words[3])
            seq_list=[]
            for i in range(4,len(words)):
                seq_list.append(words[i].split('|'))
            pair2seq[(a,b)]=seq_list
            pair2seq[(b,a)]=seq_list
        else:
            condition=json.loads(line)
            pair2condition[(a,b)]=condition
            pair2condition[(b,a)]=condition

        num+=1

vis={}
delete_id=[]
for i in range(iter):
    print(i)
    flag=True
    while(flag):
        node=random.choice(nodes)
        to=random.choice(id2adj[node])
        if (node,to) not in vis.keys() and (to,node) not in vis.keys():
            flag=False
            vis[(node,to)]=1
            vis[(to,node)]=1
    id2fa[str(cnt)]=[]
    id2and[str(cnt)]=pair2and[(node,to)]
    id2condition[str(cnt)]=pair2condition[(node,to)]
    if len(pair2seq[(node,to)])>0:
        id2seq[str(cnt)]=pair2seq[(node,to)][0]
    else:
        id2seq[str(cnt)]=[]
    tem_list1=[]
    tem_list2=[]
    cur_cost=cal_cost(id2and[str(cnt)],id2condition[str(cnt)])
    sum_cost=0
    for fa in id2fa[node]:
        if fa not in delete_id and check(str(cnt),fa)==False:        
            c2=cal_cost(id2and[fa],id2condition[fa])
            sum_cost+=c2
            tem_list1.append(fa)
    for fa in id2fa[to]:
        if fa not in delete_id and check(str(cnt),fa)==False:
            c2=cal_cost(id2and[fa],id2condition[fa])
            sum_cost+=c2
            tem_list2.append(fa)
    if cur_cost>sum_cost:
        for item in tem_list1:
            id2fa[node].remove(item)
            delete_id.append(item)
        for item in tem_list2:
            id2fa[to].remove(item)
            delete_id.append(item)
        id2fa[node].append(str(cnt))
        id2fa[to].append(str(cnt))
    else:
        delete_id.append(str(cnt))
    cnt+=1
with open(str(test_type)+'/'+str(test_type)+'_tree_'+str(method)+str(test_num)+'.txt','w',encoding='utf8') as f:
#with open('baseline3/tree.txt','w',encoding='utf8') as f:
    for i in range(1,cnt):
        if str(i) not in delete_id:
            f.write(str(i)+' ')
            if id2fa[str(i)]==[]:
                f.write('0 ')
            else:
                tem_list=[]
                for item in id2fa[str(i)]:
                    if item in delete_id:
                        tem_list.append(item)
                for item in tem_list:
                    id2fa[str(i)].remove(item)
                if id2fa[str(i)]==[]:
                    f.write('0 ')
                else:
                    fa_str='|'.join(id2fa[str(i)])
                    f.write(fa_str+' ')
            and_str='|'.join(id2and[str(i)])
            f.write(and_str)
            seq_str='|'.join(id2seq[str(i)])
            
            f.write(' '+seq_str+'\n')
            json_str=json.dumps(id2condition[str(i)])
            f.write(json_str+'\n')
endtime = time.time()
dtime = endtime - starttime
#runtime:5425.43         
print('run_time:',dtime)

