#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: rbeast-frontend-runnable.py
#------------------------------------------------------------------------------
# Version 0.1
# 18 February, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
# Dataframe libraries:
import numpy as np
import pandas as pd
#import pickle
# Plotting libraries:
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
# OS libraries:
import os
from  optparse import OptionParser
import sys
# R libraries:
import subprocess
#from subprocess import Popen

# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

#------------------------------------------------------------------------------

def main():

    # Get runtime arguments

    filename = sys.argv[1]
    code = str(sys.argv[2])

    # Set paths and filenames

#   path = "/users/mataylor/rbeast/"
#   path = "~/Documents/REPOS/rbeast/"
    path = ""
    file_in = path+filename      
    file_out = path+code+".png"

    # Return if file already processed

    if os.path.exists(file_out):
        print(code + ': already generated')
        return

    # Return if no input file

    if not os.path.exists(file_in):
        print('input file missing')
        return

    #------------------------------------------------------------------------------
    # SETTINGS: 
    #------------------------------------------------------------------------------

    fontsize = 12
    normalsfile = 'normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt'

    #------------------------------------------------------------------------------
    # LOAD: station monthly data (CRUTEM format)
    #------------------------------------------------------------------------------

    nheader = 0
    f = open(file_in)
    lines = f.readlines()
    dates = []
    stationcodes = []
    obs = []
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        if len(words) == 9:
            stationcode = '0'+words[0][0:6]
        elif len(words) == 13:
            date = int(words[0])
            val = (len(words)-1)*[None]
            for j in range(len(val)):                
                try: val[j] = int(words[j+1])
                except:                    
                    pass
            stationcodes.append(stationcode)
            dates.append(date)
            obs.append(val) 
    f.close()    
    dates = np.array(dates)
    obs = np.array(obs)

    # Create pandas dataframe

    df = pd.DataFrame(columns=['stationcode','year','1','2','3','4','5','6','7','8','9','10','11','12'])
    df['stationcode'] = stationcodes
    df['year'] = dates
    for j in range(12):        
        df[df.columns[j+2]] = [ obs[i][j] for i in range(len(obs)) ]

    # Replace monthly fill value -999 with np.nan    

    for j in range(12):        
        df[df.columns[j+2]].replace(-999, np.nan, inplace=True)
        
    # Apply /10 scale factor to absolute temperatures   

    for j in range(12):       
        df[df.columns[j+2]] = df[df.columns[j+2]]/10.0

    #------------------------------------------------------------------------------
    # LOAD: normals5
    #------------------------------------------------------------------------------

    nheader = 0
    f = open(normalsfile)
    lines = f.readlines()
    stationcodes = []
    sourcecodes = []
    obs = []
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        stationcode = words[0][0:6]
        sourcecode = int(words[17])
        val = (12)*[None]
        for j in range(12):                         
            try: val[j] = float(words[j+5])
            except:                                    
                pass
        stationcodes.append(stationcode)
        sourcecodes.append(sourcecode)
        obs.append(val)     
    f.close()    
    obs = np.array(obs)

    # Create pandas dataframe 

    dn = pd.DataFrame(columns=['stationcode','sourcecode','1','2','3','4','5','6','7','8','9','10','11','12'])
    dn['stationcode'] = stationcodes
    dn['sourcecode'] = sourcecodes
    for j in range(12):        
        dn[dn.columns[j+2]] = [ obs[i][j] for i in range(len(obs)) ]

    # Replace monthly fill value -999 with np.nan    

    for j in range(12):        
        dn[dn.columns[j+2]].replace(-999., np.nan, inplace=True)

    # Filter out stations with missing normals

    df_normals = df[df['stationcode'].isin(dn[dn['sourcecode']>1]['stationcode'])].reset_index()
    dn_normals = dn[dn['stationcode'].isin(df_normals['stationcode'])].reset_index()

    df_anom = df_normals.copy()
    for i in range(len(df_normals)):
        normals = dn_normals[dn_normals['stationcode']==df_normals['stationcode'][i]]
        for j in range(1,13):            
            df_anom[str(j)][i] = df_normals[str(j)][i] - normals[str(j)]
    df = df_anom.copy()

    #------------------------------------------------------------------------------
    # CALL RBEAST FOR STATION
    #------------------------------------------------------------------------------

    # Generate station file for R

    da = df[df['stationcode']==code]
    ts_monthly = np.array(da.groupby('year').mean().iloc[:,1:]).ravel() 
    t_monthly = pd.date_range(start=str(da['year'].iloc[0]), periods=len(ts_monthly), freq='M')           
    dg = pd.DataFrame({'t':t_monthly,'ts':ts_monthly})
    dg = dg.replace(r'^\s+$', np.nan, regex=True)   # replace space with NaN (meeded for Rbeast)
    dg.to_csv(code+'.csv', index=False)                

    # Call Rbeast
 
    command = '/usr/bin/Rscript'
