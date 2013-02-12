import numpy as np
import fasthist as fh

the_length=15
test=np.ones([the_length],dtype=np.float32)
new_hist=fh.pyhist(test)
print new_hist.get_data()
print new_hist.indata
