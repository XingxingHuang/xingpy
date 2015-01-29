#!/usr/bin/env python
# Xingxing, Huang
# email: hxx@mail.ustc.edu.cn
# Jan 06, 2013

# To do:
# printinfo: if set, print enough informations.

import os,sys,string,glob,time
import pdb
import numpy as np

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
        #if (x1-self.x)**2+(y1-self.y)**2 < self.err**2 :
        if abs(x1-self.x) < self.err and abs(y1-self.y)< self.err :
            index.append(i)
      
      # print result 
      if len(index)==0:
        sys.exit('not found!')   
      for i in index:
        #text = ''
        #for j in range(len(read[i])):
         # text += '%s ' %(read[i][j])
        text = '%s ' %(read[i][self.colx])
        print text

    
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  text = 'Tips: add | awk \'{printf "%f\n",$1}\' '
  usage=mod+" [-i] catalog colx coly x y [err] \n"+text
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
  if len(args) >= 5:
    catalog = args[0]
    colx  = int(args[1])
    coly  = int(args[2])
    x	 = float(args[3])
    y    = float(args[4])
    err  = -1
    if len(args) == 6 : err=float(args[5])
  else:
    sys.exit(usage)
  run(catalog=catalog,colx=colx,coly=coly, x=x,y=y, err=err,  printinfo=printinfo)
  
  
  
  
  
  
  
  
  

