"""Demo script showing how to read a level1b
   Modis radiance data set.   To get started with pyhdf, do
   >> import pyhdf.SD
   >> help(pyhdf.SD)
"""

import pyhdf.SD
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
#
# edit this to put in your file name
#

filename='MOD021KM.A2006275.0440.005.2008107091833.hdf'

sd = pyhdf.SD.SD(filename)
#read all attributes and datasets
theAtts=sd.attributes()
theData=sd.datasets()
#get the datasets for Latitude and longitude
#(every fifth pixel)
coarseLats=sd.select('Latitude')
coarseLats=coarseLats.get()
coarseLons=sd.select('Longitude')
coarseLons=coarseLons.get()
#get the longwave radiances
longWave=sd.select('EV_1KM_Emissive')
allRadiances=longWave.get()
meta=sd.__getattr__('CoreMetadata.0')
theChans=longWave.attributes()['band_names']
#
# single channel name is padded with zeros for
# some reason, treat it separately if padding is found
#
if theChans.find('\x00') == -1:
    band_names=theChans.split(',')
else:
    theChans=theChans[:2]
band_names=theChans.split(',')
#find the location of channel 31 in the allRadiances array
index31=band_names.index('31')
chan31=allRadiances[index31,:,:]
#
# get the calliberation
#
if len(band_names)!=1:
    scale31=longWave.attributes()['radiance_scales'][index31]
    offset31=longWave.attributes()['radiance_offsets'][index31]
else:
    scale31=longWave.attributes()['radiance_scales']
    offset31=longWave.attributes()['radiance_offsets']    
chan31 = scale31 * (chan31 - offset31)
print "finished callibration"
sd.end()
#histogram the first 5000 values
fig1=plt.figure(1)
fig1.clf()
axis1=fig1.add_subplot(111)
axis1.hist(chan31.ravel()[:5000])
axis1.set_title('channel 31 radiances in W/m^2/micron/sr')
fig1.canvas.draw()
 
fig2=plt.figure(2)
fig2.clf()
axis2=fig2.add_subplot(111)
cax=axis2.imshow(chan31)
axis2.set_title('raw channel 31 radiance, no mapping')
the_bar=fig2.colorbar(cax)
the_bar.ax.set_ylabel('radiance $(W/m^{-2} \mu m^{-1} sr^{-1})$',rotation=270)
fig2.canvas.draw()
plt.show()
