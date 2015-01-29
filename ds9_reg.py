#!/usr/bin/env python
#
#  create region files

import pdb,os,sys
import numpy as np
#from program import printlog
from os.path import *
from readcol import fgetcols


def usage():  
  #print '%s [-h|-h|-h] [--help|--help=] args' %(mod)
  txt = '\n\tUsage: '+ mod + ' [options] file col1 col2\n\n'\
        '\t--r=0.15\t for background\n'\
        '\t--c=green\t for color\n'
  print txt     
  sys.exit()


if __name__ == '__main__':
  ############################################################
  # parameters
  ############################################################
  import getopt
  option1 = "h"
  option2 = ["help","option",'r=','c=']
  mod  = os.path.basename(sys.argv[0])
  try:
    opts, args = getopt.getopt(sys.argv[1:],option1,option2)
    #params = params_cl()
  except getopt.GetoptError:      
    usage()
  if args==[]: usage()   
  
  # initial parameters
  r = 1.5
  color = 'green'
  # 
  for o, a in opts:  
    if o in ("-h", "--help"):  
        usage() 
    if o in '--r':
        r=float(a) 
    if o in '--c':
        color = a    
  #
  incat = args[0]
  index1 = int(args[1])
  index2 = int(args[2])
  outcat = incat.replace(splitext(incat)[-1],'.reg') 
  ras,decs = fgetcols(incat,index1,index2)       
  
  
  f=open(outcat,'w')
  txt="global color=%s dashlist=8 3 width=1 font='helvetica 10 normal roman' select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n fk5"  %(color)
  print >>f,txt
  for i,ra in enumerate(ras):
    ra = ras[i]
    dec = decs[i]
    ID = int(i)+1
    txt = "circle(%f,%f,%f\")# font=\"helvetica 10 bold roman\" text={%i}" %(ra,dec,r,ID)
    print >>f,txt
  f.close()
  print 'Done ',outcat 