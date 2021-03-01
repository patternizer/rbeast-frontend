![image](https://github.com/patternizer/rbeast-frontend/blob/master/rbeast-040011.png)

# rbeast-frontend

Python + R front-end for changepoint detection using Rbeast in monthly land surface air temperature monitoring station timeseries from CRUTEM5 in the [GloSAT](https://www.glosat.org) project: www.glosat.org

* python code to prepare station data, call Rbeast and return output arrays for plotting extracted trend, seasonality, changepoints and 95% credible intervals

## Contents

* `make-stationfile.py` - helper file to extract 'stationfile.txt' from the latest GloSAT.p0x archive in Pandas pickle format (.pkl)
* `local-rpy2-station.py` - local env run applied to CRUTEM formatted station file: 'stationfile.txt'
* `local-rpy2-subset.py` - local env run applied to CRUTEM formatted file containing a subset (e.g. regional / country) of station files with one stationcode selected: change lines containing filename and code
* `run_rpy2_subset.py` - SLURM shell script generator to loop through all stationcodes in the subset file
* `rbeast-frontend-runnable-rpy2-subset.py` - SLURM generic runnable called by run_rpy2_subset
* `rbeast-frontend-runnable-rpy2-station.py` - SLURM generic runnable called by run_rpy2_station.sh to run a single station timeseries
* `rbeast_tests.R` - R env Rbeast benchmark demos
* `rbeast-frontend.py` - python code to generate station homogenisation dataframes for Rbeast via Rscript (not rpy2) call to R env
* `rbeast-frontend.R` - R code called by Rscript via control passed by rbeast-frontend.py
* `rbeast_frontend_runnable.R` - R env frontend code calling Rbeast (NB: not called by rpy2 but control passed by python subprocess to Rscript)
 
The first step is to clone the latest rbeast-backend code and step into the check out directory: 

    $ git clone https://github.com/patternizer/rbeast-frontend.git
    $ cd rbeast-frontend

### Using Standard Python

The code should run with the [standard CPython](https://www.python.org/downloads/) installation and was tested in a conda virtual environment running a 64-bit version of Python 3.8.5.

rbeast-frontend scripts can be run from sources directly, once the dependencies are satisfied (both needed python libraries and a working R installation). The R packages required include: Rbeast, readr, utils. Historical data rescue means that we are now working with temperature observation timeseries starting before the Pandas timestamps range limit of 1677, it has been necessary to use the Xarray cftime.datetime() solution documented here: http://xarray.pydata.org/en/stable/weather-climate.html#cftimeindex. For the repo code to work on such stations, you will need to install the nc-time-axis library as described here: https://github.com/scitools/nc-time-axis. 

A single station timeseries changepoint analysis might involve extracting a single station file and applying Rbeast. This is achieved by changing the selected stationcode in make-stationfile.py and then the 2 calls:

    $ python make-stationfile.py
    $ python local-rpy2-station.py

A single station timeseries changepoint analysis for one station embedded in a large CRUTEM format extract of stations can be accomplished by changing the filename of the subset file and specifying the station code in local-rpy2-subset.py and then calling:

    $ python local-rpy2-subset.py

A SLURM run looping over all stations in a large CRUTEM format extract of stations can be accomplished by entering an activated conda renv on JASMIN and calling:

    (renv)$ run_rpy2_subset.py

Work is in progress to cater for more run set up variations.

## License

The code is distributed under terms and conditions of the [Open Government License](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Contact information

* [Michael Taylor](michael.a.taylor@uea.ac.uk)

