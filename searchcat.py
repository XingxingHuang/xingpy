#!/usr/bin/env python
import os,sys,string,glob,time
import pdb
from pyraf import iraf
import numpy as np
from pylab import *
import shutil
import popen2
'''
  show FileName LineNumber
'''

class run():
  """
    
  """
  def __init__(self,catalog='',filedir='./',x=0,y=0,column='false'):
    #mag_num    = 46     # choose mag_iso
    #magerr_num = 63     # choose magerr_iso
    #ra_num  = 79
    #dec_num = 80
    self.indir = filedir
    self.cat   = catalog
    self.x   = x
    self.y   = y
    self.band  = ['f225w', 'f275w', 'f336w', 'f390w', 'f435w', 'f475w','f606w', 'f625w', 'f775w', 'f814w', 'f850lp','f105w', 'f110w', 'f125w','f140w', 'f160w']

    if 1:
      fname = os.path.join(self.indir,self.cat)
      r=open(fname,'r')
      lines=r.readlines()
      read_all = [line.split() for line in lines] 
      read = [i for i in read_all if not ('#' in i[0]) ]     # delete the elements begin with '#'
      
      lineline = [tmp for tmp in lines if not('#' in tmp)]
      if column=='true':
        print '%s' %(lineline[int(x)-1])
      if column=='false':
        for i in range(len(lineline)):
          #if abs(x-float(lineline[i].split()[1]) ) <3. and abs(y-float(lineline[i].split()[2])) <3.:           ################### for x y
          distance = 1.3
          if abs(x-float(lineline[i].split()[1]) ) <distance/3600. and abs(y-float(lineline[i].split()[2])) <distance/3600.:           ###################  for ra dec
            print '%s' %(lineline[i])
      #for i in range(len(read[self.x])):
      #   print '%2d : %10s' %(i, read[self.x][i])
    
  def printlog(self,text):
    '''
    write the text you define to the run.log file
    '''
    fname='/media/BACK/results/find.log'
    if os.path.exists(fname):
      f = open(fname,'a')
    else:
      f = open(fname,'w')   
      txt='####This file is used for recording the magnitudes ####\n'
      print >> f, txt
      del txt
      print 'find.log created!'
    ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
    format = '%s %s'  
    print >> f, format % (ptime,text)
    print text
    f.close()     
    
    
    
    
    
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  usage=mod+" [--column] FileName [dir] x y       (only for column 1 2)"
  long_options='column'
  try:
    #pdb.set_trace()
    opts,arg  = getopt.getopt(sys.argv[1:],'',long_options)
  except getopt.GetoptError:
    # print help information and exit:
    sys.exit(usage) 
    
  if len(arg) <2:
     print usage
     sys.exit()
  x=0.
  y=0.   
  if len(arg) == 4:
     filename = arg[0]
     filedir  = arg[1]
     x      = float(arg[2])
     y      = float(arg[3])
  elif len(arg) == 3 :
     filename = arg[0]
     x      = float(arg[1])
     y      = float(arg[2])
    
  column = 'false' 
  cl=[]
  if opts:
    for o, a in opts:
        #pdb.set_trace()
        if a:
            cl.append(o+"="+a)
        else:
            cl.append(o)
            
        if o in ("--column"):
            column = 'true'


   
  run(catalog=filename,x=x,y=y,column=column)
  
  
  
  
  
  
  
  
  

