#!/usr/bin/python3

import sampler
import threshold
import numpy as np
import ceec 
import os
import sys

def postfn(params):
#    print('postfn, params:',params) 
    experiment = ceec.Experiment(0, params[0], params[1], params[2])
    simSites = ceec.runCeec(experiment, sites, False)
    return simSites

sites = '../data/cities_weights.csv'
#data = ceec.loadHistoricalSites(sites)
data=0
print "oooooooooooookkkkk"

eps = threshold.LinearEps(5, 25, 5)
print(eps)
##priors:market_size,mu,N,G,step)
priors = sampler.TophatPrior([0,0,100,2,1],[1,.5,800,10,50])

sampler = sampler.Sampler(N=10, Y=data, postfn=postfn, dist=ceec.dist, threads=4)
print "oooooooooooookkkkka"
print priors
print eps

for pool in sampler.sample(priors, eps):
    print "oooooooooooookkkkkb"
    print("DEFUK T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))
    np.savetxt("result_"+str('%.2f')%pool.eps+'.csv', pool.thetas, delimiter=";", fmt='%1.5f')

print(pool.thetas)
np.savetxt("foo.csv", pool.thetas, delimiter=";", fmt='%1.5f')

