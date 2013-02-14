import pyhdf.SD
import matplotlib
matplotlib.use('osx')
#
# fastbin used fastbinit.pyx cython binning
# compile with
# python setup_fast.py build_ext --install 
#
#  or on windows
#
# python setup_fast.py build_ext --install --compiler=mingw32
#
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
    vmin= 7.5
    vmax= 8.5
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
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
    model2_file='*D021KM*{0:s}*hdf'.format(granule_info)
    model2_file=glob.glob(model2_file)[0]
    sdrad=pyhdf.SD.SD(model2_file)
    longWave=sdrad.select('EV_1KM_Emissive')

    allRadiances=longWave.get()
    #
    # find the index for channel 31 (it's 10, i.e. channel 31 is
    # the 11th channel)
    #
    theChans=longWave.attributes()['band_names']
    band_names=theChans.split(',')
    index31=band_names.index('31')
    #
    #  get the radiances as 16 bit integers
    #
    chan31=allRadiances[index31,:,:]
    #
    # apply scale and offset to convert to 64 bit floats
    #
    scale31=longWave.attributes()['radiance_scales'][index31]
    offset31=longWave.attributes()['radiance_offsets'][index31]
    chan31 = scale31 * (chan31 - offset31)
    sdrad.end()
    fullLats,fullLons,chan31=orient(fullLats,fullLons,chan31)
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
    partRads=chan31[:max_rows,:max_cols]

    numlatbins=550
    numlonbins=550

    bin_lats=fastbin(south,north,numlatbins,-999,-888)
    bin_lons=fastbin(west,east,numlonbins,-999,-888)

    lon_centers=bin_lons.get_centers()
    lat_centers=bin_lats.get_centers()

    tic=time.clock()
    new_hist=fh.pyhist(partLats,partLons,bin_lats,bin_lons)
    rad_grid=new_hist.get_mean(partRads)
    toc=time.clock() - tic
    ## print "slow and fast plus speedup: ",fasttime,toc,fasttime/toc

    
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    im=axis1.pcolor(lon_centers,lat_centers,rad_grid,cmap=cmap,\
                      norm=the_norm)
    cb=plt.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis1.set_title('MODIS channel 31 radiances (lat/lon binned)')
    fig1.canvas.draw()

    hist2d=new_hist.get_hist2d()
    print "ready to do fig 2"
    fig2=plt.figure(2)
    fig2.clf()
    #
    # new color map without limits
    #
    del cmap
    cmap=cm.RdBu_r
    axis2=fig2.add_subplot(111)
    im=axis2.pcolor(lon_centers,lat_centers,hist2d,cmap=cmap)
    cb=plt.colorbar(im)
    the_label=cb.ax.set_ylabel('counts',rotation=270)
    axis2.set_title('2-d histogram (pixel count in each lat/lon bin')
    fig2.canvas.draw()
    
    plt.show()

