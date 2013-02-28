import pyhdf.SD
import matplotlib

import numpy as np
import matplotlib.pyplot as plt
from plot_fields import loadvars

import fasthist as fh
from binit import fastbin
from plot_rads import make_dir

if __name__=="__main__":

    from matplotlib.colors import Normalize
    from matplotlib import cm

    #place stored variables in the global namespace
    infile='gridded_fields.npz'
    loadvars(infile,namespace=globals())
    dirname='plots'
    make_dir(dirname)

        #
    # select a sub region that goes from -120 -> -115 deg lon and
    #   20 - 25 deg lat
    #
    lon_hit=np.logical_and(lon_centers > -120, lon_centers < -115)
    lon_indices=np.where(lon_hit)[0]
    lat_hit=np.logical_and(lat_centers > 20, lat_centers < 25)
    lat_indices=np.where(lat_hit)[0]
    sub_lons=lon_centers[lon_indices]
    sub_lats=lat_centers[lat_indices]
    sub_chan1ref=chan1ref_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    sub_chan31=chan31_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]

    bin_chan1ref=fastbin(0.05,0.6,50.,-999,-888)
    bin_chan31=fastbin(2.,18.,50.,-999,-888)

    chan1_centers=bin_chan1ref.get_centers()
    chan31_centers=bin_chan31.get_centers()
    the_hist=fh.pyhist(sub_chan31,sub_chan1ref,bin_chan31,bin_chan1ref)

    counts=the_hist.get_hist2d()

    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 10.
    vmax= 400.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    counts=counts.astype(np.float32)
    ## hit= (counts == 0)
    ## counts[hit] = 1.e-3
    ## log_counts=np.log10(counts)

    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    im=axis1.pcolormesh(chan31_centers,chan1_centers,counts,cmap=cmap,norm=the_norm)
    cb=fig1.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('log10 of histogram counts',rotation=270)
    axis1.set_title('A2010215.2145 histogram')
    axis1.set_xlabel('Channel 31 radiance ($W/m^2/\mu m/sr$)')
    axis1.set_ylabel('Channel 1 reflectance (unitless)')
    fig1.canvas.draw()
    fig1.savefig('{0:s}/hist2d.png'.format(dirname))

    
    plt.show()

