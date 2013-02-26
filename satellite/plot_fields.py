import matplotlib
#matplotlib.use('osx')
import numpy as np
import matplotlib.pyplot as plt
import time 

if __name__=="__main__":


    from matplotlib.colors import Normalize
    from matplotlib import cm

    def loadvars(filename, namespace=None):
        """
            load a dictionary of variables into
            the global namespace
        """
        if namespace is None:
            namespace = globals()
        out_files=np.load(filename)
        namespace.update(out_files)

    tic=time.clock()
    infile='gridded_fields.npz'
    loadvars(infile)
    time1=time.clock() - tic

    tic=time.clock()
    infile='outgrid.npz'
    loadvars(infile)
    time2=time.clock() - tic
    print "times: ",time1,time2
    
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 7.5
    vmax= 8.5
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    lowlimit=0.
    uplimit=None
    im=axis1.pcolormesh(lon_centers[lowlimit:uplimit],lat_centers[lowlimit:uplimit],rad_grid[lowlimit:uplimit,lowlimit:uplimit],
                    cmap=cmap,norm=the_norm)
    cb=fig1.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis1.set_title('MODIS channel 31 radiances (lat/lon binned)')
    fig1.canvas.draw()

    print "ready to do fig 2"
    fig2=plt.figure(2)
    fig2.clf()
    #
    # new color map without limits
    #
    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 1
    vmax= 5
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    axis2=fig2.add_subplot(111)
    im=axis2.pcolormesh(lon_centers[lowlimit:uplimit],lat_centers[lowlimit:uplimit],
                    hist2d[lowlimit:uplimit],cmap=cmap,norm=the_norm)
    cb=fig2.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('counts',rotation=270)
    axis2.set_title('2-d histogram (pixel count in each lat/lon bin')
    fig2.canvas.draw()

    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 7.5
    vmax= 8.5
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    lowlimit=0
    uplimit=150
    fig3=plt.figure(3)
    fig3.clf()
    axis3=fig3.add_subplot(111)
    a=np.ascontiguousarray(lon_centers[lowlimit:uplimit])
    b=np.ascontiguousarray(lat_centers[lowlimit:uplimit])
    c=np.ascontiguousarray(rad_grid[lowlimit:uplimit,lowlimit:uplimit])
    im=axis3.pcolormesh(a,b,c,cmap=cmap,norm=the_norm)
    cb=fig3.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis3.set_title('MODIS channel 31 radiances (lat/lon binned)  B')
    fig3.canvas.draw()

    del cmap
    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('k')
    vmin= 0
    vmax= 3
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    fig4=plt.figure(4)
    fig4.clf()
    axis4=fig4.add_subplot(111)
    c=np.ascontiguousarray(mask_grid[lowlimit:uplimit,lowlimit:uplimit])
    im=axis4.pcolormesh(a,b,c,cmap=cmap,norm=the_norm)
    cb=fig4.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('cloud mask',rotation=270)
    axis4.set_title('cloud mask')
    fig4.canvas.draw()

    
    plt.show()

