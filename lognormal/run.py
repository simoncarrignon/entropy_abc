#!/usr/bin/python3

import lognorm
import numpy as np

def main():
    alpha = 0.9
    beta = 0.05
    meanlog = 0.1
    sdlog = 0.1
#    multipleRuns(alpha,beta,meanlog,sdlog)
    singleRun(alpha,beta,meanlog,sdlog)

def singleRun(alpha,beta,meanlog,sdlog):
    sites = '../data/cities_weights.csv'
    # it speeds up the run
    numSites = 140
    costs = lognorm.loadCosts('../data/costMatrixSea.csv',numSites)

    data = lognorm.loadHistoricalSites(sites, numSites)
    experiment = lognorm.Experiment(alpha,beta,meanlog,sdlog, numSites, costs, np.amax(data))
    result = lognorm.run(experiment, True)
    dist = lognorm.distPerc(data, result)

def multipleRuns(alpha,beta,meanlog,sdlog):
    numRuns = 100

    sites = '../data/cities_weights.csv'
    # it speeds up the run
    numSites = 140
    costs = lognorm.loadCosts('../data/costMatrixSea.csv',numSites)

    data = lognorm.loadHistoricalSites(sites, numSites)

    for i in range(numRuns):
        experiment = lognorm.Experiment(alpha,beta,meanlog, sdlog, numSites, costs, np.amax(data))
        result = lognorm.run(experiment, True)
        dist = lognorm.distPerc(data, result)

if __name__ == "__main__":
    main()

