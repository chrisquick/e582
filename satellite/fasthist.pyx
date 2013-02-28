#cython: embedsignature=True
import numpy as np
cimport numpy as np
from libcpp.vector cimport vector

cdef extern from "histo.hpp" namespace "hist":
    cdef cppclass Histo:
        Histo(int numrowbins,int numcolbins,int num_datapts,int *row_index,\
                                 int *col_index) except +
        vector[int] get_vec(int row, int col)
        void get_mean(float *datain,float *meanout)
        void get_hist2d(int *histout)

cdef class pyhist:
    """
      cython wrapper around Histo.cpp
    """
    cdef Histo *thisptr      # hold a C++ instance which we're wrapping
    cdef float[:] col_view
    cdef int[:] row_index_view
    cdef int[:] col_index_view
    cdef int numrowbins
    cdef int numcolbins
    cdef int num_datapts
    
    def __cinit__(self, object row_vals, object col_vals, object bin_row_vals, object bin_col_vals):
        row_vals=row_vals.ravel()
        col_vals=col_vals.ravel()
        row_count,row_index,lowrow_vals,highrow_vals=bin_row_vals.do_bins(row_vals)    
        col_count,col_index,lowcol_vals,highcol_vals=bin_col_vals.do_bins(col_vals)    
        self.numrowbins=bin_row_vals.numbins
        self.numcolbins=bin_col_vals.numbins
        self.num_datapts=<int>row_index.size
        self.col_view=col_vals
        self.row_index_view=row_index
        self.col_index_view=col_index
        self.thisptr = new Histo(self.numrowbins,self.numcolbins,self.num_datapts, 
                                 <int*> np.PyArray_DATA(row_index), <int*> np.PyArray_DATA(col_index))

    def get_vec(self,int row, int col):
        """
          return a  row of gridded data
        """  
        out=self.thisptr.get_vec(row,col)
        return np.asarray(out)

    def get_hist2d(self):
        hist2d=np.zeros([self.numrowbins,self.numcolbins],dtype=np.int32)
        self.thisptr.get_hist2d(<int*> np.PyArray_DATA(hist2d))
        return hist2d
                   
    def get_mean(self,object data_vec):
        data_vec=data_vec.astype(np.float32)
        grid_mean=np.empty([self.numrowbins,self.numcolbins],dtype=np.float32)
        grid_mean[:,:]=np.nan
        self.thisptr.get_mean(<float*> np.PyArray_DATA(data_vec),<float*> np.PyArray_DATA(grid_mean))
        return grid_mean
        
    def __dealloc__(self):
        del self.thisptr


