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

id2seq={}
id2and={}
id2condition={}
id2interval={}
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
        result[i]=str(int(result[i]))
    return result
def read_file(edges,degree,g_dict,connected_fields):
    w=[]
    edge={}
    visit={}
    cnt=1
    sum=0
    n=0
    m=0
    for item in edges:         
        a=item[0]
        b=item[1]
        v=item[2]
        if a not in connected_fields or b not in connected_fields:
            continue
        m+=1
        g_dict[(a,b)]=v
        g_dict[(b,a)]=v
        sum+=v
        if a not in degree.keys():
            degree[a]=v
            edge[a]=[b]
        else:
            degree[a]+=v
            edge[a].append(b)
        if b not in degree.keys():
            degree[b]=v
            edge[b]=[a]
        else:
            degree[b]+=v
            edge[b].append(a)
    n=len(degree)
    return n,m,degree,g_dict,sum,edge
def update(index,id2child,id2deep): #更新qu[index]的所有子节点的深度
    if len(id2child[index])>1:
        for node in id2child[index]:
            #qu[node]=(qu[node][0],qu[node][1],qu[node][2],qu[node][3],qu[node][4],qu[node][5],qu[node][6]+1)
            id2deep[node]=id2deep[node]+1
            id2deep=update(node,id2child,id2deep)
    return id2deep
def get_deep(index,id2child,id2deep):
    deep=id2deep[index]
    if len(id2child[index])>1:
        for node in id2child[index]:
            deep=max(deep,get_deep(node,id2child,id2deep))
    return deep
def sub_list(l1,l2):
    for item in l1:
        if item not in l2:
            return False
    return True
def sub_seq(l1,l2):
    if len(l1)>len(l2):
        return False
    for i in range(len(l1)):
        if l1[i]!=l2[i]:
            return False
    return True
def cal_sub_mode(id1,id2):
    sub_and=[]
    sub_seq=LCS(id2seq[id1], id2seq[id2])
    for id in id2and[id1]:
        if id in id2and[id2]:
            sub_and.append(id)
    return sub_seq,sub_and
