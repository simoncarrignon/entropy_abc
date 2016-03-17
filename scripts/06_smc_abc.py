#!/usr/bin/python3

import random
import multiprocessing as mp
import os
import entropy
import argparse
import math
import time
import sys

class Prior:
    def __init__(self, weightProm, weightFarming, alpha, beta, harbourBonus): 
        self.weightProm = weightProm
        self.weightFarming = weightFarming

        self.alpha = alpha
        self.beta = beta

        self.harbourBonus = harbourBonus

    def sampleWeightProm(self):
        return random.uniform(self.weightProm[0], self.weightProm[1])

    def sampleWeightFarming(self):
        return random.uniform(self.weightFarming[0], self.weightFarming[1])

    def sampleAlpha(self):
        return random.uniform(self.alpha[0], self.alpha[1])

    def sampleBeta(self):
        return random.uniform(self.beta[0], self.beta[1])

    def sampleHarbourBonus(self):
        return random.uniform(self.harbourBonus[0], self.harbourBonus[1])

"""
def abcPar(q, numCpu, prior, runs, bestRuns, sites, costMatrix):
    resolution = 1
    results = list()
    logFile = open('log_'+str(numCpu),'w')
    logFile.write('logs for thread: '+str(numCpu)+'\n')
    logFile.close()
    
    initTime = time.time()

    for i in range(runs[0],runs[1]):
        experiment = entropy.Experiment(i,prior.sampleWeightProm(), prior.sampleWeightFarming(), prior.sampleAlpha(), prior.sampleBeta(), prior.sampleCoastBonus())
        experiment.distRelevance = entropy.runEntropy(experiment, costMatrix, sites, False)
        if i%resolution== 0:
            logFile = open('log_'+str(numCpu),'a')
            logFile.write('thread: '+str(numCpu)+' time: '+str('%.2f'%(time.time()-initTime))+'s. run: '+str(i-runs[0])+'/'+str(runs[1]-runs[0])+' - '+str(experiment)+'\n')
            logFile.close()

        # if results list not full
        if len(results)<bestRuns:
            results.append(experiment)
            results = sorted(results, key = lambda experiment : experiment.distRelevance)
            continue
        # if dist < worse result then change and sort again
        if result.distRelevance < results[-1].distRelevance:
            results[-1] = result
            results = sorted(results, key = lambda experiment : experiment.distRelevance)

    results = sorted(results, key = lambda experiment : experiment.distRelevance)
    q.put(results)
"""

def getNextValues(t, prior, prevPops):

    pop = {}

    # PRC2.1
    # first time, sample theta_** from priors
    if t==0:
        pop['weightProm'] = prior.sampleWeightProm()
        pop['weightFarming'] = prior.sampleWeightFarming()
        pop['alpha'] = prior.sampleAlpha()
        pop['beta'] = prior.sampleBeta()
        pop['harbourBonus'] = prior.sampleHarbourBonus()
    else:
        pop = random.choice(prevPops).copy()
        # apply a markov transition kernel

    return pop

def runSMC_ABC(prior, sites, cost, runs, tolerances):

    costMatrix = entropy.loadCosts(cost)
    
#    bestRuns = int(runs*tolerance)

#    numCpus = mp.cpu_count()
#    numCpus = 1
#    runsPerCpu = math.ceil(runs/numCpus)
#    bestRunsCpu = math.ceil(runs*tolerance)

#    print('selecting: ',bestRuns,'from:',runs,'with tolerance:',tolerance,'cpus:',numCpus,'best runs/cpu',bestRunsCpu,'num runs/cpu:',runsPerCpu)

    # tolerances Et can be computed from the number of thresholds and the target (i.e. 10 levels, Et10 = 80.000, and Et=1/2(3*Et-1 - Et10))
    print('executing sequential ABC with tolerances:',tolerances)

    results = list()
    prevPops = list()

    # PRC1 - set populator indicator to 0
    t = 0
    # PRC2 - set particle indicator to 0
    i = 0
    
    distance = sys.float_info.max
    while distance>tolerances[t]:
        print('nope:',distance)
        pop = getNextValues(t, prior, prevPops)
        experiment = entropy.Experiment(i,pop['weightProm'], pop['weightFarming'], pop['alpha'], pop['beta'], pop['harbourBonus'])
        distance = entropy.runEntropy(experiment, costMatrix, sites, False)
    print('oeoe')

            


        
        # sample from previous pop
        # perturb particle to new values using Kt
        # generate new dataset using these new values
        # if dist is more than tolerance_t, then go to PRC2.1 again
        

    """
    procs = list()
    q = mp.Queue()

    runs = [0,runsPerCpu]
    for i in range(numCpus):
        p = mp.Process(target=abcPar, args=(q,i, prior, runs, bestRunsCpu,sites, costMatrix))
        p.start()
        print('starting thread:',i,'runs:',runs)
        runs[0] = runs[1]
        runs[1] = runs[0]+runsPerCpu
        if i==(numCpus-1):
            runs[1] =runs 
        procs.append(p)

    for i in range(numCpus):
        results.extend(q.get())

    for p in procs:
        p.join()
    for p in procs:
        p.terminate() 
    """

    return results

def storeResults(results, outputFile):
    # reorder results for each thread
    results = sorted(results, key = lambda experiment : experiment.distRelevance)
    output = open(outputFile, 'w')

    output.write('run;weightProm;weightFarming;alpha;beta;harbourBonus;dist\n')
    for result in results:
        output.write(str(result.numRun)+';'+str('%.2f')%result.weightProm+';'+str('%.2f')%result.weightFarming+';'+str('%.2f')%result.alpha+';'+str('%.2f')%result.beta+';'+str('%.2f')%result.harbourBonus+';'+str('%.2f')%result.distRelevance+'\n')
    output.close()

def runExperiment(priorWeightProm, priorWeightFarming, priorAlpha, priorBeta, priorCoastBonus, sites, cost, output, runs, tolerances):
    prior = Prior(priorWeightProm, priorWeightFarming, priorAlpha, priorBeta, priorCoastBonus)
    results = runSMC_ABC(prior, sites, cost, runs, tolerances)
    storeResults(results,output)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--sites", help="sites file", default='../data/cities_weights.csv')
    parser.add_argument("-c", "--cost", help="cost matrix file", default='../data/costMatrix.csv')
    parser.add_argument("-o", "--output", help="CSV file to store output", default='asia_minor')
    parser.add_argument("-r", "--runs", help="number of runs", type=int, default=1000)
    parser.add_argument("-t", "--tolerances", help="tolerance level list", type=str, default="200000 100000 80000")
    args = parser.parse_args()

    tolerancesList = [float(item) for item in args.tolerances.split(' ')]
    runExperiment([0,1],[0,1],[0,2],[0,2],[0,2], args.sites, args.cost, args.output+'.csv', args.runs, tolerancesList)

if __name__ == "__main__":
    main()

