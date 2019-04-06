# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:40:14 2014

@author: ensheng
"""
import numpy as np
import pyodbc
import csv
import random
import matplotlib.pyplot as plt
import operator

# Read in SLA data

#%%
f=open('SLA_allPlants_TRY2.csv','rb')
#f=open('SLA_all_TRY3.csv','rb')
#next(f) # skip headings
TreeList=list(csv.reader(f,delimiter=','))
f.close()

TreeList.sort(key=lambda TreeList: TreeList[1])

TreeSLA=np.array(TreeList)
SLA = TreeSLA[:,5].astype(np.float)
spSLA=[]
startPSLA=[]
endPSLA=[]
spSLA.append(TreeSLA[0,1])
startPSLA.append(0)
endPSLA.append(0)
n=1
totalSP=1
for i in range(1,len(TreeSLA)):
    if(TreeSLA[i-1,1] ==TreeSLA[i,1]):
        n=n+1
        endPSLA[totalSP-1]=i
    else:
        totalSP=totalSP+1
        spSLA.append(TreeSLA[i,1])
        startPSLA.append(i)
        endPSLA.append(i)
random.choice(SLA[startPSLA[0]:endPSLA[0]+1])
print spSLA[0].split()[0]
del TreeList,TreeSLA

#%%
f=open('Ra_allPlants_TRY2.csv','rb')
next(f) # skip headings
TreeList=list(csv.reader(f,delimiter=','))
f.close()

TreeList.sort(key=lambda TreeList: TreeList[1])

TreeRa=np.array(TreeList)
Ra = TreeRa[:,5].astype(np.float)
spRa=[]
startPRa=[]
endPRa=[]
spRa.append(TreeRa[0,1])
startPRa.append(0)
endPRa.append(0)
n=1
totalSP=1
for i in range(1,len(TreeRa)):
    if(TreeRa[i-1,1] ==TreeRa[i,1]):
        n=n+1
        endPRa[totalSP-1]=i
    else:
        totalSP=totalSP+1
        spRa.append(TreeRa[i,1])
        startPRa.append(i)
        endPRa.append(i)
random.choice(Ra[startPRa[0]:endPRa[0]+1])
print spRa[0].split()[0]
del TreeList,TreeRa

#%%
f=open('PSa_allPlants_TRY2.csv','rb')
next(f) # skip headings
TreeList=list(csv.reader(f,delimiter=','))
f.close()

TreeList.sort(key=lambda TreeList: TreeList[1])

TreePSa=np.array(TreeList)
PSa = TreePSa[:,5].astype(np.float)
spPSa=[]
startPPSa=[]
endPPSa=[]
spPSa.append(TreePSa[0,1])
startPPSa.append(0)
endPPSa.append(0)
n=1
totalSP=1
for i in range(1,len(TreePSa)):
    if(TreePSa[i-1,1] ==TreePSa[i,1]):
        n=n+1
        endPPSa[totalSP-1]=i
    else:
        totalSP=totalSP+1
        spPSa.append(TreePSa[i,1])
        startPPSa.append(i)
        endPPSa.append(i)
random.choice(PSa[startPPSa[0]:endPPSa[0]+1])
print spPSa[0].split()[0]
del TreeList,TreePSa
#traitData.append(list(csv.reader(f2,delimiter='\t')))

#f2.close()

#sort traitData
"""
student_tuples = [
        ('john', 'A', 15),
        ('jane', 'B', 12),
        ('dave', 'B', 10),]
sorted(student_tuples, key=lambda student: student[2])
"""
#def sortByColumn(bigList,*args)
#    bigList.sort(key=operator.itemgetter(*args)) 

#%%
#state =['WI','MN','MI']
state1 =['MI','MN','WI','ME','VT','NH','MA','NY','CT','PA','MD']
state2 =['AK','WA','OR','MT','ID','WY','VA','WV','TN','NC','SC']

state  = ['MI'] #state1
fig = plt.figure()
ipanel = 0
for istate in state:
    print istate
    # read in data from database
    #inputfile ='C:\\FIAanalysis\\FIAdata\\'+istate+'.accdb'
    inputfile ='E:\\FIAdata\\'+istate+'.accdb'
    db_file = inputfile
    user = 'admin'
    password = ''
    odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % \
                    (db_file, user, password)
    conn = pyodbc.connect(odbc_conn_str)
     
    cursor = conn.cursor()
    livetreesLMA ='from  TREE,REF_SPECIES '\
                 'where TREE.SPCD=REF_SPECIES.SPCD AND '\
                 'TREE.DIA>2.0 AND TREE.INVYR>2005 AND '\
                 'TREE.STATUSCD=1 AND TREE.SUBP<5  ' \
                 'ORDER by REF_SPECIES.GENUS,REF_SPECIES.SPECIES'
                 
    SQLallTrees='select TREE.SPCD,REF_SPECIES.GENUS,REF_SPECIES.SPECIES,'\
                 'TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,TREE.INVYR,'\
                 'TREE.STATUSCD,TREE.DIA,TREE.TPA_UNADJ,TREE.TPA_UNADJ,'\
                 'TREE.TPA_UNADJ,TREE.TPA_UNADJ '\
                 + livetreesLMA
    Trees   = cursor.execute(SQLallTrees).fetchall()

    cursor.close()
    conn.close()    
    #a.sort(key=operator.itemgetter(2,3)) 
    Trees.sort(key=operator.itemgetter(1,2))
    Trees = np.array(Trees)
    Trees[:,10]=-1.0
    Trees[:,11]=-1.0
    Trees[:,12]=-1.0
    m=0
    for i in range(len(Trees)):
        for j in xrange(m,len(spSLA)):
            if(Trees[i,1]==spSLA[j].split()[0] and \
               Trees[i,2]==spSLA[j].split()[1]):
                Trees[i,10]=random.choice(SLA[startPSLA[j]:endPSLA[j]+1])
                print spSLA[j],i,j,Trees[i,10]
                m=max(0,j-1)
                break
    m=0
    for i in range(len(Trees)):
        for j in xrange(m,len(spRa)):
            if(Trees[i,1]==spRa[j].split()[0] and \
               Trees[i,2]==spRa[j].split()[1]):
                Trees[i,11]=random.choice(Ra[startPRa[j]:endPRa[j]+1])
                print spRa[j],i,j,Trees[i,11]
                m=max(0,j-1)
                break
    m=0
    for i in range(len(Trees)):
        for j in xrange(m,len(spPSa)):
            if(Trees[i,1]==spPSa[j].split()[0] and \
               Trees[i,2]==spPSa[j].split()[1]):
                Trees[i,12]=random.choice(PSa[startPPSa[j]:endPPSa[j]+1])
                print spPSa[j],i,j,Trees[i,12]
                m=max(0,j-1)
                break
    #plt.figure(istate)
    ipanel = ipanel +1
    ax = fig. add_subplot(4,3,ipanel)
    plt.hist(Trees[:,10].astype(np.float),bins=50, range=(-2,80))
    ax.set_title(istate)
    outf=istate+"_TreesSLA.csv"
    np.savetxt(outf, Trees, delimiter=",",fmt='%s')