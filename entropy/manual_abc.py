#!/usr/bin/python3

import csv, math, sys, argparse, random,os,errno
from bs4 import BeautifulSoup as bs
import numpy as np
import multiprocessing as mp
import logging
import time

#index of the different parameters
#indices= {  "mu"            : 0, 
#            "market_size"   : 1,
#            "nag_good"       : 2,
#            "ngoods"        : 3,
#            "cstep"         : 4}

indices= {  "mu"            : 0, 
            "nstep"        : 1,
            "cstep"         : 2}

##Compute the distance from the exp to the real data
def dist(x,y):
    diff= x-y;
    return diff

##Check consistency of paramter
##generate the folders and files for the xp
class Experiment: 
    def __init__(self, expId, params,binpath,outpath):
        self.consistence=True
        self.params = params
        #self.expId = "_".join([str(int(self.params[indices['ngoods']])),str(int(self.params[indices['nag_good']])),str(self.params[indices['market_size']]),str(int(self.params[indices['cstep']])),str(self.params[indices['mu']])])
        self.expId = "_".join([str(int(self.params[indices['cstep']])),str(self.params[indices['mu']])])
        self.binpath=binpath #binpath is the path where the executable & generic config ifle are stored 
        self.outpath=outpath
        #for key in indices.keys():
        #    print(key, ": ", self.params[indices[key]])
        # priors
        #print("prepare config file folder")

        if((int(self.params[indices['cstep']]) < 1 ) or  #No experiments if no cultural step
           #(int(self.params[indices['nag_good']]) < 1) or  #if num <2 
           #(int(self.params[indices['ngoods']]) < 2 ) or #No exchange possible if we don't have at least 2 goods
           (self.params[indices['mu']] <= 0 ) or #No meaning if mutation rate <0 or >1
           (self.params[indices['mu']] > 1 ) #or 
           #(self.params[indices['market_size']] > 1 ) or  #no need to explore more than 100% of the market
           #(self.params[indices['market_size']] <= 0 ) #agent has to visit the market to exchange stuff
          ):
            #print("baddd",params)
            self.consistence=False

        soup = bs(open(self.binpath+"/config.xml"),'xml') #read a generic config file ##need lxml installed
        
        print(params) 


        ##change the different value in the XML file with the parameters (thetas) of this experiments (particle)

        #soup.goods['num']=str(int(self.params[indices['ngoods']]))
        #soup.numAgents['value']=str(int(self.params[indices['ngoods']])*int(self.params[indices['nag_good']]))
        #soup.market['size']=str(self.params[indices['market_size']])
        soup.culture['step']=str(int(self.params[indices['cstep']]))
        soup.culture['mutation']=str(self.params[indices['mu']])
        soup.numSteps['serializeResolution']=str(int(self.params[indices['cstep']])*3)
        soup.numSteps['value']=200
        #soup.numSteps['value']=str(int(self.params[indices['cstep']])*3*100)
        soup.numSteps['serializeResolution']=soup.numSteps['value']


        #create a directory to run experiment associated to this particle
        self.particleDirectory=os.path.join(self.outpath,self.expId)
        
        #print("num of good=",soup.goods['num'])
        #print("num of ag=",soup.numAgents['value'])
        #print("num of ms=",soup.market['size'])
        #print("num of ms=",soup.culture['step'])
        #print("num of mu=",soup.culture['mutation'])

        #print("config_"+str(self.expId)+".xml")
        if (not os.path.isdir(self.particleDirectory)) and self.consistence:
            os.mkdir(self.particleDirectory) #create folder for the exp
            os.mkdir(os.path.join(self.particleDirectory,"logs"))
            os.mkdir(os.path.join(self.particleDirectory,"data"))
            os.symlink(self.binpath+"/province",self.particleDirectory+ "/province") 
            os.symlink(self.binpath+"/AnalyseTools/analysis",self.particleDirectory+ "/analysis") 

            with open(self.particleDirectory+"/config.xml","a") as out:
                out.write(soup.prettify())
                out.close()
        else:
            if (os.path.isdir(self.particleDirectory)):  
                logging.warning( "particle already tested")  
            else:
                logging.warning( "unconsistent particle")  
            self.consistence=False

    def id(self):
        return(self.expId)

    def getScore(self,qscore):
        file_score=os.path.join(self.particleDirectory,"score.txt")
        while not os.path.exists(file_score):
                time.sleep(1)
                if os.path.isfile(file_score):
                    with open(file_score,"r") as score:
                        last_score=score.readline().strip()
                        qscore[self.expId]=last_score
                    print(last_score)
        return(int(last_score))

    def __str__(self):
        result = 'experiment: '+str(self.expId)#+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' harbour bonus: '+str('%.2f')%self.harbourBonus
        return result

    def generateTask(experiment, storeResults):
            #print("run pandora")
            bashCommand = 'cd '+experiment.particleDirectory + ' && ./province && ./analysis ' +' && cd -- \n'
            #output, error = process.communicate()
            bashCommand += 'bash ./extractlast.sh '+os.path.join(experiment.particleDirectory,'agents.csv \n')
            #output, error = process.communicate()
            bashCommand += 'rm -rf '+os.path.join(experiment.particleDirectory,"data") + ' '+os.path.join(experiment.particleDirectory,"logs")+ ' '+os.path.join(experiment.particleDirectory,"*.gdf \n")
        return bashCommand
        
    
class TophatPrior(object):
    """
    Tophat prior
    
    :param min: scalar or array of min values
    :param max: scalar or array of max values
    """
    
    def __init__(self, min, max):
        self.min = np.atleast_1d(min)
        self.max = np.atleast_1d(max)
        self._random = np.random.mtrand.RandomState()
        assert self.min.shape == self.max.shape
        assert np.all(self.min < self.max)
        
    def __call__(self, theta=None):
        if theta is None:
            return np.array([self._random.uniform(mi, ma) for (mi, ma) in zip(self.min, self.max)])
        else:
            return 1 if np.all(theta < self.max) and np.all(theta >= self.min) else 0


if __name__ == '__main__' :
    priorsDistr={}
    numParticule=10
    numproc=10
    pdict=mp.Manager().dict()

    while(len(pdict) < numParticule):
        with open("totry.out","w") as ttexp:
            ttexp.write("")
        for p in range(numproc):
            priors = TophatPrior([0,0,5,2,10],[1,1,200,6,30])
            one=Experiment("gege",priors(),"/home/scarrign/ceeculture",".")
            runCeec(one,'200')
        print(pdict)
