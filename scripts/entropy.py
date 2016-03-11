#!/usr/bin/python3

import csv, math, sys, argparse, random
import numpy

class Site:

    sites = list()
    cost = {}
    weight = 'prom'

    def __init__(self, ident, size, x, y, weight):
        self.ident = ident
        self.size = size
        self.x = x
        self.y = y
        self.weight = weight
        self.originalWeight = weight
        self.variation = 0
        self.occupations = 0

        self.relativeSizes = None

    def __eq__(self, other):
        return self.ident == other.ident

    def computeFlow(self, sizeFlow, alpha, beta):
        print('computing flow from:',self)
        for site in Site.sites:
            code = self.ident+'_'+site.ident
            print('\tfrom:',self,'to',site,'dist:',Site.cost[code])
            flow = sizeFlow * math.pow(site.weight, alpha) * math.exp(-1.0 * beta * Site.cost[code])
            totalFlow = 0
            for siteK in Site.sites:
                codeK = self.ident+'_'+siteK.ident
                totalFlow +=  math.pow(siteK.weight, alpha) * math.exp(-1.0 * beta * Site.cost[codeK])
            print('\tfrom:',site,'flow:',flow,'total:',totalFlow)
            flow = flow/totalFlow
            self.variation -= flow
            site.variation += flow
        print('aggregated flow from:',self,'var: {0:.5f}'.format(self.variation))

    def applyVariation(self, changeRate): 
        oldWeight = self.weight
        self.weight = self.weight + changeRate*(self.variation - self.weight)
        self.variation = 0
        print('old:',oldWeight,'new:',self,'diff:',abs(self.weight-oldWeight))
        return abs(self.weight-oldWeight)

    def __str__(self):
        return 'site '+self.ident+' size: '+str(self.size)+' pos: '+str(self.x)+'/'+str(self.y)+' weight: {0:.5f}'.format(self.weight)

class Experiment:

    def __init__(self, numRun, weight, alpha, beta, coastBonus):
        self.numRun = numRun
        # priors
        self.weight = weight
        self.alpha = alpha 
        self.beta = beta
        self.coastBonus = coastBonus

        self.delta = 100.0
        self.changeRate = 0.1
        self.sizeFlow = 1.0

        self.distRelevance = 0.0
        print('weight:',weight,'alpha',alpha,'beta',beta,'coast',coastBonus)

    def __str__(self):
        result = 'experiment: '+str(self.numRun)+' with weight: '+str(self.weight)+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' coast bonus: '+str('%.2f')%self.coastBonus+' distance: '+str('%.2f')%self.distRelevance
        return result

def computeRelativeSizes():
    Site.relativeSizes = numpy.full((len(Site.sites), len(Site.sites)), 0, dtype=float)

    for i in range(len(Site.sites)):
        for j in range(i):
            Site.relativeSizes[i][j] = Site.sites[i].size/Site.sites[j].size

def loadSites( inputFileName, weight ):
    inputFile = open(inputFileName, 'r')
    csvReader = csv.reader(inputFile, delimiter=',')

    headerLine = next(csvReader)

    index = 0
    for column in headerLine:
        if column==weight:
            break
        index += 1
    if index==len(headerLine):
        print('error, weight column:',weight,'not found')
        return

    for siteLine in csvReader:
        ident = siteLine[0]
        size = float(siteLine[1])
        x = float(siteLine[3])
        y = float(siteLine[4])
        weight = float(siteLine[index])
        Site.sites.append(Site(ident, size, x, y, weight))

    computeRelativeSizes()

def loadCosts( distFileName ):
    distFile = open(distFileName, 'r')
    csvReader = csv.reader(distFile, delimiter=';')
    # skip header
    next(csvReader)

    for dist in csvReader:
        code = dist[0]
        cost = float(dist[1])
        # from seconds to days
        Site.cost[code] = cost/(3600.0*24.0)

def runEntropy(experiment, costMatrix, sites):
    Site.sites = list()
    loadSites(sites, experiment.weight)

    print('beginning run with priors', experiment)
    diff = sys.float_info.max
    i = 0
    while diff > experiment.delta:
        print('step:',i,'last diff:',diff)
        for site in Site.sites:
            site.computeFlow(experiment.sizeFlow, experiment.alpha, experiment.beta)
        diff = 0
        for site in Site.sites:
            diff += site.applyVariation(experiment.changeRate)
        i += 1
    print('simulation finished with diff;',diff)
   
    relativeWeights = numpy.full((len(Site.sites), len(Site.sites)), 0, dtype=float)
    for i in range(len(Site.sites)):
        for j in range(i):
            relativeWeights[i][j] = Site.sites[i].weight/Site.sites[j].weight

    result = Site.relativeSizes-relativeWeights            
   
    """
    numpy.set_printoptions(suppress=True, precision=2)            
    outputFile = open('output.csv','w')
    outputFile.write('id;size;x;y;weight\n')
    for site in Site.sites:
        outputFile.write(site.ident+';'+str(site.size)+';'+str(site.x)+';'+str(site.y)+';'+'%.2f'%site.weight+'\n')
    outputFile.close()
    """
    return numpy.absolute(result.sum())
    

