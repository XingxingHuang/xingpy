#!/usr/bin/env python


H0=70
WM=0.27


import os,sys,string,glob,time,math
import random
import pdb
from pyraf import iraf
import numpy as np
from pylab import *
import shutil
import popen2
from scipy.optimize import leastsq

import pyfits
from cosmocalc import cosmocalc
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from matplotlib import cm
from matplotlib import pyplot as plt
from pylab import *
from scipy import constants

'''
def printlog(text,fname='tmp.log'):
def getew_flux(data=None,bandchoose='f125w',other=None,getdmag=0.,z=1.7,figname = None):
def gauss_function(x, a, x0, sigma):
def getbeta(data=None):
def getew(data=None,redshift=0.):
def getamp(z1=None,z2=None,z3=None,ra=None,dec=None,xfits=None,yfits=None, name= None, image = 0):
def angular_distance(z1,z2):
def myfunct(p, fjac=None, x=None, y=None, err=None):
def flux2mag(flux, zero_pt="", abwave=""):
def mag2flux(mag, zero_pt="", abwave=""):
def mage2fluxe(mag, mage, zero_pt="", abwave=""):
'''
def radec(ra,dec):
  # ra
  txt = ra.split(':')
  if len(txt)!=3:
    print 'ERROR: ',txt
    pdb.set_trace()
  ra_degree =  ( float(txt[0])+float(txt[1])/60.+float(txt[2])/3600. )*360./24.
  # dec
  txt = dec.split(':')
  if len(txt)!=3:
    print 'ERROR: ',txt
    pdb.set_trace()
  if '-' in dec:
   dec_degree =   float(txt[0])-float(txt[1])/60.-float(txt[2])/3600. 
  else:
   dec_degree =   float(txt[0])+float(txt[1])/60.+float(txt[2])/3600.  
  print 'RA, DEC\n\t %s %s \n\t %f %f' %(ra,dec, ra_degree, dec_degree) 

def printlog(text,fname='tmp.log',ptime=0,printtxt=0):
    '''
    write the text you define 
    '''
    if os.path.exists(fname):
      f = open(fname,'a')
    else:
      f = open(fname,'w')   
      #txt='####This file is used for recording the results  ####'
      #print >> f, txt
      #del txt
      print fname+' created!'
    #ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
    #format = '%s %s'  
    #print >> f, format % (ptime,text)
    if ptime==1:
        ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
        format = '#\n###  %s  ###'  
        print >> f, format % (ptime)    
    print >>  f, text
    if printtxt==1:
        print text
    f.close()     
   
