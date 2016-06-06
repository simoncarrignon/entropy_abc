#!/usr/bin/python3

import lognorm


def singleRun():
    alpha = 1.788
    beta = 0.544
    innovationRate = 0.007
  
    sites = '../data/cities_weights.csv'
    # it speeds up the run
    numSites = 140

    data = lognorm.loadHistoricalSites(sites, numSites)
    experiment = lognorm.Experiment(0,alpha,beta,innovationRate, numSites)
    result = lognorm.run(experiment, True)
    dist = lognorm.distRelative(data, result)



if __name__ == "__main__":
    singleRun()

