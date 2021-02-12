# rbeast-frontend

Python + R front-end for changepoint detection using Rbeast in monthly land surface air temperature monitoring station timeseries from CRUTEM5 in the [GloSAT](https://www.glosat.org) project:

* python code to prepare station data, call Rbeast and return output arrays for plotting extracted trend, seasonality, changepoints and 95% credible intervals

## Contents

* `rbeast-frontend.py` - python code to generate station homogenisation dataframes for Rbeast call and then to analyse and plot Rbeast output
* `rbeast-frontend.R` - R code to import python dataframes, call Rbeast and save output arrays
* `Rbeast` - R package

The first step is to clone the latest rbeast-backend code and step into the check out directory: 

    $ git clone https://github.com/patternizer/rbeast-frontend.git
    $ cd rbeast-frontend

### Using Standard Python

The code should run with the [standard CPython](https://www.python.org/downloads/) installation and was tested in a conda virtual environment running a 64-bit version of Python 3.8+.

rbeast-frontend scripts can be run from sources directly, once the dependencies are satisfied (both needed python libraries and a working R installation).

Run with:

    $ python rbeast-frontend.py

## License

The code is distributed under terms and conditions of the [Open Government License](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Contact information

* [Michael Taylor](michael.a.taylor@uea.ac.uk)