'''      
def getew_flux(data=None,bandchoose='f125w',other=None,getdmag=0.,z=1.7,figname = None):
    
     get the EW from F105W F125W F160W
     "data"		: size =7+32  
     "bandchoose"	: defines the band which line falls in.
     "other" 		: defines the bands for analyzing the continuum, will used default bands if not defined.
     "getdmag"  	: if the value equal 1, the dmag and error other than the EW will be return
     "z"		: redshift of the objects which will be used for convert the EW to rest frame
    
    bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
    width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
    	 [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]     
    if bandchoose == 'f125w':
        index = [11,13,15]		############ choosed bands for analysis    can be changed
    elif bandchoose == 'f105w':
        index = [9,11,15]
    elif bandchoose == 'f110w':
        index = [11,12,15]
    elif bandchoose == 'f140w':
        index = [11,14,15]
    elif bandchoose == 'f336w':
        index = [99,2,99]
    else:
        sys.exit('ERROR: '+bandchoose+' not defined in getew_!')    
    centerwave = width[index[1]][0]*10. ##### wavelength of the boost band    
    if len(data)<39:
      pdb.set_trace()
      sys.exit('size ERROR: check the input file!')

    if other!=None:
      index[0]=bands.index(other[0])   	##########
      index[2]=bands.index(other[1]) 	###########
    obj	= data[0]
    ra	= data[5]
    dec = data[6]
    mag = []
    for band in range(0,16):
	mag.append([float(data[(7+band*2)]), float(data[(7+band*2+1)]) ] )		# [flux,flux error]
    f1 = mag[index[0]][0]				### contiuum
    e1 = mag[index[0]][1]
    f2 = mag[index[1]][0]				### flux of the band with emission line
    e2 = mag[index[1]][1]
    f3 = mag[index[2]][0]				### contiuum
    e3 = mag[index[2]][1]
    mag1 = flux2mag(f1,abwave=width[index[0]][0]*10.)
    mag3 = flux2mag(f3,abwave=width[index[2]][0]*10.)
    mag1e = e1/f1*2.5/np.log(10.)  
    mag3e = e3/f3*2.5/np.log(10.)  
    con  = mag2flux( (mag1+mag3)/2.  ,abwave=centerwave)			# average flux of continuum
    average_mag = (mag1/mag1e+mag3/mag3e)/(1./mag1e+1./mag3e)
    average_mage = 1./(1./mag1e+1./mag3e)
    con  = mag2flux( average_mag  ,abwave=centerwave)			# oct02 error weighted average
    cone= mage2fluxe( average_mag, average_mage  ,abwave=centerwave)
    #cone = ( e1**2. + e3**2. )**(0.5)/2.
    #cone = ( abs(e1)+ abs(e3) )/2.      # how to calculate the error
    f  = f2
    fe = e2
   
    #ew1     = (f-con)*width[index[1]][1]*10./(1+z1)/(con)
    #ew1_err = (  fe/con  + f*cone/con**2.  )*width[index[1]][1]*10./(1.+z1)
    #ew2     = (f-con)*width[index[1]][1]/(1+z2)*10./(con)
    #ew2_err = (  fe/con  + f*cone/con**2.  )*width[index[1]][1]*10./(1.+z2)  
    #ew  = abs(ew1+ew2)/2.
    #pdb.set_trace()
    #ewe = abs(ew2-ew1) + (abs(ew2_err) + abs(ew1_err))/2.		#######    
    ew     = (f-con)*width[index[1]][1]*10./(1+z)/(con)
    ewe    = (  abs(fe/con)  + abs(f*cone)/con**2.  )*width[index[1]][1]*10./(1.+z)
    ewelog = ewe/ew/np.log(10.) 

    ########## simulation for 100 times.	
    ewr=[]
    import random
    for i in range(0,1000):   
       mr1 = random.gauss(mag[index[0]][0],mag[index[0]][1])
       mr2 = random.gauss(mag[index[1]][0],mag[index[0]][1])
       mr3 = random.gauss(mag[index[2]][0],mag[index[0]][1])
       fr1 = mr1
       fr2 = mr2
       #fr1 = f1
       #fr3 = f3
       #fr2 = f2
       fr3 = mr3
       #print 'flux1 flux2 flux3:  ',fr1,fr2,fr3	
       if fr1 < 0 or fr3 < 0:
          if max(fr1,fr3) > 0:
            fr1 = max(fr1,fr3)
            fr3 = max(fr1,fr3)
          else: 
            continue
       mag1 = flux2mag(fr1,abwave=width[index[0]][0]*10.)
       mag3 = flux2mag(fr3,abwave=width[index[2]][0]*10.)
       fr  = fr2
       conr  = mag2flux( (mag1+mag3)/2.  ,abwave=centerwave)
       tmp = (fr-conr)*width[index[1]][1]*10./(1+z)/(conr)
       #if tmp <50000.:
       ewr.append(tmp)
    aa=[np.log10(i) for i in ewr if i >0 and i<1e9]   
    #average = np.mean(ewr)  
    #error2 = [(i-average)**2  for i in ewr]   
    #ewe = np.sqrt( np.sum(error2)/(len(error2)-1.) )
    average = np.mean(aa)
    average_e  = np.std(aa)

    # figure for fit the distribution with gauss
    fig2 = plt.figure()
    ax = fig2.add_subplot(111)
    xlim = [0.1,4.]
    binwidth=0.1
    bins = np.arange(xlim[0], xlim[1], binwidth)
    distribution = hist(aa, bins=bins, facecolor='blue', edgecolor='None', histtype='stepfilled',alpha=0.2,linewidth=2, normed=1)
    # fit
    import scipy.stats as stats
    gaussian = stats.norm
    Gmean, Gstd = gaussian.fit(aa)
    x = [ (distribution[1][tmp]+ distribution[1][tmp+1])/2. for tmp in range(len(distribution[1])-1)]
    y =  gaussian.pdf(x,loc=Gmean,scale=Gstd)
    #y = [gauss_function(x_value, max(distribution[0]), Gmean, Gstd) for x_value in x]
    
    print 'EW , EW_mean , GAUSS: %6.2f %4.2f,  %4.2f  %4.2f,   %4.2f %4.2f' %(np.log10(ew),ewelog, average,average_e, Gmean, Gstd  )
    #if (Gmean-average)>0.1 or (Gstd-ewe)>0.1:
    #    print 'EW mismatch'
    #    pdb.set_trace()
    if figname != None:
      ax.plot(x,distribution[0])
      ax.plot(x,y)
      print_text1 = 'EW  , EW_mean, EW_error: %6.2f  %4.2f %4.2f ' %(np.log10(ew), average,ewe  )
      print_text2 = 'GAUSS fit: EW, EW_error: %4.2f %4.2f' %( Gmean, Gstd  )
      ax.text(0.05,0.8,print_text1,transform=ax.transAxes)
      ax.text(0.05,0.85,print_text2,transform=ax.transAxes)
      if ew > 9999. or ew < 0:
        fig2.savefig('../EW_distribution/wrong_'+figname)
      else:
        fig2.savefig('../EW_distribution/'+figname)  
      
    if ew > 9999. or ew < 0:
      print 'error EW : set to 9999 : %10.4f' %(ew)
      if getdmag==0: return(9999,9999)
      else: return(9999,9999,0,0)
    if getdmag==0:
       ###########################################################################
       #return(ew,ewe)
       #return(np.log10(ew),ewelog)
       return(Gmean, Gstd)
       ###########################################################################
    else:
        pdb.set_trace()
        print 'should revise!!'
        sys.exit()
        dmag1 = mag[index[1]][0]-mag[index[0]][0]
        dmag2 = mag[index[1]][0]-mag[index[2]][0]
        #dmag1e = ((mag[index[1]][1]**2+mag[index[0]][1]**2)/2.)**0.5
        #dmag2e = ((mag[index[1]][1]**2+mag[index[2]][1]**2)/2.)**0.5
        dmag1e = (abs(mag[index[1]][1])+abs(mag[index[0]][1]) )
        dmag2e = (abs(mag[index[1]][1])+abs(mag[index[2]][1]) )
        #print 'dmag1:  ',mag[index[1]][0]-mag[index[0]][0],' dmag2:  ',mag[index[1]][0]-mag[index[2]][0]
        return(dmag1,dmag2,dmag1e,dmag2e)
      
    #if ew > 9999. or ewe > 9999:
    #  print 'error EW : set to 9999'
    #  return(9999,9999,0,0)
    #if getdmag==0:
    #   return(ew,ewe)
    #else:
    #   print 'Wrong'
    #   pdb.set_trace()
'''
def getew_flux(data=None,bandchoose='f125w',other=None,getdmag=0.,z=1.7,figname = None):
    '''
     get the EW from F105W F125W F160W
     "bandchoose" : defines the band which line falls in.
     "other"    : defines the bands for analyzing the continuum, will used default bands if not defined.
     "getdmag"    : if the value equal 1, the dmag and error other than the EW will be return
     "z"    : redshift of the objects which will be used for convert the EW to rest frame
    ''' 
    bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
    width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
       [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]     
    if bandchoose == 'f125w':
        index = [11,13,15]    ############ choosed bands for analysis    can be changed
    elif bandchoose == 'f105w':
        index = [9,11,15]
    elif bandchoose == 'f110w':
        index = [11,12,15]
    elif bandchoose == 'f140w':
        index = [11,14,15]
    else:
        sys.exit('ERROR: '+bandchoose+' not defined in getew_!')    
    centerwave = width[index[1]][0]*10. ##### wavelength of the boost band    
    if len(data)!=40:
      pdb.set_trace()
      sys.exit('ERROR: check the input file!')

    if other!=None:
       index[0]=bands.index(other[0])    ##########
       index[2]=bands.index(other[1])  ###########
    obj = data[0]
    ra  = data[5]
    dec = data[6]
    mag = []
    for band in range(0,16):
        mag.append([float(data[(7+band*2)]), float(data[(7+band*2+1)]) ] )    # [flux,flux error]
    f1 = mag[index[0]][0]       ### contiuum
    e1 = mag[index[0]][1]
    f2 = mag[index[1]][0]       ### flux of the band with emission line
    e2 = mag[index[1]][1]
    f3 = mag[index[2]][0]       ### contiuum
    e3 = mag[index[2]][1]
    la1 = width[index[0]][0]*10. # wavelegth
    la3 = width[index[2]][0]*10.
    la  = width[index[1]][0]*10.
    
    # calculate with the flux
    #con = (f1-f2)/(1./la1**2-1./la2**2) / la**2    # not good, this method does not consider the errors.
    con1 = f1*la1**2/la**2
    con1e = e1*la1**2/la**2
    con3 = f3*la3**2/la**2
    con3e = e3*la3**2/la**2
    con,cone = wmean([con1,con3],[con1e,con3e])
    
    # calculate with magnitudes
    #mag1 = flux2mag(f1,abwave=width[index[0]][0]*10.)
    #mag3 = flux2mag(f3,abwave=width[index[2]][0]*10.)   
    #mag1e = e1/f1*2.5/np.log(10.)  
    #mag3e = e3/f3*2.5/np.log(10.)  
    #average_mag = (mag1/mag1e**2+mag3/mag3e**2)/(1./mag1e**2+1./mag3e**2)
    #average_mage = np.sqrt(1./(1./mag1e**2+1./mag3e**2))
    #con  = mag2flux( average_mag  ,abwave=centerwave)     # oct02 error weighted average
    #cone= mage2fluxe( average_mag, average_mage  ,abwave=centerwave)
    f  = f2
    fe = e2
   
    #ew1     = (f-con)*width[index[1]][1]*10./(1+z1)/(con)
    #ew1_err = (  fe/con  + f*cone/con**2.  )*width[index[1]][1]*10./(1.+z1)
    #ew2     = (f-con)*width[index[1]][1]/(1+z2)*10./(con)
    #ew2_err = (  fe/con  + f*cone/con**2.  )*width[index[1]][1]*10./(1.+z2)  
    #ew  = abs(ew1+ew2)/2.
    #ewe = abs(ew2-ew1) + (abs(ew2_err) + abs(ew1_err))/2.    #######    
    ew     = (f-con)*width[index[1]][1]*10./(1+z)/(con)
    ewe    = (  abs(fe/con)  + abs(f*cone)/con**2.  )*width[index[1]][1]*10./(1.+z)
    ewelog = ewe/ew/np.log(10.) 

    
    ########## simulation for 1000 times. 
    gaussscale = 0   # using magnitudes average as the continue
    ewr=[]
    import random
    for i in range(0,1000):   
       mr1 = random.gauss(mag[index[0]][0],mag[index[0]][1])
       mr2 = random.gauss(mag[index[1]][0],mag[index[0]][1])
       mr3 = random.gauss(mag[index[2]][0],mag[index[0]][1])
       fr1 = mr1
       fr2 = mr2
       fr3 = mr3
       #print 'flux1 flux2 flux3:  ',fr1,fr2,fr3  
       if fr1 < 0 or fr3 < 0:
          if max(fr1,fr3) > 0:
            continue
            fr1 = fr1
            fr3 = fr3
          else: 
            continue
       if gaussscale ==1:      
         mag1 = flux2mag(fr1,abwave=width[index[0]][0]*10.)
         mag3 = flux2mag(fr3,abwave=width[index[2]][0]*10.)
         conr  = mag2flux( (mag1+mag3)/2.  ,abwave=centerwave)
       else:
         conr = (fr1*la1**2/la**2+ fr3*la3**2/la**2)/2.
       fr  = fr2
       tmp = (fr-conr)*width[index[1]][1]*10./(1+z)/(conr)
       ewr.append(tmp)
    if gaussscale == 1:   
       aa=[np.log10(i) for i in ewr if i >0 and i<1e9]   
    else:
       aa=[i for i in ewr if i >0 and i<1e9]   
    # delete the values out of 3 sigma   
    average = np.mean(aa)
    average_e  = np.std(aa)
    aa = np.array(aa)
    aa = aa[np.where( aa>(average-3*average_e)  )]
    aa = aa[np.where( aa<(average+3*average_e)  )]
    average = np.mean(aa)
    average_e  = np.std(aa)
    
    # figure for fit the distribution with gauss
    if gaussscale == 1:
        xlim = [2.,5.]
        binwidth=0.1   
    else:
        xlim = [000.,6000.]
        binwidth=100
    fig2 = plt.figure()
    ax = fig2.add_subplot(111)
    bins = np.arange(xlim[0], xlim[1], binwidth)
    distribution = hist(aa, bins=bins, facecolor='blue', edgecolor='None', histtype='stepfilled',alpha=0.2,linewidth=2, normed=1)
    # fit
    import scipy.stats as stats
    gaussian = stats.norm
    Gmean, Gstd = gaussian.fit(aa/average)
    x = [ (distribution[1][tmp]+ distribution[1][tmp+1])/2. for tmp in range(len(distribution[1])-1)]
    y =  gaussian.pdf(x,loc=Gmean*average,scale=Gstd*average)


    print 'EW , EW_mean , GAUSS: %6.2f %4.2f,  %4.2f  %4.2f,   %4.2f %4.2f' %(ew,ewe, average,average_e, Gmean, Gstd  )
    #if (Gmean-average)>0.1 or (Gstd-ewe)>0.1:
    #    print 'EW mismatch'
    if figname != None:
      ax.plot(x,distribution[0])
      ax.plot(x,y)
      print_text1 = 'EW  , EW_mean, EW_error: %6.2f  %7.2f %7.2f  %7.2f' %(ew, average,ewe,average_e  )
      print_text2 = 'GAUSS fit: EW, EW_error: %7.2f %7.2f' %( Gmean*average, Gstd*average  )
      ax.text(0.05,0.8,print_text1,transform=ax.transAxes)
      ax.text(0.05,0.85,print_text2,transform=ax.transAxes)
      outdir = './getew'
      if not os.path.isdir(outdir): os.mkdir(outdir)
      if ew > 9999. or ew < 0:
        fig2.savefig(os.path.join(outdir,'wrong_'+figname))
      else:
        print 
        fig2.savefig(os.path.join(outdir,figname)  )

    if ew > 9999. or ew < 0:
      print 'error EW : set to 9999'
      return(0.0,  0.0, 0, 0)
    if getdmag==0:
       ###########################################################################
       return(ew,ewe,con*ew,ewe*con+con*ewe)
       #return(ew,ewe)
       #return(np.log10(ew),ewelog)
       #return(Gmean, Gstd)
       ###########################################################################
    else:
        pdb.set_trace()
        print 'should revise!!'
        sys.exit()
        dmag1 = mag[index[1]][0]-mag[index[0]][0]
        dmag2 = mag[index[1]][0]-mag[index[2]][0]
        #dmag1e = ((mag[index[1]][1]**2+mag[index[0]][1]**2)/2.)**0.5
        #dmag2e = ((mag[index[1]][1]**2+mag[index[2]][1]**2)/2.)**0.5
        dmag1e = (abs(mag[index[1]][1])+abs(mag[index[0]][1]) )
        dmag2e = (abs(mag[index[1]][1])+abs(mag[index[2]][1]) )
        #print 'dmag1:  ',mag[index[1]][0]-mag[index[0]][0],' dmag2:  ',mag[index[1]][0]-mag[index[2]][0]
        return(dmag1,dmag2,dmag1e,dmag2e)

