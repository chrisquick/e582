import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import time 
from plot_rads import make_dir

def loadvars(filename, namespace=None):
    """
        load a dictionary of variables into
        the global namespace
    """
    if namespace is None:
        namespace = globals()
    out_files=np.load(filename)
    namespace.update(out_files)

if __name__=="__main__":

    from matplotlib.colors import Normalize
    from matplotlib import cm


    dirname='plots'
    make_dir(dirname)

    #place stored variables in the global namespace
    infile='gridded_fields.npz'
    loadvars(infile)

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
    sub_mask=mask_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    sub_chan1ref=chan1ref_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    sub_chan1rad=chan1rad_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    sub_chan31rad=chan31_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    sub_counts=lat_lon_counts[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    sub_land=land_grid[lat_indices[0]:lat_indices[-1],lon_indices[0]:lon_indices[-1]]
    
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 7.5
    vmax= 8.5
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    im=axis1.pcolormesh(sub_lons,sub_lats,sub_chan31rad,cmap=cmap,norm=the_norm)
    cb=fig1.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis1.set_title('MODIS channel 31 radiances (lat/lon binned)')
    fig1.canvas.draw()
    fig1.savefig('{0:s}/sub_chan31rad.png'.format(dirname))

    fig2=plt.figure(2)
    fig2.clf()
    axis2=fig2.add_subplot(111)
    im=axis2.pcolormesh(lon_centers,lat_centers,chan31_grid,cmap=cmap,norm=the_norm)
    cb=fig2.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis2.set_title('MODIS channel 31 radiances (lat/lon binned)')
    fig2.canvas.draw()
    fig2.savefig('{0:s}/full_chan31rad.png'.format(dirname))


    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 0
    vmax= 1.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    fig3=plt.figure(3)
    fig3.clf()
    axis3=fig3.add_subplot(111)
    im=axis3.pcolormesh(sub_lons,sub_lats,sub_chan1ref,cmap=cmap,norm=the_norm)
    cb=fig3.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis3.set_title('MODIS channel 1 reflectance (lat/lon binned)  B')
    fig3.canvas.draw()
    fig3.savefig('{0:s}/sub_chan1ref.png'.format(dirname))

    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 0
    vmax= 5

    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    fig4=plt.figure(4)
    fig4.clf()
    axis4=fig4.add_subplot(111)
    im=axis4.pcolormesh(sub_lons,sub_lats,sub_counts,cmap=cmap,norm=the_norm)
    cb=fig4.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('bin counts',rotation=270)
    axis4.set_title('pixels in each lat/lon bin')
    fig4.canvas.draw()
    fig4.savefig('{0:s}/sub_counts.png'.format(dirname))


    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    fig5=plt.figure(5)
    fig5.clf()
    axis5=fig5.add_subplot(111)
    im=axis5.pcolormesh(sub_lons,sub_lats,sub_land,cmap=cmap,norm=the_norm)
    cb=fig5.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('land mask',rotation=270)
    axis5.set_title('land mask (0=water, 1=coasta,l 2= desert, 3=land)')
    fig5.canvas.draw()
    fig5.savefig('{0:s}/sub_land.png'.format(dirname))


    fig6=plt.figure(6)
    fig6.clf()
    axis6=fig6.add_subplot(111)
    im=axis6.pcolormesh(sub_lons,sub_lats,sub_mask,cmap=cmap,norm=the_norm)
    cb=fig6.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('cloud mask',rotation=270)
    axis6.set_title('cloud mask (0=cloud, 3=clear)')
    fig6.canvas.draw()
    fig6.savefig('{0:s}/sub_cloud.png'.format(dirname))

    
    
    plt.show()

