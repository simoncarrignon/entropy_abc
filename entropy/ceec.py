#!/usr/bin/python3

import csv, math, sys, argparse, random,os,errno
from bs4 import BeautifulSoup as bs
import numpy as np
import subprocess
import logging

#index of the different parameters
indices= {  "mu"            : 0, 
            "market_size"   : 1,
            "nag_good"       : 2,
            "ngoods"        : 3,
            "cstep"         : 4}

def dist(x,y):
    diff= x-y;
    return diff

class Experiment:
    def __init__(self, expId, params,binpath,outpath):
        self.consistence=True
        self.params = params
        self.expId = "_".join([str(int(self.params[indices['ngoods']])),str(int(self.params[indices['nag_good']])),str(self.params[indices['market_size']]),str(int(self.params[indices['cstep']])),str(self.params[indices['mu']])])
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
        if((int(self.params[indices['nag_good']]) < 1) or  #if num <2 
           (int(self.params[indices['ngoods']]) < 2 ) or #No exchange possible if we don't have at least 2 goods
           (int(self.params[indices['cstep']]) < 1 ) or  #No experiments if no cultural step
           (self.params[indices['mu']] <= 0 ) or #No meaning if mutation rate <0 or >1
           (self.params[indices['mu']] > 1 ) or 
           (self.params[indices['market_size']] > 1 ) or  #no need to explore more than 100% of the market
           (self.params[indices['market_size']] <= 0 ) #agent has to visit the market to exchange stuff
          ):
            #print("baddd",params)
            self.consistence=False

        soup = bs(open(self.binpath+"/config.xml"),'xml') #read a generic config file




        ##change the different value in the XML file with the parameters (thetas) of this experiments ( particle)
        soup.goods['num']=str(int(self.params[indices['ngoods']]))
        soup.numAgents['value']=str(int(self.params[indices['ngoods']])*int(self.params[indices['nag_good']]))
        soup.market['size']=str(self.params[indices['market_size']])
        soup.culture['step']=str(int(self.params[indices['cstep']]))
        soup.culture['mutation']=str(self.params[indices['mu']])
        soup.numSteps['serializeResolution']=str(int(self.params[indices['cstep']])*3)
        soup.numSteps['value']=str(int(self.params[indices['cstep']])*3*100)
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
            out=open(self.particleDirectory+"/config.xml","wb")
            out.write(soup.prettify())
            out.close()
        else:
            if (os.path.isdir(self.particleDirectory)):  
                logging.warning( "particle already tested")  
            else:
                logging.warning( "unconsistent particle")  
            self.consistence=False

    def __str__(self):
        result = 'experiment: '+str(self.expId)#+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' harbour bonus: '+str('%.2f')%self.harbourBonus
        return result

def runCeec(experiment, storeResults):
    score = 1000
    if(experiment.consistence):
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

        last_score=output.strip().split("\n")
        try:
            last_score=map(float,last_score)
            score=np.mean(last_score)
            score=score/(experiment.params[indices['cstep']] * (experiment.params[indices['ngoods']]-1))
        except:
            logging.warning("the file agents.csv of the particule:"+experiment.expId+" seems to have a problem ")
            score = 1000

    else:
        score = 1000
    
    #logging.info(score)
    #logging.info(experiment.params[indices['cstep']] )
    #logging.info(experiment.params[indices['ngoods']] )


    logging.info("exp:"+experiment.expId+",score: "+str(score))
 
    return score
    