def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2.*sigma**2))
    
    
    
# a revised version using mpfit.
def getbeta(data=None):
   '''
    data include the magnitudes and errors for all 16 bands.
    choose the band between the index defined in the 'index' and delete the point with 0 value and too faint value
   '''
   wave = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
    	 [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]   
   wavelength = []
   mag = []
   for i in range(len(wave)):
      wavelength.append(math.log10(wave[i][0]*10.))                       
      mag.append([float(data[7+i*2]), float(data[7+i*2+1]) ] )		# [flux,flux error]
   
   index=[4,10]   			  	############# only choose ACS detectors 
   magerr_lim =  0.36                         	############# only choose magerr<0.36 to select S/N>3
   xx = wavelength        			# choose the ACS/WFC bands   F336W >> F814W
   ytmp    = [float(mag[j][0]) for j in filter( lambda j : j, range(len(mag)) )]
   ytmperr = [float(mag[j][1]) for j in filter( lambda j : j, range(len(mag)) )]
   
   x=[]
   y=[]
   yerr=[]
   for i in range(index[0],index[1]):
       if ytmp[i] != 0 and ytmperr[i] != 0:
          if ytmperr[i] < magerr_lim:
            x.append(xx[i])
            y.append(ytmp[i])
            yerr.append(ytmperr[i])
   #y 	  = tmp[index[0]:index[1]] 
   #yerr   = tmperr[index[0]:index[1]] 
   #ytmp = y
   #yerrtmp = y
   #x = [x[j] for j in range(len(ytmp))  if ytmp[j] != 0 and ytmp[j] < 28.5]
   #y = [y[j] for j in range(len(ytmp))  if ytmp[j] != 0 and ytmp[j] < 28.5]   # delete the value 0 and lower than 28.5
   #yerr = [yerr[j] for j in range(len(ytmp))  if ytmp[j] != 0 and ytmp[j] < 28.5]
   

   test = [i for i in y if i !=0]
   if test == [] or len(y)<4:
      print 'Not enough detection in all bands'
      return(0,0,0)
 
   from mpfit import mpfit
   x = array(x)
   y = array(y)
   err=array(yerr)
   p = [26.,0.1]
   fa = {'x':x, 'y':y, 'err':err}
   try:
     m = mpfit(myfunct, p, functkw=fa)
   except:
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     sys.exit()
       
   beta = m.params[1]/2.5+2.
   beta_error =  m.perror[1] /2.5
   
   print 'status = ', m.status
   if (m.status <= 0):
      print 'error message = ', m.errmsg 
      pdb.set_trace()
   print 'parameters = ', m.params
   print 'para error = ', m.perror
   print 'beta       = ',beta , ' + ' ,beta_error
   pdb.set_trace()
   return( beta, beta_error)



    
