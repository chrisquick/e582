from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from numpy import pi,cos,arccos

#take two angles that differby
#by 0.1 rads:
theta=pi/4.
thetaPrime=pi/4. + 0.1
mu=cos(theta)
muPrime=cos(thetaPrime)
phi=np.arange(0.,2*pi,0.01)
cosTHETA=mu*muPrime + (1-mu**2.)**0.5*(1-muPrime**2.)**0.5*cos(phi)
THETA=arccos(cosTHETA)
print('theta={0:5.3f} radians={1:5.3f}=degrees'.format(theta,theta*180./pi))
print('thetaprime={0:5.3f} radians ={1:5.3f} degrees'.format(thetaPrime,thetaPrime*180./pi))
print('arccosine of THETA at (phi-phiprime)=0 is {0:3.1f} rads ={1:5.2f} degrees'.format(arccos(cosTHETA[0]),arccos(cosTHETA[0])*180./pi))
print('average cosTHETA for phi=0 to 2pi: {0:5.3f}'.format(sum(cosTHETA)/len(cosTHETA)))
print('average THETA (radians): {0:5.3f}'.format(THETA.mean()))
print('average THETA (degrees): {0:5.3f}'.format(THETA.mean()*180./pi))
print('mu x muPrime: {0:5.3f}'.format(mu*muPrime))
print('arccos of mu x muprime (radians): {0:5.3f}'.format(arccos(mu*muPrime)))
print('in degrees this is: {0:5.3f}'.format(arccos(mu*muPrime)*180./pi))
print('so cos of average doesnt equal average of cos')

fig1=plt.figure(1)
fig1.clf()
ax1=fig1.add_subplot(111)
ax1.plot(phi*180./pi,cosTHETA)
ax1.set_title('plot of cos $\Theta$ vs. $\phi$ (average=0.448, arccos=63.4 degrees)')
ax1.set_xlabel('$\phi$ (degrees)')
ax1.set_ylabel('cos $\Theta$')
fig1.canvas.draw()

fig2=plt.figure(2)
fig2.clf()
ax2=fig2.add_subplot(111)
ax2.plot(phi*180./pi,THETA*180./pi)
ax2.set_title('$\Theta$ as  a function of $\phi$ (average=58.7 degrees)')
ax2.set_xlabel('$\phi$ (degress)')
ax2.set_ylabel('$\Theta$ (degrees)')
fig2.canvas.draw()

plt.show()






