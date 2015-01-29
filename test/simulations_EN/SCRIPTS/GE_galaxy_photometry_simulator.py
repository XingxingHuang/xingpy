#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Simulation to compute photometry errors
# CREATED: 20130713 davidabreu@users.sourceforge.net, clsj
# Adapted from galsim.pro from Ignacio Trujillo
#

"""Adapted from galsim.pro from Ignacio Trujillo"""

import sys
from optparse import OptionParser          # To parse options
from numpy import * # numarray not compatible with pyfits
import pyfits
import os
from random import random
from math import log10
from scipy import median
try:
   import sexcat
except ImportError:
   import catg as sexcat
import time                                 # to measure execution time
from numpy.numarray.random_array import poisson   # Poisson distribution
from numpy import numarray
from pyraf import iraf                      # to convolve images

#Initial models are generated using the GALFIT program fixing all the 
#parameters to the required values

#The convolution with the PSF is done also with GALFIT

#The Poisson noise is done with python

#The background addition is done with python

# Time counter started
t0 = time.time()

# This version is prepared to be used under condor.

def main():
   usage = "usage: %prog [options] inputImage psfImage catFile [rmsImage"
   usage+= "rmsPsfImage kernelImage]\n"
   usage+= "type %prog -h for help"
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                  help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", type=int, default=1,
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   parser.add_option("-r", "--reff", dest="reff", type=float, nargs=2,
                     default=(1., 10.),
                     help="Radio efectivo [default : %default]",
                     metavar="rMin rMax")
   parser.add_option("-e", "--elipt", dest="elipt", type=float, nargs=2,
                     default=(0., 0.8),
                     help="Elipticity range [default : %default]",
                     metavar="eMin eMax")
   parser.add_option("-m", "--mag", dest="mag", type=float, nargs=2,
                     default=(12., 22.),
                     help="Magnitude range [default : %default]",
                     metavar="mMin mMax")
   parser.add_option("-s", "--sersic", dest="sersic", type=float, nargs=2,
                     default=(2., 2.),
                     help="Sersic index range [default : %default]",
                     metavar="nMin nMax")
   parser.add_option("-i", "--iter", dest="iter", type=int, nargs=2,
                     default=(1, 1000),
                     help="Iteration range [default : %default]",
                     metavar="iMin iMax")
   parser.add_option("-x", "--sex", dest="sex",
                     default="default.sex",
                     help="Sextractor file [default : %default]",
                     metavar="FILE")
   parser.add_option("-g", "--gsex", dest="galsexfile",
                     default="galsexfile.sex",
                     help="Sextractor file for galfit [default : %default]",
                     metavar="FILE")
   (options, args) = parser.parse_args()

   verbose=options.verbose

   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")
   
   if len(args) < 3:
      output.write('Not enough arguments. Call with "--help" for help.\n')
      sys.exit()
   elif len(args) > 6:
      output.write('Too many arguments. Call with "--help" for help.\n')
      sys.exit()
   else:
      inputImage = args[0]  # Image for the simulation
      psfImage = args[1]    # PSF image fileName
      catFile = args[2]     # Name for the output catalogue
   if len(args) > 3:
      rmsImage = args[3]    # RMS Image
      rmsPsfImage = args[4] # RMS Image for psf13
      kernelImage = args[5] # Kernel Image
   else:
      rmsImage = ''
      kernelImage = ''
      rmsPsfImage = ''

   # Loading task from iraf for convolution.
   if iraf.defpac("stsdas") == 0: iraf.stsdas()
   if iraf.defpac("analysis") == 0: iraf.analysis()
   if iraf.defpac("fourier") == 0: iraf.fourier()

   #Size of the image
   cluster = pyfits.getdata(inputImage)
   tam = cluster.shape
   nx = tam[1]
   ny = tam[0]

   #Size of the box (15x15 arcsec)
   lx = 120#60. ;Number of x pixels
   ly = 120#60. ;Number of y pixels

   tmpDir='./'

   #Generation of a matrix with the size of the image
   back = zeros([ly, lx])
   if os.access(tmpDir+'back.fits',os.F_OK): os.remove(tmpDir+'back.fits')
   pyfits.writeto(tmpDir+'back.fits', back) # no header

   #Galaxy center
   xc = 60.#30.
   yc = 60.#30.

   #magnitud limits (K-band)
   mag1 = options.mag[0]
   mag2 = options.mag[1]

   #re limits (pixels)
   #@z=1, 1" is 8 kpc (h=0.7,om=0.3,ol=0.7)
   #1 pix ~ 0.25"
   #re1 = 0.25 #this is 0.5 kpc at z~1
   #re2 = 15.  #this is 30 kpc at z~1
   re1 = options.reff[0]
   re2 = options.reff[1]

   #elipticity limits
   eb1 = options.elipt[0]
   eb2 = options.elipt[1]

   #n limits
   n1 = options.sersic[0]
   n2 = options.sersic[1]

   #position angle galaxy
   pa = 0.

   ##We estimate the exptime from the header of the PSF file
   #exptime = pyfits.getval(inputImage, 'EXPTIME')
   #if verbose: output.write("Exptime "+str(exptime)+"\n")
   photgain = pyfits.getval(inputImage, 'PHOTGAIN')
   zpsex = pyfits.getval(inputImage, 'PHOTZERO')
   pixsize = pyfits.getval(inputImage, 'ARCSPIX')
   seeing = pyfits.getval(inputImage, 'PSFFWHM')
   if verbose:
	output.write("Photgain "+str(photgain)+"\n")
	output.write("Photzero "+str(zpsex)+"\n")
	output.write("Pixelsize "+str(pixsize)+"\n")
	output.write("PSF "+str(seeing)+"\n")

   corr = 0.0 # TODO: put as parameter
   zp = zpsex + corr
   zeropo = str(zp)

   #number of models to generate
   #we put 100 artificial galaxies in grids of 0.5 mag =>
   #10x10 grid => 10000 galaxies

   nsim1 = options.iter[0]
   nsim2 = options.iter[1]
   nsim = nsim2 - nsim1 + 1

   inputName=inputImage.split('/')[-1]   

   Name = "galsim_"+inputName
   Name+= "_r_"+str(re1)+"_"+str(re2)+"_e_"+str(eb1)+"_"+str(eb2)+"_m_"
   Name+= str(mag1)+"_"+str(mag2)+"_n_"+str(n1)+"_"+str(n2)+"_i_"
   Name+= str(nsim1)+"_"+str(nsim2)

   re = zeros([nsim])
   eb = zeros([nsim])
   n = zeros([nsim])
   mag = zeros([nsim])
   mag = zeros([nsim])
   modelmag = zeros([nsim])
   modelre = zeros([nsim])
   modelbest = zeros([nsim])
   #seed = 1001

   file=open(catFile,'w')

   file.write( '#  1 NUMBER\n#  2 MAG_MODEL\n#  3 RE_MODEL\n#  4 SERSIC_MODEL\n#  5 ELIP_MODEL\n#  6 MAG_APER_MODEL\n#  7 MAG_BEST_MODEL\n#  8 KRON_MODEL\n#  9 DETECTION\n# 10 MAG_BEST_IMG\n# 11 MAGERR_BEST_IMG\n# 12 MAG_APER_IMG\n# 13 MAGERR_APER_IMG\n# 14 KRON_IMG\n# 15 MAG_APER_PSF\n# 16 MAGERR_APER_PSF\n# 17 MAG_BEST_PSF\n# 18 A_IMAGE_MODEL\n# 19 B_IMAGE_MODEL\n# 20 THETA_SKY_MODEL\n# 21 FLUX_RADIUS_MODEL\n# 22 A_IMAGE_IMG\n# 23 B_IMAGE_IMG\n# 24 THETA_SKY_IMG\n# 25 FLUX_RADIUS_IMG\n') # Header

   for i in arange(nsim1, nsim2):
      j=i-nsim1
      #Sizes are generated logarithmically
      if re1 == re2:
         re[j] = re1
      else:
         u = random() # seed not used any more
         re[j] = log10(re1) + (log10(re2) - log10(re1)) * u
         re[j] = 10 ** (re[j])
      # Eccentricity
      if eb1 == eb2:
         eb[j] = eb1
      else:
         u = random()
	 eb[j] = eb1 + (eb2 - eb1) * u	
      # Sersic index are generated logarithmically
      if n1 == n2:
         n[j] = n1
      else:
         u = random()
         n[j] = log10(n1) + (log10(n2) - log10(n1)) * u      
         n[j] = 10. ** (n[j])
      # Magnitude
      if mag1 == mag2:
         mag[j] = mag1
      else:
         u = random()
         mag[j] = mag1 + (mag2 - mag1) * u
      if verbose: output.write("i mag re n eb : %i %f %f %i %f\n" %(i, mag[j], re[j], n[j], eb[j]))
   
      # Creating the GALFIT task for generating the clean models
      fileGalModel = open(tmpDir+'galmodel'+str(i)+'.script','w')
      fileGalModel.write( '# IMAGE PARAMETERS\n')
      fileGalModel.write( 'A) '+tmpDir+'back.fits ' + '# Input Data image (FITS file)\n')
      fileGalModel.write( 'B) '+tmpDir+'galmodel'+str(i)+'.fits # Name for the output image\n')
      fileGalModel.write( 'C) none                # Noise image name ' + '(made from data if blank or "none")\n')
      fileGalModel.write( 'D) '+psfImage+' # Input PSF image and (optional) diffusion kernel\n')
      fileGalModel.write( 'E) 1                   # PSF oversampling factor relative to data\n')
      fileGalModel.write( 'F) # Pixel mask (ASCII file or FITS file with non-0 values)\n')
      fileGalModel.write( 'G) none # ' + 'Parameter constraint file (ASCII)\n')
      fileGalModel.write( 'H) 0 ' + str(int(lx)) + ' 0 ' + str(int(ly)) + ' # Image region to fit (xmin xmax ymin ymax)\n')
      fileGalModel.write( 'I) 120   120           # Size of convolution box (x y)\n')
      fileGalModel.write( 'J) ' + zeropo + '       # Magnitude photometric zeropoint\n')
      fileGalModel.write( 'K) 1 1           # Plate scale (dx dy)\n')
      fileGalModel.write( 'O) regular             # Display type (regular, ' + 'curses, both)\n')
      fileGalModel.write( 'P) 0                   # Create ouput only? (1=yes; ' + '0=optimize)\n')
      fileGalModel.write( 'S) 0                   # Modify/create objects interactively?\n')
      fileGalModel.write( '\n')
      fileGalModel.write( '\n')
      fileGalModel.write( '# sky\n')
      fileGalModel.write( '\n')
      fileGalModel.write( ' 0) sky\n')
      fileGalModel.write( ' 1) ' + '0.00' + '     0  ' + '# sky background       [ADU counts]\n')
      fileGalModel.write( ' 2) 0.000      0       # dsky/dx (sky gradient in x)\n')
      fileGalModel.write( ' 3) 0.000      0       # dsky/dy (sky gradient in y)\n')
      fileGalModel.write( ' Z) 0                  # output image\n')
      fileGalModel.write( '\n')
      fileGalModel.write( '\n')
      fileGalModel.write( '# Sersic function\n')
      fileGalModel.write( '\n')
      fileGalModel.write( ' 0) sersic             # Object type\n')
      fileGalModel.write( ' 1) ' + str(xc) + ' ' + str(yc) + ' 0 0 # position x, y        [pixel]\n')
      fileGalModel.write( ' 3) ' + str(mag[j]) + '      0       # total magnitude\n')
      fileGalModel.write( ' 4) ' + str(re[j]) + '	0	#     R_e	       [Pixels]\n')
      fileGalModel.write( ' 5) ' + str(n[j]) + ' 0	 # Sersic exponent (deVauc=4, expdisk=1)\n')
      fileGalModel.write( ' 8) ' + str(1. - eb[j]) + '	 0	 # axis ratio (b/a)\n')
      fileGalModel.write( ' 9) ' + '90' + '	   0	   # position angle (PA)  [Degrees: Up=0, Left=90]\n')
      fileGalModel.write( '10) 0.0	 0	 # diskiness (< 0) or boxiness (> 0)\n')
      fileGalModel.write( ' Z) 0 		 # output image (see above)\n')
      fileGalModel.write( '\n')
   
      fileGalModel.close()
   
      # Running GALFIT to create the clean and convolved model
      cmnd='galfit '+tmpDir+'galmodel' + str(i) + '.script'
      if verbose: output.write(cmnd+"\n")
      os.system(cmnd)
      if verbose: output.write('galfit execution finished\n')   
  
      galSexFile=options.galsexfile
 
      # We run SExtractor to obtain aperture photometry of the model.
      iraf.imcopy(tmpDir+'galmodel'+str(i)+'.fits[2]',tmpDir+'galmodelaux'+str(i)+'.fits')
      if verbose: output.write('Making imcopy from galmodel to galmodelaux\n')
      cmnd ='sex '+tmpDir+'galmodelaux'+str(i)+'.fits -c '+galSexFile+' -mag_zeropoint '
      cmnd+=str(zpsex)+' -seeing_fwhm '+str(seeing)+' -catalog_name '+tmpDir
      cmnd+='source.cat'
      if verbose: output.write('We want model photometry: '+cmnd+'\n')
      os.system(cmnd)
      #iraf.imdelete(tmpDir+'galmodelaux.fits')
      data = sexcat.rcat(tmpDir+"source.cat")
      if len(data["NUMBER"])==0:
         modelmag[j] = -9
         modelre[j] = -9
         modelbest[j] = -9
         aImageModel = "-9"
         bImageModel = "-9"
         thetaSkyModel = "-9"
         fluxRadiusModel = "-9"
      else:
         modelmag[j] = data["MAG_APER"][0]
         modelre[j] = data["KRON_RADIUS"][0]
         modelbest[j] = data["MAG_BEST"][0]
         aImageModel = str(data["A_IMAGE"][0])
         bImageModel = str(data["B_IMAGE"][0])
         thetaSkyModel = str(data["THETA_SKY"][0])
         fluxRadiusModel = str(data["FLUX_RADIUS"][0])
      
      # Adding the Poisson Noise
      cleanmodel = pyfits.getdata(tmpDir+'galmodel' + str(i) + '.fits', 2)

      # these are because pyfits use numpy and poisson funtcion is only in
      # numarray. So we convert and then undo.
      noisemodel = poisson(numarray.asarray(cleanmodel.tolist())*photgain) / photgain
      noisemodel = asarray(noisemodel)

      # Adding a piece of the image
      # We select a random piece of the image
      # on the porcen/10 inner center to avoid the borders
      porcen = 8
      u = random()
      #xrandom = 9. * nx / 10. * u + (nx / 10.) / 2.
      xrandom = porcen * nx / 10. * u + ((10. - porcen) * nx / 10.) / 2.
      u = random()
      #yrandom = 9. * ny / 10. * u + (ny / 10.) / 2.
      yrandom = porcen * ny / 10. * u + ((10. - porcen) * ny / 10.) / 2.   

      xi = xrandom - lx / 2.
      xf = xrandom + lx / 2.
      yi = yrandom - lx / 2.
      yf = yrandom + lx / 2.
   
      if verbose: output.write("xi xf yi yf : %i %i %i %i\n" %(xi, xf, yi, yf))
   
      sky = cluster[int(yi):int(yf),int(xi):int(xf)]
      skyvalue = median(sky)
   
      finalmodel = noisemodel + sky
   
      namefinalmodel = tmpDir+'fgalmodel' + str(i) + '.fits'
      if os.access(namefinalmodel, os.F_OK): os.remove(namefinalmodel) 
      pyfits.writeto(namefinalmodel, finalmodel) # no header	
   
      #We run SExtractor to check the detection and magnitude estimations
      #We use MAG_BEST as a measured of the total magnitude
   
      sexfile = options.sex # File with the SExtractor input
   
      #Create the unix line to run SExtractor
   
      filesex = tmpDir+'fgalmodel'+str(i)+'.fits'
      cmnd ='sex '+filesex+' -c '+sexfile+' -mag_zeropoint '+str(zpsex)
      cmnd+=' -catalog_name '+tmpDir+'source.cat'
      if verbose: output.write(cmnd+"\n")

      # We read same image "sky" area but from rms images.
      
      imgrmso = rmsImage 
      imgrmspsf = rmsPsfImage
      
      if imgrmso != "":
         rmsoraw = pyfits.getdata(imgrmso)
	 rmso = rmsoraw[int(yi):int(yf),int(xi):int(xf)]
	 if os.access(tmpDir+"rmso.fits",os.F_OK): os.remove(tmpDir+"rmso.fits")
	 pyfits.writeto(tmpDir+"rmso.fits", rmso)
	 
         if imgrmspsf != "":
            # Convolving! (jarl)
	    kernel = kernelImage
            namefinalmodelpsf = tmpDir+'fgalmodel_psf'+str(i)+'.fits'
	    if os.access(namefinalmodelpsf,os.F_OK): os.remove(namefinalmodelpsf)
	    iraf.fconvolve(namefinalmodel, kernel, namefinalmodelpsf)
	    rmspsfraw = pyfits.getdata(imgrmspsf)
	    rmspsf = rmspsfraw[int(yi):int(yf),int(xi):int(xf)]
	    if os.access(tmpDir+"rmspsf.fits",os.F_OK): os.remove(tmpDir+"rmspsf.fits")
            pyfits.writeto(tmpDir+"rmspsf.fits", rmspsf)
	 
	    #Create the unix line to run SExtractor
	    cmnd ='sex '+namefinalmodel+' '+namefinalmodel+' -c '+sexfile
            cmnd+=' -mag_zeropoint ' + str(zpsex)+' -catalog_name '+tmpDir
            cmnd+='source.cat'
            cmnd2 ='sex '+namefinalmodel+' '+namefinalmodelpsf+' -c '+sexfile
            cmnd2+=' -mag_zeropoint ' + str(zpsex)+' -catalog_name '+tmpDir
            cmnd2+='source2.cat'
	    if verbose: output.write('Se lanza :'+cmnd+"\n"+cmnd2+"\n")
	    os.system(cmnd2)
	    #os.rename(tmpDir+'source.cat',tmpDir+'source2.cat')
	    os.remove(tmpDir+"rmspsf.fits")
	    #iraf.imcopy(tmpDir+"rmso.fits", tmpDir+"rmspsf.fits")
	    os.system("cp "+tmpDir+"rmso.fits "+tmpDir+"rmspsf.fits")
	    os.system(cmnd)
         else:
            if os.access(tmpDir+"rmspsf.fits",os.F_OK): os.remove(tmpDir+"rmspsf.fits")
	    #iraf.imcopy(tmpDir+"rmso.fits", tmpDir+"rmspsf.fits")
	    os.system("cp "+tmpDir+"rmso.fits "+tmpDir+"rmspsf.fits")
            #Create the unix line to run SExtractor
            cmnd ='sex '+namefinalmodel+' '+namefinalmodel+' -c '+sexfile
            cmnd+=' -mag_zeropoint ' + str(zpsex)+' -catalog_name '+tmpDir
            cmnd+='source.cat'