def getew(data=None,redshift=0.):    # wrong
   # not used
   'Try to get EW from spectral fit but I cannot finish it!' 
   bands = ['f225w','f275w','f336w','f390w','f435w',\
         'f475w','f606w','f625w','f775w','f814w',\
         'f850lp','f105w','f110w','f125w','f140w','f160w']
   width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
    	 [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]    
   band_choose=[6,7,8,9,10,12,13,14,15,16]    	    			# these bands are choose for fit
   # 0   1   2   3   4   N   5   6   7   8  9
   #475 606 625 775 814 850 105 110 125 140 160
   band       = [bands[i-1] for i in band_choose ]
   
   # Read filter throughout to filterOut[][]
   filterdir = '/media/BACK/data/filters/'
   filterOut  = []
   length     = 18301	# length of the 
   wavelen    = [int(i+1700.) for i in range(length)]
   wavelenlog = [math.log10(i+1700.) for i in range(length)]
   for key in band:
     if key in ['f225w','f275w','f336w','f390w','f435w',\
         'f475w','f606w','f625w','f775w','f814w',\
         'f850lp']:
        fname = key+'.UVIS1.tab'
     if key in  ['f105w','f110w','f125w','f140w','f160w']:
        fname = key+'.IR.tab'
     f = open(os.path.join(filterdir,fname),'r')
     lines=f.readlines()
     read_all = [line.split() for line in lines] 
     read = [i for i in read_all if i ]   
     read = [float(i[2]) for i in read if not ('#' in i[0]) ]     # delete the elements begin with '#'
     f.close()
     filterOut.append(read)
   print '>>>>> Read filter throughout Done!'  
     
   #calculate the mag with different redshift
   rate=[]
   filterwave=[]
   ii=[]
   for key in range(len(band)):
       ii.append([])
       # this threshold are choosed by myself
       if band[key] in ['f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w']:
           threshold = 0.05
       elif band[key] in [  'f225w','f275w','f850lp'  ]:
           threshold = 0.02
       elif band[key] in [  'f105w','f110w','f125w','f140w','f160w']:
           threshold = 0.02
        
       for i in range(length):
          if filterOut[key][i] > threshold:
            ii[key].append(i)
            break
       for i in range(length): 
          if filterOut[key][length-i-1] > threshold:
            ii[key].append(length-i)
            break
       #print rate     
       rate.append(sum(filterOut[key][ii[key][0]:ii[key][1]])/(ii[key][1]-ii[key][0]))    	# average through out rate
       filterwave.append(wavelen[ii[key][0]:ii[key][1]])			 	# useful wavelength range, choose for saving time
   print '>>>>> average through out rate and index Done!  '
   print 'rate: ',rate
   #pdb.set_trace()


   # creat the grid for continuum
   mag_lenlog = [math.log10(width[i-1][0]*10.) for i in band_choose]   	# wavelength in each band
   mag_len    = [width[i-1][1]*10. for i in band_choose ]              	# width of each band
   mag_len2   = [width[i-1][0]*10. for i in band_choose ]		# wavelength of each band 
   z	      = redshift

   low  = 1.0
   high = 3.0
   mag_con    = [[] for i in range(int(high*10.-low*10.))] 	# store the data here 
   for j in range(int(high*10.-low*10.)):
      beta = j/10.+low						# the slop beta
      print str(j)+'  beta = '+str(beta)
      flux = [0. for i in range(length)]
      for i in range(length):
         magtmp  =   26.  +2.5*(beta -2.)*wavelenlog[i]-2.5*(beta -2.)*math.log10(12486.)            ##  12486A  mag = 26
         flux[i] = flux[i]+10**( ( magtmp + 2.406+5.*wavelenlog[i] )/(-2.5) ) 
      # cost time here
      filterflux = []
      for key in range(len(band)):   			############### different bands
        filterflux.append([])
        for i in range(length):				############### wavelength
          try:
             index = int(wavelen[i]/(1.+z)-1700)
          except:
             index = 0   
          if index <=0:
             index = 0
          filterflux[key].append( flux[index]*filterOut[key][i]/rate[key] )  #/0.52 )
        sumflux= sum(filterflux[key][ii[key][0]:ii[key][1]])/(1.+z)
        width_used = (wavelen[ii[key][1]]-wavelen[ii[key][0]])*(1.+z)
        if sumflux <= 0.:
            mag_con[j].append(99)
        else:
            mag_con[j].append( -2.5*math.log10(sumflux/width_used)-5.*math.log10(mag_len2[key])-2.406 ) 
      print band[5]+'+'+band[9]+' '+'mag_con'+':  '+str(mag_con[j][5]/2.+mag_con[j][9]/2.)+'  '+str(mag_con[j][7])   # print the magnitude to check the influerence of slop 
      print "flux: " , flux2mag(mag2flux(mag_con[j][5], abwave=10552.)/2.+mag2flux(mag_con[j][9], abwave=10552.)/2., abwave=10552.)
      #print band[7]+'-'+band[9]+':  '+str(mag_con[j][7]-mag_con[j][9]),band[7]+'-'+band[5]+':  '+str(mag_con[j][7]-mag_con[j][5])    
   # mag_con[i][j]    i: beta     j: bands
   print '>>>>> Get the magnitude of continuum done!'         
   pdb.set_trace()
  
   low  = 500.
   high = 2500.
   mag_con    = [[] for i in range(int(high/100.-low/100.))]          # store the data here 
   for j in range (int(high/100.-low/100.)):
      flux	   = [1.e-20 for i in range(length)]
      ew_o3  = j*100. ################################### IMPORTANT
      sigma  = 10.
      lineflux_o3 = ew_o3*flux[int(5007.-1700.)]

      center = 5007.
      lineflux = lineflux_o3
      ew1=lineflux / flux[int(center-1700.)]
      for i in range(length):
        flux[i] = flux[i]+ lineflux* (1./2.5/sigma)*numpy.exp(-(wavelen[i]-center)**2./(2.*sigma**2.)) 
   
      center = 4959.
      lineflux = lineflux_o3 / 3.
      ew2=lineflux / flux[int(center-1700.)]
      for i in range(length):
        flux[i] = flux[i]+ lineflux* (1./2.5/sigma)*numpy.exp(-(wavelen[i]-center)**2./(2.*sigma**2.))  
        
        
   print '>>>>> Get the magnitude of [OIII] done!'         
   print '>>>>> Get the magnitude of Ha done!'         
   pdb.set_trace()      
         


