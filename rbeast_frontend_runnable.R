#!/usr/bin/Rscript

# ENABLE command line arguments
args <- commandArgs(TRUE)

#------------------------------------------------------------------------------
# PROGRAM: rbeast-frontend.R
#------------------------------------------------------------------------------
# Version 0.2
# 11 February, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------

# NB: $ chmod +x rbeast_frontend.R
# NB: $ ./rbeast_frontend.R stationcode

#install.packages('Rbeast')
#install.packages('readr')
#install.packages('rio')
#install.packages('date')
#install.packages('ggplot2')
library(Rbeast)
library(readr)
#library(rio)
#library(date)
#library(ggplot2)

#icelanddata <- read.csv("Iceland21.postmerge", sep="\t", header=TRUE)
code <- args
dg <- read.csv(file=paste(code,".csv",sep=""), head=TRUE, sep=",", stringsAsFactors=F, na.string="")
#out = beast( dg$ts, list(period=12, chainNumber=1, sample=1000, burnin=200) )

opt=list()                          #Create an empty list to append individual model parameters
opt$period=12                       #Period of the cyclic/seasonal component of the time series
opt$minSeasonOrder=2                #Min harmonic order allowed in fitting season component
opt$maxSeasonOrder=8                #Max harmonic order allowed in fititing season component
opt$minTrendOrder=0                 #Min polynomial order allowed to fit trend (0 for constant)
opt$maxTrendOrder=3                 #Max polynomial order allowed to fit trend (1 for linear term)
opt$minSepDist_Season=120           #Min seperation time btw neighboring season change-pts(mustbe >=0)
opt$minSepDist_Trend=120            #Min seperation time btw neighboring trend change-pts(must be >=0)
opt$maxKnotNum_Season=5             #Max number of season changepoints allowed
opt$maxKnotNum_Trend=5              #Max number of trend changepoints allowed
#opt$omittedValue=-999               #A customized value to indicate bad/missing values in the time
#series, in additon to those NA or NaN values.
opt$printToScreen=0
# The following parameters used to configure the reverisible-jump MCMC (RJMCC) sampler
opt$chainNumber=2                   #Number of parallel MCMC chains
opt$sample=1000                     #Number of samples to be collected per chain
opt$thinningFactor=3                #A factor to thin chains (e.g., samples taken every 3 iterations)
opt$burnin=500                      #Number of burn-in samples discarded at the start of each chain
opt$maxMoveStepSize=120             #For the move proposal, the max window allowed in jumping from
#the current changepoint
opt$resamplingSeasonOrderProb=0.2   #The probability of selecting a re-sampling proposal
#(e.g., resample seasonal harmonic order)
opt$resamplingTrendOrderProb=0.2    #The probability of selecting a re-sampling proposal
#(e.g., resample trend polynomial order)
opt$seed=42                        #A seed for the random generator: If seed=0,random numbers differ for different BEAST runs. 
opt$computeCredible=1               #If set to 1, compute 95% credible intervals: The results will be saved as sCI, tCI, and bCI in the output variable.
opt$fastCIComputation=1             #If set to 1, employ a fast algorithm to compute credible intervals
opt$computeSlopeSign=0              #If set to 1, compute the probability of having a postive slope in
#the estimated trend. The result will be saved as bsign in the output variable.
opt$computeHarmonicOrder=1          #If set to 1, compute the mean harmonic order of the fitted
#seasonal component. The result will be saved as "horder" in the output variable.
opt$computeTrendOrder=1             #If set to 1, compute the mean polynomial order of the fitted
#trend component. The result will be saved as "torder" in the output variable.
opt$outputToDisk=0                  #(if set to 1, results will be written to files in a folder)

out=beast(dg$ts, opt)
out_trend <- c(out$t)
out_trend_prob <- c(out$tProb)
out_trend_CI <- c(out$tCI)
out_trend_order <- c(out$torder)
out_trend_cp <- c(out$tcp)
out_seasonal <- c(out$s)
out_seasonal_prob <- c(out$sProb)
out_seasonal_CI <- c(out$sCI)
out_seasonal_order <- c(out$horder)
out_seasonal_cp <- c(out$scp)

#setwd("~/Desktop/Rbeast/")
write.csv(out_trend, paste(code,"_trend.csv",sep=""), row.names=FALSE)
write.csv(out_trend_prob, paste(code,"_trend_prob.csv",sep=""), row.names=FALSE)
write.csv(out_trend_CI, paste(code,"_trend_CI.csv",sep=""), row.names=FALSE)
write.csv(out_trend_order, paste(code,"_trend_order.csv",sep=""), row.names=FALSE)
write.csv(out_trend_cp, paste(code,"_trend_cp.csv",sep=""), row.names=FALSE)
write.csv(out_seasonal, paste(code,"_seasonal.csv",sep=""), row.names=FALSE)
write.csv(out_seasonal_prob, paste(code,"_seasonal_prob.csv",sep=""), row.names=FALSE)
write.csv(out_seasonal_CI, paste(code,"_seasonal_CI.csv",sep=""), row.names=FALSE)
write.csv(out_seasonal_order, paste(code,"_seasonal_order.csv",sep=""), row.names=FALSE)
write.csv(out_seasonal_cp, paste(code,"_seasonal_cp.csv",sep=""), row.names=FALSE)

#write.csv(out, "~/Desktop/Rbeast/out.csv", row.names=FALSE)
#write_csv(out, "~/Desktop/Rbeast/out.csv")
#cat(capture.output(print(out), file="out.csv"))
#lapply(out, function(x) write.table( data.frame(x), 'out.csv'  , append= T, sep=',' ))

#str1 = "rbeast-iceland-fit-"
#str2 = "rbeast-iceland-timeseries-"
#strid = args[1]
#strext = ".png"
#fname1 = paste(str1,strid,strext)
#fname2 = paste(str2,strid,strext)
#png(filename=fname1); plot(out); dev.off()
#png(filename=fname2); plot(dg$ts~as.Date(dg$t,"%Y-%m-%d"),type="l",xlab="",ylab="Temperature",main=strid); #dev.off()