# addition requested by clsj due to problems with groth_wi08-ks
            if os.access(tmpDir+"source2.cat",os.F_OK):
	       os.remove(tmpDir+"source2.cat")
# addition ends
	    if verbose: output.write('Launching: '+cmnd+"\n")
	    os.system(cmnd)
      else:
         cmnd ='sex '+namefinalmodel+' -c '+sexfile+' -mag_zeropoint '+str(zpsex)
      
      # Read the SExtractor catalog: source.cat
      # We took from here all the things from no homogeneous PSF image.
   
      data = sexcat.rcat(tmpDir+"source.cat")
      snum = data["NUMBER"]
      sx = data["X_IMAGE"]
      sy = data["Y_IMAGE"]
      smag = data["MAG_BEST"]
      smagerr = data["MAGERR_BEST"]
      smagaper = data["MAG_APER"]
      smagerraper = data["MAGERR_APER"]
      skron = data["KRON_RADIUS"]
      saImageImg = data["A_IMAGE"]
      sbImageImg = data["B_IMAGE"]
      sthetaSkyImg = data["THETA_SKY"]
      sfluxRadiusImg = data["FLUX_RADIUS"]
 
      #In case there is no source in the field
      #we locate the object out of the field so can not be identified as the central target
   
      if len(snum) == 0:
         distc = [1000.]
         idtarget = 0
      else:
         distc = sqrt((sx - xc) ** 2. + (sy - yc) ** 2.)
      # idtarget = where(ravel(distc == array(distc, copy=0).min()))[0]
      idtarget = list(distc).index(min(distc))
 
      #Criteria for detecting object R<0.5 arcsec
   
