import numpy as np
    
def ascontiguous(a):
    """ascontiguous(a) -> contiguous representation of a.

    If 'a' is allready contiguous, it is returned unchanged. Otherwise, a contiguous copy
    is returned.
   """
    a = np.asarray(a)
    if not a.flags['C_CONTIGUOUS']:
       a = np.array(a)
    return a

def flipud(value):
    print "\nflipping up/down"
    value=value[::-1,:]
    value=ascontiguous(value)
    return value

def fliplr(value):
    print "\nflipping left/right"
    value=value[:,::-1]
    value=ascontiguous(value)
    return value

def orient(lat,lon,values):
    """
       parameters
       ----------

       lat: 2d array (float)
          array of pixel latitudes
       lon: 2d array (float)
          array of pixel longitudes
       values: 2d array (float)
          array of scene radiances

       returns
       -------

       (lats,lons,values)
          three arrays flipped so that row 0 is south and
          col 0 is west
    """
    minlat=np.where(lat==lat.min())
    maxlat=np.where(lat==lat.max())
    minlon=np.where(lon==lon.min())
    maxlon=np.where(lon==lon.max())
    flippedFields=values[:,:]  #make a copy
    if len(minlat[0]) != 1:
        raise ValueError("more than one pixel has minimum lattidue? %s" % repr(minlat))
    if len(maxlat[0]) != 1:
        raise ValueError("more than one pixel has maximum lattidue? %s" % maxlat)
    if len(minlon[0]) != 1:
        raise ValueError("more than one pixel has minimum longitude? %s" % minlon)
    if len(maxlon[0]) != 1:
        raise ValueError("more than one pixel has maximum longitude? %s" % maxlon)
    if minlat[0] > maxlat[0]:
        #put smallest latitude in smallest row
        print "preparing to flip up/down"
        lat=flipud(lat)
        lon=flipud(lon)
        flippedFields=flipud(flippedFields)
    if minlon[1] > maxlon[1]:
        #put smallest (most negative) longitude  in smallest column
        print "preparing to flip left/right"
        lat=fliplr(lat)
        lon=fliplr(lon)
        flippedFields=fliplr(flippedFields)
    return (lat,lon,flippedFields)
