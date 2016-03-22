#!/usr/bin/python3

import entropy
import numpy

def singleRun():

    weightProm = 0.75
    alpha = 1.57
    beta = 0.45
    harbourBonus = 0.68
    cost = entropy.loadCosts('../data/costMatrix.csv')
    sites = '../data/cities_weights.csv'
    data = entropy.loadHistoricalSites(sites)

    experiment = entropy.Experiment(0,weightProm,alpha,beta,harbourBonus)
    result = entropy.runEntropy(experiment, cost, sites, True)   
    
    numTopSites = 25
    listTopSitesHist = entropy.identifyTopSites(data, numTopSites)
    listTopSitesSim = entropy.identifyTopSites(result, numTopSites)

    print('top 25 historical sites:')
    for site in listTopSitesHist:
        print('\t',site.ident)

    print('top 25 identified sim sites:')
    count = 0
    for site in listTopSitesSim:
        if site in listTopSitesHist:
            count += 1
            print('\t',site.ident)
    print('distance:',1-count/numTopSites)

if __name__ == "__main__":
    singleRun()