def getamp(z1=None,z2=None,z3=None,ra=None,dec=None,xfits=None,yfits=None, name= None, image = 0):
    
    '''
    z1 : cluster
    z2 : object
    z3 : multi lensed objects redshift . it can be find in the doc files
    image =0: using the ra dec  instead of xaxis y axis
    # an example of header
CTYPE1  = 'RA---TAN'                                                            
CRVAL1  =          42.01080345                                                  
CRPIX1  =                 1486                                                  
CDELT1  =     -1.388888889e-05                                                  
CUNIT1  = 'deg     '                                                            
CTYPE2  = 'DEC--TAN'                                                            
CRVAL2  =           -3.5312493                                                  
CRPIX2  =                 1108                                                  
CDELT2  =      1.388888889e-05  
    name : just for output file name and for distincting different clusters
    '''
    header = pyfits.getheader(xfits)
    CRVAL1  =  header['CRVAL1']                                                 
    CRPIX1  =  header['CRPIX1']                                 
    CDELT1  =  header['CDELT1']                                                                                               
    CRVAL2  =  header['CRVAL2']                            
    CRPIX2  =  header['CRPIX2']                         
    CDELT2  =  header['CDELT2']
    #x = CRVAL1+(ra-CRPIX1)*CDELT1
    #y = CRVAL2+(dec-CRPIX2)*CDELT2    
    if image == 0:
      x= int((ra-CRVAL1)/(CDELT1)*(math.cos(dec/180.*3.14159265))+CRPIX1)         # RA DEC >>   x y
      y= int((dec-CRVAL2)/(CDELT2)+CRPIX2)
    else:
      x = ra
      y = dec
    # (x-CRPIX1)*CDELT1+CRVAL1
    #printlog ('%8.5f %8.5f :  %4d %4d   %10f     %s' %(ra,dec,x,y,1,name)  ) 
    #pdb.set_trace()
    
    fits=pyfits.open(xfits)
    alpha_x=fits[0].data[:,:]	  	# the number of fits files used in the point   # attention about the ax ay
    fits.close()
    fits=pyfits.open(yfits)
    alpha_y=fits[0].data[:,:]	  	# the number of fits files used in the point   # attention about the ax ay
    fits.close()

    H0    =  71.
    WM    =  0.27
    H0    =  70.
    WM    =  0.3
    Dl = cosmocalc(z1,H0=H0,WM=WM)['DA_Mpc']	# distance of the cluster
    Ds = cosmocalc(z2,H0=H0,WM=WM)['DA_Mpc']	# distance of the object
    dls = angular_distance(z1,z2)
    ds = Ds
    dls_ref = angular_distance(z1,z3)
    Ds_ref = cosmocalc(z3,H0=H0,WM=WM)['DA_Mpc']
    alpha_x_ALL = alpha_x * dls/ds / (dls_ref/Ds_ref)
    alpha_y_ALL = alpha_y * dls/ds / (dls_ref/Ds_ref)
    '''
    xcopy = alpha_x_ALL.copy()
    ycopy = alpha_y_ALL.copy()

    for i in range(len(xcopy[:,1])):
       for j in range(len(xcopy[1,:])):
         xcopy[i,j]=alpha_x_ALL[j,i]
         ycopy[i,j]=alpha_y_ALL[j,i]
    pdb.set_trace()
    '''
    
    poisson_ALL =  alpha_x_ALL*0.
    magnification_ALL = alpha_x_ALL*0.
    axis_length = len(alpha_x[0,:])
    tmp = -1
    #for m in range(2,axis_length-1):
    step = 3				 # define the region which will be analyzed
    if x < 0 - step+1 or x > axis_length-step-1 or y < 0 - step+1 or y > axis_length-step-1:
       print 'WARNING: object is out of the amplification map'
       print 'RA:  %f   DEC: %f' %(ra,dec)
       print 'X : %f   Y : %f '  %(x,y)
       return(1.00)            		# out of the image.  define amplification=1.00
    
    
    for n in range(x-step,x+step):
        loop = ((n-x+step)*10)//(step*2.)      # add for check the speed
        if loop != tmp :
               #print loop*10,' %'
               tmp = loop
        #for  n in range (2,axis_length-1):
        for  m in range (y-step,y+step):
            '''
            da_x=(alpha_x_ALL[m+1,n]-alpha_x_ALL[m-1,n])/2.0
            da_y=(alpha_y_ALL[m,n+1]-alpha_y_ALL[m,n-1])/2.0
            da_x_dy=(alpha_x_ALL[m,n+1]-alpha_x_ALL[m,n-1])/2.0
            da_y_dx=(alpha_y_ALL[m+1,n]-alpha_y_ALL[m-1,n])/2.0
            '''
            da_y=(alpha_y_ALL[m+1,n]-alpha_y_ALL[m-1,n])/2.0
            da_x=(alpha_x_ALL[m,n+1]-alpha_x_ALL[m,n-1])/2.0
            da_y_dx=(alpha_y_ALL[m,n+1]-alpha_y_ALL[m,n-1])/2.0
            da_x_dy=(alpha_x_ALL[m+1,n]-alpha_x_ALL[m-1,n])/2.0
            '''
            da_x=(xcopy[m+1,n]-xcopy[m-1,n])/2.0
            da_y=(ycopy[m,n+1]-ycopy[m,n-1])/2.0
            da_x_dy=(xcopy[m,n+1]-xcopy[m,n-1])/2.0
            da_y_dx=(ycopy[m+1,n]-ycopy[m-1,n])/2.0
            '''
            poisson_ALL[m-1,n-1]=da_x+da_y
            magnification_ALL[m-1,n-1]=abs(1.0/(1.0-poisson_ALL[m-1,n-1]+da_x*da_y-da_x_dy*da_y_dx))
            #pdb.set_trace()
    magnification = magnification_ALL[y-1,x-1]
    
    
    # plot image for check
    plot3d    = 0                    	# define here for plot
    plotimage = 0			# define here for plot
    if plotimage == 1:
        fig = plt.figure()
        ax=fig.add_subplot(111)
        tt = transpose(magnification_ALL) 
        im   = imshow(magnification_ALL[y-step:y+step,x-step:x+step], vmin=0, vmax=20,origin='lower')
        #im  = imshow(tt[x-step:x+step,y-step:y+step], vmin=0, vmax=20,origin='lower')
        ax.set_xlabel('x')		
        ax.set_ylabel('y')
        ax.set_xticks([0,step,step*2])
        #ax.set_xticklabels([str(x-step),str(x),str(x+step)])
        x1= (x-step-CRPIX1)/(math.cos(dec/180.*3.14159265))*CDELT1+CRVAL1  
        x2= (x+step-CRPIX1)/(math.cos(dec/180.*3.14159265))*CDELT1+CRVAL1
        ax.set_xticklabels(['%9.5f' %(x1 ),str(ra),'%9.5f' %(x2)])
        ax.set_yticks([0,step,step*2])
        y1=(y-step-CRPIX2)*CDELT2+CRVAL2
        y2=(y+step-CRPIX2)*CDELT2+CRVAL2
        ax.set_yticklabels([ '%9.5f' %(y1),str(dec),'%9.5f' %(y2)  ])
        savefig(name+'.png')
        fig.colorbar(im, shrink=0.5, aspect=5)
        #show()
        #pdb.set_trace()
        
    if plot3d == 1:
      axis_length = len(alpha_x[0,:])
      fig = plt.figure()
      ax = Axes3D(fig) 
      #x=np.linspace(1,axis_length,axis_length)
      #y=np.linspace(1,axis_length,axis_length)
      axisx=np.linspace(y-step,y+step,step*2)
      axisy=np.linspace(x-step,x+step,step*2)
    
      # plot surface
      X, Y = np.meshgrid(axisx, axisy) 
      #surf = ax.plot_surface(X[y-50:y+50,x-50:x+50], Y[y-50:y+50,x-50:x+50], alpha_x_ALL[y-50:y+50,x-50:x+50],rstride=1, cstride=1, alpha=0.3, cmap=cm.jet)
      surf = ax.plot_surface(X, Y, magnification_ALL[y-step:y+step,x-step:x+step],rstride=1, cstride=1, alpha=0.3, cmap=cm.jet)
      #cset=plt.contour(X, Y, self.z,zdir='z',offset=0)
      #ax.clabel(cset, fontsize=9, inline=1)
      #ax.set_zlim3d(0, 30)
      ax.set_xlabel('DEC')
      ax.set_ylabel('RA')
      ax.set_zlabel('Z')
      ax.set_zlim3d(0.,20,50)
      fig.colorbar(surf, shrink=0.5, aspect=5)

      # plot contour
      cset = ax.contour(axisx, axisy, magnification_ALL[y-step:y+step,x-step:x+step],50)
      ax.clabel(cset, fontsize=11, inline=1)
      fig.colorbar(cset, shrink=0.5, aspect=5)
      #ax.set_zlim3d(0, max(maxz))
      ax.set_xlabel('y')		#(r'$\phi_\mathrm{real}$')
      ax.set_ylabel('x')		#(r'$\phi_\mathrm{im}$')
      ax.set_zlabel('counts')	#(r'$V(\phi)$')
      ax.set_zlim3d(0.,20,50)
      if name != None:
          savefig(name+'.png')
      else:
          savefig(str(x)+str(y)+os.path.basename(xfits)[0:11]+'.png')
      pdb.set_trace()    
    
    return(magnification)
      
