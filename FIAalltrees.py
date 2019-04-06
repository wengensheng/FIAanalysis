# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:40:14 2014

@author: ensheng
"""
import numpy as np
import pyodbc


state =['MI','MN','WI']
#state =['WI']
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
    
    SQLPlot= 'SELECT PLOT.CN,PLOT.LAT,PLOT.LON,COND.FLDTYPCD, '\
                     'PLOT.STATECD,PLOT.UNITCD,PLOT.COUNTYCD,PLOT.PLOT,'\
                     'PLOT.INVYR,COND.STDAGE '\
              'FROM PLOT,COND '\
              'WHERE PLOT.CN = COND.PLT_CN AND '\
                     'PLOT.WATERCD < 2 AND '\
                     'PLOT.PLOT_STATUS_CD=1 AND '\
                     'COND.STDAGE>0.0 AND COND.INVYR>1998 '\
              'Order by PLOT.UNITCD,PLOT.COUNTYCD,PLOT.PLOT,PLOT.INVYR'
              
    livetreeselection ='from  TREE,REF_SPECIES '\
                 'where TREE.SPCD=REF_SPECIES.SPCD AND '\
                 'TREE.DIA>0.0 AND TREE.INVYR>1998 AND '\
                 'TREE.STATUSCD=1 AND TREE.SUBP<5  ' \
                 'ORDER by TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,TREE.INVYR,TREE.SUBP,TREE.TREE'
    
    treeselection ='from  TREE,REF_SPECIES '\
                 'where TREE.SPCD=REF_SPECIES.SPCD AND '\
                 'TREE.INVYR>1998 AND '\
                 'TREE.STATUSCD>0 AND TREE.SUBP<5  ' \
                 'ORDER by TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,TREE.INVYR,TREE.SUBP,TREE.TREE'
    
    SQLallTreeID='select TREE.PLT_CN,TREE.UNITCD,TREE.COUNTYCD,TREE.PLOT,TREE.INVYR,'\
                 'TREE.SUBP,TREE.TREE,TREE.STATUSCD,TREE.STATUSCD '\
                 + livetreeselection
                
    SQLallTreeDIA='select TREE.DIA,TREE.TPA_UNADJ,'\
                'REF_SPECIES.JENKINS_TOTAL_B1,REF_SPECIES.JENKINS_TOTAL_B2 '\
                + livetreeselection
    
    allTreeID  = cursor.execute(SQLallTreeID).fetchall()
    allTreeDIA = cursor.execute(SQLallTreeDIA).fetchall()
    allPlots   = cursor.execute(SQLPlot).fetchall()
              
    cursor.close()
    conn.close()
    # type(Trees)
    
    # Convert to arrays
    
    treeID =np.array(allTreeID,dtype='<U15')
    treeDIA=np.array(allTreeDIA)
    plots  =np.array(allPlots,dtype='<U15')
  
    
    # Count trees in each plot
    # Count plots and trees in each plot
    plotyr = len(plots)
    totaltrees = len(treeID)
    nTrees = np.ones((2*plotyr,1),dtype=np.int32)
    sTrees = np.zeros((2*plotyr,4),dtype=np.int32)
    # col.0: plot, col.1: times, col2: nTrees, col3:sTrees
    
    j=0
    for i in range(1,totaltrees,1):
        if treeID[i-1,1]==treeID[i,1] and \
           treeID[i-1,2]==treeID[i,2] and \
           treeID[i-1,3]==treeID[i,3] and \
           treeID[i-1,4]==treeID[i,4]:
            nTrees[j,0]+=1
        else:
            sTrees[j,3]=sTrees[j,2]+nTrees[j,0]
            sTrees[j+1,2]=sTrees[j,3]
            j+=1
    
    treeplotyr=j+1
    
    sTrees[0,0]=1
    sTrees[0,1]=1
    for j in range(1,treeplotyr,1):
        if treeID[sTrees[j,2]-1,1]==treeID[sTrees[j,3]-1,1] and \
           treeID[sTrees[j,2]-1,2]==treeID[sTrees[j,3]-1,2] and \
           treeID[sTrees[j,2]-1,3]==treeID[sTrees[j,3]-1,3]:
               sTrees[j,0]=sTrees[j-1,0]
               sTrees[j,1]=sTrees[j-1,1]+1
        else:
               sTrees[j,0]=sTrees[j-1,0]+1
               sTrees[j,1]=1
    
      
    # fill DIA for dead trees
    for j in range(1,treeplotyr,1):
        for i in range(sTrees[j,2],sTrees[j,3],1):
            if (treeID[i,7]>u'1') and (sTrees[j,1]>1):
                for m in range(sTrees[j-1,2],sTrees[j-1,3],1):
                    if treeID[m,5]==treeID[i,5] and \
                       treeID[m,6]==treeID[i,6] and \
                       treeID[m,7]==u'1':
                           treeID[i,7]=u'9'
                           break
            if (not treeDIA[i,0]>0.0001) and (sTrees[j,1]>1):
                for m in range(sTrees[j-1,2],sTrees[j-1,3],1):
                    if treeID[m,5]==treeID[i,5] and \
                       treeID[m,6]==treeID[i,6] and \
                       treeDIA[m,0]>0.0001:
                           treeDIA[i,:]=treeDIA[m,:]
                           print i, treeDIA[i,:]
                           break
            if (not treeDIA[i,0]>0.0001):
                treeDIA[i,:]=1.0
                treeDIA[i,1]=0.0
    
    
    # calculate tree's biomass
    OneAcre      = 4046.85642   # % m^2
    plotarea1    = 672.4537 # % 4*3.1415936*(24.0*0.3048)^2; % m^2
    plotarea2    = 53.98309 # % 4*3.1415936*(6.80*0.3048)^2;
    TPAsubplot   = 6.018046
    TPAmicroplot = 74.965282
    TPAmacroplot = 0.999188
    
    BM = np.zeros((totaltrees,2),dtype=float64)
    # total aboveground biomass (kg dry weight)
    for i in range(0,totaltrees,1):
        BM[i,0]=np.exp(treeDIA[i,2] + treeDIA[i,3] * np.log(treeDIA[i,0]*2.54))    
    #   Convert to kg C m-2    
        BM[i,0]=0.5*BM[i,0]*treeDIA[i,1]/OneAcre
        # alive tree indicator
        if treeID[i,7]==u'1':
            BM[i,1]=1.0
    
    # live tree biomass
    (ntreeplotyr,nIDs)=treeID.shape
    livetreePlotID= np.zeros((max(sTrees[:,0]),6),dtype='<U15')
    livetreePlotBM= np.zeros((max(sTrees[:,0]),7),dtype=float64)
    iplot=0
    livetreePlotID[iplot,0:5]=treeID[0,0:5]
    livetreePlotID[iplot,5]  =sTrees[0,1]
    for i in range(sTrees[0,2],sTrees[0,3],1):
        livetreePlotBM[iplot,0]=livetreePlotBM[iplot,0]+BM[i,0]*BM[i,1]
            
                
    for j in range(1,treeplotyr,1):
        if sTrees[j,1]==1:
            iplot+=1
            livetreePlotID[iplot,0:5]=treeID[sTrees[j,2],0:5]
            for i in range(sTrees[j,2],sTrees[j,3],1):
                livetreePlotBM[iplot,0]=livetreePlotBM[iplot,0]+BM[i,0]*BM[i,1]
        else:
            for i in range(sTrees[j,2],sTrees[j,3],1):
                livetreePlotBM[iplot,3*(sTrees[j,1]-2)+1]=\
                livetreePlotBM[iplot,3*(sTrees[j,1]-2)+1]+BM[i,0]*BM[i,1]
                for m in range(sTrees[j-1,2],sTrees[j-1,3],1):
                    if treeID[m,5]==treeID[i,5] and \
                       treeID[m,6]==treeID[i,6]:
                           livetreePlotBM[iplot,3*(sTrees[j,1]-2)+2]=\
                           livetreePlotBM[iplot,3*(sTrees[j,1]-2)+2]+BM[m,0]*BM[m,1]
                           livetreePlotBM[iplot,3*(sTrees[j,1]-2)+3]=\
                           livetreePlotBM[iplot,3*(sTrees[j,1]-2)+3]+BM[i,0]*BM[i,1]
                           break
        livetreePlotID[iplot,5]  =sTrees[j,1]

    PlotID= np.zeros((len(livetreePlotID),13),dtype=np.float64)
    startpt=0
    for i in range(len(livetreePlotID)):
        PlotID[i,5:9]=livetreePlotID[i,1:5]
        
        m=0
        for j in range(startpt,len(plots),1):
            if livetreePlotID[i,1]==plots[j,5] and \
               livetreePlotID[i,2]==plots[j,6] and \
               livetreePlotID[i,3]==plots[j,7]:
                 PlotID[i,0:9]=plots[j,0:9]
                 PlotID[i,9+m]=plots[j,9]
                 m+=1
                 if m==1:
                     startpt=j
                 if m>0 and j-startpt>=2:
                     break
        #PlotID[i,12] =livetreePlotID[i,5]
        # only keep the sites that meet the conditions of plot selection
        PlotID[i,12] =min(m,livetreePlotID[i,5])
        print startpt,m,livetreePlotID[i,5]
#        startpt = 0

    # output    
    livePlotIDBM=np.concatenate((PlotID, livetreePlotBM), axis=1)
    outf1=istate+"_livePlotsBM.csv"
    np.savetxt(outf1, livePlotIDBM, delimiter=",")

    # Select plots
    (treeplots,items)=livePlotIDBM.shape
    slctIDX=np.zeros((len(livePlotIDBM)),dtype=np.int32)
    j=0
    slctIDX[j]=0
    for i in range(1,len(livePlotIDBM),1):
        if livePlotIDBM[i,9]>0 and \
           livePlotIDBM[i,12]>2 and not \
          (livePlotIDBM[i,5]==livePlotIDBM[i-1,5] and \
           livePlotIDBM[i,6]==livePlotIDBM[i-1,6] and \
           livePlotIDBM[i,7]==livePlotIDBM[i-1,7]):
               j+=1
               slctIDX[j]=i
    nslctplots=j+1
    slctplots=np.zeros((nslctplots,items))
    slctplots=livePlotIDBM[slctIDX[0:nslctplots],:]
    outf2=istate+"_slctlivePlots.csv"
    np.savetxt(outf2, slctplots, delimiter=",")

           
