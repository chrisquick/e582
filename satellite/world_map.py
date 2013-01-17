from mpl_toolkits.basemap import Basemap, shiftgrid
import numpy as np
import matplotlib.pyplot as plt
import site,os
cwd=os.getcwd()
site.addsitedir(cwd)
from plot_rads import make_dir

dirname='plots'
make_dir(dirname)

#
# extra feature: print coordinates when you click the mouse on a point
# (commented out below)
#
def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        event.button, event.x, event.y, event.xdata, event.ydata)

# read in topo data (on a regular lat/lon grid)
# see http://clouds.eos.ubc.ca/~phil/courses/e582data
etopo=np.loadtxt('etopo20data.gz')
lons=np.loadtxt('etopo20lons.gz')
lats=np.loadtxt('etopo20lats.gz')
# create Basemap instance for Robinson projection.
# control the size and screen size
#
fig1=plt.figure(1,figsize=(4,5),dpi=150)
fig1.clf()
axis1 = fig1.add_subplot(111)

#
# register the onclick function to capture a mouse click
#
cid = fig1.canvas.mpl_connect('button_press_event', onclick)

lon_mid=(lons[0] + lons[-1])/2.
vdg_transform = Basemap(projection='vandg',lon_0=lon_mid,ax=axis1)

# make filled contour plot.
#
# what is the purpose of this line?
#
lon_array,lat_array=np.meshgrid(lons, lats)
x,y=vdg_transform(lon_array,lat_array)
#do a filled contour plot of the topography
cs = axis1.contourf(x,y,etopo,30,cmap=plt.cm.jet)
# draw coastlines.
vdg_transform.drawcoastlines()
# draw parallels and meridians.
vdg_transform.drawparallels(np.arange(-60.,90.,30.))
vdg_transform.drawmeridians(np.arange(0.,360.,60.),fontsize=12)
cb=vdg_transform.colorbar(cs,location='bottom',pad='10%',fig=fig1)
cb.set_ticks([-9000,0,6000], update_ticks=True)
cb.set_label('height (m)')
axis1.set_title('topo, van der Grinten projection')
fig1.canvas.draw()
#make a png file for handin
plotfile='{0:s}/vdg.png'.format((dirname))
fig1.savefig(plotfile)

fig2=plt.figure(2,figsize=(7,7),dpi=150)
fig2.clf()
axis2 = fig2.add_subplot(111)
rob_transform = Basemap(projection='robin',lon_0=lon_mid,ax=axis2)
x,y=rob_transform(lon_array,lat_array)
#do a filled contour plot of the topography
cs = axis2.contourf(x,y,etopo,30,cmap=plt.cm.jet)
# draw coastlines.
rob_transform.drawcoastlines()
# draw parallels and meridians.
rob_transform.drawparallels(np.arange(-60.,90.,30.),labels=[1,0,0,0])
rob_transform.drawmeridians(np.arange(0.,360.,60.),labels=[0,0,0,1],fontsize=12)
cb=rob_transform.colorbar(cs,location='right',pad='10%',fig=fig2)
#cb.set_ticks([-9000,0,6000], update_ticks=True)
#cb.set_label('height (m)')
axis2.set_title('topo B, robinson projection')
fig2.canvas.draw()
#make a png file for handin
plotfile='{0:s}/rob.png'.format((dirname))
fig2.savefig(plotfile)



plt.show()
