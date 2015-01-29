#!/usr/bin/env python
# revised for anton's catalog
import os,sys,string,glob,time
import pdb
from pyraf import iraf
import numpy as np
import numpy as np
from matplotlib import cm
from matplotlib import pyplot as plt
import pyfits



class run():
  """
    
  """
  def __init__(self,fname='', x=0, y=0, size=0,outprefix=''):
    txt  = '['+str(x-size)+':'+str(x+size)+', '+str(y-size)+':'+str(y+size)+']'
    output = fname.replace('.fits','_'+outprefix+'.fits')
    iraf.imcopy(fname+txt,output)

    
    
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  usage='Usage: '+mod+" .fits x y radius [outprefix]"
  option=''
  try:
    opts, arg = getopt.getopt(sys.argv[1:],'',option)
  except getopt.GetoptError:
    # print help information and exit:
    sys.exit(usage)
  if len(arg)<4:
    sys.exit(usage)
  if len(arg) ==5:
    outprefix = arg[4]
    
  infile = []
  for i in range(len(arg)):
    if '.fits' in arg[i]:
       infile.append(arg[i])
    else:
       x      = int(float(arg[i]))
       y    = int(float(arg[i+1]))
       size   = int(float(arg[i+2]) )
       break
  #infile = glob.glob(fname)

  for fname in infile:
     print 'Cutting '+fname
     run(fname=fname, x=x, y=y, size=size,outprefix=outprefix)
  
  
  
  
  
  
  
  
  

