#!/usr/bin/python3

import csv, math, sys, argparse, random
import numpy

class Site:

    sites = list()
    cost = {}
    weight = 'prom'

    def __init__(self, ident, size, x, y, weight, isHarbour):
        self.ident = ident
        self.size = size
        self.x = int(x)
        self.y = int(y)
        self.weight = weight
        self.originalWeight = weight
        self.variation = 0
        self.occupations = 0
        self.isHarbour = isHarbour

        self.relativeSizes = None

    def __eq__(self, other):
        return self.ident == other.ident

    def computeFlow(self, sizeFlow, alpha, beta):
        # total flow
        totalFlow = 0
        for siteK in Site.sites:
            codeK = self.ident+'_'+siteK.ident
            totalFlow +=  math.pow(siteK.weight, alpha) * math.exp(-1.0 * beta * Site.cost[codeK])
#        print('total flow from:',self,'is',totalFlow)
        # for each site divide value and add to their variation
        flowToGive = 0
        flowToGive2 = 0
        for site in Site.sites:
            code = self.ident+'_'+site.ident
            flow = self.flow*math.pow(site.weight, alpha) * math.exp(-1.0 * beta * Site.cost[code])
            flow /= totalFlow
            flowToGive += flow
#            print('\tfrom:',self.ident,'to:',site.ident,'with weight:',site.weight,'and dist:',Site.cost[code],'flow:',flow)
            flowToGive2 +=  flow
            site.variation += flow
        # compute total flow
#        print('aggregated flow from:',self,'is var: {0:.5f}'.format(flowToGive),'2: {0:.5f}'.format(flowToGive2))

    def applyVariation(self, changeRate, harbourBonus):
#        print('final variation for',self.ident,'is',self.variation,'current weight:',self.weight)
        oldWeight = self.weight
        realDiff = self.variation-oldWeight
#        if self.isHarbour:
#            self.variation = self.variation + self.variation*harbourBonus
#        else:
#            self.variation = self.variation - self.variation*harbourBonus
        # TODO multiply weight by some K before modifying variation?
        self.weight = self.weight + changeRate*(self.variation - oldWeight)
#        print('old:',oldWeight,'new:',self,'size change:',changeRate*(self.variation - oldWeight),'diff:',realDiff,'variation:',self.variation)
        self.variation = 0
        return abs(changeRate*(self.variation - oldWeight))

    def __str__(self):
        return 'site '+self.ident+' size: '+str(self.size)+' weight: {0:.5f}'.format(self.weight)

class Experiment:

    def __init__(self, numRun, weight, alpha, beta, harbourBonus):
        self.numRun = numRun
        # priors
        self.weight = weight
        self.alpha = alpha 
        self.beta = beta
        self.harbourBonus = harbourBonus

        self.delta = 0.01
        self.changeRate = 0.01
        self.sizeFlow = 1.0

        self.distRelevance = 0.0
        print('weight:',weight,'alpha',alpha,'beta',beta,'coast',harbourBonus)

    def __str__(self):
        result = 'experiment: '+str(self.numRun)+' with weight: '+str(self.weight)+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' coast bonus: '+str('%.2f')%self.harbourBonus+' distance: '+str('%.2f')%self.distRelevance
        return result

def computeRelativeSizes():
    Site.relativeSizes = numpy.full((len(Site.sites), len(Site.sites)), 0, dtype=float)

    for i in range(len(Site.sites)):
        for j in range(i):
            Site.relativeSizes[i][j] = Site.sites[i].size/Site.sites[j].size

def loadSites( inputFileName, weight, harbourBonus ):
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

        isHarbour = False
        isHarbourNum = int(siteLine[7])
        if isHarbourNum!=0:
            isHarbour = True
            weight += harbourBonus*weight
        Site.sites.append(Site(ident, size, x, y, weight, isHarbour))

    computeRelativeSizes()

def loadCosts( distFileName ):
    distFile = open(distFileName, 'r')
    csvReader = csv.reader(distFile, delimiter=';')
    # skip header
    next(csvReader)

    for dist in csvReader:
        code = dist[0]
        cost = float(dist[1])/(3600.0*24.0)
        if cost<1:
            Site.cost[code] = 1
        else:
            Site.cost[code] = math.log(cost)

def adjustFlow():
    totalWeights = 0
    for site in Site.sites:
        totalWeights += site.weight

    for site in Site.sites:
        site.flow = len(Site.sites)*site.weight/totalWeights
#        print('flow from site:',site.ident,'is:',site.flow)

def runEntropy(experiment, costMatrix, sites, storeResults):
    Site.sites = list()
    loadSites(sites, experiment.weight, experiment.harbourBonus)

    print('beginning run with priors', experiment)

    diff = sys.float_info.max
    i = 0
    totalWeight = 0
    for site in Site.sites:
        totalWeight += site.weight

    for site in Site.sites:
        site.weight = site.weight*len(Site.sites)/totalWeight 
        
    while i<1000: 
        adjustFlow()
        for site in Site.sites:
            site.computeFlow(experiment.sizeFlow, experiment.alpha, experiment.beta)
        diff = 0

        for site in Site.sites:
            diff += site.applyVariation(experiment.changeRate, experiment.harbourBonus)
           
#        print('step:',i,'finished, total weight:',totalWeight,'diff:',diff)
#        for site in Site.sites:
#            print(site)
        i += 1
    print('simulation finished with diff;',diff)
   
    relativeWeights = numpy.full((len(Site.sites), len(Site.sites)), 0, dtype=float)
    for i in range(len(Site.sites)):
        for j in range(i):
            relativeWeights[i][j] = Site.sites[i].weight/Site.sites[j].weight

    result = numpy.absolute(Site.relativeSizes-relativeWeights)
   
    numpy.set_printoptions(suppress=True, precision=4, threshold=100000)
    print('results run:',experiment.numRun)


    print('#######REAL########')
    for i in range(0,len(Site.relativeSizes[0])):
            print('row:',i)
            print(Site.relativeSizes[i])

    print('#######SIM########')
    for i in range(0,len(Site.relativeSizes[0])):
            print('row:',i)
            print(relativeWeights[i])
 
    print('#######RESULT########')
    for i in range(0,len(Site.relativeSizes[0])):
            print('row:',i)
            print(result[i])

#    print('\treal:',Site.relativeSizes)
#    print('\tsim:',relativeWeights)
#    print('\tresult:',result)
    print('\tfinal distance:',result.sum())
    print('end results run:', experiment.numRun)
  
    if(storeResults):
        outputFile = open('output.csv','w')
        outputFile.write('id;size;x;y;weight\n')
        for site in Site.sites:
            outputFile.write(site.ident+';'+str(site.size)+';'+str(site.x)+';'+str(site.y)+';'+'%.2f'%site.weight+'\n')
        outputFile.close()
    
    return numpy.absolute(result.sum())
    