def  angular_distance(z1,z2):

   '''
Parameters:	for cosmocalc
z - redshift
H0 - Hubble constant (default = 71)
WM - Omega matter (default = 0.27)
WV - Omega vacuum (default = 1.0 - WM - 0.4165/(H0*H0))
Return type:	
dictionary of cosmology values (name_unit = value)
   '''
   from scipy import constants
   c_kms = constants.c / 1000.
   H0    =  71.            #####  change the cosmic constants here
   WM    =  0.27
   H0    =  70.
   WM    =  0.3
   dm1   = cosmocalc(z1,H0=H0,WM=WM)['DCMR_Mpc']
   dm2   = cosmocalc(z2,H0=H0,WM=WM)['DCMR_Mpc']
   dh_2  = (c_kms / H0 )**2
   Ok    = 1.0 - WM - 0.4165/(H0*H0)
   # check Hogg 9906116
   out = 1. / (1. + z2) * (dm2*np.sqrt(1. + Ok*dm1**2 / dh_2) -dm1*np.sqrt(1. + Ok*dm2**2 / dh_2))   
   #pdb.set_trace()
   return(out)
   


def tmp():
   #                             EXAMPLE  of MPFIT  by xingxing Huang

 x = array(range(100))
 p = [5.7, 2.2, 500., 1.5]
 #y = [ p[0] + p[1]*i + p[2]*i**2 + p[3]*sqrt(i) + p[4]*log(i)   for i in x  ]
 y =  p[0] + p[1]*x + p[2]*(x**2) + p[3]*sqrt(x) + random()*10.
 err = x*0+1.
 fa = {'x':x, 'y':y, 'err':err}
 pdb.set_trace()
 m = mpfit(myfunct, p, functkw=fa)
 print 'status = ', m.status
 if (m.status <= 0): print 'error message = ', m.errmsg
 print 'parameters = ', m.params
 print 'para error = ', m.perror
 pdb.set_trace()


   
