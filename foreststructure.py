# -*- coding: utf-8 -*-
"""
Created on Fri August 14 16:40:14 2014

@author: ensheng
"""
import numpy as np
import matplotlib.pyplot as plt
import pyodbc


#state =['MI','MN','WI']
state =['MI']

    
# define the bins of forest age
agebins = [i*10 for i in range(23)]
BAage=np.zeros((22,8), dtype=np.float)
agebins[22]=9999
    
for istate in state:
    print istate
    # read in data from database
    inputfile ='C:\\FIAanalysis\\FIAdata\\'+istate+'.accdb'
    db_file = inputfile
    user = 'admin'
    password = ''
    odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % \
                    (db_file, user, password)
    conn = pyodbc.connect(odbc_conn_str)
     
    cursor = conn.cursor()
    
#    # Acer rubrum 316; Acer saccharum 318; Populus tremuloides 746
#         '(TREE.SPCD=316 OR TREE.SPCD=318 OR TREE.SPCD=746) AND '\
#    AND PLOT.ECOSUBCD=212 AND 
    
    #livetreeselection ="from  PLOT,COND,TREE "\
    #             "where PLOT.CN = COND.PLT_CN AND TREE.PLT_CN=COND.PLT_CN AND "\
    #             "PLOT.PLOT_STATUS_CD=1 AND (PLOT.ECOSUBCD LIKE '%212%') AND "\
    #             'COND.PHYSCLCD>20 AND COND.PHYSCLCD<30 AND '\
    #             'COND.STDAGE>0.0 AND COND.INVYR>1998 AND '\
    #             '(TREE.SPCD=316 OR TREE.SPCD=318 OR TREE.SPCD=746) AND '\
    #             'TREE.DIA>0.0 AND TREE.INVYR>1998 AND '\
    #             'TREE.STATUSCD=1 AND TREE.SUBP<5  ' \
    #             'ORDER by TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,TREE.INVYR,TREE.SUBP,TREE.TREE'

    livetreeselection ="from  PLOT,COND,TREE "\
                 "where PLOT.CN = COND.PLT_CN AND TREE.PLT_CN=COND.PLT_CN AND "\
                 "PLOT.PLOT_STATUS_CD=1 AND (PLOT.ECOSUBCD LIKE '%212%') AND "\
                 'COND.PHYSCLCD>20 AND COND.PHYSCLCD<30 AND '\
                 'COND.STDAGE>0.0 AND COND.INVYR>1998 AND '\
                 'TREE.DIA>0.0 AND TREE.INVYR>1998 AND TREE.ACTUALHT>0.0 AND '\
                 'TREE.STATUSCD=1 AND TREE.SUBP<5  ' \
                 'ORDER by TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,TREE.INVYR,TREE.SUBP,TREE.TREE'
                 
    SQLallTreeID='select PLOT.CN,COND.STDAGE,'\
                 'PLOT.STATECD,TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,'\
                 'TREE.INVYR,TREE.SUBP,TREE.TREE,TREE.STATUSCD,'\
                 'TREE.SPCD,TREE.TPA_UNADJ,TREE.DIA,TREE.ACTUALHT '\
                 + livetreeselection

    allTreeID  = cursor.execute(SQLallTreeID).fetchall()
#    allTreeDIA = cursor.execute(SQLallTreeDIA).fetchall()
#    allPlots   = cursor.execute(SQLPlot).fetchall()
              
    cursor.close()
    conn.close()
    # type(Trees)
    
    # Convert to arrays
    
    #treeID =np.array(allTreeID,dtype='<U15')

    treeID =np.array(allTreeID,dtype=np.float)
#    treeDIA=np.array(allTreeDIA)
#    plots  =np.array(allPlots,dtype='<U15')
    
    
    # Output tree data
#    selectedtrees=np.concatenate((treeID, treeDIA), axis=1)
    # PLT_CN,UNITCD,COUNTYCD,PLOT,INVYR,SUBP,TREECD,STATUSCD,SPCD,TPA,DIA
    outf1=istate+"_trees.csv"
    np.savetxt(outf1, treeID, delimiter=",")
    # Some variables
    OneAcre      = 4046.85642   # % m^2
    plotarea1    = 672.4537 # % 4*3.1415936*(24.0*0.3048)^2; % m^2
    plotarea2    = 53.98309 # % 4*3.1415936*(6.80*0.3048)^2;
    TPAsubplot   = 6.018046
    TPAmicroplot = 74.965282
    TPAmacroplot = 0.999188
    #Count plots
    totaltrees = len(treeID)
    nplots = 1
    for i in range(1,totaltrees,1):
        if  (treeID[i,3]!=treeID[i-1,3] or \
               treeID[i,4]!=treeID[i-1,4] or \
               treeID[i,5]!=treeID[i-1,5] or \
               treeID[i,6]!=treeID[i-1,6] ):
            nplots = nplots + 1
    print nplots
    
