#see http://pysclint.sourceforge.net/pyhdf/
import pyhdf.SD
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import glob
from modismeta import parseMeta
import pyhdf

#get the name of files ending in hdf
the_file=glob.glob('*hdf')

#take the first one (I only have one file in the directory
the_file=the_file[0]

# here's the header information
print parseMeta(the_file)

#get the full latitude and longitude arrays
sdgeom=pyhdf.SD.SD(the_file)
fullLats=sdgeom.select('Latitude')
fullLats=fullLats.get()
fullLons=sdgeom.select('Longitude')
fullLons=fullLons.get()
sdgeom.end()

#plot the latitdue and longitude of every pixel
#for a small part of the scene
fig1,axis1=plt.subplots(1,1)
axis1.plot(fullLons.flat,fullLats.flat,'b+')
axis1.set_ylim([-44,-43.5])
axis1.set_xlim([-80,-79.5])
axis1.set_ylabel('latitude (deg North)')
axis1.set_xlabel('longitude (deg East)')

plt.show()
