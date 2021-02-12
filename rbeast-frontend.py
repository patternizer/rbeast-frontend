#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: rbeast-frontend.py
#------------------------------------------------------------------------------
# Version 0.2
# 11 February, 2021
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
import pickle
from datetime import datetime
#import nc_time_axis
#import cftime
# Plotting libraries:
import matplotlib
import matplotlib.pyplot as plt; plt.close('all')
import matplotlib.cm as cm
import cmocean
from matplotlib import colors as mcol
from matplotlib.cm import ScalarMappable
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
# OS libraries:
import os
import os.path
from pathlib import Path
import sys
import subprocess
from subprocess import Popen
import time

# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 20

#------------------------------------------------------------------------------
# LOAD: station(s) monthly data (CRUTEM format)
#------------------------------------------------------------------------------

filename = 'Iceland21.postmerge'

nheader = 0
f = open(filename)
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
f = open('normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt')
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

# Calculate monthly mean

t = pd.date_range(start=str(df['year'].min()), end=str(df['year'].max()+1), freq='M')   
dg = pd.DataFrame(columns=df['stationcode'].unique(),index=t)   

n = len(df['stationcode'].unique())
for i in range(n):
    da = df[df['stationcode']==df['stationcode'].unique()[i]]
    ts_monthly = np.array(da.groupby('year').mean().iloc[:,1:]).ravel() 
    t_monthly = pd.date_range(start=str(da['year'].iloc[0]), periods=len(ts_monthly), freq='M')   
    db = pd.DataFrame({dg.columns[i]:ts_monthly},index=t_monthly)
    dg[dg.columns[i]] = db

dg['mean'] = dg.mean(axis=1)

#------------------------------------------------------------------------------
# PLOT: ALL STATION TIMESERIES
#------------------------------------------------------------------------------

figstr = 'anomaly-timeseries-with-monthly-mean.png'
titlestr = filename
             
n = len(df['stationcode'].unique())
colors = cmocean.cm.thermal(np.linspace(0.05,0.95,n)) 
hexcolors = [ "#{:02x}{:02x}{:02x}".format(int(colors[i][0]*255),int(colors[i][1]*255),int(colors[i][2]*255)) for i in range(len(colors)) ]

fig, ax = plt.subplots(figsize=(15,10))          
for i in range(n):
    da = df[df['stationcode']==df['stationcode'].unique()[i]]
    ts_monthly = np.array(da.groupby('year').mean().iloc[:,1:]).ravel() 
    t_monthly = pd.date_range(start=str(da['year'].iloc[0]), periods=len(ts_monthly), freq='M')           
    plt.plot(t_monthly, ts_monthly, marker='None', lw=0.8, color=hexcolors[i], alpha=0.8, label=df['stationcode'].unique()[i])
plt.plot(dg['mean'].dropna().rolling(12).mean(), marker='.', ls='None', color='black', alpha=1.0, label='Annual mean')
ax.xaxis.grid(True, which='major')      
ax.yaxis.grid(True, which='major')  
plt.tick_params(labelsize=16)    
plt.legend(loc='upper left', bbox_to_anchor=(1.04,1), ncol=3, fontsize=8)
plt.xlabel('Year', fontsize=fontsize)
plt.ylabel(r'Temperature anomaly (from 1961-1990) [K]', fontsize=fontsize)
plt.title(titlestr, fontsize=fontsize)
plt.subplots_adjust(right=0.7)
plt.savefig(figstr)
plt.close(fig)

#------------------------------------------------------------------------------
# CALL RBEAST FOR EACH STATION
#------------------------------------------------------------------------------

