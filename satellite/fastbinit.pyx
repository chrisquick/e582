import numpy as np
cimport numpy as np
from libc.stdint cimport int32_t
cimport cython
from libc.stdio cimport printf

@cython.cdivision(True)
@cython.wraparound(False)
@cython.boundscheck(False)
def do_bins(object self, object data_vec):
    data_vec=np.ascontiguousarray(data_vec)
    data_vec=data_vec.astype(np.float64)
    cdef double* dataPtr= <double*> np.PyArray_DATA(data_vec) 
    cdef double binsize=self.binsize
    cdef np.int32_t[:] bin_index=np.empty([data_vec.size],dtype=np.int32)
    cdef np.int32_t[:] bin_count=np.zeros([self.numbins],dtype=np.int32)
    cdef int lowcount=0
    cdef int highcount=0
    cdef int tot_loops=data_vec.size
    cdef int i
    cdef double float_bin
    cdef double data_val
    cdef int ibin
    cdef double minval=self.minval
    cdef int missingLowValue=self.missingLowValue
    cdef int missingHighValue =self.missingHighValue
    cdef int numbins=self.numbins
    cdef double dataval

    for i in range(tot_loops):
        dataval=dataPtr[i]
        float_bin =  ((dataval - minval) /binsize)
        if float_bin < 0:
            lowcount+=1
            bin_index[i]=missingLowValue
            continue
        if float_bin > numbins:
            highcount += 1
            bin_index[i] = missingHighValue
            continue
        ibin=<int> float_bin
        bin_count[ibin]+=1
        bin_index[i]=ibin
    return (np.asarray(bin_count),np.asarray(bin_index),lowcount,highcount)

def hist_latlon(object lats,object lons,object rads,object bin_lats,object bin_lons):

    lats=lats.ravel()
    lons=lons.ravel()
    lat_count,lat_index,lowlats,highlats=bin_lats.do_bins(lats)    
    lon_count,lon_index,lowlons,highlons=bin_lons.do_bins(lons)    
    out_vals=np.empty([bin_lats.numbins,bin_lons.numbins],dtype=np.object)

    cdef int numlatbins=bin_lats.numbins
    cdef int numlonbins=bin_lons.numbins
    cdef int num_datapts=<int>lat_index.size
    cdef int row,col, data_index, grid_row,grid_col,rows,cols


    cdef int[:] lat_view=lat_index
    cdef int[:] lon_view=lon_index
    
    for row in range(numlatbins):
        for col in range(numlonbins):
            out_vals[row,col]=list()

    for data_index in range(num_datapts):
        grid_row=lat_index[data_index]
        grid_col=lon_index[data_index]
        if grid_row < 0 or grid_col < 0:
            continue
        else:
            out_vals[grid_row,grid_col].append(data_index)

    cdef float[:,:] rad_grid=np.empty_like(out_vals,dtype=np.float32)
    cdef float[:,:] lat_grid=np.empty_like(out_vals,dtype=np.float32)
    cdef float[:,:] lon_grid=np.empty_like(out_vals,dtype=np.float32)
    rows,cols=out_vals.shape
    flat_chan31=rads.ravel()

    for row in range(rows):
        for col in range(cols):
            rad_list=out_vals[row,col]
            if len(rad_list)==0:
                rad_grid[row,col]=np.nan
                lat_grid[row,col]=np.nan
                lon_grid[row,col]=np.nan
            else:
                rad_vals=np.take(flat_chan31,rad_list)
                lat_vals=np.take(lats,rad_list)
                lon_vals=np.take(lons,rad_list)
                rad_grid[row,col]=np.mean(rad_vals)
                lat_grid[row,col]=np.mean(lat_vals)                    
                lon_grid[row,col]=np.mean(lon_vals)                    

    return np.asarray(lat_grid),np.asarray(lon_grid),np.asarray(rad_grid)

