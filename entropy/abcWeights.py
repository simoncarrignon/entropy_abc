#!/usr/bin/python3

import sampler
import threshold
import numpy as np
import entropy 
import os
import sys

def postfn(params):
#    print('postfn, params:',params) 
    entropy.loadCosts('../data/costMatrixSea.csv')
    sites = '../data/cities_weights.csv'

    experiment = entropy.Experiment(0, params[0], params[1], 0, params[2:])
    simSites = entropy.runEntropy(experiment, sites, False)
    return simSites

sites = '../data/cities_weights.csv'
data = entropy.loadHistoricalSites(sites)

eps = threshold.LinearEps(15, 400, 150)

# alpha, beta, and the list of weights
numParams = 2+len(data)
leftBounds = np.zeros(numParams)
rightBounds = np.full(numParams, 100)
# alpha and beta are not 0-100 but 0-2
rightBounds[0] = 2
rightBounds[1] = 2

priors = sampler.TophatPrior(leftBounds, rightBounds)

sampler = sampler.Sampler(N=10, Y=data, postfn=postfn, dist=entropy.distRelative, threads=4)

for pool in sampler.sample(priors, eps):
    print("T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))
    np.savetxt("result_"+str('%.2f')%pool.eps+'.csv', pool.thetas, delimiter=";", fmt='%1.5f')

print(pool.thetas)
np.savetxt("foo.csv", pool.thetas, delimiter=";", fmt='%1.5f')

