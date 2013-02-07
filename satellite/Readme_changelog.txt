
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







