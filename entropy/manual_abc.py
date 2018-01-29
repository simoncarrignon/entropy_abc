#!/usr/bin/python3

import csv, math, sys, argparse, random,os,errno
from bs4 import BeautifulSoup as bs
import numpy as np
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
        self.expId = "_".join([str(int(self.params[indices['nstep']])),str(int(self.params[indices['cstep']])),str(self.params[indices['mu']])])
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
        
        self.kind=str(int(round(params[1]/1000)*1000))


        ##change the different value in the XML file with the parameters (thetas) of this experiments (particle)

        #soup.goods['num']=str(int(self.params[indices['ngoods']]))
        #soup.numAgents['value']=str(int(self.params[indices['ngoods']])*int(self.params[indices['nag_good']]))
        #soup.market['size']=str(self.params[indices['market_size']])
        soup.culture['step']=str(int(self.params[indices['cstep']]))
        soup.culture['mutation']=str(self.params[indices['mu']])
        soup.numSteps['value']=int(self.params[indices['nstep']])
        #soup.numSteps['value']=str(int(self.params[indices['cstep']])*3*100)
        soup.numSteps['serializeResolution']=int(soup.numSteps['value'])


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

    def getKind(self):
        return(self.kind)

    def getId(self):
        return(self.expId)

    #check if the score exist and return it, fi not return -1
    def getScore(self):
        file_score=os.path.join(self.particleDirectory,"score.txt")
        time.sleep(.01)
        last_score=-1
        try:
            with open(file_score,"r") as score:
                    last_score=int(score.readline().strip())
        except IOError:
            last_score=-1
            #print(self.expId+" still running")
        return(last_score)

    def __str__(self):
        result = 'experiment: '+str(self.expId)#+' alpha: '+str('%.2f')%self.alpha+' beta: '+str('%.2f')%self.beta+' harbour bonus: '+str('%.2f')%self.harbourBonus
        return result

    #generate a string that countain the command that should be run on marenostrum
    def generateTask(experiment):
        #print("run pandora")
        bashCommand = 'cd '+experiment.particleDirectory + ' && ./province && ./analysis ' +' && cd -- &&'
        #output, error = process.communicate()
        bashCommand += 'bash ./extractlast.sh '+os.path.join(experiment.particleDirectory,'agents.csv &&')
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

#generate a pool of experiment of size `size`
def genTestPool(size):
    pool_exp={}
    for p in range(size):
        priors = TophatPrior([0,300,5],[1,1000,7])
        params=priors()
        one=Experiment("gege",params,"/home/scarrign/ceeculture",".")
        with open("totry.out","a") as ttexp:
            ttexp.write(one.getId()+'\n')

        pool_exp[one.getId()]=one
    return(pool_exp)



###Write the task file and update the counter of the number of task per file
def writeNupdate(tmp_pdict):
    global countExpKind
    global countFileKind
    global tasks
    
    for pone in tmp_pdict.keys() :
        one=tmp_pdict[pone]
        kind=one.getKind()
        task=one.generateTask()

        if( not( kind in countExpKind.keys())): #check if this kind is already recorded
            countExpKind[kind]=0 
            countFileKind[kind]=0

        countExpKind[kind]=countExpKind[kind]+1 #increase number of expe of this kind

        if(countExpKind[kind] > 20): #if number of expe is too high, increase number of file 
            #TODO here should launch the file already full fullfillfillfull
            countFileKind[kind]=countFileKind[kind]+1
            countExpKind[kind]=0

        taskfilename=kind+"_"+str(countFileKind[kind])+".task"
        with open(taskfilename,'a') as tskf:
            tskf.write(task)

        tasks[taskfilename]=True

def launchExpe(taskfile):
    print(" ~/mn4_launchesamere "+taskfile)
    


if __name__ == '__main__' :
    pdict={}     #list of score for each exp
    countExpKind={} #list of launcher
    countFileKind={} #list of launcher
    tasks={}

    tmp_pdict={} #pool of particules
    numParticule=10 #This is the total number of resulta that we want
    numproc=80 #this is the number of parallele task we will try
    epsilon=10000

    with open("totry.out","w") as ttexp:
        ttexp.write("")
   
    tmp_pdict=genTestPool(numproc)
    ###initialize pool
    writeNupdate(tmp_pdict)

    ##findFileneNameAndUpdateCounter
    #Launch remaining tasks
       
    while(len(pdict) < numParticule):
        tsks=list(tasks.keys())
        if(len(tsks)>0):
            print(tsks)
            for l in tsks:
                launchExpe(l)
                tasks.pop(l,None)
            for cnt in countFileKind.keys():
                countFileKind[cnt]=countFileKind[cnt]+1


        ##update temporary experimeent
        tmp_keys=list(tmp_pdict.keys())
        for t in tmp_keys:
            tmp_exp=tmp_pdict[t]
            s=tmp_exp.getScore()
            if(s>0):
                if(s>epsilon):
                    #print("u lame")
                    tmp_pdict.pop(t,None)
                else:
                    pdict[tmp_exp.getId()]=s
                    tmp_pdict.pop(t,None)

        #the pool is empty : all simulation finished and we have not yeat enough particle
        if(len(tmp_pdict) == 0): 
            with open("totry.out","w") as ttexp:
                ttexp.write("")

            ###re-initialize pool
            tmp_pdict=genTestPool(numproc)
            writeNupdate(tmp_pdict)
            ##findFileneNameAndUpdateCounter
            #Launch remaining tasks
