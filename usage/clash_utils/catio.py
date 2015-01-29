
###
# some program related to clash catalogs
from os.path import *
import numpy as np
from os.path import *
from matplotlib import pyplot as plt
from pylab import ion
from glob import glob
import pdb
import string,sys
from program import printlog

###################################################################################################
def savecat(data,index,fname,nodata=0):   
    '''
    saving the GSD data.
    if nodata is set, 
    '''
    keys = ['cluster', 'ID', 'x','y','RA','DEC',\
         'f225w','f225we','f275w','f275we','f336w','f336we','f390w','f390we',\
         'f435w','f435we','f475w','f475we','f606w','f606we','f625w','f625we','f775w','f775we','f814w','f814we','f850lp','f850lpe',\
         'f105w','f105we','f110w','f110we','f125w','f125we','f140w','f140we','f160w','f160we']    
    keys_format = '%6s %5i  %5i %5i  %10.7f %10.7f '+'   %11.5f %11.5f'*16
    keys_format = keys_format.split()
    formats={}
    for key,form in zip(keys,keys_format):
      formats[key]=form
    #print 'Saving %s' %(fname)
    #pdb.set_trace()
    if nodata!=0:
        txt ='# '
    else:
       txt = ''
    for key in keys:
        if index>=0:
          txt += formats[key] %(data[key][index]) 
        else:
          txt += formats[key] %(data[key])  
        txt +='   '
    printlog(txt,fname)
