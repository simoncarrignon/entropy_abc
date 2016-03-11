#!/usr/bin/python3

import entropy

def singleRun():

    weight = 'farming'
    alpha = 1
    beta = 0
    coastBonus = 0.0
    cost = entropy.loadCosts('../data/costMatrix.csv')
    sites = '../data/cities_weights.csv'

    experiment = entropy.Experiment(0,weight,alpha,beta,coastBonus)
    entropy.runEntropy(experiment, cost, sites)

if __name__ == "__main__":
    singleRun()

