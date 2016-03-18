#!/usr/bin/python3

import entropy
import numpy

def singleRun():

    weightProm = 0.86
    weightFarming = 0.14
    alpha = 0.92
    beta = 0.01
    harbourBonus = 1.72
    cost = entropy.loadCosts('../data/costMatrix.csv')
    sites = '../data/cities_weights.csv'

    experiment = entropy.Experiment(0,weightProm,weightFarming,alpha,beta,harbourBonus)
    result = entropy.runEntropy(experiment, cost, sites, True)
    print('result:',result)

if __name__ == "__main__":
    singleRun()

