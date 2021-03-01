#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: load-stations.py
#------------------------------------------------------------------------------
# Version 0.4
# 1 March, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import pickle

# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

filename_txt = 'stat4.GloSATprelim03.1658-2020.txt'
load_df = True
save_df = True
use_pickle = True

#------------------------------------------------------------------------------
# METHODS
#------------------------------------------------------------------------------

def load_dataframe(filename_txt):
    
    #------------------------------------------------------------------------------
    # I/O: stat4.GloSATprelim02.1658-2020.txt
    #------------------------------------------------------------------------------

    # load .txt file (comma separated) into pandas dataframe

    # filename_txt = 'stat4.GloSATprelim02.1658-2020.txt'
    # station header sample:    
    # [067250 464  -78 1538 BLATTEN, LOETSCHENTA SWITZERLAND   20012012  982001    9999]
    # station data sample:
    # [1921  -44  -71  -68  -46  -12   17   42   53   27  -20  -21  -40]

    yearlist = []
    monthlist = []
    stationcode = []
    stationlat = []
    stationlon = []
    stationelevation = []
    stationname = []
    stationcountry = []
    stationfirstyear = []
    stationlastyear = []
    stationsource = []
    stationfirstreliable = []
    stationfirstreliable = []
    stationcruindex = []
    stationgridcell = []
    
    with open (filename_txt, 'r', encoding="ISO-8859-1") as f:  
                    
        for line in f:   

            if len(line)>1: # ignore empty lines  
       
                if (len(line.strip().split())!=13) | (len(line.split()[0])>4): # header lines
                    
                    # Station Header File (IDL numbering): 
                    # https://crudata.uea.ac.uk/cru/data/temperature/crutem4/station-data.htm
                    #
                    #    (ch. 1-7) World Meteorological Organization (WMO) Station Number with a single additional character making a field of 6 integers. WMO numbers comprise a 5 digit sub-field, where the first two digits are the country code and the next three digits designated by the National Meteorological Service (NMS). Some country codes are not used. If the additional sixth digit is a zero, then the WMO number is or was an official WMO number. If the sixth digit is not zero then the station does not have an official WMO number and an alternative number has been assigned by CRU. Two examples are given below. Many additional stations are grouped beginning 99****. Station numbers in the blocks 72**** to 75**** are additional stations in the United States.
                    #    (ch. 8-11) Station latitude in degrees and tenths (-999 is missing), with negative values in the Southern Hemisphere
                    #    (ch. 12-16) Station longitude in degrees and tenths (-1999 is missing), with negative values in the Eastern Hemisphere (NB this is opposite to the more usual convention)
                    #    (ch. 18-21) Station Elevation in metres (-999 is missing)
                    #    (ch. 23-42) Station Name
                    #    (ch. 44-56) Country
                    #    (ch. 58-61) First year of monthly temperature data
                    #    (ch. 62-65) Last year of monthly temperature data
                    #    (ch. 68-69) Data Source (see below)
                    #    (ch. 70-73) First reliable year (generally the same as the first year)
                    #    (ch. 75-78) Unique index number (internal use)
                    #    (ch. 80-83) Index into the 5° x 5° gridcells (internal use) 
                    #
                    # NB: char positions differ due to empty space counts difference
                
                    code = line[0:6]                
                    lat = line[6:10]
                    lon = line[10:15]
                    elevation = line[17:20]
                    name = line[21:41]
                    country = line[42:55]
                    firstyear = line[56:60]
                    lastyear = line[60:64]
                    source = line[64:68]
                    firstreliable = line[68:72]
                    cruindex = line[72:77]
                    gridcell = line[77:80]    
                                                
                else:           
                    yearlist.append(int(line.strip().split()[0]))                                 
                    monthlist.append(np.array(line.strip().split()[1:]))                                 
                    stationcode.append(code)
                    stationlat.append(lat)
                    stationlon.append(lon)
                    stationelevation.append(elevation)
                    stationname.append(name)
                    stationcountry.append(country)
                    stationfirstyear.append(firstyear)
                    stationlastyear.append(lastyear)
                    stationsource.append(source)
                    stationfirstreliable.append(firstreliable)
                    stationcruindex.append(cruindex)
                    stationgridcell.append(gridcell)
            else:
                continue
    f.close

    # construct dataframe
    
    df = pd.DataFrame(columns=['year','1','2','3','4','5','6','7','8','9','10','11','12'])
    df['year'] = yearlist

    for j in range(1,13):

        df[df.columns[j]] = [ monthlist[i][j-1] for i in range(len(monthlist)) ]

    df['stationcode'] = stationcode    
    df['stationlat'] = stationlat
    df['stationlon'] = stationlon
    df['stationelevation'] = stationelevation
    df['stationname'] = stationname
    df['stationcountry'] = stationcountry
    df['stationfirstyear'] = stationfirstyear
    df['stationlastyear'] = stationlastyear
    df['stationsource'] = stationsource
    df['stationfirstreliable'] = stationfirstreliable
