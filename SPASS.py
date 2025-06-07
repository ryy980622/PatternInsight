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
import copy

id2child={}
id2fa={}
id2and={}
id2condition={}
id2seq={}
id2freq={}#基础事件个数
id2prob={}#每个路口满足属性条件的个数
id2sum={}#基础事件总数量
delete_id=[]
mode_num=1000
path='processed_data_feb_june/'
def judge_sub_list(sub_l,l):
    for item in sub_l:
        if item not in l:
            return False
    return True
def judge_sub_seq(sub_s,s):
    pos=0
    for i in range(len(s)):
        if sub_s[pos]==s[i]:
            pos+=1
        if pos==len(sub_s):
            break
    if pos==len(sub_s):
        return True
    else:
        return False
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
def merge(all_id):
    sub_condition={}
    fir=True
    id=all_id[0]
    for key in id2condition[id].keys():
        tem_list=[]
        flag=True
        for other_id in all_id:
            if key in id2condition[other_id].keys():
                tem_list=list(set(tem_list+id2condition[other_id][key]))
            else:
                flag=False
                break
        if flag:
            sub_condition[key]=tem_list
    return sub_condition
def cal_sub_mode(id1,id2):
    sub_and=[]
    sub_seq=all_lcs(id2seq[id1], id2seq[id2])
    for id in id2and[id1]:
        if id in id2and[id2]:
            sub_and.append(id)
    return sub_seq,sub_and
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
def check(new_fa,child):
    for other_fa in id2fa[child]:
        for id in id2and[new_fa]:
            if id in id2and[other_fa]:
                return False
    return True
def supplement(id):
    global cnt,id2gain,id2and,id2seq,id2condition,id2child
    tem_seq=[]
    sup_seq=[]
    tem_and=[]
    sup_and=[]
    update=False
    for fa in id2fa[id]:
        for item in id2and[fa]:
            tem_and.append(item)
        for item in id2seq[fa]:
            tem_seq.append(item)
    for item in id2and[id]:
        if item not in tem_and and item not in id2seq[id]:
            sup_and.append(item)
    for item in id2seq[id]:
        if item not in tem_seq:
            sup_seq.append(item)
    #加入and结点
    if len(sup_and)>1:
        update=True
        c1=cal_cost(sup_and,id2condition[id])
        sum_cost=c1
        all_id=[id]
        for key3 in mode_dict.keys():
            if int(key3)>mode_num:
                break
            if key3!=id:
                if judge_sub_list(sup_and,id2and[key3]):
                    sum_cost+=cal_cost(sup_and,id2condition[key3])
                    all_id.append(key3)
        merge_condition=merge(all_id)
        merge_cost=cal_cost(sup_and,merge_condition)
        id2gain[str(cnt)]=merge_cost/sum_cost
        id2and[str(cnt)]=copy.deepcopy(sup_and)
        id2seq[str(cnt)]=[]
        tem_list=[]
        for key in merge_condition.keys():
            if key not in sup_and:
                tem_list.append(key)
        for key in tem_list:
            del merge_condition[key]
        id2condition[str(cnt)]=copy.deepcopy(merge_condition)
        id2child[str(cnt)]=copy.deepcopy(all_id)
        cnt+=1
    #加入seq结点
    if len(sup_seq)>1:
        update=True
        c1=cal_cost(sup_seq,id2condition[id])
        sum_cost=c1
        all_id=[id]
        for key3 in mode_dict.keys():
            if int(key3)>mode_num:
                break
            if key3!=id:
                if judge_sub_seq(sup_seq,id2seq[key3]):
                    sum_cost+=cal_cost(sup_seq,id2condition[key3])
                    all_id.append(key3)
        merge_condition=merge(all_id)
        merge_cost=cal_cost(sup_seq,merge_condition)
        id2gain[str(cnt)]=merge_cost/sum_cost
        id2and[str(cnt)]=copy.deepcopy(sup_seq)
        id2seq[str(cnt)]=copy.deepcopy(sup_seq)
        tem_list=[]
        for key in merge_condition.keys():
            if key not in sup_seq:
                tem_list.append(key)
        for key in tem_list:
            del merge_condition[key]
        id2condition[str(cnt)]=copy.deepcopy(merge_condition)
        id2child[str(cnt)]=copy.deepcopy(all_id)
        cnt+=1
    return update
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
method='SPASS'
with open(str(test_type)+'_mode_'+str(test_num)+'.json','r',encoding='utf8') as f:
    mode_dict=json.load(f)
    cnt=1
    for key in mode_dict.keys():        
        print(key)
        id_list=mode_dict[key]['id']
        #interval=mode_dict[key]['interval']
        interval=60
        condition=mode_dict[key]['condition']
        id2and[key]=mode_dict[key]['id']
        id2condition[key]={}
        id2child[key]=[]
        id2fa[key]=[]
        for id in mode_dict[key]['property']:
            id2condition[key][id]=[mode_dict[key]['condition']]
        if mode_dict[key]['logic']['seq']==1:
            id2seq[key]=mode_dict[key]['property']
        else:
            id2seq[key]=[]
        cnt+=1
        
        
