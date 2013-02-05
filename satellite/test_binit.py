import pyhdf.SD
from binit import binit
from modismeta import metaParse
import glob
from orient import orient
import numpy as np
from types import MethodType
import time

#make a new binit class that will call
#a cython version of do_bins defined in fastbinit.pyx

class fastbin(binit):
    def __init__(self,minval,maxval,numbins,missingLowValue,missingHighValue):
        binit.__init__(self,minval,maxval,numbins,missingLowValue,missingHighValue)

#
# import the cython version of do_bins
# and override the the slower python version
#
        
from fastbinit import do_bins
fastbin.do_bins=MethodType(do_bins, None, fastbin)
#
# now make sure we get the same counts in each bin
# as the numpy histogram routine
#
granule_info='A2010215.2145.005'
model3_file='*D03*{0:s}*hdf'.format(granule_info)
model3_file=glob.glob(model3_file)[0]
my_parser=metaParse(filename=model3_file)
meta_data=my_parser.get_info()
sdgeom=pyhdf.SD.SD(model3_file)
fullLats=sdgeom.select('Latitude')
fullLats=fullLats.get()
fullLons=sdgeom.select('Longitude')
fullLons=fullLons.get()
sdgeom.end()
fullLats,fullLons,fullLats=orient(fullLats,fullLons,fullLats)
#
# get the bounding box to set the lat/lon grid 
#
north,south,east,west=meta_data['nsew']
max_rows=200
max_cols=200
partLats=fullLats[:max_rows,:max_cols]
partLons=fullLons[:max_rows,:max_cols]
numlatbins=200
numlonbins=200

tic=time.clock()
bin_lats=fastbin(south,north,numlatbins,-999,-888)
bin_lons=fastbin(west,east,numlonbins,-999,-888)
lat_count,lat_index,lowlats,highlats=bin_lats.do_bins(partLats.ravel())    
lon_count,lon_index,lowlons,highlons=bin_lons.do_bins(partLons.ravel())    
fasttime=time.clock() - tic
#
# here's the correct answer from numpy
#
np_latcount,np_latbins=np.histogram(partLats.ravel(),bin_lats.bin_edges)
np_loncount,np_lonbins=np.histogram(partLons.ravel(),bin_lons.bin_edges)
#
# make sure they agree
#
#
#  uncomment this line to trigger an error
#np_latcount=np_latcount*1.5
## np.testing.assert_almost_equal(np_latcount,lat_count )
## np.testing.assert_almost_equal(np_loncount,lon_count )

tic=time.clock()
bin_lats=binit(south,north,numlatbins,-999,-888)
bin_lons=binit(west,east,numlonbins,-999,-888)
lat_count,lat_index,lowlats,highlats=bin_lats.do_bins(partLats.ravel())    
lon_count,lon_index,lowlons,highlons=bin_lons.do_bins(partLons.ravel())    
slowtime=time.clock() - tic

np.testing.assert_almost_equal(np_latcount,lat_count )
np.testing.assert_almost_equal(np_loncount,lon_count )

print "\nfastbinit time is {0:5.4e} seconds".format(fasttime)
print "binit time is {0:5.4e} seconds".format(slowtime)
print "speedup factor is {0:7.3f}".format((slowtime/fasttime))

