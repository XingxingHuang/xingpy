#!/usr/bin/env python
# ---------------------------------------------------------------------
# revised from catalog.py


import os,sys,string,glob,time
import pdb
from pyraf import iraf
import numpy as np
from pylab import *
import pyfits

class plot:
  """
  make color images using trilogy.py
    
  """
  def __init__(self,mag=[],mage=[]):
    '''
    Plot magnitudes of the all bands for a perticular object.
    '''
    self.mag = mag
    if mage == []: 
      self.mage = np.array(mag)*0.+0.1
    else:
      self.mage = mage
    
    bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
    width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
    	 [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]              
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    for i in range(len(self.mag)):
      x1 = width[i][0]-width[i][1]/2.
      x0 = width[i][1]
      y1 = self.mag[i]
      y0 = self.mage[i]
      if mag>90:
        ax.plot([width[i][0]],[y0],'v',markersize = 10.,color='red')
      ax.broken_barh([(x1, x0)]  , (y1-y0, y0*2.), facecolors='#afeeee',linestyle='dashed')
      #pdb.set_trace()
    '''
    redshift = [ii for ii in range(4)]
    lines = [121.6,372.7,500.7,656.4]
    linewidth = 10.
    for line in lines:
      pdb.set_trace()
      plot([line*(1+z) for z in redshift],[28.+z/3. for z in redshift],linestyle='dashed',color='0.4')
    plot([0,9999],[28,28],'-')  
    ax.set_xlim(200,1700)
    ax.set_yticks([29,28.67,28.3,28.,27.,26.,25.,24.,23.,22.,21.,20.])
    ax.set_yticklabels(['z=3','z=2','z=1','z=0, 28',27.,26.,25.,24.,23.,22.,21.])
    text(270,28.8,'Ly a')
    text(850,28.8,'[O II]')
    text(1350,28.8,'[O III]')
    text(1600,28.4,'Ha')
    '''
    ylimit = 26.3   # this is the upper limit for y axis
    lowlimit = 28.3 
    for mag in self.mag:
      if ylimit > mag and mag > 0. and mag < 30.:
       ylimit = mag-0.5
      if lowlimit < mag and mag > 0. and mag < 30.:
       lowlimit = mag+0.3
    ax.set_ylim(lowlimit,ylimit)
    ax.set_xticks([235.9,270.4,335.5,392.1,432.5,477.3,588.7,624.2,764.7,802.4,916.6,1055.2,1153.4,1248.6,1392.3,1536.9,268.3])
    ax.set_xticklabels(['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w'],fontsize=8)
    for label in ax.get_xticklabels():
      label.set_rotation(45)
    ax.set_xlabel('wavelength')
    ax.set_ylabel('magnitude')
    ax.grid(True)
    plt.ion()
    plt.show()
    savefig('./tmp.png')
    pdb.set_trace()


# Just make a test with the following:
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  txt  = 'plot a image with 16 band magnitudes: ' 
  usage=txt+mod+" mag1 mag2 mag3 ... mag16 "
  long_options='aa'
  try:
    opts,arg  = getopt.getopt(sys.argv[1:],'',long_options)
  except getopt.GetoptError:
    # print help information and exit:
    print 'ERROR:'
    sys.exit(usage) 
  
  mag = []
  for i in range(len(arg)):
    mag.append(float(arg[i])) 
  if len(arg) <16:
    print 'length of arg:'+str(len(arg))
    sys.exit(usage)
  else:
    if len(arg)==32:
      mag16 = [mag[i*2] for i in range(16)]
      mag16e = [mag[i*2+1] for i in range(16)]
      plot(mag16,mag16e)
    else:  
      plot(mag)  
  
  
  
  

