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
    vmin= 7.5
    vmax= 8.5
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
    longWave=sdrad.select('EV_1KM_Emissive')
    allRadiances=longWave.get()

    model35_file='*D35*{0:s}*hdf'.format(granule_info)
    model35_file=glob.glob(model35_file)[0]
    mask=pyhdf.SD.SD(model35_file)
    maskVals=mask.select('Cloud_Mask')
    maskVals=maskVals.get()
    byte0=maskVals[0,...] #get the first byte
    maskout,landout=bitmap.getmask_zero(byte0)
    maskout=maskout.astype(np.float32)
    landout=landout.astype(np.float32)
    fullLats,fullLons,maskout=orient(fullLats_raw,fullLons_raw,maskout)
    fullLats,fullLons,landout=orient(fullLats_raw,fullLons_raw,landout)
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
    fullLats,fullLons,chan31=orient(fullLats_raw,fullLons_raw,chan31)
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
    partMask=maskout[:max_rows,:max_cols]
    partLand=landout[:max_rows,:max_cols]
    partChan1rad=chan1[:max_rows,:max_cols]
    partChan1ref=chan1ref[:max_rows,:max_cols]
    
    numlatbins=800
    numlonbins=600

    bin_lats=fastbin(south,north,numlatbins,-999,-888)
    bin_lons=fastbin(west,east,numlonbins,-999,-888)

    lon_centers=bin_lons.get_centers()
    lat_centers=bin_lats.get_centers()

    new_hist=fh.pyhist(partLats,partLons,bin_lats,bin_lons)
    chan31_grid=new_hist.get_mean(partRads)
    mask_grid=new_hist.get_mean(partMask)
    land_grid=new_hist.get_mean(partLand)
    chan1rad_grid=new_hist.get_mean(partChan1rad)
    chan1ref_grid=new_hist.get_mean(partChan1ref)

    
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    im=axis1.pcolormesh(lon_centers,lat_centers,chan31_grid,cmap=cmap,\
                      norm=the_norm)
    cb=plt.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis1.set_title('MODIS channel 31 radiances (lat/lon binned)')
    fig1.canvas.draw()

    
    lat_lon_counts=new_hist.get_hist2d()
    print "ready to do fig 2"
    fig2=plt.figure(2)
    fig2.clf()
    #
    # new color map without limits
    #
    del cmap
    cmap=cm.RdBu_r
    axis2=fig2.add_subplot(111)
    im=axis2.pcolormesh(lon_centers,lat_centers,lat_lon_counts,cmap=cmap)
    cb=plt.colorbar(im)
    the_label=cb.ax.set_ylabel('counts',rotation=270)
    axis2.set_title('2-d histogram (pixel count in each lat/lon bin')
    fig2.canvas.draw()

    #new colormap
    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('w')
    vmin= 0
    vmax= 3
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    fig3=plt.figure(3)
    fig3.clf()
    axis3=fig3.add_subplot(111)
    mask_grid[mask_grid < 0] = -1
    im=axis3.pcolormesh(lon_centers,lat_centers,mask_grid,cmap=cmap,\
                      norm=the_norm)
    cb=fig3.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('cloud mask',rotation=270)
    axis3.set_title('cloud mask (0=cloud, 3=clear)')
    fig3.canvas.draw()


    fig4=plt.figure(4)
    fig4.clf()
    axis4=fig4.add_subplot(111)
    mask_grid[mask_grid < 0] = -1
    im=axis4.pcolormesh(lon_centers,lat_centers,land_grid,cmap=cmap,\
                      norm=the_norm)
    cb=fig4.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('land mask',rotation=270)
    axis4.set_title('land mask (0=water, 1=coasta,l 2= desert, 3=land)')
    fig4.canvas.draw()

    savefile='gridded_fields'
    arrays={'chan31_grid':chan31_grid,'lat_lon_counts':lat_lon_counts,'lon_centers':lon_centers,
            'lat_centers':lat_centers,'mask_grid':mask_grid,'land_grid':land_grid,
            'chan1rad_grid':chan1rad_grid,'chan1ref_grid':chan1ref_grid}
    np.savez_compressed(savefile,**arrays)
    
    plt.show()

