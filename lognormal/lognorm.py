#!/usr/bin/python3

import numpy as np
import csv

def distAbs(x,y):  
    maxValues = np.maximum(x,y)
    minValues = np.minimum(x,y)
    diff = np.sum(maxValues-minValues)
    print('diff abs:',diff)
    return diff

def distLog(x,y):
    # logarithmic to penalize huge sites
    diff = np.sum(np.absolute(np.log(x)-np.log(y)))
    print('diff log:',diff)
    return diff

def distPerc(x,y):
    maxValues = np.maximum(x,y)
    minValues = np.minimum(x,y)
    diff = np.sum(maxValues/minValues)
    print('diff perc:',diff)
    return diff

def loadHistoricalSites( inputFileName, numSites ):
    sites = np.empty([numSites])
    inputFile = open(inputFileName, 'r')
    
    csvReader = csv.reader(inputFile, delimiter=',')
    headerLine = next(csvReader)

    for siteLine in csvReader:
        ident = int(siteLine[0])
        size = float(siteLine[1])
        sites[ident-1] = size
    return sites    

class Experiment:
    def __init__(self, alpha, beta, meanlog, sdlog, numSites, costs, maxObservedSize):
        # priors

        self.alpha = alpha
        self.beta = beta
        self.meanlog = meanlog
        self.sdlog = sdlog

        self.numSites = numSites
        self.costs = costs
        self.maxObservedSize = maxObservedSize

    def __str__(self):
        result = 'experiment - alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta
        return result

def loadCosts( distFileName, numSites):
    costs = np.empty([numSites,numSites])
    distFile = open(distFileName, 'r')
    csvReader = csv.reader(distFile, delimiter=';')
    # skip header
    next(csvReader)

    for dist in csvReader:
        code = dist[0].split('_')
        cost = float(dist[1])
        costs[int(code[0])-1,int(code[1])-1] = cost
    return costs           


def applyUpdate(weights, costs, alpha, meanlog, sdlog):
#    newWeights = np.copy(weights)
    newWeights = np.exp(np.log(weights) + np.log(1+np.random.normal(meanlog, sdlog, len(weights))))
    # entropy method
    result = 0.9*np.copy(newWeights)
    poweredWeights = np.power(newWeights,alpha)

#    print('old sum:',np.sum(weights),'weights:',weights)
#    print('new sum:',np.sum(newWeights),'newWeights:',newWeights)

    for i in range(len(result)):   
        finalCosts = poweredWeights*costs[i]
        finalCosts = 0.1*newWeights[i]*finalCosts/np.sum(finalCosts)
#        print('i:',i,'sum:',np.sum(finalCosts),'finalCosts:',finalCosts)
        result += finalCosts 

#    print('final sum:',np.sum(result),'result:',result)
    return result
    
def updateWeights(weights, strategies):
    result = np.exp(np.log(weights) + np.log(1+np.random.normal(strategies,0.1)))
#    print('update weight:',result)
    return result               

def updateStrategies(strategies, innovationRate):
    result = np.copy(strategies)
    for i in range(len(result)):
        if np.random.uniform(0,1)<innovationRate:
            newStrategy = np.random.normal(0,0.1)
            if newStrategy > result[i]:
                result[i] = newStrategy
#            print('innovation!')
    return result

def selectStrategies(strategies, costs, weights, alpha):
    result = np.copy(strategies)
    poweredWeights = np.power(weights,alpha)
    # it should be linked to communication cost
    for i in range(len(result)):
        finalCosts = poweredWeights*costs[i]
        finalCosts = finalCosts/np.sum(finalCosts)
        strategyToCopy = np.random.choice(strategies, p=finalCosts)
        if strategyToCopy > strategies[i]:
            result[i] = strategyToCopy 
    return result

def run(experiment, storeResults):
    maxSteps = 1000

    weights = np.empty([experiment.numSites, maxSteps])
    weights[:,0] = np.full(experiment.numSites, 1)

    costs = np.exp(-1.0*experiment.beta*experiment.costs)

    maxSize = 1
    i = 1

    while maxSize<experiment.maxObservedSize and i<maxSteps:
        weights[:,i] = applyUpdate(weights[:,i-1], costs, experiment.alpha, experiment.meanlog, experiment.sdlog)
        maxSize = np.amax(weights[:,i])
#        print('step:',i,'max size:',maxSize)
        i += 1
    
    if(storeResults):
        output = open('output.csv', 'w')
        output.write('step;site;size\n')

        for z in range(i):
            for j in range(experiment.numSites):
                output.write(str(z)+';'+str(j)+';'+str(weights[j,z])+'\n')
        output.close()
    
    return weights[:,i-1]

