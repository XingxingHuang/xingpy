#!/usr/bin/env python
################### main step ##############
# ds9 with optimized zscale
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


def usage():  
  #print '%s [-h|-h|-h] [--help|--help=] args' %(mod)
  txt = '\n\tUsage: '+ mod + ' [options] obs\n\n'\
        '\t--sigma=3.\n'\
        '\t--iters=3\n'
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


if __name__ == '__main__':
  ############################################################
  # parameters
  ############################################################
  import getopt
  option1 = "h"
  option2 = ["help","option",'sigma=','iters=','size=']
  mod  = os.path.basename(sys.argv[0])
  try:
    opts, args = getopt.getopt(sys.argv[1:],option1,option2)
    params = params_cl()
  except getopt.GetoptError:      
    usage()
  if args==[]: usage()  
  
  # values
  sigma = 3.
  iters = 3  
  size = None
  for o, a in opts:  
    if o in ("-h", "--help"):  
        usage() 
    if o in '--sigma':
        sigma = a
    if o in '--iters':
        if a=='None':
          iters =None
        else:  
          iters = int(a)
    if o in '--size':
        size = a      
                   
  if len(args)==1 and '*' in args:
    infiles = glob(args)
  else:
    infiles=args  

  #
  radius = 3.
  print '='*80
  print '    Limiting magnitude calculated with radius of %i pixels' %(radius)
  print '='*80
  print 
  
  # start 
  zscale = []
  cmd = 'ds9 '
  for fitsfile in infiles: 
     data = pyfits.getdata(fitsfile)
     maskedarr = sigma_clip(data, sig=sigma,iters=iters,copy=False)
     odata = maskedarr.data[-maskedarr.mask]
     mean = np.mean(odata)
     std = np.std(odata)
     zscale1 = mean-std
     zscale2 = mean+3*std
     zscale.append([zscale1,zscale2])
     zeropoint = HSTzp(fitsfile)
     lim_mag = -2.5*np.log10(std*np.pi*(radius)**2)+zeropoint
     print '%s  \n     lim_mag: %5.2f   zscale  %f  %f ' %(fitsfile,lim_mag, zscale1, zscale2)
     cmd += '%s    -scale limits %f %f    -cmap Heat ' %(fitsfile, zscale1, zscale2)
  cmd +='  &'   
  print 
  print
  print cmd
  print
     
  
sys.exit()
