import pdb,os
import pyfits
import numpy as np
from os.path import *
from matplotlib import pyplot as plt
from pylab import ion
        


def savefits(data, headerfile,output, overwrite =1):
    '''
  save fits file based on the header of the other file.
    '''
    hdu = pyfits.PrimaryHDU(data)
    hdu.header = pyfits.getheader(headerfile)
    hdulist = pyfits.HDUList([hdu]) 
    if isfile(output):
       if overwrite ==1:
          os.remove(output)
       else:
          print 'Files exits!  ', output
          return()   
    hdulist.writeto(output)   
    

def savefits2(data, filename):
    '''
    save fits without header
    '''
    output = pyfits.PrimaryHDU(data)
    header = output.header  
    if os.path.isfile(filename): os.remove(filename)
    pyfits.writeto(filename, data, header)
