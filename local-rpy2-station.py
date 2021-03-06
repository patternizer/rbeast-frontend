#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: local-rpy2-station.py
#
# RUN SYNTAX: python local-rpy2-station.py
#------------------------------------------------------------------------------
# Version 0.1
# 24 February, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
# michael DOT a DOT taylor AT uea DOT ac DOT uk
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
# Dataframe libraries:
import numpy as np
import pandas as pd
# Long time series support:
import xarray as xr
from datetime import datetime
import nc_time_axis
import cftime
# Plotting libraries:
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.dates as mdates
# R libraries:
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
base = importr('base')
utils = importr('utils')
Rbeast = importr('Rbeast')
readr = importr('readr')
# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 12
period = 12 # monthly
use_rpy2 = True
use_defaults = True
use_normals = True
filename = 'stationfile.txt'
normalsfile = 'normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt'

if use_rpy2 == True:

    #------------------------------------------------------------------------------
    # LOAD: station monthly data (CRUTEM format) --> df
    #------------------------------------------------------------------------------

    nheader = 0
    f = open(filename)
    lines = f.readlines()
    stationcodes = []
    dates = []
    obs = []
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        if len(words) != 13:
            stationcode = '0'+words[0][0:6]
        elif len(words) == 13:
            date = int(words[0])
            val = (len(words)-1)*[None]
            for j in range(len(val)):                
                try: val[j] = int(words[j+1])
                except:                    
                    pass
            dates.append(date)
            obs.append(val)            
        if i>0:
            stationcodes.append(stationcode)
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

    code = df['stationcode'].unique()[0]

    if use_normals == False:
        da = df.copy()
    else:

        #------------------------------------------------------------------------------
        # LOAD: normals5 --> dn
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
            stationsource = int(words[17])
            val = (12)*[None]
            for j in range(12):                         
                try: val[j] = float(words[j+5])
                except:                                    
                    pass
            stationcodes.append(stationcode)
            sourcecodes.append(stationsource)
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

        normals = dn[dn['stationcode']==code]

        da = df.copy()    
        for i in range(len(da)):    
            for j in range(1,13):                        
                da[str(j)][i] = df[str(j)][i] - normals[str(j)]

    #------------------------------------------------------------------------------
    # CALL RBEAST FOR STATION
    #------------------------------------------------------------------------------

    # Generate station file format for R

    ts_monthly = np.array(da.groupby('year').mean().iloc[:,0:]).ravel() 

    # FIX: pandas <1678 and >2262 calendar limit

    if da['year'][0] > 1678:
        t_monthly = pd.date_range(start=str(da['year'].iloc[0]), periods=len(ts_monthly), freq='M')          
    else:
        t_monthly_xr = xr.cftime_range(start=str(da['year'].iloc[0]), periods=len(ts_monthly), freq='M', calendar='gregorian')     
        year = [t_monthly_xr[i].year for i in range(len(t_monthly_xr))]
        year_frac = []
        for i in range(len(t_monthly_xr)):
            if i%12 == 0:
                istart = i
                iend = istart+11   
                frac = np.cumsum([t_monthly_xr[istart+j].day for j in range(12)])
                year_frac += list(frac/frac[-1])
            else:
                i += 1
        year_decimal = [float(year[i])+year_frac[i] for i in range(len(year))]    
        t_monthly = year_decimal
    
    # Call Rbeast
 
    ts = robjects.FloatVector(ts_monthly)
    if use_defaults == True:
        opt = robjects.r.list(period=period, computeCredible=1, computeHarmonicOrder=1, computeTrendOrder=1)
        out = robjects.r.beast(ts, opt)
    else:
        opt = robjects.r.list(period=period, minSeasonOrder=2, maxSeasonOrder=8, minTrendOrder=0, maxTrendOrder=3, minSepDist_Season=120, minSepDist_Trend=120, maxKnotNum_Season=5, maxKnotNum_Trend=5, printToScreen=0, chainNumber=2, sample=1000, thinningFactor=3, burnin=500, maxMoveStepSize=120, resamplingSeasonOrderProb=0.2, resamplingTrendOrderProb=0.2, seed=42, computeCredible=1, fastCIComputation=1, computeSlopeSign=0, computeHarmonicOrder=1, computeTrendOrder=1, outputToDisk=0)
        out = robjects.r.beast(ts, opt)

    # Rbeast DEFAULTS: 
    #
    #   opt$period=12 
    #   opt$startTime=1.000000
    #   opt$timeInterval=1.000000
    #   opt$minSeasonOrder=1
    #   opt$maxSeasonOrder=5
    #   opt$minTrendOrder=0
    #   opt$maxTrendOrder=1
    #   opt$minSepDist_Trend=6
    #   opt$minSepDist_Season=6
    #   opt$maxKnotNum_Trend=617
    #   opt$maxKnotNum_Season=617
    #   opt$maxMoveStepSize=3
    #   opt$samples=3000
    #   opt$thinningFactor=1
    #   opt$burnin=200
    #   opt$chainNumber=3
    #   opt$resamplingTrendOrderProb=0.100000
    #   opt$resamplingSeasonOrderProb=0.170000
    #   opt$omissionValue=-9999.000000
    #   opt$seed=0
    #   opt$outputToDisk=0
    #   opt$outputFolder=NOT USED
    #   opt$lengthPerTimeSeries_infile=4332
    #   opt$printToScreen=0
    #   opt$printCharLen=80
    #   opt$computeCredible=1
    #   opt$fastCIComputation=1
    #   opt$computeChangepoints=1
    #   opt$computeSlopeSign=0
    #   opt$computeHarmonicOrder=1
    #   opt$computeTrendOrder=1

    # Rbeast OUTPUTS:
    #
    # [1] "time"     "sN"       "tN"       "sNProb"   "tNProb"   "sProb"   
    # [7] "tProb"    "s"        "sCI"      "sSD"      "t"        "tCI"     
    #[13] "tSD"      "b"        "bCI"      "bSD"      "marg_lik" "sig2"    
    #[19] "horder"   "torder"   "scp"      "tcp"      "scpCI"    "tcpCI"  

    out_trend = np.array(out.rx('t')[0]).ravel()
    out_trend_prob = np.array(out.rx('tProb')[0]).ravel()
    out_trend_CI = pd.Series(out.rx('tCI')[0]).astype(float).values # 95% credible
    out_trend_CI_upper = out_trend_CI[0:len(out_trend)].ravel()
    out_trend_CI_lower = out_trend_CI[len(out_trend):].ravel()
    out_trend_order = np.array(out.rx('torder')[0]).ravel()
    out_trend_cp = sorted(pd.Series(out.rx('tcp')[0]).dropna().astype(int).values)
    out_seasonal = np.array(out.rx('s')[0]).ravel()
    out_seasonal_prob = np.array(out.rx('sProb')[0]).ravel()
    out_seasonal_CI = pd.Series(out.rx('sCI')[0]).astype(float).values # 95% credible
    out_seasonal_CI_upper = out_seasonal_CI[0:len(out_seasonal)].ravel()
    out_seasonal_CI_lower = out_seasonal_CI[len(out_seasonal):].ravel()
    out_seasonal_order = np.array(out.rx('horder')[0]).ravel()
    out_seasonal_cp = sorted(pd.Series(out.rx('scp')[0]).dropna().astype(int).values)

    out = pd.DataFrame({'time':t_monthly, 'trend':out_trend, 'trend_prob':out_trend_prob, 'trend_CI_lower':out_trend_CI_lower, 'trend_CI_upper':out_trend_CI_upper, 'seasonal':out_seasonal, 'seasonal_prob':out_seasonal_prob, 'seasonal_CI_lower':out_seasonal_CI_lower, 'seasonal_CI_upper':out_seasonal_CI_upper, 'trend_order':out_trend_order, 'seasonal_order':out_seasonal_order})
    out_tcp = pd.DataFrame({'trend_cp':out_trend_cp})   
    out_scp = pd.DataFrame({'seasonal_cp':out_seasonal_cp})   
    out_tcp['time'] = [ t_monthly[out_trend_cp[i]] for i in range(len(out_trend_cp)) ]  
    out_scp['time'] = [ t_monthly[out_seasonal_cp[i]] for i in range(len(out_seasonal_cp)) ]  
    out.to_csv(code +'_out.csv', index=False)
    out_tcp.to_csv(code +'_out_trend_cp.csv', index=False)
    out_scp.to_csv(code +'_out_seasonal_cp.csv', index=False)

    #------------------------------------------------------------------------------
    # PLOT: timeseries, extracted trend & seasonal components + Bayesian changepoint probabilities + changepoint locations
    #------------------------------------------------------------------------------

    titlestr = 'Rbeast: ' + code
    figstr = code + '.png'

    fig, axes = plt.subplots(5,1,sharex=True, figsize=(15,10))      
    axes[0].set_title(titlestr, fontsize=20)
    axes[0].plot(t_monthly, ts_monthly, lw=1, color='navy', alpha=1.0)
    axes[0].xaxis.grid(True, which='major')      
    axes[0].yaxis.grid(True, which='major')  
    if use_normals == False:
        axes[0].set_ylabel('Temperature [°C]', fontsize=fontsize)
    else:
        axes[0].set_ylabel('Anomaly [°C]', fontsize=fontsize)
    axes[0].tick_params(labelsize=fontsize)    
    axes[1].plot(t_monthly, out_trend, lw=2, color='red', alpha=1.0)
    axes[1].fill_between(t_monthly, np.array(out_trend_CI_lower), np.array(out_trend_CI_upper), color='lightgrey', alpha=1.0)
    for i in range(len(out_trend_cp)):
        axes[1].axvline(x=t_monthly[out_trend_cp[i]], linestyle='dashed', color='blue')
    axes[1].xaxis.grid(True, which='major')      
    axes[1].yaxis.grid(True, which='major')  
    axes[1].set_ylabel('Trend [°C]', fontsize=fontsize)
    axes[1].tick_params(labelsize=fontsize)    
    axes[2].plot(t_monthly, out_trend_prob, lw=1, color='blue', alpha=1.0)
    axes[2].xaxis.grid(True, which='major')      
    axes[2].yaxis.grid(True, which='major')  
    axes[2].set_ylabel('p(Trend)', fontsize=fontsize)
    axes[2].tick_params(labelsize=fontsize)    
    axes[3].plot(t_monthly, out_seasonal, lw=2, color='red', alpha=1.0)
    axes[3].fill_between(t_monthly, np.array(out_seasonal_CI_lower), np.array(out_seasonal_CI_upper), color='lightgrey', alpha=1.0)
    for i in range(len(out_seasonal_cp)):
        axes[3].axvline(x=t_monthly[out_seasonal_cp[i]], linestyle='dashed', color='blue')
    axes[3].xaxis.grid(True, which='major')      
    axes[3].yaxis.grid(True, which='major')  
    axes[3].set_ylabel('Seasonal [°C]', fontsize=fontsize)
    axes[3].tick_params(labelsize=fontsize)    
    axes[4].plot(t_monthly, out_seasonal_prob, lw=1, color='blue', alpha=1.0)
    axes[4].xaxis.grid(True, which='major')      
    axes[4].yaxis.grid(True, which='major')  
    axes[4].set_ylabel('p(Seasonal)', fontsize=fontsize)
    axes[4].set_xlabel('Year', fontsize=fontsize)
    axes[4].tick_params(labelsize=fontsize)    
    plt.savefig(figstr)
    plt.close(fig)