def myfunct(p, fjac=None, x=None, y=None, err=None):
    # Parameter values are passed in "p"
    # If fjac==None then partial derivatives should not be
    # computed.  It will always be None if MPFIT is called with default
    # flag.
    model = func(x, p)
    # Non-negative status value means MPFIT should continue, negative means
    # stop the calculation.
    status = 0
    return([status, (y-model)/err] )

def median(numbers):
  '''
  Return the median of the list of numbers
  '''
  # Sort the list of numbers and take the middle element.
  n = len(numbers)
  copy = numbers[:] # So that 'numbers' keeps its original order
  copy.sort()
  if n & 1: # There is an odd number of elements
    return copy[n / 2]
  else:
    return (copy[n / 2 - 1] + copy[n / 2]) / 2

def func(x, p):
   a,b=p
   f= a + b*x
   return(f)

   
def residuals(p, y, x):
   return y - func(x, p)  
   
   
def flux2mag(flux, zero_pt="", abwave=""):
    """ flux2mag(flux, zero_pt="", abwave="")
    http://www.astrobetter.com/wiki/tiki-index.php?page=Python+Switchers+Guide
    Convert from flux (ergs/s/cm^2/A) to magnitudes
    returns a float or array of magnitudes
    
    INPUTS: 
      flux -  float or array flux vector, in erg cm-2 s-1 A-1

    OPTIONAL INPUTS:
      zero_pt - float giving the zero point level of the magnitude.
                If not supplied then zero_pt = 21.1 (Code et al 1976)
                Ignored if the abwave is supplied
      abwave - wavelength float or array in Angstroms.   If supplied, then 
               FLUX2MAG() returns Oke AB magnitudes (Oke & Gunn 1983, ApJ, 266,
               713). 
      
    OUTPUTS: 
      mag - magnitude vector.
        
    NOTES:
      1. If the abwave input is set then mag is given by the expression 
         abmag = -2.5*alog10(f) - 5*alog10(abwave) - 2.406
         Otherwise, mag is given by the expression
         mag = -2.5*alog10(flux) - zero_pt
    
    >>>flux2mag(10.0)
    -23.6
    """

    if not bool(zero_pt): zero_pt = 21.10        #Default zero pt
    if flux <=0:
        print 'flux warning: ',flux
        return(99)
        
    if abwave != "":
        mag = -2.5*math.log10(flux) - 5*math.log10(abwave) - 2.406
    else:
        mag = -2.5*math.log10(flux) + zero_pt    
    return mag
    
    
