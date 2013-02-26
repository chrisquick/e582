#this new file uses plotvis and fast_coakley combined partly
import pyhdf.SD
import matplotlib
import bitmap
from binit import fastbin
from modismeta import metaParse
import glob
from orient import orient
import numpy as np
import time
import matplotlib.pyplot as plt
import fasthist as fh

### first grab Chan31 radiance
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
    chan31 = scale31 * (chan31 - offset31) ###########################
    sdrad.end()
   
### then grab Chan1 reflectance
    
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
    chan1ref = scale1ref * (chan1raw - offset1ref) #############################


  