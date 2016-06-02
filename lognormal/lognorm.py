#!/usr/bin/python3

import numpy as np
import csv

def distRelative(x,y):
    # logarithmic to penalize huge sites
    xValues = np.log(x)
    yValues = np.log(y)
 
    diff = np.sum(np.absolute(xValues-yValues))
    print('diff:',diff)
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
    def __init__(self, numRun, alpha, beta, innovationRate,numSites):
        self.numRun = numRun
        # priors

        self.alpha = alpha
        self.beta = beta
        self.innovationRate = innovationRate
        self.numSites = numSites

    def __str__(self):
        result = 'experiment: '+str(self.numRun)+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' innovation rate: '+str('%.2f')%self.innovationRate
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

def updateWeights(weights, strategies):
    result = np.zeros(len(weights))
    for i in range(len(result)):
        growth = np.random.normal(strategies[i], 0.1)
        result[i] = np.exp(np.log(weights[i]) + np.log(1+growth))
    return result

def updateStrategies(strategies, innovationRate):
    result = np.copy(strategies)
    for i in range(len(result)):
        if np.random.uniform(0,1)<innovationRate:
            result[i] = np.random.normal(0,0.1)
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
    steps = 100

    weights = np.zeros([experiment.numSites, steps])
    weights[:,0] = np.full(experiment.numSites, 50)

    strategies = np.zeros([experiment.numSites, steps])
    strategies[:,0] = np.full(experiment.numSites, 0)

    costs = loadCosts('../data/costMatrixSea.csv',experiment.numSites)
    costs = np.exp(-1.0*experiment.beta*costs)

    for i in range(1,steps):
        weights[:,i] = updateWeights(weights[:,i-1], strategies[:,i-1])
        # transmission
        strategies[:,i] = selectStrategies(strategies[:,i-1], costs, weights[:,i], experiment.alpha)
        # innovation in strategies
        strategies[:,i] = updateStrategies(strategies[:,i], experiment.innovationRate)
        strategies[:,i] = strategies[:,i] - np.mean(strategies[:,i])
#        print('step:',i)
    
    if(storeResults):
        output = open('output.csv', 'w')
        output.write('step;site;size\n')

        for i in range(steps):
            for j in range(experiment.numSites):
                output.write(str(i)+';'+str(j)+';'+str(weights[j,i])+'\n')
        output.close()
    
    return weights[:,steps-1]

