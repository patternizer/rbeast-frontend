#!/usr/bin/Rscript

# ENABLE command line arguments
args <- commandArgs(TRUE)
commandArgs()

# NB: $ chmod +x test.R
# NB: $ ./test.R myarg1 myarg2

install.packages('Rbeast')
library(Rbeast)

# NB: set all missing data to NAs, NaNs
# NB: period is estimated via auto-correlation

# LOAD: timeseries

# modis_ohio is a vector comprising 14 years’ MODIS EVI data at a pixel in Southern Ohio

data(modis_ohio)

# SET: output directory

#getwd()
setwd("PLOTS/")

# PLOT: timeseries

png(filename="rbeast-ohio-timeseries.png"); plot(modis_ohio,type='l'); dev.off()

# PLOT: beast fit components (auto-period)

out=beast(modis_ohio)
png(filename="rbeast-ohio-auto.png"); plot(out); dev.off()

# PLOT: beast fit components (period=23)

out=beast(modis_ohio,23)
png(filename="rbeast-ohio-seasonal.png"); plot(out$s,type='l'); dev.off()                            #The same as plot(out$s[,1]): plot the seasonal curve
png(filename="rbeast-ohio-prob-changepoints-seasonal.png"); plot(out$sProb,type='l'); dev.off()       #Plot the probability of observing seasonal changepoints
png(filename="rbeast-ohio-trend.png"); plot(out$t,type='l'); dev.off()                               #The same as plot(out$t[,1]): plot the trend
png(filename="rbeast-ohio-prob-changepoints-trend.png"); plot(out$tProb,type='l'); dev.off()         #Plot the probability of observing trend changepoints

# PLOT: beast fit components (period=23) using GUI (windows x64 only)
# out=beast(modis_ohio, 23, demoGUI=TRUE)

# LOAD: simulated timeseries

# simdata [300 x 3] equal timeseries to illustrate BEAST can handle multiple time series at a single call

data(simdata)
png(filename="rbeast-simdata.png"); plot(simdata,type='l'); dev.off()
png(filename="rbeast-simdata-1.png"); plot(simdata[,1]); dev.off()
#out=beast(simdata)
out=beast( simdata, list(period=24, chainNumber=3, sample=1000, burnin=200) )
png(filename="rbeast-simdata-1-fit.png"); plot(out,1,type='l'); dev.off()
png(filename="rbeast-simdata-2-fit.png"); plot(out,2,type='l'); dev.off()
png(filename="rbeast-simdata-3-fit.png"); plot(out,3,type='l'); dev.off()

##########################################################################
# EXAMPLE WITH ALL OPTIONS
##########################################################################

opt=list()                          #Create an empty list to append individual model parameters
opt$period=23                       #Period of the cyclic/seasonal component of the modis time series
opt$minSeasonOrder=2                #Min harmonic order allowed in fitting season component
opt$maxSeasonOrder=8                #Max harmonic order allowed in fititing season component
opt$minTrendOrder=0                 #Min polynomial order allowed to fit trend (0 for constant)
opt$maxTrendOrder=1                 #Max polynomial order allowed to fit trend (1 for linear term)
opt$minSepDist_Season=20            #Min seperation time btw neighboring season change-pts(mustbe >=0)
opt$minSepDist_Trend=20             #Min seperation time btw neighboring trend change-pts(must be >=0)
opt$maxKnotNum_Season=4             #Max number of season changepoints allowed
opt$maxKnotNum_Trend=10             #Max number of trend changepoints allowed
opt$omittedValue=-999               #A customized value to indicate bad/missing values in the time
#series, in additon to those NA or NaN values.
opt$printToScreen=1
opt$printCharLen=150                #If set to 1, display some progress status while running
#The length of chars in each status line when printToScreen=1
# The following parameters used to configure the reverisible-jump MCMC (RJMCC) sampler
opt$chainNumber=2                   #Number of parallel MCMC chains
opt$sample=1000                     #Number of samples to be collected per chain
opt$thinningFactor=3                #A factor to thin chains (e.g., samples taken every 3 iterations)
opt$burnin=500                      #Number of burn-in samples discarded at the start of each chain
opt$maxMoveStepSize=30              #For the move proposal, the max window allowed in jumping from
#the current changepoint
opt$resamplingSeasonOrderProb=0.2   #The probability of selecting a re-sampling proposal
#(e.g., resample seasonal harmonic order)
opt$resamplingTrendOrderProb=0.2    #The probability of selecting a re-sampling proposal
#(e.g., resample trend polynomial order)
opt$seed=65654                      #A seed for the random generator: If seed=0,random numbers differ
#for different BEAST runs. Setting seed to a chosen non-zero integer
#will allow reproducing the same result for different BEAST runs.
opt$computeCredible=0               #If set to 1, compute 95% credible intervals: The results will be
#saved as sCI, tCI, and bCI in the output variable.
opt$fastCIComputation=0             #If set to 1, employ a fast algorithm to compute credible intervals
opt$computeSlopeSign=1              #If set to 1, compute the probability of having a postive slope in
#the estimated trend. The result will be saved as bsign in the output
#variable.
opt$computeHarmonicOrder=1          #If set to 1, compute the mean harmonic order of the fitted
#seasonal component. The result will be saved as "horder" in
#the output variable.
opt$computeTrendOrder=1             #If set to 1, compute the mean polynomial order of the fitted
#trend component. The result will be saved as "torder" in
#the output variable.
#opt$outputToDisk=0
#(if set to 1, results will be written to files in a folder)
#opt$outputFolder ='c:/out'#Specify the output folder when outputToDisk=1
#opt$lengthPerTimeSeries_infile=300#the time series length if input data come from a binary file
# Use "opt" defined above in the beast function. Note that to run beast(), not all the individual
# parameters in option need to be explicitly specified. If an parameter is not given in option, its
# default value will be used.
out=beast(modis_ohio, opt)
png(filename="rbeast-ohio-all-opts.png"); plot(out); dev.off()









