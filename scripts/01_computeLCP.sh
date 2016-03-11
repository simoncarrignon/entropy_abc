#!/bin/bash

echo 'least cost path computation'

# each 1 km
#g.region res=30
g.region res=150

dem='dem2'
sitesFile='cities'
friction=`r.mapcalc 'friction=1'`

#sites=`v.db.select map=$sitesFile columns=cat -c`
sites=`v.db.select map=$sitesFile columns=cat where='cat>=43' -c`
sitesFull=`v.db.select map=$sitesFile columns=cat -c`
indexSite=43
#indexSite=0
echo 'starting least cost path analysis'

rm dists_*

for siteId in $sites;
	do
		x=`v.db.select map=$sitesFile columns=XCOORD where='cat='$siteId'' -c`
		y=`v.db.select map=$sitesFile columns=YCOORD where='cat='$siteId'' -c`
		
        echo 'least cost paths to site: '$siteId' index:'$indexSite' coordinates: '$x','$y		
		walkMap='walk_'$siteId
		g.remove $walkMap
        r.walk elevation=$dem friction=friction output=$walkMap coordinate=$x,$y
        # header
        outputFile='dists_'$siteId
        echo 'siteId;x;y' >> $outputFile
        echo $siteId';'$x';'$y >> $outputFile
        for targetId in $sitesFull;
			do
				routeMap='routeMap_'$siteId'_'$targetId
				echo 'calculating cost route from: '$siteId' to: '$targetId'...'
				targetX=`v.db.select map=$sitesFile columns=XCOORD where='cat='$targetId'' -c`
				targetY=`v.db.select map=$sitesFile columns=YCOORD where='cat='$targetId'' -c`
                g.remove $routeMap
				r.drain input=$walkMap coordinate=$targetX,$targetY output=$routeMap -c
                echo $targetId';'$targetX';'$targetY >> $outputFile
                r.univar map=$routeMap -g >> $outputFile
                g.remove $routeMap
			done
		let indexSite=$indexSite+1
		echo 'site number:'$indexSite ' with id: '$siteId' done!'
		g.remove $walkMap

	done
echo 'least cost path analysis finished'

