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

def all_lcs(x,y):
    dp = [[0 for _ in range(101)] for _ in range(101)]

    for i in range(1, len(x) + 1):  # 构造dp数组
        for j in range(1, len(y) + 1):
            if x[i - 1] == y[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                dp[i][j] = dp[i - 1][j]
            else:
                dp[i][j] = dp[i][j - 1]

    res = []
    #string = str()
    string=[]
    def all(temp, m, n):  # 求出所有解
        while m != 0 and n != 0:
            if x[m - 1] == y[n - 1]:
                #temp = x[m - 1] + temp
                #print(x[m-1])
                temp = [x[m - 1]] + temp
                m, n = m - 1, n - 1
            elif dp[m - 1][n] > dp[m][n - 1]:
                m -= 1
            elif dp[m - 1][n] < dp[m][n - 1]:
                n -= 1
            elif dp[m - 1][n] == dp[m][n - 1]:
                all(temp, m - 1, n)
                all(temp, m, n - 1)
                return
        #print(temp)
        if temp!=[] and temp not in res:
            res.append(temp)
    all(string, len(x), len(y))
    return res
def cal_sub_mode(id1,id2):
    sub_and=[]
    sub_seq=all_lcs(id2seq[id1], id2seq[id2])
    for id in id2and[id1]:
        if id in id2and[id2]:
            sub_and.append(id)
    return sub_seq,sub_and
id2and={}
id2condition={}
id2seq={}
test_num=100
test_type='traffic'
method='RW'
starttime = time.time()
with open(str(test_type)+'_mode_'+str(test_num)+'.json','r',encoding='utf8') as f:
    mode_dict=json.load(f)
    cnt=0
    for key in mode_dict.keys():  
        
        cnt+=1
        print(key)
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
with open('RW/graph'+test_type+str(test_num)+'.txt','w',encoding='utf8') as f:
    for key1 in mode_dict.keys():
        print(int(key1))
        for key2 in mode_dict.keys():
            if int(key1)>=int(key2):
                continue
            sub_seq,sub_and=cal_sub_mode(key1,key2)
            sub_condition={}
            for id in id2condition[key1].keys():
                if id in id2condition[key2].keys():
                    sub_condition[id]=list(set(id2condition[key1][id]+id2condition[key2][id]))
            if len(sub_and)>=2:
                
                and_str='|'.join(sub_and)
                f.write(str(key1)+' '+str(key2)+' '+and_str+' '+str(len(sub_seq)))
                for item in sub_seq:
                    seq_str='|'.join(item)
                    f.write(' '+seq_str)
                f.write('\n')
                json_str=json.dumps(sub_condition)
                f.write(json_str+'\n')
endtime = time.time()
dtime = endtime - starttime
#runtime:5425.43         
print('run_time:',dtime)