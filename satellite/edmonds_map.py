"""
  zoom the top map to the area around edmonds, wa
"""

from mpl_toolkits.basemap import Basemap, shiftgrid
import numpy as np
import matplotlib.pyplot as plt

from plot_rads import make_dir

#
# write the png files to the plots directory
#
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
rob_transform = Basemap(projection='robin',lon_0=lon_mid,ax=axis1)

# make filled contour plot.
#
# what is the purpose of this line?
#
lon_array,lat_array=np.meshgrid(lons, lats)
x,y=rob_transform(lon_array,lat_array)
#do a filled contour plot of the topography
cs = axis1.contourf(x,y,etopo,30,cmap=plt.cm.jet)
# draw coastlines.
rob_transform.drawcoastlines()
# draw parallels and meridians.
rob_transform.drawparallels(np.arange(-60.,90.,30.),labels=[1,0,0,0])
rob_transform.drawmeridians(np.arange(0.,360.,60.),labels=[0,0,0,1],fontsize=12)
cb=rob_transform.colorbar(cs,location='bottom',pad='10%',fig=fig1)
cb.set_ticks([-9000,0,6000], update_ticks=True)
cb.set_label('height (m)')

# add a title.
axis1.set_title('Robinson Projection, Edmonds, WA')
#
# google lat and lon for edmonds, convert from degrees west longitude
# to degrees east longitude
#
my_lat=47.8108
my_lon=360. - 122.3761
#convert to plotting coordinates
xpoint,ypoint=rob_transform(my_lon,my_lat)
axis1.plot(xpoint,ypoint,'b.',markersize=15)
view_width=15
#
# set the axis limits to show only a box of width view_width
#
axis1_xlim,axis1_ylim=rob_transform([my_lon - view_width, my_lon + view_width],\
                                  [my_lat - view_width, my_lat + view_width])
box_width=5  #my box is 10 degrees wide
#                   ll              ul               ur                 lr              ll
corner_lats=[my_lat-box_width,my_lat+box_width,my_lat+box_width,my_lat-box_width,my_lat-box_width]
corner_lons=[my_lon-box_width,my_lon-box_width,my_lon+box_width,my_lon+box_width,my_lon-box_width]
#convert to plotting cooridinates
x_coord,y_coord=rob_transform(corner_lons,corner_lats)
axis1.plot(x_coord,y_coord,'b-',linewidth=5)
axis1.set_xlim(axis1_xlim)
axis1.set_ylim(axis1_ylim)
fig1.subplots_adjust(left=0.0,right=1.0)
fig1.canvas.draw()
#make a png file for handin
plotfile='{0:s}/robinson.png'.format((dirname))
fig1.savefig(plotfile)

#
# now do lambert conformal conic
#

fig2=plt.figure(2,figsize=(4,5),dpi=150)
fig2.clf()
axis2 = fig2.add_subplot(111)

#cid = fig1.canvas.mpl_connect('button_press_event', onclick)


lcc_transform = Basemap(width=3000000,height=2400000,
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',area_thresh=1000.,projection='lcc',\
            lat_1=45,lat_2=55,lat_0=47.8,lon_0=-122.)

# make filled contour plot.
#
# what is the purpose of this line?
#
lon_array,lat_array=np.meshgrid(lons, lats)
x,y=lcc_transform(lon_array,lat_array)
#do a filled contour plot of the topography
cs = axis2.contourf(x,y,etopo,30,cmap=plt.cm.jet)
# draw coastlines.
lcc_transform.drawcoastlines()
# draw parallels and meridians.
lcc_transform.drawparallels(np.arange(-60.,90.,30.),labels=[1,0,0,0])
lcc_transform.drawmeridians(np.arange(0.,360.,60.),labels=[0,0,0,1],fontsize=12)
cb=lcc_transform.colorbar(cs,location='bottom',pad='10%',fig=fig2)
cb.set_ticks([-9000,0,6000], update_ticks=True)
cb.set_label('height (m)')
# add a title.
axis2.set_title('LCC Projection, Edmonds, WA')
xpoint,ypoint=lcc_transform(my_lon,my_lat)
axis2.plot(xpoint,ypoint,'b.',markersize=15)
view_width=15
axis2_xlim,axis2_ylim=lcc_transform([my_lon - view_width, my_lon + view_width],\
                                  [my_lat - view_width, my_lat + view_width])
x_coord,y_coord=lcc_transform(corner_lons,corner_lats)
axis2.plot(x_coord,y_coord,'b-',linewidth=5)
axis2.set_xlim(axis2_xlim)
axis2.set_ylim(axis2_ylim)
fig2.subplots_adjust(left=0.,right=1.0)
fig2.canvas.draw()
#make a png file for handin
plotfile='{0:s}/lcc.png'.format((dirname))
fig2.savefig(plotfile)


plt.show()
