import numpy as np
cimport numpy as np
from libc.stdint cimport int32_t
cimport cython

@cython.cdivision(True)
@cython.wraparound(False)
@cython.boundscheck(False)
def do_bins(object self, object data_vec):
    data_vec=np.ascontiguousarray(data_vec)
    data_vec=data_vec.astype(np.float32)
    cdef float* dataPtr= <float*> np.PyArray_DATA(data_vec) 
    cdef float binsize=self.binsize
    cdef np.int32_t[:] bin_index=np.empty([data_vec.size],dtype=np.int32)
    cdef np.int32_t[:] bin_count=np.zeros([self.numbins],dtype=np.int32)
    cdef int lowcount=0
    cdef int highcount=0
    cdef int tot_loops=data_vec.size
    cdef int i
    cdef float float_bin
    cdef float data_val
    cdef int ibin
    cdef float minval=self.minval
    cdef int32_t missingLowValue=self.missingLowValue
    cdef int32_t missingHighValue =self.missingHighValue
    cdef int numbins=self.numbins
    cdef float dataval
    
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
        bin_index[ibin]=ibin
    return (np.asarray(bin_count),np.asarray(bin_index),lowcount,highcount)




