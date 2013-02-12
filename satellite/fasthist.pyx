import numpy as np
cimport numpy as np

cdef extern from "histo.hpp" namespace "hist":
    cdef cppclass Histo:
        Histo(np.float32_t* indata) except +
        float* indata

cdef class pyhist:
    cdef Histo *thisptr      # hold a C++ instance which we're wrapping
    cdef float[:] indata_view
    def __cinit__(self, object indata):
        self.indata_view=indata
        self.thisptr = new Histo(<float*> np.PyArray_DATA(indata))
    def get_data(self):
        return np.asarray(self.indata_view)
    @property
    def indata(self):
        return np.asarray(self.indata_view)
    def __dealloc__(self):
        del self.thisptr

the_length=15        
test=np.ones([the_length],dtype=np.float32)
cdef Histo* try_this=new Histo(<float*> np.PyArray_DATA(test))

