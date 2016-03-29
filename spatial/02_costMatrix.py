#!/usr/bin/python3

def main():
    numSites = 140
    prefix = '../raw_data/dists/dists_'


    coordsFileName = 'coords.csv'
    outputFileName = 'costMatrix.csv'
    
    outputFile = open(outputFileName, 'w')
    outputFile.write('code;cost\n')

#    coordsFile = open(coordsFileName, 'w')
#    coordsFile.write('id;x;y\n')

    for site in range(1,1+numSites):
        print('site:',site,'of:',numSites)
        distFileName = prefix+str(site)
        distFile = open(distFileName, 'r')

        # header
        distFile.readline()
        header = distFile.readline()
        headerSplit = header.strip().split(';')
        siteId = int(headerSplit[0])
        x = float(headerSplit[1])
        y = float(headerSplit[2])

#        coordsFile.write(str(siteId)+';'+str(x)+';'+str(y)+'\n')
        

        # each site has 13 lines: 0 is id and 5 is max
        untilNextSite = 0
        untilNextMax = 5
        for line in distFile:
            if untilNextSite!=0:
                untilNextSite -= 1
                continue

            if untilNextMax == 5:
                target = line.strip().split(';')
                targetId = int(target[0])
                targetX = float(target[1])
                targetY = float(target[2])
                untilNextMax -= 1
            elif untilNextMax != 0:
                untilNextMax -= 1
            else:
                splitMax = line.strip().split('=')
                maxCost = int(float(splitMax[1]))
                print('\tcost:',maxCost,'to',targetId,'pos:',targetX,targetY)
                code = str(siteId)+'_'+str(targetId)
                outputFile.write(code+';'+str(maxCost)+'\n')
                untilNextSite = 7
                untilNextMax = 5


if __name__ == "__main__":
    main()

