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
        #print abs(x1-self.x), abs(y1-self.y), self.err
        if  x1 ==101.911119:
           pdb.set_trace()
      # print result 
      if len(index)==0:
        sys.exit('not found!')   
      for i in index:
        text = ''
        for j in range(len(read[i])):
          text += '%s ' %(read[i][j])
        print text

    
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  text = 'Tips: add | awk \'{printf "%f\\n",$1}\' '
  text+= '\n      | awk \'{printf "%f %f %f %f %f %f\\n",$110,$111  ,$74,$75  ,$56,$57}\' '
  text+= '\n\n FRONTIER:\n      | awk \'{printf "%f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f\\n",$110,$111, $104,$105, $98,$99, $86,$87, $74,$75  ,$56,$57  ,$38,$39}\' '
  text+= '\nF160W 110   F140W 104   F125w 98    f110w 92    f105w 86    f814w 74    f775w 68    f625w 62    f606w 56    f475w 44    f336w 26  '
  text+= '\n\n CLASH_My:\n      | awk \'{printf "%f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f\\n",$110,$111, $104,$105, $98,$99,$92,$93, $86,$87, $80,$81, $74,$75, $68,$69, $62,$63 ,$56,$57,$44,$45,$38,$39 ,$32,$33 ,$26,$27 ,$20,$21 ,$14,$15}\' '
  text+= '\n\n CLASH_My:\n      | awk \'{printf "%f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f\\n",$14,$15,  $20,$21,   $26,$27,   $32,$33,   $38,$39,   $44,$45,  $56,$57,   $62,$63,    $68,$69,   $74,$75,   $80,$81,   $86,$87,  $92,$93,   $98,$99,   $104,$105,  $110,$111 }\' '
  text+= '\nF160W 110   F140W 104   F125w 98    f110w 92    f105w 86  f850lp 80  f814w 74    f775w 68    f625w 62    f606w 56    f475w 44   f435w 38   f390w 32   f336w 26  f275w 20  f225w 14 '
  text+= '\n\n CLASH_WEI:\n      | awk \'{printf "%f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f\\n",$11,$12, $56,$57, $81,$82, $16,$17, $61,$62, $26,$27, $46,$47, $41,$42 ,$66,$67, $31,$32, $36,$37 ,$21,$22 ,$51,$52 ,$71,$72 ,$76,$77, $86,$87}\' '
  text+= '\n\n CLASH_WEI:\n      | awk \'{printf "%f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f  %f %f\\n", $86,$87,  $76,$77,  $71,$72,   $51,$52,   $21,$22,    $36,$37,    $31,$32,  $66,$67,   $41,$42,    $46,$47,   $26,$27,   $61,$62,   $16,$17,   $81,$82,   $56,$57,  $11,$12 }\' '
  text+= '\nF160W 11   F140W 56  F125w 81    f110w 16    f105w 61  f850lp 26  f814w 46    f775w 41    f625w 66    f606w 31    f475w 36   f435w 21   f390w 51   f336w 71  f275w 76  f225w 86 '
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
  
  
  
  
  
  
  
  
  