def flux2fv(flux,  abwave=""):
    """ flux2fv(flux, zero_pt="", abwave="")
    """
    constant_c = 299792458.0 
     
    #if flux <=0:
    #    print 'flux warning: ',flux
    #    return(99)
        
    if abwave != "":
        fv = flux*abwave**2/(constant_c*1.e10)
    else:
        sys.exit('No wavelength defined!')   
    return fv
    
def fluxe2fve(fluxe,  abwave=""):
    constant_c = 299792458.0
    fve = fluxe*abwave**2/(constant_c*1.e10)
    return(fve)

def fv2mag(fv):
    mag = -2.5*np.log10(fv)-48.6
    return(mag)        
    
def mag2flux(mag, zero_pt="", abwave=""):
    """ 
    >>>mag2flux(20.0)
    """
    
    if not bool(zero_pt): zero_pt = 21.10        #Default zero pt
    
    if abwave != "":
        #mag = -2.5*n.log10(flux) - 5*n.log10(abwave) - 2.406
        flux = 10**( (mag+2.406+5*math.log10(abwave))/(-2.5) ) 
    else:    
        flux = 10**( (mag+zero_pt)/(-2.5) ) 
    return flux        


def mage2fluxe(mag, mage, zero_pt="", abwave=""):
    """ 
    >>>mag2flux(20.0)
    """
    if not bool(zero_pt): zero_pt = 21.10        #Default zero pt
    
    if abwave != "":
        #mag = -2.5*n.log10(flux) - 5*n.log10(abwave) - 2.406
        fluxe = (mage/(-2.5) ) * mag2flux(mag,abwave=abwave)*2.30
    else:    
        fluxe = (mage/(-2.5) ) * mag2flux(mag,zero_pt = zero_pt )*2.30
    return abs(fluxe)       

def fluxe2mage(flux,fluxe, zero_pt="", abwave=""):

    if not bool(zero_pt): zero_pt = 21.10        #Default zero pt


    mage = fluxe/flux*2.5/np.log(10.)        # using the method as in Sextractor
    #mage1 = 2.5*np.log10(1+fluxe/flux)    
    
    if flux<0:
        mag = flux2mag(fluxe,zero_pt=zero_pt, abwave=abwave)      
        return(mag)
    else:
        return mage
        
def jy2flux(jy, abwave=5007.):     
    #jy = jy *1.e6
    flux = 1.e-23*constants.c*1.e10/abwave**2*jy
    return(flux)

def jy2mag(jy):    
    #jy = jy *1.e6 
    # 1 jy = 1.e-23 erg s-1 Hz-1 cm-2
    #flux = 1.e-23*constants.c*1.e10/abwave**2*jy
    #mag  = flux2mag(flux, abwave=abwave)
    mag = -2.5*np.log10(jy)+8.9
    return(mag)    
    
def wmean(data, err): 
      '''
      you can also use :
         np.average([],weights=[])
      '''
      sumdata=0.
      sumerr = 0.
      sumweight = 0.
      for i in range(len(data)):
          if err[i]==0: 
              continue
          sumdata += data[i]/err[i]**2
          #sumerr += 1./err[i]
          sumweight += 1./err[i]**2
      if sumweight ==0:
          return(0,0)    
      mean = sumdata/sumweight
      
      meane = np.sqrt(1./sumweight)
      return(mean, meane)  

def get_con(f1,f1e,f2,f2e,index = [9,13,15]):
    '''
    return the continuum and the error. 
    In default calculate the F814W, F125W, F160W
    '''
    bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
    width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
       [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]] 
    zero = [4.5743944000000001e-18, 3.2266885000000002e-18, 1.3112398000000001e-18, 5.0740468999999999e-19, 3.1489897000000001e-19, 1.8267533000000001e-19, 7.8443327999999996e-20, 1.1931234e-19, 9.9942164999999995e-20, 7.0073061000000005e-20, 1.5213060999999999e-19, 3.0385746000000003e-20, 1.5274191e-20, 2.2483535e-20, 1.473721e-20, 1.9275671999999999e-20]
    la1 = width[index[0]][0]*10. # wavelegth
    la3 = width[index[2]][0]*10.
    la  = width[index[1]][0]*10.
    con1 = f1*la1**2/la**2
    con1e = f1e*la1**2/la**2
    con3 = f2*la3**2/la**2
    con3e = f2e*la3**2/la**2
    con,cone = wmean([con1,con3],[con1e,con3e])
    mag = flux2mag(con,abwave=width[index[1]][0]*10.)
    mage = cone/con*2.5/np.log(10.)  
    return(mag,mage)