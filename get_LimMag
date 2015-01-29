#!/usr/bin/env python

'''
get the limiting magnitude for the fits file
# Xingxing, Huang
# email: hxx@mail.ustc.edu.cn
# Jan 28, 2013
'''

'''
Aperture size from Ford's email:
My first comment is that a 4'' aperture (is 4'' the diameter ?) is far too large for computing a limiting magnitude. 
Our high-z sources are barely resolved or unresolved,
 in which case the aperture size should be small enough to encompass approximately half the light for very faint objects. 
 The FWHM for stars is ~3.0 pixels (measured with ATV), which implies that the aperture diameter should be ~0.18''.   
 Figure 7.5 in the Cycle 21 WFC3/IR Handbook shows that the diameter encompassing half the light is ~0.26''. 
Rychard Bouwens calculates his 5-sigma limiting magnitudes for an aperture with a diameter of 0.35''.
'''
# To do:



import os,sys,string,glob,time
import pdb
import numpy as np
import pyfits
from scipy.ndimage.filters import median_filter

## personal import
#from HSTzp import HSTzp



def savefits(data, headerfile,output):
    '''
  save fits file based on the header of the other file.
    '''
    hdu = pyfits.PrimaryHDU(data)
    hdu.header = pyfits.getheader(headerfile)
    hdulist = pyfits.HDUList([hdu]) 
    hdulist.writeto(output)   

class run():
    """
    
    run
    """

    def __init__(self,indir='',outdir ='', infile='',outfile=None,counts=1, zero=0, sigma = 5., box = 10, photobox=6.15,wavelength = 0., printinfo=0):

      self.indir   = indir
      self.infile   = infile
      #self.infile  = '../a2744_galfit/files/ca2744_f160w_sci.fits'
      self.outdir = outdir
      self.outfile  = outfile
      self.wavelength = wavelength #Pivot wavelength (Angstroms)
      self.sigma = sigma    # 5 sigma limiting magitude ?
      self.box   = box         # box size to calculate. It will cost time when this is set to a large number.
      self.photobox = photobox  # aperture size that used for limiting mag calculation
      self.zero    = zero     # zero point
      self.counts = 1          # in units of counts or counts/s
      self.index  = 0           # in case there is multi fits 
      self.filename = os.path.join(self.indir,self.infile)
      if not os.path.isfile(self.filename):
          sys.exit('File not found:  '+os.path.join(self.filename))
      if self.outfile == None:
           self.output =self.filename.replace('.fits','_lim.fits')
      else:
           self.output = os.path.join(self.outdir,self.outfile)     
              

    def run(self):
      box = self.box
      sigma = self.sigma
      wavelength = self. wavelength
      photobox = self. photobox
      output = self.output

      f=pyfits.open(self.filename)
      # zeropoint
      #fexptime=f[self.index].header['EXPTIME']
      #if wavelength ==0 :
      #    wavelength = f[self.index].header['PHOTPLAM']
      if self.counts ==1 :
          zeropoint = self.zero 
      else:
          zeropoint = self.zero
      # data
      data = f[self.index].data
      xsize = np.shape(data)[0]
      ysize = np.shape(data)[1]
      f.close()

      print 'run the median filter ...'
      data_median = median_filter(data,size=box)
      print 'run the sigma filter ...'
      data_sigma   = (data - data_median)**2
      data_std       = np.sqrt(median_filter(data_sigma,size=box))*sigma*np.pi*photobox**2/4.  # 4 is used to convert diameter to radius.
      print 'calculate the magnitude'
      data_mag     = -2.5*np.log10(data_std)+zeropoint
      #  wrong
      #limmag = np.zeros(shape=(xsize,ysize))
      #flux2mag = lambda c :-2.5*np.log10(c) - 5*np.log10(wavelength) - 2.406
      #getmag = lambda c : flux2mag(np.std(c)*sigma) +zeropoint
      #limmag = [ getmag(data[(i-box):(i+box),(j-box):(j+box)])   for i in range(box,xsize-box,box) for j in range(box,ysize-box,box)]
      # exclude the edge
      #data[0:box,:]=0
      #data[:xsize-box,:]=0
      #data[:,0:box]=0
      #data[:,ysize-box:]=0
      savefits(data_mag,self.filename,output)
      print 'DONE!'
      pdb.set_trace()




      

if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  text = 'Tips:  Use the codes to change more parameters.\n       Use the aperture size of 6.15 (0.4 arcsec) for HST.\n  '
  usage='USAGE: '+mod+" file [aperture size]\n"+text
  opts1="i"
  opts2=[]
  
  try:
    opts, args = getopt.getopt(sys.argv[1:],opts1,opts2)
  except getopt.GetoptError:
    sys.exit(usage)

  # options
  printinfo = 0
  for opt,arg in opts:
    if '-i' in opt:
        printinfo = 1
    
  # args
  try:
    infile = args[0]
    photobox = args[1]
  except Exception:
    print
    sys.exit(usage)

  #zero = HSTzp(infile)
  zero = 21.58
  photobox = 6.15 # 0.4"
  output = 'output.fits'
  outdir = './'
  if os.path.isfile(os.path.join(outdir,output)):
  	sys.exit('File exits! '+ os.path.join(outdir,output))
  a=run(indir='',outdir =outdir, infile=infile, outfile=output,counts=1, zero=zero, sigma = 5., box = 10, photobox=photobox,wavelength = 0., printinfo=0)
  a.run()
  
  
  
  
  
  
  
  
  

