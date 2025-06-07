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
import copy

def cal_similarity(list1,list2):
    cnt=0
    for id2 in list2:
        if id2 in list1:
            cnt+=1
    return cnt/len(list1)
def construct_tree(filename):
    global choose_id
    cnt2child={}
    cnt2fa={}
    cnt2and={}
    cnt2seq={}
    cnt2condition={}
    cnt2interval={}
    cnt2combinations={}
    cnt2deep={}
    num=1
    with open(filename,'r',encoding='utf8') as f:
        for line in f:
            line=line.strip('\n')
            if num%2==1:
                a=int(line.split(' ')[0])
                choose_id.append(a)
                b=line.split(' ')[1]
                fa_list=b.split('|')
                cnt2deep[a]=int(line.split(' ')[5])
                #print(fa_list)
                for i in range(len(fa_list)):
                    fa_list[i]=int(fa_list[i])
                cnt2fa[a]=fa_list
                for fa in fa_list:
                    if fa not in cnt2child.keys():
                        cnt2child[fa]=[a]
                    else:
                        cnt2child[fa].append(a)
                if a not in cnt2child.keys():
                    cnt2child[a]=[]
                cnt2interval[a]=int(line.split(' ')[2])
                And=line.split(' ')[3]
                and_list=And.split('|')
                seq=line.split(' ')[4]
                if seq=="":
                    seq_list=[]
                else:
                    seq_list=seq.split('|')
                for i in range(len(and_list)):
                    and_list[i]=int(and_list[i])
                for i in range(len(seq_list)):
                    seq_list[i]=int(seq_list[i])
                cnt2and[a]=and_list
                cnt2seq[a]=seq_list
                cnt2combinations[a]={}
            else:
                condition=json.loads(line)
                cnt2condition[a]=condition
            cnt=a+1
            num+=1
    print(num/2)
    return cnt2child,cnt2fa,cnt2and,cnt2seq,cnt2condition,cnt2interval,cnt2combinations,cnt2interval,cnt,cnt2deep
def LCS(list_a, list_b):
    if list_a==[] or list_b==[]:
        return []
    length_a = len(list_a)  # list_a长度
    length_b = len(list_b)  # list_b长度
    value = np.zeros((length_a+1, length_b+1)) # value和is_take的大小都是[(len_a+1)*(len_b+1)]的(因为有前述边界条件(2.3))
    is_take = np.zeros((length_a+1, length_b+1), dtype=int)
    for i in range(1, length_a+1):
        for j in range(1, length_b+1):
            # value[i, j]: 价值信息
            if list_a[i-1] == list_b[j-1]:
                value[i][j] = value[i-1][j-1] + 1
            else:
                value[i][j] = max(value[i-1][j], value[i][j-1])
            #is_take[i, j]: 取数信息
            if list_a[i-1] == list_b[j-1]:            
                is_take[i][j] = 2**(length_a-i) + is_take[i-1][j-1]
            else:             
                if value[i-1][j] > value[i][j-1]:  # 注意，这里无论取不取等号都有可能出现bug，因为相等时理论上应该要把两个is_take的信息都包含进来
                    is_take[i][j] = is_take[i-1][j]
                else:
                    is_take[i][j] = is_take[i][j-1]
    # (3)通过value和is_take求解
    ## (3.1)获得value最大时的取数编码
    max_value = value.max()
    max_is_take = is_take[np.where(value==max_value)]  # 取最大价值时的取数编码
    max_is_take = np.unique(max_is_take)  # 去重，需要注意的是，取数编码可能不止一个
    length_max_is_take = len(max_is_take)
    pos_info = np.array([list(bin(i)[2:].zfill(length_a)) for i in max_is_take])  # 将每一个取数编码转换为二进制，得到一个位置信息矩阵pos_info
    if isinstance(list_a, str):  # 分情况讨论，因为输入的list可能是string也可能是list或np.array
        list_LCS = np.stack([np.array(list(list_a)) for n in range(length_max_is_take)], axis=0)
        list_LCS[pos_info=='0'] = ''
    elif isinstance(list_a, list):
        list_LCS = np.stack([np.array(list_a).astype('float') for n in range(length_max_is_take)], axis=0)
        list_LCS[pos_info=='0'] = np.nan
    else:
        list_LCS = np.stack([list_a.astype('float') for n in range(length_max_is_take)], axis=0)
        list_LCS[pos_info=='0'] = np.nan
    result = list_LCS[0].tolist()
    flag=True
    while(flag):
        flag=False
        for item in result:
            if math.isnan(item):
                result.remove(item)
                flag=True
    for i in range(len(result)):
        result[i]=int(result[i])
    return result
def judge_sub_list(sub_l,l):
    for item in sub_l:
        if item not in l:
            return False
    return True
def judge_sub_seq(sub_s,s):
    pos=0
    for i in range(len(s)):
        if pos==len(sub_s):
            break
        if sub_s[pos]==s[i]:
            pos+=1      
    if pos==len(sub_s):
        return True
    else:
        return False
def merge(all_id):
    sub_condition={}
    fir=True
    id=all_id[0]
    for key in cnt2condition[id].keys():
        tem_list=[]
        flag=True
        for other_id in all_id:
            if key in cnt2condition[other_id].keys():
                tem_list=list(set(tem_list+cnt2condition[other_id][key]))
            else:
                flag=False
                break
        if flag:
            sub_condition[key]=tem_list
    return sub_condition
def cal_sub_mode(id1,id2):
    sub_and=[]
    sub_seq=LCS(cnt2seq[id1], cnt2seq[id2])
    for id in cnt2and[id1]:
        if id in cnt2and[id2]:
            sub_and.append(id)
    return sub_seq,sub_and
