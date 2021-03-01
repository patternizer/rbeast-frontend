#!/usr/bin/env python
    
#------------------------------------------------------------------------------
# PROGRAM: run_rpy2_subset.py
#------------------------------------------------------------------------------
# Version 0.2
# 28 February, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
# michael DOT a DOT taylor AT uea DOT ac DOT uk
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------

import numpy as np
import datetime 
import calendar
import os
import os.path
import sys
import uuid
import glob
import stat
from  optparse import OptionParser
import subprocess

def make_shell_command(filename,stationcode):
         
    currentdir = os.getcwd()
    outdir = '{0}/{1}'.\
        format(currentdir,stationcode)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    os.chdir(outdir)
    try:
        os.symlink('../rbeast-frontend-runnable-rpy2-subset.py','rbeast-frontend-runnable-rpy2-subset.py')
        os.symlink('../rbeast-frontend/Iceland21.postmerge','Iceland21.postmerge')
        os.symlink('../rbeast-frontend/normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt','normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt')
    except:
        pass

    # job submission script file 
    job_file = 'run.{0}.sh'.format(stationcode)
    with open(job_file,'w') as fp:
        job_id = 'SBATCH --job-name=mataylor.{0}\n'.format(stationcode)
        job_str = 'python rbeast-frontend-runnable-rpy2-subset.py {0} {1}\n'.format(filename,stationcode)
        fp.write('#!/bin/bash\n')
        fp.write('SBATCH --partition=short-serial\n')
        fp.write(job_id)
        fp.write('SBATCH -o %j.out\n')
        fp.write('SBATCH -e %j.err\n') 
        fp.write('SBATCH --time=30:00\n')
        fp.write('conda activate\n')
        fp.write('conda activate renv\n')
        fp.write(job_str)    

    os.chmod(job_file,stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    job = ['sbatch',job_file]
    subprocess.call(job)
    os.chdir(currentdir)                    

def run_all_stations(filename):

    nheader = 0
    f = open(filename)
    lines = f.readlines()
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        if len(words) == 9:
            stationcode = '0'+words[0][0:6]
            make_shell_command(filename,stationcode)       
    f.close()    
 
if __name__ == "__main__":
    
    parser = OptionParser("usage: %prog subset")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    filename = args[0]
    run_all_stations(filename)



