#!/usr/bin/python3

import entropy
import numpy

def singleRun():

    weight = 'prom'
    alpha = 1.49
    beta = 0.01
    harbourBonus = 1.9
    cost = entropy.loadCosts('../data/costMatrix.csv')
    sites = '../data/cities_weights.csv'

    experiment = entropy.Experiment(0,weight,alpha,beta,harbourBonus)
    entropy.runEntropy(experiment, cost, sites, True)
 
    relativeWeights = numpy.full((len(entropy.Site.sites), len(entropy.Site.sites)), 0, dtype=float)
    for i in range(len(entropy.Site.sites)):
        for j in range(i):
            relativeWeights[i][j] = entropy.Site.sites[i].weight/entropy.Site.sites[j].weight

    result = numpy.absolute(entropy.Site.relativeSizes-relativeWeights)
    print('diff:',result.sum())

if __name__ == "__main__":
    singleRun()

