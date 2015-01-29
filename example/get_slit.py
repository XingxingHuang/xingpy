import os,sys,string,glob,time                                                                                    
import pdb
from pyraf import iraf
from pyraf.iraf import stsdas
import numpy as np
from pylab import *
import pyfits


def run(x = 1, y = 1, width = 10.,fits='ibo1l4010_drz.fits',outname='spec.png'):
    if isinstance(x, float) and isinstance(x, float):
      print 'Convert ot pixel scale for X Y.'
      # old way   wrong
      '''
      ra = x
      dec = y
      header = pyfits.getheader(fits,1)
      CRVAL1  =  header['CRVAL1']                                                 
      CRPIX1  =  header['CRPIX1']                                 
      #CDELT1  =  header['CDELT1'] 
      CDELT1  =  header['CD1_1']                                                                                               
      CRVAL2  =  header['CRVAL2']                            
      CRPIX2  =  header['CRPIX2']                         
      #CDELT2  =  header['CDELT2']
      CDELT2  =  header['CD2_2']
      x= int((ra-CRVAL1)/(CDELT1)*(math.cos(dec/180.*3.14159265))+CRPIX1)         # RA DEC >>   x y
      y= int((dec-CRVAL2)/(CDELT2)+CRPIX2)
      '''
      header = pyfits.getheader(fits,1)
      xsize  = header['NAXIS2']
      ysize  = header['NAXIS1']
      
      iraf.stsdas.toolbox.imgtools.rd2xy(fits+"[1]",x,y,hour=False)
      x = iraf.stsdas.toolbox.imgtools.rd2xy.x
      y = iraf.stsdas.toolbox.imgtools.rd2xy.y
      x = int(x)
      y = int(y)
      # new way
      print 'X,Y %i %i' %(x,y )
    elif isinstance(x, int) and isinstance(x, int):  
      print 'Using pixel scale for X Y.'
    else:
      print 'ERROR:  wrong value for X Y'
      pdb.set_trace()
    f=pyfits.open(fits)
    wave = []
    flux = []
    flux2 = []  # paralel slit
    dsize = 2  # the seperate width    # need to change
    for i in range(x-10.,x+230):                                                                                  
      wave.append(i)
      flux.append(0.)
      flux2.append(0.)
      if i>xsize-1: 
           print 'Out of size X:',x,xsize
           return(0)
      for j in range(y-width,y+width+1):
        #pdb.set_trace()
        if j>ysize-1: 
           print 'Out of size Y:',y,ysize
           return(0)
        flux_xy=f[1].data[j,i]
        flux[i-x+10] = flux[i-x+10]+flux_xy
      flux2[i-x+10] = flux2[i-x+10]+f[1].data[y+width+dsize,i]+f[1].data[y-width-dsize,i]

    fig = plt.figure(figsize=(8,6))
    #pdb.set_trace()
    ax = fig.add_subplot(111)    
    plot([x,x],[0,0.3],'--')
    plot(wave,flux,'-')
    plot(wave,np.array(flux)-1.5*np.array(flux2),'.-')
    #ylim(0,1)
    xlim(x-10,x+280)
    savefig(outname)

    
# Just make a test with the following:
if __name__ == '__main__':

  width = 1

  fits1 = 'ibo1l4010_drz.fits'  
  fits2 = 'ibo1l4020_drz.fits'  
  fits3 = 'ibo1l3010_drz.fits'  
  fits4 = 'ibo1l3020_drz.fits'                                                                                    
  fits = fits3

  namepre = fits.split('_')[0]
  namepre = './spec/'+namepre
  #star 
  x = 260.09191
  y = 35.614844
  name = namepre+'_'+str(width)+'_star.png'
  run(x = x, y = y, width = width,fits=fits,outname=name)
  print name
  print 

  # Jsample1  out of the bouder
  x = 260.059016 
  y = 35.627975
  name = namepre+'_'+str(width)+'_J29.png'
  run(x = x, y = y, width = width,fits=fits,outname=name)
  print name
  print 

  # J sample 2
  x = 260.072527 
  y = 35.620200
  name = namepre+'_'+str(width)+'_J30.png'
  run(x = x, y = y, width = width,fits=fits,outname=name)
  print name
  print 

  # Y sample
  x = 260.084840 
  y = 35.606984
  name = namepre+'_'+str(width)+'_Y9.png'
  run(x = x, y = y, width = width,fits=fits,outname=name)
  print name
  print 
  pdb.set_trace()

