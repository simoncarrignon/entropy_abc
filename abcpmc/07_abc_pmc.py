#!/usr/bin/python3

import sampler
import threshold
import numpy as np
import entropy 
import os

def dist(x,y):
    numTopSites = 25
    listTopSitesX = entropy.identifyTopSites(x, numTopSites)
    listTopSitesY = entropy.identifyTopSites(y, numTopSites)

    count = 0
    for site in listTopSitesX:
        if site in listTopSitesY:
            count += 1
    return 1 - count/numTopSites            

def postfn(params):
    print('postfn, params:',params) 
    cost = entropy.loadCosts('../data/costMatrix.csv')
    sites = '../data/cities_weights.csv'

    experiment = entropy.Experiment(0, params[0], params[1], params[2], params[3])
    simSites = entropy.runEntropy(experiment, cost, sites, False)
    return simSites


sites = '../data/cities_weights.csv'
data = entropy.loadHistoricalSites(sites)

eps = threshold.LinearEps(5, 0.9, 0.5)
priors = sampler.TophatPrior([0,0,0,0], [1,2,2,2])
sampler = sampler.Sampler(N=3, Y=data, postfn=postfn, dist=dist, threads=16)
logFile = open('log.txt', 'w')
logFile.write('logs starting''\n')
logFile.close()

for pool in sampler.sample(priors, eps):
    logFile = open('general_'+str(os.getpid())+'.txt', 'a')
    logFile.write('logs for eps: '+str(pool.eps)+'\n')
    logFile.close()
    print("T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))

print(pool.thetas)
np.savetxt("foo.csv", pool.thetas, delimiter=";", fmt='%1.5f')