#    df['stationcruindex'] = stationcruindex # NB: there are merge issues here for some stations --> DtypeWarning
#    df['stationgridcell'] = stationgridcell # NB: there are merge issues here for some stations --> DtypeWarning

    # trim strings
    
    df['stationname'] = [ str(df['stationname'][i]).strip() for i in range(len(df)) ] 
    df['stationcountry'] = [ str(df['stationcountry'][i]).strip() for i in range(len(df)) ] 

    # convert numeric variables from list of str to int (important due to fillValue)   
    
    for j in range(1,13):

        df[df.columns[j]] = df[df.columns[j]].astype('int')

    df['stationlat'] = df['stationlat'].astype('int')
    df['stationlon'] = df['stationlon'].astype('int')
    df['stationelevation'] = df['stationelevation'].astype('int')    
    df['stationfirstreliable'] = df['stationfirstreliable'].astype('int')    
    
    # replace fill values in int variables:
        
    # -999 for stationlat
    # -9999 for stationlon
    # -9999 for station elevation
    # (some 999's occur elsewhere - fill all bad numeric cases with NaN)
    
    for j in range(1,13):

        df[df.columns[j]].replace(-999, np.nan, inplace=True)

    df['stationlat'].replace(-999, np.nan, inplace=True) 
    df['stationlon'].replace(-9999, np.nan, inplace=True) 
    df['stationelevation'].replace(-9999, np.nan, inplace=True) 
#   df['stationfirstreliable'].replace(8888, np.nan, inplace=True) 
                    
    return df

#------------------------------------------------------------------------------
# LOAD DATAFRAME
#------------------------------------------------------------------------------

if load_df == True:

    if use_pickle == True:
        df = pd.read_pickle('df_temp.pkl', compression='bz2')    
    else:
        df = pd.read_csv('df_temp.csv', index_col=0)

else:    

    df = load_dataframe(filename_txt)

    #------------------------------------------------------------------------------
    # ADD LEADING 0 TO STATION CODES (str)
    #------------------------------------------------------------------------------

    df['stationcode'] = [ str(df['stationcode'][i]).zfill(6) for i in range(len(df)) ]

    #------------------------------------------------------------------------------
    # APPLY SCALE FACTORS
    #------------------------------------------------------------------------------

    df['stationlat'] = df['stationlat']/10.0
    df['stationlon'] = df['stationlon']/10.0

    for j in range(1,13):

        df[df.columns[j]] = df[df.columns[j]]/10.0

    #------------------------------------------------------------------------------
    # CONVERT LONGITUDES FROM +W to +E
    #------------------------------------------------------------------------------

    df['stationlon'] = -df['stationlon']

    #------------------------------------------------------------------------------
    # CONVERT DTYPES FOR EFFICIENT STORAGE
    #------------------------------------------------------------------------------

    df['year'] = df['year'].astype('int16')

    for j in range(1,13):

        df[df.columns[j]] = df[df.columns[j]].astype('float32')
        
    df['stationlat'] = df['stationlat'].astype('float32')
    df['stationlon'] = df['stationlon'].astype('float32')
    df['stationelevation'] = df['stationelevation'].astype('int16')
    df['stationfirstyear'] = df['stationfirstyear'].astype('int16')
    df['stationlastyear'] = df['stationlastyear'].astype('int16')
    df['stationsource'] = df['stationsource'].astype('int8')
    df['stationfirstreliable'] = df['stationfirstreliable'].astype('int16')

#------------------------------------------------------------------------------
# SAVE SCALED DATAFRAME
#------------------------------------------------------------------------------

if save_df == True:

    if use_pickle == True:
        df.to_pickle('df_temp.pkl', compression='bz2')
    else:
        df.to_csv('df_temp.csv')

#------------------------------------------------------------------------------
print('** END')

