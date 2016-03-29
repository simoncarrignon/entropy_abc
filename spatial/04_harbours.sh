
r.mapcalc "isSea=if(isnull(dem_1km),1,0)"
r.null map=isSea setnull=0
r.grow.distance input=isSea distance=distToSea 

# coast distance is 5 km 
r.mapcalc "isCoast=if(distToSea<=5000,1,0)"

v.db.addcol map=cities_caa columns="isCoast INT"
v.what.rast vector=cities_caa raster=isCoast column=isCoast

v.out.ogr input=cities_caa type=point format=CSV dsn=cities_weights.csv

