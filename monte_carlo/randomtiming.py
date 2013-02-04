"""
   demonstrate how to use a processor pool to
   generate random numbers in parallel
"""

import matplotlib.pyplot as plt
from numpy.random.mtrand import RandomState as randomstate
from multiprocessing import Pool
import numpy as np
import time
#
# try generating random numbers on multiple processors
# using the multiprocessing module
#
#  here is the function we will call in each process
#
def makenums(seed,the_size):
    random=randomstate(seed=seed)
    return random.uniform(size=the_size)

if __name__=="__main__":
    #
    # now get a pool of processors
    #
    numprocs=2
    p = Pool(numprocs)
    #
    # choose different seeds to make sure 
    # generators are independent
    #
    seeds=[123,987]
    the_size=5.e6
    jobs = list()
    #
    # now send the makenums job out to the processors,
    # and retrieve the results, keep track of the time
    #
    tic=time.clock()
    for i in range(numprocs):
        the_seed=seeds[i]
        jobs.append(p.apply_async(makenums, (the_seed,the_size)))
    #
    # put the results in a new list
    #
    out=[j.get() for j in jobs]
    p.close()
    toc=time.clock()
    print "two processor time is {0:5.4e} seconds".format((toc-tic))
    #
    # repeat this with a single process
    #
    tic=time.clock()
    seed=12345
    randomval=randomstate(seed=seed)
    #
    # double the size since we only have one processor
    #
    the_size=the_size*2.
    out=randomval.uniform(size=the_size)
    toc=time.clock()
    print "one processor time is {0:5.4e} seconds".format((toc-tic))

