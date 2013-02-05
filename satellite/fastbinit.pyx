import numpy as np
cimport numpy as np

def do_bins(object self, object data_vec):
    data_vec=np.ascontiguousarray(data_vec)
    data_vec=data_vec.astype(np.float32)
    cdef float* dataPtr= <float*> np.PyArray_DATA(data_vec) 
    cdef float binsize=self.binsize
    cdef np.float32_t[:] data_view=data_vec
    cdef np.int32_t[:] bin_index=np.empty([data_vec.size],dtype=np.int32)
    cdef np.int32_t[:] bin_count=np.zeros([self.numbins],dtype=np.int32)
    cdef int lowcount=0
    cdef int highcount=0
    cdef int tot_loops=data_vec.size
    cdef int i
    cdef float float_bin
    cdef float data_val
    cdef int ibin
    
    for i in range(tot_loops):
        dataval=data_vec[i]
        float_bin =  ((dataval - self.minval) /binsize)
        if float_bin < 0:
            lowcount+=1
            bin_index[i]=self.missingLowValue
            continue
        if float_bin > self.numbins:
            highcount += 1
            bin_index[i] = self.missingHighValue
            continue
        ibin=<int> float_bin
        bin_count[ibin]+=1
        bin_index[ibin]=ibin
    return (np.asarray(bin_count),np.asarray(bin_index),lowcount,highcount)




