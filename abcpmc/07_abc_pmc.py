#!/usr/bin/python3

import sampler
import threshold
import numpy as np
import entropy 
import os
import sys

def distRelative(x,y):
    maxSiteX = sys.float_info.min
    minSiteX = sys.float_info.max

    if x[0].weight == -1 and y[0].weight == -1:
        return 1.0

    for site in x:
        if site.weight != -1:
            if site.weight < minSiteX:
                minSiteX = site.weight
            elif site.weight > maxSiteX:
                maxSiteX = site.weight
        else:
            if site.size < minSiteX:
                minSiteX = site.size
            elif site.size > maxSiteX:
                maxSiteX = site.size
    
    listValuesX = list()           
    for site in x:
        if site.weight != -1:
            listValuesX.append((site.weight-minSiteX)/(maxSiteX-minSiteX))
        else:
            listValuesX.append((site.size-minSiteX)/(maxSiteX-minSiteX))

    maxSiteY = sys.float_info.min
    minSiteY = sys.float_info.max

    for site in y:    
        if site.weight != -1:
            if site.weight < minSiteY:
                minSiteY = site.weight
            elif site.weight > maxSiteY:
                maxSiteY = site.weight
        else:
            if site.size < minSiteY:
                minSiteY = site.size
            elif site.size > maxSiteY:
                maxSiteY = site.size

    listValuesY = list()           
    for site in y:
        if site.weight != -1:
            listValuesY.append((site.weight-minSiteY)/(maxSiteY-minSiteY))
        else:
            listValuesY.append((site.size-minSiteY)/(maxSiteY-minSiteY))

    diff = 0

    for i in range(len(listValuesX)):
        diff += abs(listValuesX[i] - listValuesY[i])
    print('diff:',diff/len(listValuesX))
    return diff/len(listValuesX)

"""        
def dist(x,y):
    numTopSites = 25
    listTopSitesX = entropy.identifyTopSites(x, numTopSites)
    listTopSitesY = entropy.identifyTopSites(y, numTopSites)

    count = 0
    for site in listTopSitesX:
        if site in listTopSitesY:
            count += 1
    return 1 - count/numTopSites            
"""

def postfn(params):
    print('postfn, params:',params) 
    cost = entropy.loadCosts('../data/costMatrix.csv')
    sites = '../data/cities_weights.csv'

    experiment = entropy.Experiment(0, params[0], params[1], params[2], params[3])
    simSites = entropy.runEntropy(experiment, cost, sites, False)
    return simSites


sites = '../data/cities_weights.csv'
data = entropy.loadHistoricalSites(sites)

eps = threshold.LinearEps(10, 0.3, 0.05)
priors = sampler.TophatPrior([0,0,0,0], [1,2,2,2])
sampler = sampler.Sampler(N=5, Y=data, postfn=postfn, dist=distRelative, threads=4)

for pool in sampler.sample(priors, eps):
    logFile = open('general_'+str(os.getpid())+'.txt', 'a')
    logFile.write('starting eps: '+str(pool.eps)+'\n')
    logFile.close()
    print("T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))

print(pool.thetas)
np.savetxt("foo.csv", pool.thetas, delimiter=";", fmt='%1.5f')