def structual_entropy(edges,nodes,mx_deep,M):
    degree={}
    g_dict={}
    n,m,degree,g_dict,sum,edge=read_file(edges,degree,g_dict,nodes)
    h1=0
    for i in range(1,n+1):
        h1+=(-degree[i]/(2.0*sum)*math.log(degree[i]/(2.0*sum),2))
    print(h1)
    nums=[]
    for i in range(1,n+1):
        nums.append(i)
    qu=[(0,2*sum,[],[],0)]
    id2sister={}
    id2child={0:nums}
    id2deep={0:1}
    id2fa={0:-1}
    id2interval[0]=300
    for i in range(1,n+1):
        qu.append((degree[i],degree[i])) #分别表示团的割边数，度的和，点集，姐妹点集，编号和父节点编号，深度，子节点编号
        id2sister[i]=edge[i]
        id2child[i]=[i]
        id2deep[i]=2
        id2fa[i]=0
    result=0
    cnt=n+1
    flag=True
    flag2=True
    delete_id=[]
    merge_dict={}#记录算过的合并i和j之后的dif
    combine_dict={}
    #print(id2sister)
    iter=1
    while(flag or flag2):   
    #while(flag2):
        flag2=True
        #while(flag2):
        if flag2:
            iter+=1
            print(iter)
            mn=1e9
            mx=1e-6
            flag2=False
            for i in range(1,len(qu)):
                if i in delete_id:
                    continue
                item1=qu[i]
                g1=item1[0]
                for j in id2sister[i]:
                                
                    item2=qu[j]
                    if len(id2child[id2fa[i]])<=2 or j in delete_id:
                        #print("error")
                        continue                  
                    g2=item2[0]
                    #new_edge=item1[3]+item2[3]    
                    v=item1[1]+item2[1]            
                    #new_node=item1[2]+item2[2]
                    v_fa=qu[id2fa[i]][1]
                    if (i,j) in g_dict.keys():
                        g=g1+g2-2*g_dict[(i,j)]
                    else:
                        g=g1+g2
                    #按照combine后熵减小最多的两个团combine
                    #深度不能超过max_deep
                    
                    if (g1+g2-g)/(2*sum)*math.log((v_fa)/v,2)>mx and get_deep(i,id2child,id2deep)+1<=mx_deep and get_deep(j,id2child,id2deep)+1<=mx_deep:
                        new_seq,new_and=cal_sub_mode(i,j)
                        if len(new_and)<=1:
                            continue
                        update_seq=new_seq
                        update_and=new_and
                        mx=(g1+g2-g)/(2*sum)*math.log((v_fa)/v,2)
                        add=mx

                        ans=(g,v)
                        id1=i
                        id2=j
                        flag2=True
            if flag2:
                #print(len(qu),index1,index2)
                #print('combine',qu[id1][2],qu[id2][2],cnt)
                id2interval[cnt]=max(id2interval[id1],id2interval[id2])
                #更新新节点的condition
                id2condition[cnt]={}
                for id in id2condition[id1].keys():
                    if id in id2condition[id2].keys():
                        id2condition[cnt][id]=list(set(id2condition[id1][id]+id2condition[id2][id]))
                #更新新节点的and和seq
                id2and[cnt]=update_and
                id2seq[cnt]=update_seq
                #更新父节点
                id2fa[cnt]=id2fa[id1]
                id2fa[id1]=cnt
                id2fa[id2]=cnt
                #更新子节点
                id2child[cnt]=[id1,id2]
                fa_id=id2fa[cnt]
                #print('combine',fa_id,id1,id2)
                id2child[fa_id].remove(id1)
                id2child[fa_id].remove(id2)
                id2child[fa_id].append(cnt)
                #print(id2child)
                #更新深度
                #print(qu[index1][0],qu[index2][0],ans[0]) 
                id2deep[cnt]=id2deep[id1]
                id2deep[id1]=id2deep[cnt]+1
                id2deep[id2]=id2deep[cnt]+1
                id2deep=update(id1,id2child,id2deep)
                id2deep=update(id2,id2child,id2deep)
                #print(mn)
                result+=add
                #print(result)
                #更新g_dict
                for i in range(0,len(qu)):
                    if id2deep[cnt]==id2deep[i] and id2fa[cnt]==id2fa[i] and i not in delete_id:
                        if (id1,i) in g_dict.keys():
                            c1=g_dict[(id1,i)]
                        else:
                            c1=0
                        if (id2,i) in g_dict.keys():
                            c2=g_dict[(id2,i)]
                        else:
                            c2=0
                        c=c1+c2
                        if c>0:
                            g_dict[(cnt,i)]=g_dict[(i,cnt)]=c
                #更新id2sister:
                id2sister[id2].remove(id1)
                id2sister[id1].remove(id2)
                id2sister[cnt]=list(set(id2sister[id1]+id2sister[id2]))
                
                for id in id2sister[id1]:
                    
                    id2sister[id].remove(id1)
                    id2sister[id].append(cnt)
                for id in id2sister[id2]:
                    id2sister[id].remove(id2)
                    if cnt not in id2sister[id]:
                        id2sister[id].append(cnt)
                id2sister[id1]=[id2]
                id2sister[id2]=[id1]
                #print(id1,id2sister[id1])
                #print(id2,id2sister[id2])
                #print(cnt,id2sister[cnt])
                #print(id2sister)
                qu.append(ans)
                cnt+=1
            
        flag=True
        while(flag):
            iter+=1
            print(iter)
            flag=False         
            mx=1e-5
            item1=qu[cnt-1]
            if len(id2child[id2fa[cnt-1]])<=2:
                break
            v1=item1[1]
            g1=item1[0]
            for j in id2sister[cnt-1]:
                #计算merge cnt和j的收益
                
                item2=qu[j]
                if j in delete_id :
                    continue                                
                v2=item2[1]                
                g2=item2[0]
                #print(item1[2],item2[2],new_node)
                v12=item1[1]+item2[1]
                     
                if (cnt-1,j) in g_dict.keys():
                    g12=g1+g2-2*g_dict[(cnt-1,j)]
                else:
                    g12=g1+g2
                v_fa=qu[id2fa[cnt-1]][1]
                #new_node=item1[2]+item2[2]
                #计算merge后的熵
                after_merge=-g12/(2*sum)*math.log(v12/v_fa,2)
                for node in id2child[cnt-1]+id2child[j]:
                    after_merge+=-qu[node][0]/(2*sum)*math.log(qu[node][1]/v12,2)
                #print(after_merge)
                before_merge=-g1/(2*sum)*math.log(v1/v_fa,2)-g2/(2*sum)*math.log(v2/v_fa,2)
                for node in id2child[cnt-1]:
                    before_merge+=-qu[node][0]/(2*sum)*math.log(qu[node][1]/v1,2)
                for node in id2child[j]:
                    before_merge+=-qu[node][0]/(2*sum)*math.log(qu[node][1]/v2,2)
                dif=before_merge-after_merge
                #print(before_merge,after_merge)
                        
                    
                if dif>mx:
                    new_seq,new_and=cal_sub_mode(cnt-1,j)
                    if sub_list(id2and[cnt-1],id2and[j]) and sub_seq(id2seq[cnt-1],id2seq[j]) and len(new_and)>1:                   
                        update_seq=new_seq
                        update_and=new_and
                        mx=dif
                        ans=(g12,v12)
                        add=dif
                        id2=j
                        flag=True
            if flag:               
                id1=cnt-1
                if len(id2child[id1])>1:
                    delete_id.append(id1)
                if len(id2child[id2])>1:
                    delete_id.append(id2)
                id2interval[cnt]=max(id2interval[id1],id2interval[id2])
                #更新新节点的condition
                id2condition[cnt]={}
                for id in id2condition[id1].keys():
                    if id in id2condition[id2].keys():
                        id2condition[cnt][id]=list(set(id2condition[id1][id]+id2condition[id2][id]))
                #更新新节点的and和seq
                id2and[cnt]=update_and
                id2seq[cnt]=update_seq
                #print('merge',qu[id1][2],qu[id2][2],cnt)
                #更新父节点
                id2fa[cnt]=id2fa[id1]

                #更新父亲id的子节点
                id2child[cnt]=id2child[id1]+id2child[id2]
                fa_id=id2fa[cnt]
                #print('merge',fa_id,id1,id2)
                id2child[fa_id].remove(id1)
                id2child[fa_id].remove(id2)
                id2child[fa_id].append(cnt)
                #print(id2child)
                #更新深度和子节点的父节点
                id2deep[cnt]=id2deep[id1]
                for node in id2child[cnt]:
                    id2deep[node]=id2deep[cnt]+1
                    id2fa[node]=cnt           
                result+=add
                for i in range(0,len(qu)):
                    if id2deep[cnt]==id2deep[i] and id2fa[cnt]==id2fa[i] and i not in delete_id:
                        if (id1,i) in g_dict.keys():
                            c1=g_dict[(id1,i)]
                        else:
                            c1=0
                        if (id2,i) in g_dict.keys():
                            c2=g_dict[(id2,i)]
                        else:
                            c2=0
                        c=c1+c2
                        if c>0:
                            g_dict[(cnt,i)]=g_dict[(i,cnt)]=c
                #更新id2sister
                id2sister[id2].remove(id1)
                id2sister[id1].remove(id2)         
                id2sister[cnt]=list(set(id2sister[id1]+id2sister[id2]))
                #print(cnt,id2sister[cnt],id2sister[id1],id2sister[id2])
                for id in id2sister[id1]:
                    id2sister[id].remove(id1)
                    id2sister[id].append(cnt)
                for id in id2sister[id2]:
                    id2sister[id].remove(id2)
                    if cnt not in id2sister[id]:
                        id2sister[id].append(cnt)
                for sub_id1 in id2child[id1]+id2child[id2]:
                    id2sister[sub_id1]=[]
                    for sub_id2 in id2child[id1]+id2child[id2]:
                        if sub_id1!=sub_id2 and (sub_id1,sub_id2) in g_dict.keys():
                            id2sister[sub_id1].append(sub_id2)

                qu.append(ans)
                cnt+=1
        
        
    mx_deep=0  
    print("************")
    
    with open('data'+'/'+str(test_type)+'/'+str(test_type)+'_tree_'+str(method)+str(test_num)+'.txt','w',encoding='utf8') as f:
        for i,item in enumerate(qu):
            
            if i not in delete_id and i>0:
                seq_str='|'.join(id2seq[i])
                and_str='|'.join(id2and[i])
                f.write(str(i)+' '+str(id2fa[i])+' '+str(id2interval[i])+' '+and_str+' '+seq_str+' '+str(id2deep[i])+'\n')
                json_str=json.dumps(id2condition[i])
                f.write(json_str+'\n')
                mx_deep=max(mx_deep,id2deep[i])
    
    '''
    for i,item in enumerate(qu):
        if i not in delete_id:
            print(i,id2fa[i],id2deep[i],id2child[i])
    '''
    return h1,h1-result,mx_deep

