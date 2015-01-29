###
# some program related to clash data
from os.path import *
import numpy as np
from os.path import *
from matplotlib import pyplot as plt
from pylab import ion
from glob import glob
import pdb
import string,sys

from clash_utils.readio import getimage
from pro_img import savefits
import pyfits

clusters =   ['a209', 'a383', 'a611', 'a1423', 'a2261', \
         'm0329', 'm0416', 'm0429', 'm0647', 'm0717', \
         'm0744', 'm1115', 'm1149', 'm1206', 'm1423', \
         'm1720', 'm1931', 'm2129', 'm2137', 'r1347', \
         'r1532', 'r2129', 'r2248', 'c1226', 'm1311'] 

bands = ['f225w','f275w','f336w','f390w',\
         'f435w','f475w','f555w','f606w','f625w','f775w','f814w','f850lp',\
         'f105w','f110w','f125w','f140w','f160w']
         
bands = ['f126n']         

'''
# for tot 
for field in clusters:         
   print '\n\n\t\t',field,'\n' 
   whtfiles = getimage(field,special ='*acs-wfc3ir*tot*wht.fits')
   whtfiles2 = getimage(field,special ='*_wfc3ir*tot*wht.fits')
   for band in whtfiles.keys():
      if band in bands:
        print 'Not found',band
        continue
      wht = whtfiles[band]
      rms = wht.replace('wht','rms')
      data_wht = pyfits.getdata(wht)
      data_wht = np.clip(data_wht, 1e-44, 1e99)
      data_rms = np.sqrt(1./data_wht)
      savefits(data_rms,wht,rms)
      print band,rms
   for band in whtfiles2.keys():
      if band in bands:
        print 'Not found',band
        continue
      wht = whtfiles2[band]
      rms = wht.replace('wht','rms')
      data_wht = pyfits.getdata(wht)
      data_wht = np.clip(data_wht, 1e-44, 1e99)
      data_rms = np.sqrt(1./data_wht)
      savefits(data_rms,wht,rms)
      print band,rms
pdb.set_trace()
sys.exit()
'''


# for different bands
for field in clusters:         
   print '\n\n\t\t',field,'\n' 
   whtfiles = getimage(field,wht=1)
   for band in bands:
      if band not in whtfiles.keys():
        print 'Not found',band
        continue
      wht = whtfiles[band]
      rms = wht.replace('wht','rms')
      if rms==wht:
        print '\n\nWARNING: will overwrite!!!\n'
        pdb.set_trace()
      data_wht = pyfits.getdata(wht)
      data_wht = np.clip(data_wht, 1e-44, 1e99)
      data_rms = np.sqrt(1./data_wht)
      savefits(data_rms,wht,rms)
      print band,rms
      
pdb.set_trace()
   
   
   