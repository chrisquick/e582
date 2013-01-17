"""
   Demonstrate a random number generator using the Day 4
   beta example
"""
import matplotlib.pyplot as plt
from numpy.random.mtrand import RandomState as randomstate
import numpy as np
import numpy.random as nr
random1=randomstate(seed=5)
size=int(10.e6)
beta= 1./3.
out=random1.uniform(size=size)
xval=-1./beta*np.log( 1. - out)
fig1=plt.figure(1)
fig1.clf()
ax1=fig1.add_subplot(111)
ax1.hist(out)

fig2=plt.figure(2)
fig2.clf()
ax2=fig2.add_subplot(111)
pdf,bins,patches=ax2.hist(xval,bins=np.arange(0,30.,0.01),normed=True)
ax2.set_xlim(0,10)
test_norm=np.sum(pdf*np.diff(bins))
print test_norm
xval_an=np.linspace(0.,10.,300.)
an_fun=beta*np.exp(-beta*xval_an)
line=ax2.plot(xval_an,an_fun,lw=5)
plt.show()