cnt2id={}
nodes=[]
test_num=500
test_type='pollution'
method='ours'
m=10
with open('data'+'/'+str(test_type)+'/'+str(test_type)+'_mode_'+str(test_num)+'.json','r',encoding='utf8') as f:
    dict=json.load(f)
    all_id=[]
    cnt=1
    for key in dict:
        all_id.append(dict[key]['id'])
        #stock
        id2and[cnt]=dict[key]['id']
        id2condition[cnt]={}
        for id in dict[key]['property']:
            id2condition[cnt][id]=[dict[key]['condition']]
        id2interval[cnt]=dict[key]['interval']
        '''
        if dict[key]['seq']==1:
            id2seq[cnt]=dict[key]['property']
        else:
            id2seq[cnt]=[]
        '''
        if dict[key]['logic']['seq']==1:
            id2seq[cnt]=dict[key]['property']
        else:
            id2seq[cnt]=[]
        
        cnt2id[cnt]=dict[key]['id']
        nodes.append(cnt)
        cnt+=1
'''
with open('traffic_mode_filter.txt','r',encoding='utf8') as f:
    all_dict={}
    cnt=1
    for line in f:
        line=line.strip()
        ids=line.split(" ")
        cnt2id[cnt]=ids
        nodes.append(cnt)
        cnt+=1
'''
edges={}
edge_list=[]


