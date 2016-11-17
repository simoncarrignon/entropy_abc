#!/usr/bin/python3

import csv, math, sys, argparse, random,os,errno
from bs4 import BeautifulSoup as bs
import numpy as np
import subprocess

#index of the different parameters
indices= {  "mu"            : 0, 
            "market_size"   : 1,
            "nagents"       : 2,
            "ngoods"        : 3,
            "cstep"         : 4}

def dist(x,y):
    print("reading pandora/ceec result and checkl if the score mean is close to 0")
    diff= 0;
    return diff

class Experiment:
    def __init__(self, expId, params,binpath,outpath):

        self.params = params
        self.expId = "_".join([str(int(self.params[indices['ngoods']])),str(int(self.params[indices['nagents']])),str(self.params[indices['market_size']]),str(int(self.params[indices['cstep']])),str(self.params[indices['mu']])])
        self.binpath=binpath
        self.outpath=outpath

        for key in indices.keys():
            print(key, ": ", self.params[indices[key]])
        # priors
        #= alpha
        #self.beta = beta
        #self.harbourBonus = harbourBonus
        #self.weights = weights
        print("create new config file")

        soup = bs(open(self.binpath+"/config.xml"),'xml') #read a generic config file

        ##change the different value in the XML file with the parameters (thetas) of this experiments ( particle)
        soup.goods['num']=str(int(self.params[indices['ngoods']]))
        soup.numAgents['value']=str(int(self.params[indices['nagents']]))
        soup.market['size']=str(self.params[indices['market_size']])
        soup.culture['step']=str(int(self.params[indices['cstep']]))
        soup.culture['mutation']=str(self.params[indices['mu']])
        soup.numSteps['serializeResolution']=str(int(self.params[indices['cstep']])*3)


        #create a directory to run experiment associated to this particle
        self.particleDirectory=os.path.join(self.outpath,self.expId)
        
        #print("num of good=",soup.goods['num'])
        #print("num of ag=",soup.numAgents['value'])
        #print("num of ms=",soup.market['size'])
        #print("num of ms=",soup.culture['step'])
        #print("num of mu=",soup.culture['mutation'])
        print("create:"+self.particleDirectory)
        #print("config_"+str(self.expId)+".xml")
        if not os.path.isdir(self.particleDirectory):
            os.mkdir(self.particleDirectory) #create folder for the exp
            os.mkdir(os.path.join(self.particleDirectory,"logs"))
            os.mkdir(os.path.join(self.particleDirectory,"data"))
            os.symlink(self.binpath+"/province",self.particleDirectory+ "/province") 
            out=open(self.particleDirectory+"/config.xml","wb")
            out.write(soup.prettify())
            out.close()
        else:
            print ( "particle already tested")  

    def __str__(self):
        result = 'experiment: '+str(self.expId)#+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' harbour bonus: '+str('%.2f')%self.harbourBonus
        return result

def runCeec(experiment, storeResults):
    print("run pandora")
    print("wait till this experiment finish")
    bashCommand = 'echo "boo"> uu.txt'
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("Coomputed score mean",error,output)
    subprocess.call('date')
    
    score = np.random.random_integers(10)
 
    return  score
    