#   command = '/apps/jasmin/jaspy/miniconda_envs/jaspy3.7/m3-4.6.14/envs/jaspy3.7-m3-4.6.14-r20200606/bin/Rscript'

    path2rscript = 'rbeast_frontend_runnable.R'
    args = [code]
    cmd = [command, path2rscript] + args
    subprocess.call(cmd, universal_newlines=True)
    #subprocess.check_output(cmd, universal_newlines=True)

    # Read Rbeast output dataframes back into python

    out_trend = pd.read_csv(code+'_trend.csv').astype(float).values.ravel()
    out_trend_prob = pd.read_csv(code+'_trend_prob.csv')
    out_trend_CI = pd.read_csv(code+'_trend_CI.csv').astype(float).values # 95% credible
    out_trend_CI_upper = out_trend_CI[0:len(out_trend)].ravel()
    out_trend_CI_lower = np.fliplr(out_trend_CI[len(out_trend):]).ravel()
    out_trend_order = pd.read_csv(code+'_trend_order.csv') # polynormial order
    out_trend_cp = pd.read_csv(code+'_trend_cp.csv').dropna().astype(int).values
    out_seasonal = pd.read_csv(code+'_seasonal.csv').astype(float).values.ravel()
    out_seasonal_prob = pd.read_csv(code+'_seasonal_prob.csv')
    out_seasonal_CI = pd.read_csv(code+'_seasonal_CI.csv').astype(float).values # 95% credible
    out_seasonal_CI_upper = out_seasonal_CI[0:len(out_seasonal)].ravel()
    out_seasonal_CI_lower = np.fliplr(out_seasonal_CI[len(out_seasonal):]).ravel()
    out_seasonal_order = pd.read_csv(code+'_seasonal_order.csv') # harmonic order
    out_seasonal_cp = pd.read_csv(code+'_seasonal_cp.csv').dropna().astype(int).values

    #------------------------------------------------------------------------------
    # PLOT: timeseries, extracted trend & seasonal components + Bayesian changepoint probabilities + changepoint locations
    #------------------------------------------------------------------------------

    titlestr = 'Rbeast: ' + code
    figstr = file_out

    fig, axes = plt.subplots(5,1,sharex=True, figsize=(15,10))      
    axes[0].set_title(titlestr, fontsize=20)
    axes[0].plot(t_monthly, ts_monthly, lw=1, color='navy', alpha=1.0)
    axes[0].xaxis.grid(True, which='major')      
    axes[0].yaxis.grid(True, which='major')  
    axes[0].set_ylabel('anomaly [°C]', fontsize=fontsize)
    axes[0].tick_params(labelsize=fontsize)    
    axes[1].plot(t_monthly, out_trend, lw=2, color='red', alpha=1.0)
    axes[1].fill_between(t_monthly, np.array(out_trend_CI_lower), np.array(out_trend_CI_upper), color='lightgrey', alpha=1.0)
    for i in range(len(out_trend_cp)):
        axes[1].axvline(x=t_monthly[out_trend_cp[i]], linestyle='dashed', color='blue')
    axes[1].xaxis.grid(True, which='major')      
    axes[1].yaxis.grid(True, which='major')  
    axes[1].set_ylabel('trend [°C]', fontsize=fontsize)
    axes[1].tick_params(labelsize=fontsize)    
    axes[2].plot(t_monthly, out_trend_prob, lw=1, color='blue', alpha=1.0)
    axes[2].xaxis.grid(True, which='major')      
    axes[2].yaxis.grid(True, which='major')  
    axes[2].set_ylabel('P(trend)', fontsize=fontsize)
    axes[2].tick_params(labelsize=fontsize)    
    axes[3].plot(t_monthly, out_seasonal, lw=2, color='red', alpha=1.0)
    axes[3].fill_between(t_monthly, np.array(out_seasonal_CI_lower), np.array(out_seasonal_CI_upper), color='lightgrey', alpha=1.0)
    for i in range(len(out_seasonal_cp)):
        axes[3].axvline(x=t_monthly[out_seasonal_cp[i]], linestyle='dashed', color='blue')
    axes[3].xaxis.grid(True, which='major')      
    axes[3].yaxis.grid(True, which='major')  
    axes[3].set_ylabel('seasonal [°C]', fontsize=fontsize)
    axes[3].tick_params(labelsize=fontsize)    
    axes[4].plot(t_monthly, out_seasonal_prob, lw=1, color='blue', alpha=1.0)
    axes[4].xaxis.grid(True, which='major')      
    axes[4].yaxis.grid(True, which='major')  
    axes[4].set_ylabel('P(seasonal)', fontsize=fontsize)
    axes[4].set_xlabel('Year', fontsize=fontsize)
    axes[4].tick_params(labelsize=fontsize)    
    plt.savefig(figstr)
    plt.close(fig)

if __name__ == "__main__":

    main()