#      distlim = 0.5 #Limiting threshold arcsec -> changed for wi08-ks
      distlim = 1.0 #Limiting threshold arcsec
   
      formato = "%f" 
      if distc[idtarget] < distlim / pixsize:   
         detect = 1
         magsexbest = formato %smag[idtarget]
         magerrsexbest = formato %smagerr[idtarget]
	 magsexaper = formato %smagaper[idtarget]
	 magerrsexaper = formato %smagerraper[idtarget]
         resex = formato %skron[idtarget]
         aImageImg = formato %saImageImg[idtarget]
         bImageImg = formato %sbImageImg[idtarget]
         thetaSkyImg = formato %sthetaSkyImg[idtarget]
         fluxRadiusImg = formato %sfluxRadiusImg[idtarget]
      if distc[idtarget] >= distlim / pixsize:   
         detect = 0
         magsexbest = "-9"
         magerrsexbest = "-9"
	 magsexaper = "-9"
	 magerrsexaper = "-9"
         resex = "-9"
         aImageImg = "-9"
         bImageImg = "-9"
         thetaSkyImg = "-9"
         fluxRadiusImg = "-9"

      # Taking things from homogeneous psf image.
      # source2 should exist.
      if os.access(tmpDir+"source2.cat",os.F_OK):
         data = sexcat.rcat(tmpDir+"source2.cat")
         snum = data["NUMBER"]
         sx = data["X_IMAGE"]
         sy = data["Y_IMAGE"]
         smagaper = data["MAG_APER"]
         smagerraper = data["MAGERR_APER"]
	 smagbest = data["MAG_BEST"]
         if distc[idtarget] < distlim / pixsize:
            magpsfaper = formato %smagaper[idtarget]
            magerrpsfaper = formato %smagerraper[idtarget]
	    magpsfbest = formato %smagbest[idtarget]
         if distc[idtarget] >= distlim / pixsize: 
            magpsfaper = "-9"
	    magerrpsfaper = "-9"
	    magpsfbest = "-9"
      else:
         magpsfaper = magsexaper
         magerrpsfbest = magerrsexaper
	 magpsfbest = magsexbest
         magerrpsfaper = "-9"
      
      file.write(str(i) + "\t" + formato %mag[j] + "\t" + formato %re[j] + "\t" + str(n[j]) + "\t" + formato %eb[j] + "\t" + formato %modelmag[j] + "\t" + formato %modelbest[j] + "\t" + formato %modelre[j] + "\t" + str(detect) + "\t" + magsexbest + "\t" + magerrsexbest + "\t" + magsexaper + "\t" + magerrsexaper + "\t" + resex + "\t" + magpsfaper + "\t" + magerrpsfaper + "\t" + magpsfbest+"\t"+aImageModel+'\t'+bImageModel+'\t'+thetaSkyModel+'\t'+fluxRadiusModel+'\t'+ aImageImg+'\t'+bImageImg+'\t'+thetaSkyImg+'\t'+fluxRadiusImg+'\n')

      borrar=['galmodel'+str(i)+'.script',
              'galmodel'+str(i)+'.fits',
              'fgalmodel'+str(i)+'.fits',
              'fgalmodel_psf'+str(i)+'.fits',
              'galmodelaux'+str(i)+'.fits',
               filesex]
      for i in borrar:
         try: os.remove(i)
         except: pass
      os.system("rm galfit.*")
   #if os.access(tmpDir,os.F_OK): os.system('rm -r '+tmpDir) #fuera del bucle

   file.close()

   if verbose: output.write("================\n%i sources executed in %s\n================\n" %(nsim, time.strftime("%H:%M:%S",time.gmtime((time.time() - t0)))))

   sys.exit()

if __name__ == "__main__":
   main()
