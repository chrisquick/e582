
2013/Feb/07
__________

New code:

coakley.py -- uses hist_latlon, borrowed from plot_rads.py, to
produce a lat/lon gridded radiance field.  Plotting is done
using pcolor instead of contourf

fastbinit.pyx now contains cythonized versions of both
do_bins  and hist_latlon

compile as before with:

python setup_fast.py build_ext --inplace

and run with

python coakley.py

git tag is coakley1 on master branch


2013/Feb/12
___________

added

fast_coakley.py which uses a new cython class in
fasthist.pyx and gets a speedup of about 350
over the histogram in plot_rads.py

* thursday feb 14
-----------------

add scatter/angles.py working with the scattering angle
and Stevens equation A1.3

added new method to fast_coakley.py to sum counts
in each bin and return the 2-d histogram:

    new_hist=fh.pyhist(partLats,partLons,bin_lats,bin_lons)
    hist2d=new_hist.get_hist2d()