def left_sub_mode(id1,id2,sub_seq,sub_and):
    tem_list=[]
    for id in sub_and:
        flag=False
        for fa in cnt2fa[id1]:
            if id in cnt2and[fa]:
                flag=True
        for fa in cnt2fa[id2]:
            if id in cnt2and[fa]:
                flag=True
        if flag:
            tem_list.append(id)
    for id in tem_list:
        sub_and.remove(id)
    tem_list=[]
    for id in sub_seq:
        flag=False
        for fa in cnt2fa[id1]:
            if id in cnt2seq[fa]:
                flag=True
        for fa in cnt2fa[id2]:
            if id in cnt2seq[fa]:
                flag=True
        if flag:
            tem_list.append(id)
    for id in tem_list:
        sub_seq.remove(id)
    return sub_seq,sub_and
def check(new_fa,child):
    for other_fa in cnt2fa[child]:
        for id in cnt2and[new_fa]:
            if id in cnt2and[other_fa]:
                return False
    return True
def dif_fa(id1,id2):
    for id in cnt2fa[id1]:
        if id in cnt2fa[id2]:
            return False
    return True
test_num=500
test_type='traffic'
method='baseline5'
filename=str(test_type)+'/'+str(test_type)+'_tree_our'+str(test_num)+'.txt'
choose_id=[]
cnt2child,cnt2fa,cnt2and,cnt2seq,cnt2condition,cnt2interval,cnt2combinations,cnt2interval,cnt,cnt2deep=construct_tree(filename)
cnt2sim={}
delete_id=[]
starttime = time.time()
for id1 in cnt2fa.keys():
    print(id1)
    #if id1>20:
        #break
    for id2 in cnt2fa.keys():
        if id1<id2 and cnt2deep[id1]==cnt2deep[id2] and dif_fa(id1,id2):
            
            sub_seq,sub_and=cal_sub_mode(id1,id2)
            sub_seq,sub_and=left_sub_mode(id1,id2,sub_seq,sub_and)
            if len(sub_and)>1:
                cnt2sim[cnt]=cal_similarity(cnt2and[id1],cnt2and[id2])
                #cnt2fa[cnt]=0
                all_id=[id1,id2]
                for id3 in cnt2fa.keys():
                    if id2<id3 and cnt2deep[id2]==cnt2deep[id3] and dif_fa(id2,id3) and dif_fa(id1,id3):                 
                        if judge_sub_list(sub_and,cnt2and[id3]) and judge_sub_seq(sub_seq,cnt2seq[id3]):
                            all_id.append(id3)
                cnt2seq[cnt]=copy.deepcopy(sub_seq)
                cnt2and[cnt]=copy.deepcopy(sub_and)
                cnt2condition[cnt]=merge(all_id)
                cnt2deep[cnt]=cnt2deep[id1]
                cnt2interval[cnt]=max(cnt2interval[id1],cnt2interval[id2])
                tem_list=[]
                for key in cnt2condition[cnt].keys():
                    if key not in sub_and:
                        tem_list.append(key)
                for key in tem_list:
                    del cnt2condition[cnt][key]
                cnt2child[cnt]=copy.deepcopy(all_id)
                cnt+=1
sorted_list=sorted(cnt2deep.items(), key = lambda x: x[1]) 
#print(sorted_list)
limit_num=20
top_id=[]
tem_dic={}
pre_deep=2
for i,item in enumerate(sorted_list):
    id=item[0]
    if item[1]<=2 or id not in cnt2sim.keys():
        continue
    if i==0 or item[1]>pre_deep:
        #print("???")
        if len(tem_dic)>0:
            sorted_tem_list=sorted(tem_dic.items(), key = lambda x: x[1],reverse=True) 
            for key in tem_dic.keys():
                if len(top_id)<limit_num:
                    print(cnt2deep[key])
                    top_id.append(key)
                else:
                    break
        tem_dic={id:item[1]}
        pre_deep=item[1]
    else:
        #print("!!!")
        tem_dic[id]=item[1]
        pre_deep=item[1]
print(top_id)  
for id in top_id:
    tem_list=[]
    for child in cnt2child[id]:
        if check(id,child):
            tem_list.append(child)
    if len(tem_list)>1:
        choose_id.append(id)
        for child in tem_list:
            cnt2fa[child].append(id)
    else:
        delete_id.append(id)
with open(str(test_type)+'/'+str(test_type)+'_tree_'+str(method)+str(test_num)+'.txt','w',encoding='utf8') as f:
    for i in cnt2and.keys():
        if i not in delete_id and i in choose_id:
            f.write(str(i)+' ')
            if i not in cnt2fa.keys() or cnt2fa[i]==[]:
                f.write('0 ')
            else:
                tem_list=[]
                for item in cnt2fa[i]:
                    if item in delete_id:
                        tem_list.append(item)
                for item in tem_list:
                    cnt2fa[i].remove(item)
                for j in range(len(cnt2fa[i])):
                    cnt2fa[i][j]=str(cnt2fa[i][j])
                if cnt2fa[i]==[]:
                    fa_str='0'
                else:
                    fa_str='|'.join(cnt2fa[i])
                f.write(fa_str+' ')
            f.write(str(cnt2interval[i])+' ')
            for j in range(len(cnt2and[i])):
                cnt2and[i][j]=str(cnt2and[i][j])
            for j in range(len(cnt2seq[i])):
                cnt2seq[i][j]=str(cnt2seq[i][j])
            and_str='|'.join(cnt2and[i])
            f.write(and_str)
            #print(cnt2seq[i])
            seq_str='|'.join(cnt2seq[i])
            
            f.write(' '+seq_str+'\n')
            json_str=json.dumps(cnt2condition[i])
            f.write(json_str+'\n')
endtime = time.time()
dtime = endtime - starttime
print('time:',dtime)

