# some program about image reduction
import os
import numpy as np 
from os.path import *
import pyfits
import sys

'''
    The commands in this file
img_rebin
savefits
point_in_poly
'''

def  img_rebin(a, xshape, yshape):
    '''
    rebin an array.  image will be rebinned with the size xshape, yshape
    test:   
        a = np.arange(24).reshape((4,6))
        img_rebin(a, 2, 3)
    
    '''
    shape = [xshape , yshape]
    xsize = shape[0]
    ysize = a.shape[0]//shape[0]
    zsize = shape[1]
    msize = a.shape[1]//shape[1]
    #sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    sh = xsize, ysize, zsize, msize
    if np.size(a)!= xsize*ysize*zsize*msize:
          print 'The size are not available;\n  '
          print 'image:  ', np.shape(a)
          print 'output: ', xsize, ysize, zsize, msize
          print
          sys.exit()
    out = a.reshape(sh).mean(-1).mean(1)
    return out
    
    
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
    
    
    
def point_in_poly(x,y,poly):
    '''
    Decide whether the point is inside the polygon.
    '''
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside    