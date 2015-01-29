#!/usr/bin/env python
################### main step ##############
# photometry for a position
#
import sys
import os,pdb
import numpy as np
from pyraf import iraf
import pyfits
from glob import glob

# notice
from coeio import params_cl, decapfile
from astropy.stats import sigma_clip
from pro_img import savefits
from pro_tools import checkinfo

def usage():  
  #print '%s [-h|-h|-h] [--help|--help=] args' %(mod)
  txt = '\nAperture photometry \n'\
        '\n\tUsage: '+ mod + ' [options] x y obs\n\n'\
        '\t--sigma=3.\t for background\n'\
        '\t--iters=None\t for background\n'\
        '\t--size=3\t for limiting manitude\n'\
        "\t--det='f160w\t for detection image'\n"\
        "\t--threshold=2.\n"\
        "\t please revise the program to choose a different size of radius"
  print txt     
  sys.exit()

def HSTzp(infile, forcesec=False, forcetot=False):
    """
    Zeropoint of HST image derived from FITS keywords
    http://www.stsci.edu/hst/acs/analysis/zeropoints
    http://www.stsci.edu/hst/wfc3/phot_zp_lbn
    """
    if not (infile.endswith('.fits') or infile.endswith('.fits.gz')):
        infile = infile + '.fits'
    
    f = pyfits.open(infile, memmap=1)
    header = f[0].header
    photflam = header.get('PHOTFLAM', None)  # inverse sensitivity (erg / cm^2 / s / Ang)
    photplam = header.get('PHOTPLAM', None)  # pivot wavelength
    photplam0 = 5475.4
    pzpt     = header.get('PHOTZPT')
    bunit    = header.get('BUNIT').strip()
    exptime  = header.get('EXPTIME')
    #print infile
    #print pzpt, bunit, exptime, photflam, photplam
    #print bunit,
    #if ((bunit[-2:] <> '/S') or (forcesec == True)) and (forcetot == False):
    if ((bunit[-2:] <> '/S') or (forcetot == True)) and (forcesec == False):
        #print 'NOT SEC'
        photflam = photflam / exptime
    #zp = -21.10 - 2.5 * log10(photflam) - 5 * log10(photplam) + 18.6921
    zp = pzpt - 2.5 * np.log10(photflam) - 5 * np.log10(photplam / photplam0)
    #import pdb;pdb.set_trace()
    #print infile, zp
    return zp

def get_dist(imgdata,x,y):
    ''' return an array include the distance'''
    size1, size2 = imgdata.shape
    num1 = np.arange(size1).reshape(size1,1)
    num2 = np.arange(size2).reshape(1,size2)
    index = num1+num2*1.j
    position = posx+posy*1.j
    distance = np.sqrt( (index.real-position.real )**2+(index.imag-position.imag )**2  )
    return(distance)

def flux2mag(flux,fluxe,zeropoint):
    if flux<=0:
      mage = -2.5*np.log10(fluxe)+zeropoint
      return(99,mage)
    mag = -2.5*np.log10(flux)+zeropoint
    mage = fluxe/flux*2.5/np.log(10.)
    return(mag,mage)

def center_func(data):
    out = 2.5*np.median(data)-1.5*np.mean(data)  
    return(out)

def get_mask(infiles,det_img,threshold,posx,posy,radius,r0,r1,r2,sigma,iters):
  '''
  get the mask for the infiles with keys defined in det_img
  '''
  # mask
  images = {}
  for i,fitsfile in enumerate(infiles): 
     for key in det_img:
      if not key in fitsfile:
        continue
      else:
        images[key]=fitsfile
 
  #out_mask_back = None     
  #out_mask_obj0 = None
  out_mask_obj1 = None
  outfits = None
  out_mask_back_used = None  
  out_mean=None
  out_std = None 
  for key in det_img:
    fitsfile = images[key]
    data = pyfits.getdata(fitsfile)
    distance = get_dist(data,posx,posy)
    mask_back = np.where(((distance>r1) & (distance<r2)), True, False)
    mask_obj0  = np.where((distance<r0), True, False)
    maskedarr = sigma_clip(data[mask_back], sig=sigma,iters=iters,cenfunc=center_func,copy=False)
    odata = maskedarr.data[-maskedarr.mask]
    #pdb.set_trace()
    mean = np.mean(odata)
    std = np.std(odata)
    mask_obj1  = np.where((distance<r0) & (data>mean+threshold*std),True, False)
    mask_back_used =  np.where(((distance>r1) & (distance<r2) & (abs(data-mean)/std<sigma) ),True,False)
    zeropoint = HSTzp(fitsfile,forcesec=True)   
    exptime = pyfits.getheader(fitsfile)['EXPTIME']
    lim_mag = -2.5*np.log10(std*np.sqrt(np.pi*(radius)**2) )+zeropoint
    #lim_mag0 = -2.5*np.log10(std*N_pixel)+zeropoint
    print '%s  \n\tlim_mag\t %5.2f \tzeropoint %6.3f' %(fitsfile,lim_mag, zeropoint)
    print '\tmean std:\t%f %f' %(mean*exptime, std*exptime)     
    #out_mask_back = None
    #out_mask_obj0 = None
    if out_mask_obj1==None:
       out_mask_obj1 = mask_obj1
    else:   
       out_mask_obj1 += mask_obj1 
    if len(det_img)==1:
       outfits = fitsfile
       out_mask_back_used = mask_back_used   
       out_mean = mean
       out_std = std
       return(out_mask_obj1,outfits,out_mean,out_std,out_mask_back_used)
  return(out_mask_obj1)   
      
if __name__ == '__main__':
  ############################################################
  # parameters
  ############################################################
  import getopt
  option1 = "h"
  option2 = ["help","option",'save','sigma=','iters=','size=','det=','threshold=']
  mod  = os.path.basename(sys.argv[0])
  try:
    opts, args = getopt.getopt(sys.argv[1:],option1,option2)
    params = params_cl()
  except getopt.GetoptError:      
    usage()
  if args==[]: usage()  
  
  # values
  save = True
  sigma = 3.
  iters = None  
  size = 0.4/0.06/2.
  det_img = ['f160w','f140w','f125w']
  spec_det_img = ['f160w']
  threshold=2.
  for o, a in opts:  
    if o in ("-h", "--help"):  
        usage() 
    if o in 'save':
        save=True    
    if o in '--sigma':
        sigma = float(a)
    if o in '--iters':
        if a=='None':
          iters =None
        else:  
          iters = int(a)
    if o in '--size':
        size = float(a)      
    if o in '--det':
        spec_det_img = [a]
    if o in '--threshold':
        threshold = float(a)   
        
  posy = float(args[0])
  posx = float(args[1])
  if len(args)==3 and '*' in args[2]:
    infiles = glob(args[2])  
  else:
    infiles=args[2:]  

  #
  r0 = 4.
  r1 = 6.
  r2 = 10.

  r0 = 3.
  r1 = 13.
  r2 = 20.
  
  r0 = 4.
  r1 = 6.
  r2 = 10.

  #r0 = 2.
  #r1 = 5.
  #r2 = 8.
  
  radius = size
  print '='*80
  print '    Limiting magnitude calculated with radius of %i pixels' %(radius)
  print '='*80
  print 
  
  # mask
  mask_obj1 = get_mask(infiles,det_img,threshold,posx,posy,radius,r0,r1,r2,sigma,iters)
  print
  _mask_obj1,spec_fits,mean,std,mask_back_used=get_mask(infiles,spec_det_img,threshold,posx,posy,radius,r0,r1,r2,sigma,iters)
  
  # save
  if save==True:
     outname = spec_fits.replace('.fits','_seg.fits')
     data = pyfits.getdata(spec_fits)
     outdata = np.where((mask_obj1)|(mask_back_used),data,-1.e11)
     savefits(outdata,spec_fits,outname)
       # ds9 
     zscale1 = mean-std
     zscale2 = mean+3*std
     cmd_check = 'ds9 %s    -scale limits %f %f    -cmap Heat %s &' %(spec_fits, zscale1, zscale2,outname)
     #print '\t',cmd
     #print '\n\n'
     #pdb.set_trace()
  N_pixel_iso = np.sum( np.where(mask_obj1,1.,0)  )


        
  # data
  cmd='ds9 '
  mag_aper = []
  mage_aper = []  
  mag_iso = []
  mage_iso = []  
  for i,fitsfile in enumerate(infiles): 
     data = pyfits.getdata(fitsfile)
     distance = get_dist(data,posx,posy)
     N_pixel = np.sum(np.where(distance<r0,1,0))
     mask_back = np.where(((distance>r1) & (distance<r2)), True, False)
     mask_obj0  = np.where((distance<r0), True, False)
     maskedarr = sigma_clip(data[mask_back], sig=sigma,iters=iters,cenfunc=center_func,copy=False)
     odata = maskedarr.data[-maskedarr.mask]
     mean = np.mean(odata)
     std = np.std(odata)
     #mask_obj1  = np.where((distance<5.) & (data>mean+std*threshold),True, False)
     
     zeropoint = HSTzp(fitsfile,forcesec=True)
     zscale1 = mean-std
     zscale2 = mean+3*std
     flux = np.sum(data[mask_obj0]-mean)
     fluxe = np.sum(data[mask_obj0]*0.+std)/np.sqrt(N_pixel)
     flux1 = np.sum(data[mask_obj1]-mean)
     flux1e = np.sum(data[mask_obj1]*0.+std)/np.sqrt(N_pixel_iso)
     #pdb.set_trace()
     # aperture and iso magnitudes
     mag,mage = flux2mag(flux,fluxe,zeropoint)
     mag1,mag1e = flux2mag(flux1,flux1e,zeropoint)
     mag_aper.append(mag)
     mage_aper.append(mage)
     mag_iso.append(mag1)
     mage_iso.append(mag1e)    
     # 
     lim_mag0 = -2.5*np.log10(std*np.sqrt(N_pixel))+zeropoint
     lim_mag = -2.5*np.log10(std*np.sqrt(np.pi*(radius)**2) )+zeropoint
     print '%s  \n\tzeropoint %6.3f lim_mag %5.2f %5.2f ' %(fitsfile, zeropoint,lim_mag,lim_mag0)
     print '\tzscale\t%f %f' %( zscale1, zscale2)
     print '\tflux\t%f %f' %(flux,fluxe)
     print '\tmagnitude(aper,iso)\t%7.2f %4.2f \t%7.2f %4.2f' %(mag, mage, mag1,mag1e)
     cmd += '%s    -scale limits %f %f    -cmap Heat ' %(fitsfile, zscale1, zscale2)
  cmd +='  &'   
  
  print
  print cmd_check
  print
  print 'Aperture photometry'
  for i in range(len(mag_aper)): print '%6.2f %6.2f    ' %(mag_aper[i], mage_aper[i]),
  print '\nISO photometry'
  for i in range(len(mag_iso)): print '%6.2f %6.2f    ' %(mag_iso[i], mage_iso[i]),
  print 
  print
  print cmd
  print
  checkinfo('')   
  
sys.exit()
