#!/usr/bin/env python
import os
import sys
    
if __name__ == '__main__':
 
  mod  = os.path.basename(sys.argv[0])
  usage='Usage: '+mod+" <a209>"
  try:
    cluster = sys.argv[1]
  except:
    sys.exit(usage)

  indir = '/Users/xing/data/clash_cat/%s/cat_RED/**/' %(cluster)
  infile ='*.*'
  outdir ='./'
  copyfile = os.path.join(indir, infile)
  cmd = 'cp %s  %s' %(copyfile, outdir)
  print cmd
  os.system(cmd)
  
  
  
  
  
  
  
  
  

