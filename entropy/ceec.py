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
    diff= x-y;
    return diff

class Experiment:
    def __init__(self, expId, params,binpath,outpath):

        self.params = params
        self.expId = "_".join([str(int(self.params[indices['ngoods']])),str(int(self.params[indices['nagents']])),str(self.params[indices['market_size']]),str(int(self.params[indices['cstep']])),str(self.params[indices['mu']])])
        self.binpath=binpath
        self.outpath=outpath

        #for key in indices.keys():
        #    print(key, ": ", self.params[indices[key]])
        # priors
        #= alpha
        #self.beta = beta
        #self.harbourBonus = harbourBonus
        #self.weights = weights
        #print("prepare config file folder")

        soup = bs(open(self.binpath+"/config.xml"),'xml') #read a generic config file

        ##change the different value in the XML file with the parameters (thetas) of this experiments ( particle)
        soup.goods['num']=str(int(self.params[indices['ngoods']]))
        soup.numAgents['value']=str(int(self.params[indices['nagents']]))
        soup.market['size']=str(self.params[indices['market_size']])
        soup.culture['step']=str(int(self.params[indices['cstep']]))
        soup.culture['mutation']=str(self.params[indices['mu']])
        soup.numSteps['serializeResolution']=str(int(self.params[indices['cstep']])*3)
        soup.numSteps['value']=str(int(self.params[indices['cstep']])*3*10)
        soup.numSteps['serializeResolution']=soup.numSteps['value']


        #create a directory to run experiment associated to this particle
        self.particleDirectory=os.path.join(self.outpath,self.expId)
        
        #print("num of good=",soup.goods['num'])
        #print("num of ag=",soup.numAgents['value'])
        #print("num of ms=",soup.market['size'])
        #print("num of ms=",soup.culture['step'])
        #print("num of mu=",soup.culture['mutation'])

        #print("config_"+str(self.expId)+".xml")
        if not os.path.isdir(self.particleDirectory):
            os.mkdir(self.particleDirectory) #create folder for the exp
            os.mkdir(os.path.join(self.particleDirectory,"logs"))
            os.mkdir(os.path.join(self.particleDirectory,"data"))
            os.symlink(self.binpath+"/province",self.particleDirectory+ "/province") 
            os.symlink(self.binpath+"/AnalyseTools/analysis",self.particleDirectory+ "/analysis") 
            out=open(self.particleDirectory+"/config.xml","wb")
            out.write(soup.prettify())
            out.close()
        else:
            print ( "particle already tested")  

    def __str__(self):
        result = 'experiment: '+str(self.expId)#+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' harbour bonus: '+str('%.2f')%self.harbourBonus
        return result

def runCeec(experiment, storeResults):
    #print("run pandora")
    bashCommand = 'cd '+experiment.particleDirectory + '&& ./province && ./analysis ' +' && cd --'
    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE,shell=True)
    output, error = process.communicate()
    bashCommand = 'bash ./extractlast.sh '+os.path.join(experiment.particleDirectory,'agents.csv')
    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE,shell=True)
    output, error = process.communicate()
    bashCommand = 'rm -rf '+os.path.join(experiment.particleDirectory,"data") + ' '+os.path.join(experiment.particleDirectory,"logs")+ ' '+os.path.join(experiment.particleDirectory,"*.gdf")
    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE,shell=True)
    #print("pandora run with particule: "+experiment.expId+", done with exit:"+str(error))

    score = 1000
    last_score=output.strip().split("\n")
    try:
        last_score=map(float,last_score)
        score=np.mean(last_score)
    except:
        print("the file agents.csv of the particule:"+experiment.expId+" seems to have a problem ")

    print("Coomputed score mean: "+str(score))
    
 
    return  score
    