#   define a matrix for tree numbers
    plotTrees    = np.zeros((nplots,1), dtype=np.int64)
    plotheight   = np.zeros((nplots,1), dtype=np.float)
#   Count trees in each plot
    iplot   = 0
    plotTrees[iplot,0]=1
    for i in range(1,totaltrees,1):
        if (treeID[i,3]==treeID[i-1,3] and \
            treeID[i,4]==treeID[i-1,4] and \
            treeID[i,5]==treeID[i-1,5] and \
            treeID[i,6]==treeID[i-1,6] ):
            plotTrees[iplot,0] = plotTrees[iplot,0]+1 # tree numbers
            plotheight[iplot,0]= plotheight[iplot,0] + treeID[i,13]*0.3048
        else:
            plotheight[iplot,0]= plotheight[iplot,0]/plotTrees[iplot,0]
            iplot = iplot + 1
            plotTrees[iplot,0]=1
            plotheight[iplot,0]= plotheight[iplot,0] + treeID[i,13]*0.3048
            
    print iplot,i,totaltrees
#   define matrixes for three species



#   Basal area
    basalarea    = np.zeros((nplots,8), dtype=np.float) # aspen,rm,sm

    i = 0
    for iplot in range(nplots):
        basalarea[iplot,0]=treeID[i,0]
        basalarea[iplot,1]=treeID[i,1]
        for itrees in range(plotTrees[iplot,0]):
            if treeID[i,10]==316: # Red maple
               basalarea[iplot,6]=basalarea[iplot,6]                        \
                                  + treeID[i,11]*10000.0/OneAcre
               basalarea[iplot,3]=basalarea[iplot,3]                        \
                                  + 3.14159*(0.5*treeID[i,12]*2.54/100.)**2 \
                                  * treeID[i,11]*10000.0/OneAcre
                       
            if treeID[i,10]==318: # Sugar maple
               basalarea[iplot,7]=basalarea[iplot,7]                        \
                                  + treeID[i,11]*10000.0/OneAcre
               basalarea[iplot,4]=basalarea[iplot,4]                        \
                                  + 3.14159*(0.5*treeID[i,12]*2.54/100.)**2 \
                                  * treeID[i,11]*10000.0/OneAcre
                         
            if treeID[i,10]==746: # Quaking aspen
               basalarea[iplot,5]=basalarea[iplot,5]                        \
                                  + treeID[i,11]*10000.0/OneAcre
               basalarea[iplot,2]=basalarea[iplot,2]                        \
                                  + 3.14159*(0.5*treeID[i,12]*2.54/100.)**2 \
                                  * treeID[i,11]*10000.0/OneAcre
            i=i+1
    outf1=istate+"_basalarea.csv"
    np.savetxt(outf1, basalarea, delimiter=",")
#   calculate plot basal area
    for i in range(nplots):
        for j in range(len(agebins)-1):
            if basalarea[i,1]>=agebins[j] and basalarea[i,1]<agebins[j+1]:
                BAage[j,0]  = BAage[j,0] + 1              
                BAage[j,1:8]= BAage[j,1:8]+basalarea[i,1:8]
                break

BAage[:,1]=BAage[:,1]/BAage[:,0]
BAage[:,2]=BAage[:,2]/BAage[:,0]
BAage[:,3]=BAage[:,3]/BAage[:,0]
BAage[:,4]=BAage[:,4]/BAage[:,0]
BAage[:,5]=BAage[:,5]/BAage[:,0]
BAage[:,6]=BAage[:,6]/BAage[:,0]
BAage[:,7]=BAage[:,7]/BAage[:,0]

## plot
font = {'family' : 'serif',
        'color'  : 'darkred',
        'weight' : 'normal',
        'size'   : 16,
        }
#x = np.linspace(0.0, 5.0, 100)
#y = np.cos(2 * np.pi * x) * np.exp(-x)
plt.figure(1)
plt.plot(BAage[:,1], BAage[:,2], 'b',BAage[:,1], BAage[:,3], 'r',BAage[:,1], BAage[:,4], 'k')
plt.title('Forest Succession', fontdict=font)
#plt.text(2, 0.65, r'$\cos(2 \pi t) \exp(-t)$', fontdict=font)
plt.xlabel('Year', fontdict=font)
plt.ylabel('Basal area (m$^2$)', fontdict=font)

# Tweak spacing to prevent clipping of ylabel
plt.subplots_adjust(left=0.15)
plt.show()

plt.figure(2)
plt.scatter(plotTrees, plotheight)
plt.axis([0, 100, 0, 50])
plt.title('Tree density', fontdict=font)
plt.xlabel('Height', fontdict=font)
plt.ylabel('Tree number', fontdict=font)
plt.show()
