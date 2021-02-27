#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: make-stationfile.py
#------------------------------------------------------------------------------
# Version 0.1
# 26 February, 2021
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

stationfile = 'stationfile.txt'
stationcode = '037401'

#------------------------------------------------------------------------------
# LOAD: GloSAT absolute temperature archive in pickled pandas dataframe format
#------------------------------------------------------------------------------

df_temp = pd.read_pickle('df_temp.pkl', compression='bz2')
try:
    value = np.where(df_temp['stationcode'].unique()==stationcode)[0][0]
except:        
    print('Stationcode not in archive')

#------------------------------------------------------------------------------
# EXTRACT: station data + metadata
#------------------------------------------------------------------------------

station_data = df_temp[df_temp['stationcode']==df_temp['stationcode'].unique()[value]].iloc[:,range(0,13)].reset_index(drop=True)
station_metadata = df_temp[df_temp['stationcode']==df_temp['stationcode'].unique()[value]].iloc[0,range(14,23)]

#------------------------------------------------------------------------------
# FORMAT: station header components in CRUTEM format
#
# 37401 525  -17  100 HadCET on 29-11-19   UK            16592019  351721     NAN
#2019   40   66   78   91  111  141  175  171  143  100 -999 -999
#------------------------------------------------------------------------------

stationlat = "{:<4}".format(str(int(station_metadata[0]*10)))
stationlon = "{:<4}".format(str(int(station_metadata[1]*10)))
stationelevation = "{:<3}".format(str(station_metadata[2]))
stationname = "{:<20}".format(station_metadata[3][:20])
stationcountry = "{:<13}".format(station_metadata[4][:13])
stationfirstlast = str(station_metadata[5]) + str(station_metadata[6])
stationsourcefirst = "{:<8}".format(str(station_metadata[7]) + str(station_metadata[8]))
stationgridcell = "{:<3}".format('NAN')
station_header = ' ' + stationcode[1:] + ' ' + stationlat + ' ' + stationlon + ' ' + stationelevation + ' ' + stationname + ' ' + stationcountry + ' ' + stationfirstlast + '  ' + stationsourcefirst + '   ' + stationgridcell 

#------------------------------------------------------------------------------
# WRITE: station header + yearly rows of monthly values in CRUTEM format
#------------------------------------------------------------------------------

with open(stationfile,'w') as f:
    f.write(station_header+'\n')
    for i in range(len(station_data)):  
        year = str(int(station_data.iloc[i,:][0]))
        rowstr = year
        for j in range(1,13):
            if np.isnan(station_data.iloc[i,:][j]):
                monthstr = str(-999)
            else:
                monthstr = str(int(station_data.iloc[i,:][j]*10))
            rowstr += f"{monthstr:>5}"          
        f.write(rowstr+'\n')
    
#------------------------------------------------------------------------------
print('** END')

