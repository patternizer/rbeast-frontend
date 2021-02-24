#!/usr/bin/env python
    
#------------------------------------------------------------------------------
# PROGRAM: run_rbeast.py
#------------------------------------------------------------------------------
# Version 0.1
# 23 February, 2021
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

def make_shell_command(filename,directory,stationcode):
         
    currentdir = os.getcwd()
    outdir = '{0}/{1:06d}'.\
        format(currentdir,stationcode)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    os.chdir(outdir)
    try:
        os.symlink('/users/mtaylor/checkouts/rbeast-frontend/rbeast-frontend-runnable-rpy2-subset.py','rbeast-frontend-runnable-rpy2-subset.py')
    except:
        pass

    # job submission script file 
    job_file = 'run.{0:06d}.sh'.format(stationcode)
    with open(job_file,'w') as fp:
        job_id = 'SBATCH --job-name=mataylor.{0:06d}'.format(stationcode)
        job_str = 'python rbeast-frontend-runnable-rpy2-subset.py {0} {1:06d}\n'.format(filename,stationcode)
        fp.write('#!/bin/bash')
        fp.write('SBATCH --partition=short-serial')
        fp.write(job_id)
        fp.write('SBATCH -o %j.out')
        fp.write('SBATCH -e %j.err') 
        fp.write('SBATCH --time=30:00')
        fp.write('conda activate')
        fp.write('conda activate renv')
        fp.write(job_str)    

    os.chmod(job_file,stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    job_name='./'+job_file
    job = ['sbatch',job_name]
    subprocess.call(job)
    os.chdir(currentdir)                    

def run_all_stations(filename):

    #-----------------------------------
    # EDIT: extract list of stationcodes
    #-----------------------------------
    stationcode = '040300'

    directory = '/users/mtaylor/checkouts/rbeast-frontend/{0:06d}'.format(stationcode)
    make_shell_command(filename,directory,stationcode)       
 
if __name__ == "__main__":
    
    parser = OptionParser("usage: %prog subset")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    filename = args[0]
    run_all_stations(filename)



