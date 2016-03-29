
#############
# prominence index
# install this with g.extension extension=r.prominence

r.mapcalc "dem_1km_fp=1.0*dem_1km"
r.prominence input=dem_1km_fp output=prom_1km radius=4



#############
# access to farming lands

r.slope.aspect elevation=dem_1km slope=slope_1km
# compute access to flat lands (<5 degrees)
r.mapcalc "flat_land_1km=if(slope_1km<5,1,0)"
# set nulls to 0
#r.null map=flat_land_1km null=0

g.remove rast=farming_1km
# we are looking for something similar to 5km radius. -c makes it circular
r.neighbors input=flat_land_1km method=sum size=11 output=farming_1km -c

# we need to be weights > 0
r.mapcalc "farming_1km=farming_1km+1"
# r.univar to get min value of map
r.mapcalc "prom_1km_ok=prom_1km+909.162+1"

# store values in vector
v.db.addcol map=cities_caa columns="farming DOUBLE PRECISION"
v.db.addcol map=cities_caa columns="prom DOUBLE PRECISION"
v.what.rast vector=cities_caa raster=prom_1km_ok column=prom
v.what.rast vector=cities_caa raster=farming_1km column=farming

v.out.ogr input=cities_caa type=point format=CSV dsn=cities_weights.csv

