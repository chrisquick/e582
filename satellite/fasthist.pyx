import numpy as np
cimport numpy as np
from libcpp.vector cimport vector

cdef extern from "histo.hpp" namespace "hist":
    cdef cppclass Histo:
        Histo(int numlatbins,int numlonbins,int num_datapts,int *lat_index,\
                                 int *lon_index) except +
        vector[int] get_vec(int row, int col)
        void get_mean(float *datain,float *meanout)
        void get_hist2d(int *histout)

cdef class pyhist:
    cdef Histo *thisptr      # hold a C++ instance which we're wrapping
    cdef float[:] lat_view
    cdef float[:] lon_view
    cdef int[:] lat_index_view
    cdef int[:] lon_index_view
    cdef int numlatbins
    cdef int numlonbins
    cdef int num_datapts
    
    def __cinit__(self, object lats, object lons, object bin_lats, object bin_lons):
        lats=lats.ravel()
        lons=lons.ravel()
        lat_count,lat_index,lowlats,highlats=bin_lats.do_bins(lats)    
        lon_count,lon_index,lowlons,highlons=bin_lons.do_bins(lons)    
        self.numlatbins=bin_lats.numbins
        self.numlonbins=bin_lons.numbins
        self.num_datapts=<int>lat_index.size
        self.lat_view=lats
        self.lon_view=lons
        self.lat_index_view=lat_index
        self.lon_index_view=lon_index
        self.thisptr = new Histo(self.numlatbins,self.numlonbins,self.num_datapts, 
                                 <int*> np.PyArray_DATA(lat_index), <int*> np.PyArray_DATA(lon_index))

    def get_vec(self,int row, int col):
        out=self.thisptr.get_vec(row,col)
        return out

    def get_hist2d(self):
        hist2d=np.zeros([self.numlatbins,self.numlonbins],dtype=np.int32)
        self.thisptr.get_hist2d(<int*> np.PyArray_DATA(hist2d))
        return hist2d
                   
    def get_mean(self,object data_vec):
        data_vec=data_vec.astype(np.float32)
        grid_mean=np.empty([self.numlatbins,self.numlonbins],dtype=np.float32)
        grid_mean[:,:]=np.nan
        self.thisptr.get_mean(<float*> np.PyArray_DATA(data_vec),<float*> np.PyArray_DATA(grid_mean))
        return grid_mean
        
    def __dealloc__(self):
        del self.thisptr


