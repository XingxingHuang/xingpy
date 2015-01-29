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
  def __init__(self,catalog='',indir='./', column = 2, num=0.):
    #mag_num    = 46     # choose mag_iso
    #magerr_num = 63     # choose magerr_iso
    #ra_num  = 79
    #dec_num = 80
    self.indir = indir
    self.cat   = catalog
    self.num   = num
    self.col   = column - 1

    if 1:
      fname = os.path.join(self.indir,self.cat)
      r = open(fname,'r')
      r=open(fname,'r')
      lines=r.readlines()
      read_all = [line.split() for line in lines] 
      read = [i for i in read_all if not ('#' in i[0]) ]     # delete the elements begin with '#'
      
      results=[]
      for i in range(len(read)):
        if abs(float(read[i][self.col]) - num) < 0.1/60./60. :
         results.append(i)
         
      if len(results) > 1.:
        print 'More than 1 detected!!'
      if len(results) < 1.:
        print 'None detected!!'
      lineline = [tmp for tmp in lines if not('#' in tmp)]
      for i in range(len(results)):
        print '%s' %(lineline[results[i]])
      
      #for i in range(len(read[self.num])):
      #   print '%2d : %10s' %(i, read[self.num][i])
    
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
  usage=mod+"   catalog [dir] column num"
  option=''
  try:
    opts, arg = getopt.getopt(sys.argv[1:],'',option)
  except getopt.GetoptError:
    # print help information and exit:
    sys.exit(usage)
  if len(arg) <2:
     print usage
     sys.exit()
  if len(arg) == 4:
   catalog = arg[0]
   filedir = arg[1]
   column  = int(arg[2])
   num	   = float(arg[3])
  elif len(arg) == 3 :
   catalog = arg[0]
   filedir = './'
   column  = int(arg[1])
   num	   = float(arg[2])
  run(catalog=catalog,indir = filedir, column = column, num = num)
  
  
  
  
  
  
  
  
  

