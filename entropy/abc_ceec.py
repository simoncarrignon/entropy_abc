#!/usr/bin/python3

import sampler
import threshold
import numpy as np
import ceec 
import os
import sys
import logging,operator


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
    #print('postfn, params:',params) 
    experiment = ceec.Experiment(0, params,ceec_path,expe_path)
    simResult = ceec.runCeec(experiment, False)
    return simResult

logging.basicConfig(filename=os.path.join(expe_path,'ceec_abc.log'),level=logging.INFO,filemode="w")


data=0 #Our idealized input

#eps = threshold.ExponentialConstEps(.3, .01,5,5)
eps = threshold.ExponentialEps(2,3000,.25)

##priors:market_size,mu,N,G,step)
#priors = sampler.TophatPrior([0,0,5,2,10],[1,1,200,6,30])
priors = sampler.TophatPrior([0],[1])
 
sampler = sampler.Sampler(N=201, Y=data, postfn=postfn, dist=ceec.dist, threads=4)

for pool in sampler.sample(priors, eps):
    print("T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))
    print(ceec.indices.keys())
    print(sorted(ceec.indices.items(),key=operator.itemgetter(1)))
    s=(sorted(ceec.indices.items(),key=operator.itemgetter(1)))
    slsit=[v[0] for e,v in enumerate(s)]
    print(slsit)
    np.savetxt(os.path.join(expe_path,"result_"+str('%.2f')%pool.eps+'.csv'), pool.thetas, delimiter=",", header=",".join(slsit),fmt='%1.5f',comments="")


print(pool.thetas)
#np.savetxt("foo.csv", pool.thetas, delimiter=";", fmt='%1.5f')