id2gain={}
for key1 in mode_dict.keys():
    print(int(key1))
    for key2 in mode_dict.keys():
      
        if int(key1)>=int(key2):
            continue
        sub_seq,sub_and=cal_sub_mode(key1,key2)
        #print(key1,key2)
        #print('sub_seq:',sub_seq)
        if len(sub_and)>=2:#还要确保不交叉
            #挑选seq结点
            mn_ratio=1e18
            if sub_seq!=[] and len(sub_seq[0])>1:
                for seq in sub_seq:
                    c1=cal_cost(seq,id2condition[key1])
                    c2=cal_cost(seq,id2condition[key2])
                    sum_cost=c1+c2
                    all_id=[key1,key2]
                    for key3 in mode_dict.keys():
                        if key3!=key1 and key3!=key2:
                            if judge_sub_seq(seq,id2seq[key3]):
                                sum_cost+=cal_cost(seq,id2condition[key3])
                                all_id.append(key3)
                    merge_condition=merge(all_id)
                    merge_cost=cal_cost(seq,merge_condition)
                    #print('ratio:',merge_cost/sum_cost)
                    if merge_cost/sum_cost<mn_ratio:
                        mn_ratio=merge_cost/sum_cost
                        choose_seq = copy.deepcopy(seq)
                        choose_condition = copy.deepcopy(merge_condition)
                        children=copy.deepcopy(all_id)
                id2gain[str(cnt)]=mn_ratio
                id2and[str(cnt)]=copy.deepcopy(choose_seq)
                id2seq[str(cnt)]=copy.deepcopy(choose_seq)
                tem_list=[]
                for key in choose_condition.keys():
                    if key not in choose_seq:
                        tem_list.append(key)
                for key in tem_list:
                    del choose_condition[key]
                id2condition[str(cnt)]=copy.deepcopy(choose_condition)
                id2child[str(cnt)]=copy.deepcopy(children)
                cnt+=1
            else:
                choose_seq=[]
            #加入and结点
            
            #print('sub_and:',sub_and)
            #print('choose_seq:',choose_seq)

            for item in choose_seq:
                sub_and.remove(item)
            if len(sub_and)>1:
                c1=cal_cost(sub_and,id2condition[key1])
                c2=cal_cost(sub_and,id2condition[key2])
                sum_cost=c1+c2
                all_id=[key1,key2]
                for key3 in mode_dict.keys():
                    if key3!=key1 and key3!=key2:
                        if judge_sub_list(sub_and,id2and[key3]):
                            sum_cost+=cal_cost(id2and[key3],id2condition[key3])
                            all_id.append(key3)

                merge_condition=merge(all_id)
                merge_cost=cal_cost(sub_and,merge_condition)
                id2gain[str(cnt)]=merge_cost/sum_cost
                id2and[str(cnt)]=copy.deepcopy(sub_and)
                id2seq[str(cnt)]=[]
                tem_list=[]
                for key in merge_condition.keys():
                    if key not in sub_and:
                        tem_list.append(key)
                for key in tem_list:
                    del merge_condition[key]
                id2condition[str(cnt)]=copy.deepcopy(merge_condition)
                id2child[str(cnt)]=copy.deepcopy(all_id)
                cnt+=1
endtime = time.time()
dtime = endtime - starttime
#runtime:5425.43         
print('run_time:',dtime)
starttime = time.time()
sorted_gain_list=sorted(id2gain.items(), key = lambda x: x[1]) 
for item in sorted_gain_list:
    id=item[0]
    tem_list=[]
    for child in id2child[id]:
        if check(id,child):
            tem_list.append(child)
    if len(tem_list)>1:
        for child in tem_list:
            id2fa[child].append(id)
    else:
        delete_id.append(id)

update=True
while(update):
    id2gain={}
    update=False
    for i in range(1,test_num+1):
        flag=supplement(str(i))
        
        sorted_gain_list=sorted(id2gain.items(), key = lambda x: x[1]) 
        for item in sorted_gain_list:
            id=item[0]
            tem_list=[]
            for child in id2child[id]:
                if check(id,child):
                    tem_list.append(child)
            if len(tem_list)>0:
                for child in tem_list:
                    id2fa[child].append(id)
                    update=True
with open(str(test_type)+'/'+str(test_type)+'_tree_'+str(method)+str(test_num)+'.txt','w',encoding='utf8') as f:
    for i in range(1,cnt):
        if str(i) not in delete_id:
            f.write(str(i)+' ')
            if str(i) not in id2fa.keys() or id2fa[str(i)]==[]:
                f.write('0 ')
            else:
                tem_list=[]
                for item in id2fa[str(i)]:
                    if item in delete_id:
                        tem_list.append(item)
                for item in tem_list:
                    id2fa[str(i)].remove(item)
                if id2fa[str(i)]==[]:
                    fa_str='0'
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