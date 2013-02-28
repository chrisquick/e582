"""Python script to do monte carlo scattering with a Henyey Greenstein
   phase function.  It calculates direct and diffuse fluxes at specified
   tau levels, and the bidirectional reflectivity at cloud top
   Output is stored in binary pickle files, with the filename taken from
   the name of the computer and process id of the run.   I use
   this with a shell script to get multiple simultaneous runs on a
   multiprocessor machine
"""

import scipy.io as sio
import numpy as np
from numpy import cos,sin,pi,arctan2,floor,arccos
import matplotlib.pyplot as plt
import time,copy,pickle,os
import argparse
from numpy.random import RandomState as rn
from configobj import ConfigObj


class mcstruct:
    """empty struct to hold
       statistics
    """
    pass

def findbin(tottau,tauvalue,nbins):
    """Find the fractional distance travelled and
       convert that into a bin number
    """
    return int(np.floor(np.abs(tauvalue)/tottau*nbins))

if __name__=="__main__":

#
#  get the host name to generate unique filename and
#  random number seed for multiprocessor runs
#

    start=time.time()
    uname=os.uname()
    hostname=uname[1]

    parser = argparse.ArgumentParser()

    parser.add_argument('configfile', type=str,help="name of configuration file")
    args=parser.parse_args()

    config = ConfigObj(args.configfile,unrepr=True)
    vals=config['fluxes']
    radvals=config['radiances']
    nphotons=vals['nphotons']

    #
    # include the process id in the output file name
    #
    pid=os.getpid()
    outprefix=vals['outprefix']
    outfile="%s_%s_%d.pic" % (outprefix,hostname,pid,)
    outpic=open(outfile,'w')

    do_plot=True

    do_print=False

    do_debug=False

    # Propagate a given number of photons through the cloud.
 
    # Set the state of the random number generator in order to reproduce the
    # results.
    #
    # use the clock for a seed
    #
    thetime=time.time()
    intpart=int(np.floor(thetime))
    fracpart=int(np.floor((thetime - intpart)*1.e11))
    intseed=[intpart,fracpart,pid]
    decname=[ord(i) for i in hostname]
    intseed.extend(decname)
    print "using seed: ",intseed

    if do_print:
        print "seed: ",intseed
    rs = np.random.RandomState(intseed)
    #rs = np.random.RandomState([12345678, 90123456, 78901234])

    # Optical thickness of the cloud.
    F0=vals['F0'] #W/m^2
    cldtau = vals['cldtau']
    nbins=vals['ntaubins']
    halfwidth=cldtau/nbins/2.
    #
    # we want to find the cneter of each bin, there are
    # nbins layers and nbins+1 levels
    # tau=0 is at the top of bin 0
    #
    center_taus=np.linspace(0.,cldtau,nbins,endpoint=False) + halfwidth
    # Asymmetry parameter.
    g = vals['g']
    # Single scatter albedo.
    ssa = vals['ssa']
    # Number of photons.

    # Initial propagation direction.
    theta0 = vals['theta0_deg'] / 180.*np.pi
    phi0 = vals['phi0_deg'] / 180.*np.pi

    # Initialise a field for the statistics.
    mcstats=mcstruct()

    mcstats.directtrans = 0
    mcstats.albedo = 0
    mcstats.diffusetrans = 0
    mcstats.nthetabins=radvals['nthetabins']
    mcstats.nphibins=radvals['nphibins']
    mcstats.phi_angles=np.linspace(radvals['lowphi'],radvals['hiphi'],mcstats.nphibins) #degrees
    delphi=mcstats.phi_angles[1] - mcstats.phi_angles[0]*pi/180. #radians
    mcstats.theta_angles=np.linspace(radvals['lowtheta'],radvals['hitheta'],mcstats.nthetabins) #degrees
    deltheta=mcstats.theta_angles[1] - mcstats.theta_angles[0]*pi/180. #radians
    mcstats.angle_bins=np.zeros([mcstats.nthetabins,mcstats.nphibins],dtype=np.float)
    delomega=2*pi/(mcstats.nphibins*mcstats.nthetabins)
    mcargs=mcstruct()
    mcargs.g=g
    mcargs.cldtau=cldtau
    mcargs.ssa=ssa
    mcargs.nphotons=nphotons
    mcargs.theta0_deg=vals['theta0_deg']
    mcargs.phi0=phi0
    mcargs.F0=F0

    path=[]

    #
    # start a plot
    #
    if do_plot:
        fig=plt.figure(1)
        fig.clf()
        ax1=fig.add_subplot(111)
 
    isup={-1:False,1:True}
    upcolor={-1:'red',1:'green'}
    upwords={-1:'down',1:'up'}
    directflux=np.zeros([nbins])
    diffuseflux={}
    diffuseflux['up']=np.zeros([nbins])
    diffuseflux['down']=np.zeros([nbins])
    scatternum=[]
    for nph in range(nphotons):
        #
        # direct flux will always enter the first bin
        #
        directflux[0] += 1
        if np.mod(nph,500)==0:
            print "processor, photon %d: %d" % (pid,nph)
        # Compute initial propagation vector in model coordinates: This is the
        # initial z-axis of the photon coordinate system, rotated into model
        # coordinates.  Note the minus sign on the the z coordinate, because
        # we are defining the zenith angle looking towards the sun, not
        # in the direction of the solar photons
        km = np.array([sin(theta0)*cos(phi0), sin(theta0)*sin(phi0), -cos(theta0)])

        # We start with the photon at cloud top.
        ktauz = 0

        # Track the path of the photon for plotting.
        path.append(np.array([0., 0., 0.]))
        ip = 0

        # Absorption weight of the photon.
        abswght = 1.0
        oldbin=0
        while True:
            # Compute the optical distance taup travelled by the photon.
            randdev=rs.uniform()
            taup = -np.log(1-randdev)

            # Compute the vertical displacement in the cloud.
            ktauz = ktauz - taup*km[2]
            # Compute the new position of the photon.
            path.append(path[ip] - np.dot(taup,km))
            newtau=ktauz

            ip = ip+1

            # Check if the photon has left the cloud.
            if ktauz <= 0:
                # Photon has left at cloud top. Reflected photon,
                # moving upward.  Add the weight to all
                # bins it travels through
                newbin=0
                bins=np.arange(newbin,oldbin)
                diffuseflux['up'][bins] += abswght
                mcstats.albedo = mcstats.albedo + abswght
                scatternum.append(ip)
                ctmu=km[2]
                cttheta = arccos(ctmu)
                cttheta=cttheta*180./pi;  #degrees
                ctphi = arctan2(km[1],km[0])*180./pi;  #degrees
                if ctphi < 0: # atan2 returns phi[-pi..pi], convert to [0..2pi].
                    ctphi = ctphi + 360.
                #
                # find the theta,phi bin
                #
                frac_dist_theta=(cttheta - radvals['lowtheta'])/(radvals['hitheta'] - radvals['lowtheta'])
                if (frac_dist_theta < 0) or (frac_dist_theta >= 1.):
                    break
                frac_dist_phi=(ctphi - radvals['lowphi'])/(radvals['hiphi'] - radvals['lowphi'])
                if (frac_dist_phi < 0) or (frac_dist_phi >= 1.):
                    break
                thetabin = floor(frac_dist_theta*mcstats.nthetabins);
                phibin = floor(frac_dist_phi*mcstats.nphibins);
                #
                # see Petty Monte Carlo notes section 4.6
                #
                mcstats.angle_bins[thetabin, phibin] += abswght/ctmu/delomega;
                #
                # units are weight/sr
                #
                break
            if ktauz >= cldtau:
                # Photon has left at cloud bottom. Direct or diffuse
                # transmittance, moving downwards
                # add the weight to all bins it travels through
                newbin=nbins
                bins=np.arange(oldbin+1,newbin)
                if ip == 1:
                    mcstats.directtrans = mcstats.directtrans + abswght
                    directflux[bins] += abswght
                else:
                    mcstats.diffusetrans = mcstats.diffusetrans + abswght
                    diffuseflux['down'][bins] += abswght
                break


            # Compute an x-axis for the photon coordinate system and express it in
            # model coordinates.
            denom = np.sqrt(km[0]**2 + km[1]**2)
            if denom < 0.0001:
                xp = np.array([-sin(phi0), cos(phi0), 0])
            else:
                xp = [-km[1], km[0], 0] / denom

            # Scattering angle.
            randdev=rs.uniform()
            if g == 0:
                cosTheta = 2.0*randdev - 1.0
            else:
                gsq = g**2
                a = (1.0-gsq) / (1+g*(2.0*randdev-1.0))
                cosTheta = (1.0+gsq-a**2) / (2.0*g)
            sinTheta = np.sqrt(1.0-cosTheta**2)
            randdev=rs.uniform()
            phi = 2*np.pi*randdev

            # Compute the new propagation direction in photon coordinates. This is the
            # same as the initial transformation of the incident photon vector into
            # model coordinates.
            kp = np.array([sinTheta*cos(phi),sinTheta*sin(phi), cosTheta])

            # Finally rotate this new propagation vector into model coordinates.
            km = np.array([xp[0]*kp[0] - km[2]*xp[1]*kp[1] + km[0]*kp[2],
                           xp[1]*kp[0] + km[2]*xp[0]*kp[1] + km[1]*kp[2],
                           kp[1]*km[0]*xp[1] - kp[1]*km[1]*xp[0] + km[2]*kp[2]])

            km = km / np.sqrt(np.dot(km,km))
            newbin=findbin(cldtau,newtau,nbins)
            vert_direc=(newbin - oldbin)
            docross='crossed'
            if ip == 1:
                if vert_direc < 0:
                    raise('upward direct beam is impossible')
                bins=np.arange(oldbin+1,newbin+1)
                is_diffuse=False
                #
                # add photon to direct beam
                # nothing will be added if oldbin=newbin
                #
                directflux[bins] += abswght
            else:
                if vert_direc > 0:
                    #flux is downward
                    # arange stops at newbin
                    # if oldbin=2 and newbin=5
                    # then bins=3,4,5 
                    #
                    bins=np.arange(oldbin+1,newbin+1)
                    updown='down'
                    add_diffuse=True
                elif vert_direc < 0:
                    #
                    # flux is upward
                    # if olbin=8 and newbin=5 then
                    # bins = 5,6,7
                    #
                    bins=np.arange(newbin,oldbin)
                    updown='up'
                    add_diffuse=True
                else:
                    #
                    # stayed within bin
                    #
                    direc=None
                    docross='nocross'
                    add_diffuse=False
                if add_diffuse:
                    if do_debug:
                        print "adding diffuse flux: ",updown,ip,nph,oldbin,newbin,bins
                    diffuseflux[updown][bins] += abswght

            oldbin=newbin
            textstring='%d' % ip
            vert_direc=int(np.sign(-path[-1][2] - (-path[-2][2])))
            #
            # add the scatter event with a colored background
            # red for down and green for up
            #
            if do_plot:
                ax1.text(path[-1][0],-path[-1][2],textstring,
                         bbox=dict(facecolor=upcolor[vert_direc], alpha=0.5))
            # Decrease the absorption weight.
            abswght = abswght * ssa
            # Check if photon has been absorbed.
            if abswght < 0.001:
                break
        #plot the trajectory of the photon in
        #the x,z plane
        path=np.array(path)
        if nph==0:
            #save the first path to show the incoming solar direction
            firstpath=copy.copy(path)
        if do_plot:
            ax1.plot([path[2:,0],path[1:-1,0]],\
                     [-path[2:,2],-path[1:-1,2]],'b-')
        # Clear path variable for next photon.
        path=[]

    if do_plot:
        #
        # plot the first two points to show the solar angle
        #
        ax1.plot([firstpath[0,0],firstpath[1,0]],\
                 [-firstpath[0,2],-firstpath[1,2]],'m-',linewidth=2)
        ax1.plot(0,0,'mo',markersize=10)

        ax1.set_ylim([1,-10])
        ax1.invert_yaxis()
        plt.show()

    # Convert statistics.
    mcstats.directtrans = mcstats.directtrans / nphotons
    mcstats.albedo = mcstats.albedo / nphotons
    mcstats.diffusetrans = mcstats.diffusetrans / nphotons

    scatternum=np.array(scatternum)
    #get the bdrf
    mcstats.angle_bins=mcstats.angle_bins*pi
    #get the anisotropic factor
    mcstats.anisotrop=mcstats.angle_bins/mcstats.albedo
    
    
    outDict={'mcstats':mcstats,'diffuse':diffuseflux,
             'directFlux':directflux,'randomseed':intseed,
             'nphotons':nphotons,'scatternum':scatternum,
             'center_taus':center_taus,'mcargs':mcargs,
             'mcstats':mcstats}

    pickle.dump(outDict,outpic)
    outpic.close()
    elapsed=time.time() - start

    #save parameters so matlab can calculate eddington solution
    out_dict={'g':g,'ssa':ssa,'theta0_deg':vals['theta0_deg'],'tottau':cldtau,
              'F0':F0,'prefix':outprefix}
    outfile='%s_eddington_params.mat' % outprefix
    sio.savemat(outfile,{'plot_params':out_dict})
    print "wrote %s, edit plotDeltaEd.m to load this file and produce two stream fluxes" % outfile
    print "run completed in %8.1g seconds" % elapsed
    
    
