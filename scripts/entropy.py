#!/usr/bin/python3

import csv, math, sys, argparse, random
import numpy

class Site:

    sites = list()
    cost = {}
    weightedCost = {}

    def __init__(self, ident, size, x, y, weight, isHarbour):
        self.ident = ident
        self.size = size
        self.x = int(x)
        self.y = int(y)
        self.weight = weight
        self.weightAlpha = 0
        self.variation = 0
        self.isHarbour = isHarbour

        self.relativeSizes = None

    def __eq__(self, other):
        return self.ident == other.ident

    def computeFlow(self):
        # total flow
        totalFlow = 0
        for siteK in Site.sites:
            if siteK.ident==self.ident:
                continue
            codeK = self.ident+'_'+siteK.ident
            totalFlow +=  siteK.weightAlpha * Site.weightedCost[codeK]
        # for each site divide value and add to their variation
        flowToGive = 0
        for site in Site.sites:
            if site.ident==self.ident:
                continue
            code = self.ident+'_'+site.ident
            flow = self.weight*site.weightAlpha * Site.weightedCost[code]
            flow /= totalFlow
            flowToGive += flow
            site.variation += flow
        return flowToGive            

    def applyVariation(self, changeRate, harbourBonus):
        realDiff = self.variation-self.weight
        self.weight = self.weight + changeRate*(self.variation - self.weight)
        self.variation = 0
        return abs(realDiff)

    def __str__(self):
        return 'site '+self.ident+' size: '+str(self.size)+' weight: {0:.5f}'.format(self.weight)

class Experiment:

    def __init__(self, numRun, weightProm, weightFarming, alpha, beta, harbourBonus):
        self.numRun = numRun
        # priors
        # sum of weights must be equal to 1
        self.weightProm = weightProm/(weightProm+weightFarming)
        self.weightFarming = weightFarming/(weightProm+weightFarming)

        self.alpha = alpha 
        self.beta = beta
        self.harbourBonus = harbourBonus

        self.changeRate = 0.01
        self.distRelevance = 0

    def __str__(self):
        result = 'experiment: '+str(self.numRun)+' with weightProm: '+str(self.weightProm)+' and weightFarming: '+str(self.weightFarming)+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' coast bonus: '+str('%.2f')%self.harbourBonus+' dist:'+str('%.2f')%self.distRelevance
        return result

def computeRelativeSizes():
    Site.relativeSizes = numpy.full((len(Site.sites), len(Site.sites)), 0, dtype=float)

    for i in range(len(Site.sites)):
        for j in range(i):
            Site.relativeSizes[i][j] = Site.sites[i].size/Site.sites[j].size

def loadSites( inputFileName, weightProm, weightFarming, harbourBonus ):
    inputFile = open(inputFileName, 'r')
    
    # all prom and farming must be between 1 (best value) and 0 (worst value)
    csvReader = csv.reader(inputFile, delimiter=',')
    headerLine = next(csvReader)

    minFarming = sys.float_info.max
    maxFarming = sys.float_info.min
    minProm = sys.float_info.max
    maxProm = sys.float_info.min

    for siteLine in csvReader:
        prom = float(siteLine[5])
        if prom<minProm:
            minProm = prom
        elif prom>maxProm:
            maxProm = prom

        farming = float(siteLine[6])
        if farming<minFarming:
            minFarming = farming
        elif farming>maxFarming:
            maxFarming = farming

    inputFile.close()            
    inputFile = open(inputFileName, 'r')

    csvReader = csv.reader(inputFile, delimiter=',')
    headerLine = next(csvReader)
    for siteLine in csvReader:
        ident = siteLine[0]
        size = float(siteLine[1])
        x = float(siteLine[3])
        y = float(siteLine[4])
        prom = (float(siteLine[5])-minProm)/(maxProm-minProm)
        farming = (float(siteLine[6])-minFarming)/(maxFarming-minFarming)
        # weights between 101 and 1
        weight = 1+100*(prom*weightProm+farming*weightFarming)

        isHarbour = False
        isHarbourNum = int(siteLine[7])
        if isHarbourNum!=0:
            isHarbour = True
            weight += harbourBonus*weight
        Site.sites.append(Site(ident, size, x, y, weight, isHarbour))

    computeRelativeSizes()

def loadCosts( distFileName):
    distFile = open(distFileName, 'r')
    csvReader = csv.reader(distFile, delimiter=';')
    # skip header
    next(csvReader)

    for dist in csvReader:
        code = dist[0]
        cost = float(dist[1])/(3600.0*24.0)
        Site.cost[code] = cost

def computeBetaCosts(beta):
    for code,cost in Site.cost.items():
        Site.weightedCost[code] = math.exp(-1.0*beta*cost)

def computeAlphaWeights(alpha):
    for site in Site.sites:
        site.weightAlpha = math.pow(site.weight, alpha)
    
def runEntropy(experiment, costMatrix, sites, storeResults):
    Site.sites = list()
    loadSites(sites, experiment.weightProm, experiment.weightFarming, experiment.harbourBonus)
    computeBetaCosts(experiment.beta)

    print('beginning run with priors', experiment)

    i = 0
    relativeWeights = numpy.full((len(Site.sites), len(Site.sites)), 0, dtype=float)

    maxIter = 5000
    maxIterOut = 100
    iterOut = 0
    tolerance = 0.1
    test = tolerance

    while i<maxIter and iterOut<maxIterOut: 
        if test>tolerance:
            iterOut = 0
        else:
            iterOut += 1

        computeAlphaWeights(experiment.alpha)            

        aggregatedFlow = 0
        for site in Site.sites:
            aggregatedFlow += site.computeFlow()
        aggregatedDiff = 0
        for site in Site.sites:
            aggregatedDiff += site.applyVariation(experiment.changeRate, experiment.harbourBonus)

        test = aggregatedDiff/aggregatedFlow

#        print('step:',i,'iter2:',iterOut,'finished, flow:',aggregatedFlow,'diff:',aggregatedDiff,'test:',test)
        i += 1
  
    for z in range(len(Site.sites)):
        for j in range(z):
            relativeWeights[z][j] = Site.sites[z].weight/Site.sites[j].weight
            
    result = numpy.absolute(Site.relativeSizes-relativeWeights)
    diff = result.sum()
    print('simulation finished after:',i,'steps with distance:',diff)

    if(storeResults):
        outputFile = open('output.csv','w')
        outputFile.write('id;size;x;y;weight\n')
        for site in Site.sites:
            outputFile.write(site.ident+';'+str(site.size)+';'+str(site.x)+';'+str(site.y)+';'+'%.2f'%site.weight+'\n')
        outputFile.close()
 
    return diff
    
