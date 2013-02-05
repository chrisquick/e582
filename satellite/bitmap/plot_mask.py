from __future__ import division
import matplotlib
import site, glob
site.addsitedir('/Users/phil/Library/Python/2.7/lib/python/site-packages')
site.addsitedir('/Users/phil/repos/e582_code/satellite')
matplotlib.use('Agg')
from modismeta import metaParse
import numpy as np
import pyhdf.SD
import matplotlib.pyplot as plt
from dateutil.parser import parse
from plot_rads import make_dir

import dateutil.tz as tz
import re
import bitmap

plot_dir='plots'
make_dir(plot_dir)


mask_file=glob.glob('MYD35*2010215*.hdf')[0]
my_parser=metaParse(filename=mask_file)
meta_data=my_parser.get_info()
mask=pyhdf.SD.SD(mask_file)

theDate=parse(meta_data['startdate'][:-3] + meta_data['starttime'])
theDate=theDate.replace(tzinfo=tz.tzutc())

maskVals=mask.select('Cloud_Mask')
maskVals=maskVals.get()
byte0=maskVals[0,...] #get the first byte
#
# pass the byte to bitmap and get back the cloudmask
# and the landmask
#
maskout,landout=bitmap.getmask_zero(byte0)
oceanvals=(landout==0)
cloudvals=np.logical_and(maskout==0,oceanvals)
cloudfrac=np.sum(cloudvals)/oceanvals.size
oceanfrac=np.sum(oceanvals)/landout.size
print "Cloud fraction is {0:8.4f}".format(cloudfrac)
print "fraction of scene surface that is ocean is {0:8.4f}".format(oceanfrac)

byte1=maskVals[1,...] #get the next byte
thinout,highout=bitmap.getmask_one(byte1)
no_thin_frac=np.sum(thinout.flat)/thinout.size
no_high_frac=np.sum(highout.flat)/highout.size

print "fraction of scene that is covered by thin clouds is {0:8.4f}".format((1. - no_thin_frac))
print "fraction of scene that is covered by high clouds is {0:8.4f}".format((1. - no_high_frac))

## fig=plt.figure(1)
## fig.clf()
## ax1=fig.add_subplot(111)
## ax1.plot()
## fig.tight_layout()
## fig.canvas.draw()
## plt.show()






