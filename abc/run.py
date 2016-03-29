#!/usr/bin/python3

import entropy
import numpy

def singleRun():

    alpha = 1.1
    beta = 2
    entropy.loadCosts('../data/costMatrixSea.csv')
    sites = '../data/cities_weights.csv'
    data = entropy.loadHistoricalSites(sites)

    experiment = entropy.Experiment(0,alpha,beta)
    result = entropy.runEntropy(experiment, sites, True)

    dist = entropy.distRelative(data, result)

if __name__ == "__main__":
    singleRun()

