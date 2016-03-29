#!/usr/bin/python3

import csv, math, sys, argparse, random
import numpy
from scipy.stats.stats import pearsonr

def distRelative(x,y):
    if x[0].weight == -1 and y[0].weight == -1:
        return sys.float_info.max

    # take size
    xValues = None
    yValues = None

    # x is data, y is sim
    if x[0].weight == -1:
        xValues = numpy.array([site.size for site in x])
        yValues = numpy.array([site.weight for site in y])
        # normalize
        yValues = (yValues-min(yValues))/(max(yValues)-min(yValues))
        # transform weights to sizes
        yValues = yValues*(max(xValues)-min(xValues))+min(xValues)
       
    # y is data, x is sim
    else:
        yValues = numpy.array([site.size for site in y])
        xValues = numpy.array([site.weight for site in x])
        # normalize
        xValues = (xValues-min(xValues))/(max(xValues)-min(xValues))
        # transform weights to sizes
        xValues = xValues*(max(yValues)-min(yValues))+min(yValues)

    # logarithmic to penalize huge sites
    xValues = numpy.log(xValues)
    yValues = numpy.log(yValues)
 
    diff = 0
    for i in range(len(xValues)):
        diff += abs(xValues[i]-yValues[i])

    print('diff:',diff)
    return diff

class Site:

    sites = list()
    largestSites = list()
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

    def applyVariation(self, changeRate):
        realDiff = self.variation-self.weight
        self.weight = self.weight + changeRate*(self.variation - self.weight)
        self.variation = 0
        return abs(realDiff)

    def __str__(self):
        return 'site '+self.ident+' size: '+str(self.size)+' weight: {0:.5f}'.format(self.weight)

class Experiment:
    def __init__(self, numRun, alpha, beta, harbourBonus):
        self.numRun = numRun
        # priors

        self.alpha = alpha
        self.beta = beta
        self.harbourBonus = harbourBonus

        self.changeRate = 0.1

    def __str__(self):
        result = 'experiment: '+str(self.numRun)+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' harbour bonus: '+str('%.2f')%self.harbourBonus
        return result

def loadHistoricalSites( inputFileName ):
    sites = list()
    inputFile = open(inputFileName, 'r')
    
    csvReader = csv.reader(inputFile, delimiter=',')
    headerLine = next(csvReader)

    for siteLine in csvReader:
        ident = siteLine[0]
        size = float(siteLine[1])
        x = float(siteLine[3])
        y = float(siteLine[4])

        isHarbour = False
        isHarbourNum = int(siteLine[7])
        if isHarbourNum!=0:
            isHarbour = True

        sites.append(Site(ident, size, x, y, -1, isHarbour))
    return sites    
    
def loadSites( inputFileName, harbourBonus):
    inputFile = open(inputFileName, 'r')
    
    # all prom and farming must be between 1 (best value) and 0 (worst value)
    csvReader = csv.reader(inputFile, delimiter=',')
    headerLine = next(csvReader)

    i = 0
    for siteLine in csvReader:
        ident = siteLine[0]
        size = float(siteLine[1])
        x = float(siteLine[3])
        y = float(siteLine[4])
        weight = random.randint(1,100)
        i += 1

        isHarbour = False
        isHarbourNum = int(siteLine[7])
        if isHarbourNum!=0:
            isHarbour = True
            weight += weight*harbourBonus
        Site.sites.append(Site(ident, size, x, y, weight, isHarbour))

def loadLandCostsInMeters( distFileName):
    distFile = open(distFileName, 'r')
    csvReader = csv.reader(distFile, delimiter=';')
    # skip header
    next(csvReader)

    for dist in csvReader:
        code = dist[0]
        cost = float(dist[1])/(3600.0*24.0)
        Site.cost[code] = cost

def loadCosts( distFileName):
    distFile = open(distFileName, 'r')
    csvReader = csv.reader(distFile, delimiter=';')
    # skip header
    next(csvReader)

    for dist in csvReader:
        code = dist[0]
        cost = float(dist[1])
        Site.cost[code] = cost

def computeBetaCosts(beta):
    for code,cost in Site.cost.items():
        Site.weightedCost[code] = math.exp(-1.0*beta*cost)

def computeAlphaWeights(alpha):
    for site in Site.sites:
        site.weightAlpha = math.pow(site.weight, alpha)
    
def runEntropy(experiment, sites, storeResults):
    Site.sites = list()
    loadSites(sites, experiment.harbourBonus)

    # if any value is negative in particle then return max dist
    if experiment.alpha < 0 or experiment.beta < 0:
        print('returning 1 because:',experiment.alpha, experiment.beta)
        for site in Site.sites:
            site.weight = -1
        return Site.sites

    computeBetaCosts(experiment.beta)

#    print('beginning run with priors', experiment)

    i = 0

    maxIter = 5000
    maxIterOut = 10
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
            aggregatedDiff += site.applyVariation(experiment.changeRate)

        test = aggregatedDiff/aggregatedFlow

#        print('step:',i,'iter2:',iterOut,'finished, flow:',aggregatedFlow,'diff:',aggregatedDiff,'test:',test)
        i += 1
  
#    result = 1-countNumLargestSites()/len(Site.largestSites)

    print('simulation finished after:',i,'steps') # with result:',result)

    if(storeResults):
        outputFile = open('output.csv','w')
        outputFile.write('id;size;x;y;weight\n')
        for site in Site.sites:
            outputFile.write(site.ident+';'+str(site.size)+';'+str(site.x)+';'+str(site.y)+';'+'%.2f'%site.weight+'\n')
        outputFile.close()
 
    return Site.sites 
    
