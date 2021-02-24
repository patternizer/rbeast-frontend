#!/bin/bash
SBATCH --partition=short-serial 
SBATCH --job-name=mataylor
SBATCH -o %j.out 
SBATCH -e %j.err 
SBATCH --time=30:00

module load jaspy
python rbeast-frontend-runnable-rpy2-station.py stationfile.txt

