import pyhdf.SD
import matplotlib

#matplotlib.use('osx')
#
# fastbin used fastbinit.pyx cython binning
# compile with
# python setup_fast.py build_ext --install 
#
#  or on windows
#
# python setup_fast.py build_ext --install --compiler=mingw32
#
import bitmap
from binit import fastbin
from modismeta import metaParse
import glob
from orient import orient
import numpy as np
import time
import matplotlib.pyplot as plt
#
# fasthist.pyx -- calls histo.cpp C++ code from cython
# use cython: compile with
# python setup_hist.py build_ext --install 
#
#  or on windows
#
# python setup_hist.py build_ext --install --compiler=mingw32
#
import fasthist as fh

if __name__=="__main__":

    import copy
    from matplotlib.colors import Normalize
    from matplotlib import cm
    cmap=copy.deepcopy(cm.RdBu_r)
    cmap.set_over('y')
    cmap.set_under('w')
    vmin= 0
    vmax= 350.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    granule_info='A2010215.2145.005'
    model3_file='*D03*{0:s}*hdf'.format(granule_info)
    model3_file=glob.glob(model3_file)[0]
    my_parser=metaParse(filename=model3_file)
    meta_data=my_parser.get_info()
    sdgeom=pyhdf.SD.SD(model3_file)
    fullLats_raw=sdgeom.select('Latitude')
    fullLats_raw=fullLats_raw.get()
    fullLons_raw=sdgeom.select('Longitude')
    fullLons_raw=fullLons_raw.get()
    sdgeom.end()
    model2_file='*D021KM*{0:s}*hdf'.format(granule_info)
    model2_file=glob.glob(model2_file)[0]
    sdrad=pyhdf.SD.SD(model2_file)
    shortWave=sdrad.select('EV_250_Aggr1km_RefSB')
    allRadiances=shortWave.get()

    theChans=shortWave.attributes()['band_names']
    band_names=theChans.split(',')
    index1=band_names.index('1')
    #
    #  get the radiances as 16 bit integers
    #
    chan1raw=allRadiances[index1,:,:]
    #
    # apply scale and offset to convert to 64 bit floats
    #
    scale1=shortWave.attributes()['radiance_scales'][index1]
    offset1=shortWave.attributes()['radiance_offsets'][index1]
    chan1 = scale1 * (chan1raw - offset1)

    scale1ref=shortWave.attributes()['reflectance_scales'][index1]
    offset1ref=shortWave.attributes()['reflectance_offsets'][index1]
    chan1ref = scale1ref * (chan1raw - offset1ref)


    sdrad.end()
    fullLats,fullLons,chan1=orient(fullLats_raw,fullLons_raw,chan1)
    fullLats,fullLons,chan1ref=orient(fullLats_raw,fullLons_raw,chan1ref)
    #
    # get the bounding box to set the lat/lon grid 
    #
    north,south,east,west=meta_data['nsew']
    #
    # select none here to see the full image
    #
    max_rows= None
    max_cols= None
    partLats=fullLats[:max_rows,:max_cols]
    partLons=fullLons[:max_rows,:max_cols]
    partRads=chan1[:max_rows,:max_cols]
    partRefs=chan1ref[:max_rows,:max_cols]
    
    numlatbins=550
    numlonbins=550

    bin_lats=fastbin(south,north,numlatbins,-999,-888)
    bin_lons=fastbin(west,east,numlonbins,-999,-888)

    lon_centers=bin_lons.get_centers()
    lat_centers=bin_lats.get_centers()

    tic=time.clock()
    new_hist=fh.pyhist(partLats,partLons,bin_lats,bin_lons)
    rad_grid=new_hist.get_mean(partRads)
    ref_grid=new_hist.get_mean(partRefs)

    
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    im=axis1.pcolormesh(lon_centers,lat_centers,rad_grid,cmap=cmap,\
                      norm=the_norm)
    cb=plt.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis1.set_title('MODIS channel 1 radiances (lat/lon binned)')
    fig1.canvas.draw()

    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('w')
    vmin= 0
    vmax= 1.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    fig2=plt.figure(2)
    fig2.clf()
    axis2=fig2.add_subplot(111)
    im=axis2.pcolormesh(lon_centers,lat_centers,ref_grid,cmap=cmap,\
                      norm=the_norm)
    cb=plt.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('reflectances',rotation=270)
    axis2.set_title('MODIS channel 1 reflectance (lat/lon binned)')
    fig2.canvas.draw()

    
    plt.show()

