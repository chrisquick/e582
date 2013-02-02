from __future__ import division
import site, glob
site.addsitedir('/Users/phil/Library/Python/2.7/lib/python/site-packages')
site.addsitedir('/Users/phil/repos/e582_code/satellite')
from modismeta import metaParse
import numpy as np
import pyhdf.SD


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
maskVals=maskVals[0,...] #get the first byte
#
# pass the byte to bitmap and get back the cloudmask
# and the landmask
#
maskout,landout=bitmap.getmask_zero(maskVals)
oceanvals=(landout==0)
cloudvals=np.logical_and(maskout==0,oceanvals)
cloudfrac=np.sum(cloudvals)/oceanvals.size
oceanfrac=np.sum(oceanvals)/landout.size
print "Cloud fraction is {0:8.4f}".format(cloudfrac)
print "fraction of scene surface that is ocean is {0:8.4f}".format(oceanfrac)

thinout,highout=bitmap.getmask_zero(maskVals)
clear_thin_frac=np.sum(thinout.flat)/thinout.size
clear_high_frac=np.sum(highout.flat)/highout.size

print "fraction of scene that is covered by thin clouds is {0:8.4f}".format(1. - clear_thin_frac)
print "fraction of scene that is covered by high clouds is {0:8.4f}".format(1. - clear_high_frac)





