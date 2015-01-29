#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Script to replace file inside all the .tar.gz
# CREATED: 20070524 davidabreu@users.sourceforge.net
# This script was made to replace goya.param that was inside all the .tar.gz
#

"""Script to replace file inside all the .tar.gz"""

import sys
from optparse import OptionParser
import os

def main():
   usage = "usage: %prog [options] fileOut fileIn\n\n"
   usage+= "fileIn must be in the same directory as tar.gz files\n\n"
   usage+= "If you put '-' as fileOut -> fileIn is appended\n"
   usage+= "If you put '-' as fileIn -> fileOut is deleted\n"
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                     help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", default=1,
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   
   (options, args) = parser.parse_args()

   verbose=options.verbose

   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")

   if len(args)<2 or len(args)>3:
      output.write('Problems in call. Use "--help" for help\n')
      sys.exit()
   else:
      fileOut=args[0]
      fileIn=args[1]

   if verbose: output.write("Replacing "+fileOut+" by "+fileIn+"\n")

   # TODO: use also .tar.bz2 or .tar

   allFiles=os.listdir('.')
   targzFiles=[]
   for i in allFiles:
      if 'tar.gz' in i: targzFiles.append(i)
   for i in targzFiles:
      if verbose: output.write("Go with "+str(i)+"\n")  
      os.system('gunzip '+i)
      if not(fileIn=='-'): os.system('tar --delete -f '+i[:-3]+' '+fileOut)
      if not(fileOut=='-'): os.system('tar -rf '+i[:-3]+' '+fileIn)
      os.system('gzip '+i[:-3])

   if verbose: output.write("End\n")
   sys.exit()

if __name__ == "__main__":
   main()