for i in range(n):

    da = df[df['stationcode']==df['stationcode'].unique()[i]]
    ts_monthly = np.array(da.groupby('year').mean().iloc[:,1:]).ravel() 
    t_monthly = pd.date_range(start=str(da['year'].iloc[0]), periods=len(ts_monthly), freq='M')           
    dg = pd.DataFrame({'t':t_monthly,'ts':ts_monthly})
    dg = dg.replace(r'^\s+$', np.nan, regex=True)
    dg.to_csv('dg.csv', index=False)
    code = df['stationcode'].unique()[i]

    command = '/usr/bin/Rscript'
    path2rscript = 'rbeast_frontend.R'
    args = [code]
    cmd = [command, path2rscript] + args
    subprocess.call(cmd, universal_newlines=True)
    #subprocess.check_output(cmd, universal_newlines=True)
    out_trend = pd.read_csv('out_trend.csv').astype(float).values.ravel()
    out_trend_prob = pd.read_csv('out_trend_prob.csv')
    out_trend_CI = pd.read_csv('out_trend_CI.csv').astype(float).values # 95% credible
    out_trend_CI_upper = out_trend_CI[0:len(out_trend)].ravel()
    out_trend_CI_lower = np.fliplr(out_trend_CI[len(out_trend):]).ravel()
    out_trend_order = pd.read_csv('out_trend_order.csv') # polynormial order
    out_trend_cp = pd.read_csv('out_trend_cp.csv').dropna().astype(int).values
    out_seasonal = pd.read_csv('out_seasonal.csv').astype(float).values.ravel()
    out_seasonal_prob = pd.read_csv('out_seasonal_prob.csv')
    out_seasonal_CI = pd.read_csv('out_seasonal_CI.csv').astype(float).values # 95% credible
    out_seasonal_CI_upper = out_seasonal_CI[0:len(out_seasonal)].ravel()
    out_seasonal_CI_lower = np.fliplr(out_seasonal_CI[len(out_seasonal):]).ravel()
    out_seasonal_order = pd.read_csv('out_seasonal_order.csv') # harmonic order
    out_seasonal_cp = pd.read_csv('out_seasonal_cp.csv').dropna().astype(int).values

    titlestr = 'Rbeast: ' + df['stationcode'].unique()[i]
    figstr = "rbeast-" + df['stationcode'].unique()[i] + '.png'

    fig, axes = plt.subplots(5,1,sharex=True, figsize=(15,10))      
    axes[0].set_title(titlestr, fontsize=fontsize)
    axes[0].plot(t_monthly, ts_monthly, lw=1, color=hexcolors[i], alpha=1.0)
    axes[0].xaxis.grid(True, which='major')      
    axes[0].yaxis.grid(True, which='major')  
    axes[0].legend(loc='upper left', fontsize=8)
    axes[0].set_ylabel('anomaly [°C]')
    axes[1].plot(t_monthly, out_trend, lw=2, color='red', alpha=1.0)
#    axes[1].fill_between(t_monthly, np.array(out_trend)-np.array(out_trend_CI_lower), np.array(out_trend)+np.array(out_trend_CI_upper), color='lightgrey', alpha=1.0, label='95% credible interval')
    axes[1].fill_between(t_monthly, np.array(out_trend_CI_lower), np.array(out_trend_CI_upper), color='lightgrey', alpha=1.0)
    for i in range(len(out_trend_cp)):
        axes[1].axvline(x=t_monthly[out_trend_cp[i]], linestyle='dashed', color='blue')
    axes[1].xaxis.grid(True, which='major')      
    axes[1].yaxis.grid(True, which='major')  
    axes[1].legend(loc='upper left', fontsize=12)
    axes[1].set_ylabel('trend [°C]')
    axes[2].plot(t_monthly, out_trend_prob, lw=1, color='blue', alpha=1.0)
    axes[2].xaxis.grid(True, which='major')      
    axes[2].yaxis.grid(True, which='major')  
    axes[2].legend(loc='upper left', fontsize=12)
    axes[2].set_ylabel('P(trend)')
    axes[3].plot(t_monthly, out_seasonal, lw=2, color='red', alpha=1.0)
    axes[3].fill_between(t_monthly, np.array(out_seasonal_CI_lower), np.array(out_seasonal_CI_upper), color='lightgrey', alpha=1.0)
    for i in range(len(out_seasonal_cp)):
        axes[3].axvline(x=t_monthly[out_seasonal_cp[i]], linestyle='dashed', color='blue')
    axes[3].xaxis.grid(True, which='major')      
    axes[3].yaxis.grid(True, which='major')  
    axes[3].legend(loc='upper left', fontsize=12)
    axes[3].set_ylabel('seasonal [°C]')
    axes[4].plot(t_monthly, out_seasonal_prob, lw=1, color='blue', alpha=1.0)
    axes[4].xaxis.grid(True, which='major')      
    axes[4].yaxis.grid(True, which='major')  
    axes[4].legend(loc='upper left', fontsize=12)
    axes[4].set_ylabel('P(seasonal)')
    axes[4].set_xlabel('Year', fontsize=fontsize)
#    axes[4].tick_params(labelsize=16)    
    plt.savefig(figstr)
    plt.close(fig)

#------------------------------------------------------------------------------
print('** END')

