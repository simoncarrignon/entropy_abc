#!/usr/bin/python3

import entropy
import math

def main():

    speedKn = 4
    # sailing 18 hours a day, 1.852 km is a knot ~~ 90 km per day
    speedKmDay = speedKn*1.852*18

    costFile = '../data/costMatrix.csv'
    sitesFile = '../data/cities_weights.csv'

    baseCost = entropy.loadLandCostsInMeters(costFile)
    sites = entropy.loadHistoricalSites(sitesFile)

    seaCostFile = '../data/costMatrixSea.csv'
    seaCost = open(seaCostFile, 'w')
    seaCost.write('code;cost\n')
    
    for fromSite in sites:
        print('checking sea connections for:',fromSite)
        for toSite in sites:
            code = str(fromSite.ident)+'_'+str(toSite.ident)
            if toSite is fromSite:
                seaCost.write(code+';0\n')
                continue
            # write land values
            elif not fromSite.isHarbour or not toSite.isHarbour:
                seaCost.write(code+';'+str(entropy.Site.cost[code])+'\n')
                continue
            print('\tfrom:',fromSite.ident,'to:',toSite.ident,'sea connection')
            distance = math.sqrt(math.pow(toSite.x-fromSite.x,2)+math.pow(toSite.y-fromSite.y,2))/1000
            travelDays = distance/speedKmDay
            print('\tland cost',entropy.Site.cost[code],'sea cost:',travelDays,'with distance:',distance)
            finalDist = min(travelDays, entropy.Site.cost[code])
            seaCost.write(code+';'+str(finalDist)+'\n') 
    seaCost.close()

if __name__ == "__main__":
    main()

