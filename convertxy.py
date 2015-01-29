#!/usr/bin/env python
# Xingxing, Huang
# email: hxx@mail.ustc.edu.cn
# Jan 06, 2013


# Purpose:
#   get convert the ra dec to x y using a fits file.
#
# Need:
#   
#
# To do:
# 

import os,sys,string,glob,time
import pdb
import numpy as np
from pyraf import iraf
from pyraf.iraf import stsdas
#from drizzlepac import skytopix


'''
class run():
    """
    
    
    """

    def __init__(self,catalog='',colx=1,coly=2,x=1,y=1, err=-1, printinfo=0):

      self.indir = './'
      self.cat   = catalog
      self.colx  = colx-1
      self.coly  = coly-1
      self.x     = x
      self.y     = y
      self.err   = err if err>0 else 2.   # the search radus
      self.printinfo = printinfo
      
      # read
      fname = os.path.join(self.indir,self.cat)
      if not os.path.isfile(fname):
          sys.exit('ERROR: Check '+fname)
      r = open(fname,'r')
      lines=r.readlines()
      read_all = [line.split() for line in lines] 
      read = [i for i in read_all if not ('#' in i[0]) and (i!=[])]     # delete the elements begin with '#'
      readtmp = [i for i in read_all if ('#' in i[0]) or (i==[])]      #  the elements begin with '#'
      
      # search
      index=[]
      for i in range(len(read)):
        x1 = float(read[i][self.colx])
        y1 = float(read[i][self.coly])
        if (x1-self.x)**2+(y1-self.y)**2 < self.err**2 :
            index.append(i)
      
      # print result 
      if len(index)==0:
        sys.exit('not found!')   
      for i in index:
        text = ''
        for j in range(len(read[i])):
          text += '%s ' %(read[i][j])
        print text
'''
    
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  text = 'Tips:  '
  usage=mod+" catalog colx coly fitsfile [output]\n"+text
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
  output = None
  if len(args) >= 4:
    catalog = args[0]
    colx  = int(args[1])
    coly  = int(args[2])
    fitsfile = args[3]
    if len(args)>4:
        output = args[4]
  else:
    sys.exit(usage)
  
  # read
  f = open(catalog,'r')
  lines=f.readlines()
  f.close()
  if output==None: 
         output = 'input.reg'
  o = open(output,'w')

  # write
  for line in lines:
      if '#' in line[0]:
          o.write(line)
      elif line.split()==[]:
          continue    
      else:
          data = line.split()
          ra = float(data[colx-1])
          dec = float(data[coly-1])
          iraf.stsdas.toolbox.imgtools.rd2xy(fitsfile,ra,dec,hour=False)
          x = iraf.stsdas.toolbox.imgtools.rd2xy.x
          y = iraf.stsdas.toolbox.imgtools.rd2xy.y
          #x,y = skytopix.rd2xy(fitsfile,ra,dec)
          data[colx-1] = str(x)
          data[coly-1] = str(y)
          for key in data:
              o.write(key+' \t')
          o.write(' \n')
          print '%f  %f  >  %f  %f' %(ra,dec, x,y)    
  print 
  print 'DONE'

  o.close()      
  #run(catalog=catalog,colx=colx,coly=coly, x=x,y=y, err=err,  printinfo=printinfo)
  
  
  
  
  
  
  
  
  