#m=30*2+4
#m=20
with open('data'+'/'+str(test_type)+'/'+str(test_type)+'_similarity_'+str(test_num)+'.txt','r',encoding='utf8') as f:
    cnt=1
    for line in f:
        line=line.strip()
        words=line.split(' ')
        tem_id={}
        for i,item in enumerate(words): #id从1开始
            tem_id[i+1]=float(item)
        sorted_id = sorted(tem_id.items(), key=lambda e: e[1],reverse=True)
        for i,item in enumerate(sorted_id):
            if i<m:
                if item[0]!=cnt and (item[0],cnt) not in edges.keys() and item[1]>0.1:
                    edges[(cnt,item[0])]=1
                    edge_list.append((cnt,item[0],1))
                    #print(cnt,item[0],item[1])
        cnt+=1

with open('data'+'/'+str(test_type)+'/'+str(test_type)+'_edges_'+str(method)+str(test_num)+'.txt','w',encoding='utf8') as f:
    for item in edges.items():
        f.write(str(item[0][0])+' '+str(item[0][1])+' '+str(1)+'\n')
starttime = time.time()
mx_deep=3
print(len(nodes))
h1,entropy,mx_deep=structual_entropy(edge_list,nodes,mx_deep,m)

print(m,h1,entropy,mx_deep)#deep:31

endtime = time.time()
dtime = endtime - starttime
print('time:',dtime)



