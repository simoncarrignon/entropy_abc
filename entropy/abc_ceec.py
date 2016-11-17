#!/usr/bin/python3

import sampler
import threshold
import numpy as np
import ceec 
import os
import sys


if len(sys.argv) < 2:
    print ("usage: ./abc_ceec.py path_to_ceec expe_path")
    exit(0)
elif len(sys.argv) == 2:
    expe_path=os.path.abspath("particle")
else:
    expe_path=os.path.abspath(sys.argv[2])

ceec_path=os.path.abspath(sys.argv[1])
if not os.path.isdir(expe_path):
    os.mkdir(expe_path)



def postfn(params):
    global ceec_path,expe_path
#    print('postfn, params:',params) 
    print ceec_path,expe_path
    experiment = ceec.Experiment(0, params,ceec_path,expe_path)
    simResult = ceec.runCeec(experiment, False)
    return simResult



data=0 #Our idealized input

eps = threshold.LinearEps(5, 25, 5)

##priors:market_size,mu,N,G,step)
priors = sampler.TophatPrior([0,.5,100,2,10],[1,1,101,2.1,10.1])

sampler = sampler.Sampler(N=10, Y=data, postfn=postfn, dist=ceec.dist, threads=4)

for pool in sampler.sample(priors, eps):
    print("T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))
    np.savetxt("result_"+str('%.2f')%pool.eps+'.csv', pool.thetas, delimiter=";", fmt='%1.5f')

print(pool.thetas)
np.savetxt("foo.csv", pool.thetas, delimiter=";", fmt='%1.5f')
