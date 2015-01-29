#!/usr/bin/env python
# plot the column 1 and 2 in the catalog
import os,sys,string,glob,time
import pdb
import numpy as np
import shutil
import popen2
from pylab import *


def run(catalog=None,colum=1):
   indir='./'   
      
   fname = os.path.join(indir,catalog)
   r=open(fname,'r')
   tmp=r.readlines()
   lines = [line.split() for line in tmp] 
   lines2 = [line for line in tmp if not('#' in line)]   # each line in the catalog is one dimension    
   cat = [line for line in lines if not ('#' in line[0]) ]     # delete the elements begin with '#'
   data=[]
   for i in range(len(cat)):
      #data.append( [float(num) for num in cat[i] ] )  
      data.append( float(cat[i][colum-1]) )  
   return(data)   


if __name__ == '__main__':
  import getopt

  mod  = os.path.basename(sys.argv[0])
  txt = 'read catlog to a list \n'
  usage = txt+mod+" --xlimit=m,n  --ylimit=m,n   catalog"
  long_options=['xlimit=',\
                'ylimit=']
  try:
    #pdb.set_trace()
    opts,arg  = getopt.getopt(sys.argv[1:],' ',long_options)
  except getopt.GetoptError:
    # print help information and exit:
    sys.exit(usage) 
    
  if len(arg) <1:
     print usage
     sys.exit()
     
  column = 'false' 
  cl=[]
  xlimit1 = -99
  xlimit2 = -99
  ylimit1 = -99
  ylimit2 = -99
  if opts:
    for o, a in opts:
        #pdb.set_trace()
        if a:
            cl.append(o+"="+a)
        else:
            cl.append(o)
            
        if o in ("--xlimit"):
            if ',' not in a:
                sys.exit(usage)
            xlimit1,xlimit2 = (int(a.split(',')[0]),int(a.split(',')[1]))
            
        if o in ("--ylimit"):
            if ',' not in a:
                sys.exit(usage)
            ylimit1,ylimit2 = (int(a.split(',')[0]),int(a.split(',')[1]))
            
  x = run(catalog=arg[0],colum=1)
  y = run(catalog=arg[0],colum=2)
  
  print 'plot cat'
  copy = y[:]
  n = len(y)
  copy.sort()
  if n & 1: # There is an odd number of elements
    median = copy[n / 2]
  else:
    median = (copy[n / 2 - 1] + copy[n / 2]) / 2  
  #if median != 0:
  #   y = [i/median for i in y] 
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot(x,y,'.')
  if ylimit1 != -99 :
    ax.set_ylim(ylimit1,ylimit2)
  if xlimit1 != -99:
    ax.set_xlim(xlimit1,xlimit2)
    
  ion()
  plt.show()
  pdb.set_trace()




