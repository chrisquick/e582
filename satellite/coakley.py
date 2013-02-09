import pyhdf.SD
from binit import binit, fastbin
from modismeta import metaParse
import glob
from orient import orient
import numpy as np
import time
import matplotlib.pyplot as plt
from fastbinit import hist_latlon as fasthist

#
# now make sure we get the same counts in each bin
# as the numpy histogram routine
#

binit_class=fastbin

#
# here's the slow version of hist_latlon -- taken from
# the plot_rads.py script
#
def hist_latlon(lats,lons,rads,bin_lats,bin_lons):

    lat_count,lat_index,lowlats,highlats=bin_lats.do_bins(partLats.ravel())    
    lon_count,lon_index,lowlons,highlons=bin_lons.do_bins(partLons.ravel())    
    out_vals=np.empty([bin_lats.numbins,bin_lons.numbins],dtype=np.object)
    for row in range(bin_lats.numbins):
        for col in range(bin_lons.numbins):
            out_vals[row,col]=list()

    for data_index in range(lat_index.size):
        grid_row=lat_index[data_index]
        grid_col=lon_index[data_index]
        if grid_row < 0 or grid_col < 0:
            continue
        try:
            out_vals[grid_row,grid_col].append(data_index)
        except:
            print "trouble at: data_index {0:d}, gives {1:d},{2:d}".format(data_index,grid_row,grid_col)

    rad_grid=np.empty_like(out_vals,dtype=np.float)
    lat_grid=np.empty_like(out_vals,dtype=np.float)
    lon_grid=np.empty_like(out_vals,dtype=np.float)
    rows,cols=rad_grid.shape
    flat_chan31=rads.ravel()
    for the_row in range(rows):
        for the_col in range(cols):
            rad_list=out_vals[the_row,the_col]
            if len(rad_list)==0:
                rad_grid[the_row,the_col]=np.nan
                lat_grid[the_row,the_col]=np.nan
                lon_grid[the_row,the_col]=np.nan
            else:
                try:
                    rad_vals=np.take(flat_chan31,rad_list)
                    lat_vals=np.take(partLats.ravel(),rad_list)
                    lon_vals=np.take(partLons.ravel(),rad_list)
                    rad_grid[the_row,the_col]=np.mean(rad_vals)
                    lat_grid[the_row,the_col]=np.mean(lat_vals)                    
                    lon_grid[the_row,the_col]=np.mean(lon_vals)                    
                except IndexError:
                    print "oops: ",rad_list
    return lat_grid,lon_grid,rad_grid


class hist_class(object):

    def __init__(self,lats,lons,rads,bin_lats,bin_lons):
        self.lats=lats.ravel()
        self.lons=lons.ravel()
        self.rads=rads.ravel()
        self.bin_lats=bin_lats
        self.bin_lons=bin_lons
        self.lat_count,self.lat_index,self.lowlats,self.highlats=bin_lats.do_bins(lats)    
        self.lon_count,self.lon_index,self.lowlons,self.highlons=bin_lons.do_bins(lons)    
        self.out_vals=np.empty([bin_lats.numbins,bin_lons.numbins],dtype=np.object)

    def calc_vals(self):

        numlatbins=self.bin_lats.numbins
        numlonbins=self.bin_lons.numbins

        for row in range(numlatbins):
            for col in range(numlonbins):
                self.out_vals[row,col]=list()
        num_datapts=self.lats.size
        for data_index in range(num_datapts):
            grid_row=self.lat_index[data_index]
            grid_col=self.lon_index[data_index]
            if grid_row < 0 or grid_col < 0:
                continue
            else:
                self.out_vals[grid_row,grid_col].append(data_index)

    def calc_mean(self):
        
        self.calc_vals()
        rad_grid=np.empty_like(self.out_vals,dtype=np.float32)
        lat_grid=np.empty_like(self.out_vals,dtype=np.float32)
        lon_grid=np.empty_like(self.out_vals,dtype=np.float32)
        rows,cols=self.out_vals.shape
        
        for row in range(rows):
            for col in range(cols):
                rad_list=self.out_vals[row,col]
                if len(rad_list)==0:
                    rad_grid[row,col]=np.nan
                    lat_grid[row,col]=np.nan
                    lon_grid[row,col]=np.nan
                else:
                    rad_vals=np.take(self.rads,rad_list)
                    lat_vals=np.take(self.lats,rad_list)
                    lon_vals=np.take(self.lons,rad_list)
                    rad_grid[row,col]=np.mean(rad_vals)
                    lat_grid[row,col]=np.mean(lat_vals)                    
                    lon_grid[row,col]=np.mean(lon_vals)                    

        return np.asarray(lat_grid),np.asarray(lon_grid),np.asarray(rad_grid)


    

if __name__=="__main__":

    from matplotlib.colors import Normalize
    from matplotlib import cm
    cmap=cm.RdBu_r
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
    fullLats=sdgeom.select('Latitude')
    fullLats=fullLats.get()
    fullLons=sdgeom.select('Longitude')
    fullLons=fullLons.get()
    sdgeom.end()
    model2_file='*D021KM*{0:s}*hdf'.format(granule_info)
    model2_file=glob.glob(model2_file)[0]
    sdrad=pyhdf.SD.SD(model2_file)
    longWave=sdrad.select('EV_1KM_Emissive')

    allRadiances=longWave.get()
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
    chan31 = scale31 * (chan31 - offset31)
    sdrad.end()
    fullLats,fullLons,chan31=orient(fullLats,fullLons,chan31)
    #
    # get the bounding box to set the lat/lon grid 
    #
    north,south,east,west=meta_data['nsew']
    #
    # select none here to see the full image
    #
    max_rows= 500
    max_cols= 500
    partLats=fullLats[:max_rows,:max_cols]
    partLons=fullLons[:max_rows,:max_cols]
    partRads=chan31[:max_rows,:max_cols]

    numlatbins=2
    numlonbins=2

    bin_lats=binit_class(south,north,numlatbins,-999,-888)
    bin_lons=binit_class(west,east,numlonbins,-999,-888)

    #slow version
    tic=time.clock()
    slowlat_grid,slowlon_grid,slowrad_grid=hist_latlon(partLats,partLons,partRads,bin_lats,bin_lons)
    slowtime=time.clock() - tic

    #fast version
    tic=time.clock()
    #lat_grid,lon_grid,rad_grid=fasthist(partLats,partLons,partRads,bin_lats,bin_lons)
    the_hist=hist_class(partLats,partLons,partRads,bin_lats,bin_lons)
    lat_grid,lon_grid,rad_grid=the_hist.calc_mean()
    fasttime=time.clock() - tic
    ## print "slow and fast plus speedup: ",slowtime,fasttime,slowtime/fasttime
    np.testing.assert_almost_equal(slowrad_grid,rad_grid)
    lon_centers=bin_lons.get_centers()
    lat_centers=bin_lats.get_centers()

    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(111)
    im=axis1.pcolor(lon_centers,lat_centers,rad_grid,cmap=cmap,\
                      norm=the_norm)
    cb=plt.colorbar(im,extend='both')
    the_label=cb.ax.set_ylabel('radiances ($W\,m^{-2}\,{\mu m}^{-1}\,sr^{-1}$)',rotation=270)
    axis1.set_title('MODIS channel 31 radiances (lat/lon binned)')
    plt.show()


