#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Script to delete files from a certain simulation
# CREATED: 20130713 davidabreu@users.sourceforge.net
# This script deletes all the files result from a simulation. It is needed
# because amount of files is too large and error is obtained from "rm".
#
# Usage: GE_clean.py -p paramFileName all
#

"""Script to delete files from a certain simulation"""

import sys
from optparse import OptionParser
import os

# head path. Edit manually.
parentDir='/home/user/'

# Function to read simulation parameters
def readParams(file):
   """readParams(file) -> returns a dictionary with parameter file data and
			values as string or list"""
   parametros={}
   f=open(file,'r')
   lineas=f.readlines()
   f.close()
   for linea in lineas:
      if linea[0]=='#':
         continue
      else:
         trozos=linea.split('#')[0]
	 trozos=trozos.split()
	 if len(trozos[1:])>1: # parameter with more than one value
	    parametros[trozos[0]]=trozos[1:] # return as list
	 else:
	    parametros[trozos[0]]=trozos[1]

   return parametros

def main():
   usage = "usage: %prog [options] string \n\n"
   usage+="Using 'all' as argument, all the files from the simulation defined\n"
   usage+="by parameter file are deleted."
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                     help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", default=1,
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   parser.add_option("-p", "--par", dest="param", default=None,
                     help="Parameter filename [default : %default]",
                     metavar="FILE")
   parser.add_option("-e", "--exclude", dest="exclude", default=None,
                     help="Excluded directory [default : %default]",
                     metavar="DIR")
   
   (options, args) = parser.parse_args()

   verbose=options.verbose
   parameterFileName=options.param
   excludedDir=options.exclude

   if len(args)<1:
      print "Type --help for help\n"
      sys.exit()
   else:
      string=args[0]
   
   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")

   directorios=['LockFiles','Catalogs']
   
   if excludedDir != None:
      try:
         directories.remove(excludedDir)
      except:
         pass
   
   if parameterFileName == None:
      if string == 'all':
         # Delete ALL files
         for directorio in directorios:
            files=os.listdir(parentDir+'/'+directorio+'/')
            for file in files:
               os.remove(parentDir+'/'+directorio+'/'+file)

            if(verbose): output.write("Deleted all files from "+directorio+"\n")
         
      else:
         # Delete files that contain string
	 for directorio in directorios:
	    files=os.listdir(parentDir+'/'+directorio+'/')
	    for file in files:
	       if string in file: os.remove(parentDir+'/'+directorio+'/'+file)

            if(verbose): output.write("Deleted files from "+directorio+"\n")

   else:
      # must read then parameter file
      paramValues=readParams(parameterFileName)

      step        = int(paramValues['STEPSIZE'])   
      reff        = [float(i) for i in paramValues['REFF']]
      elipt       = [float(i) for i in paramValues['ELIPT']]
      mag         = [float(i) for i in paramValues['MAG']]
      sersic      = [float(i) for i in paramValues['SERSIC']]
      inputImage  = paramValues['INPUTIMAGE']
      psfImage    = paramValues['PSFIMAGE']
      sexFile     = paramValues['SEXFILE']
      galSexFile  = paramValues['GALSEXFILE']
      rmsImage    = paramValues['RMSIMAGE']
      rmsPsfImage = paramValues['RMSPSFIMAGE']

      re1   = str(reff[0])
      re2   = str(reff[1])
      eb1   = str(elipt[0])
      eb2   = str(elipt[1])
      mag1  = str(mag[0])
      mag2  = str(mag[1])
      n1    = str(sersic[0])
      n2    = str(sersic[1])

      inputName=inputImage.split('/')[-1]

      simulationName = "galsim_"+inputName
      simulationName+= "_r_"+re1+"_"+re2+"_e_"+eb1+"_"+eb2+"_m_"
      simulationName+= mag1+"_"+mag2+"_n_"+n1+"_"+n2

      if string == '*':
         # ALL files from this simulation are deleted
         for directorio in directorios:
            files=os.listdir(parentDir+'/'+directorio+'/')
            for file in files:
               if simulationName in file: os.remove(parentDir+'/'+directorio+'/'+file)

            if(verbose): output.write("Deleted all files from "+directorio+"\n")
               
      else:
         # Delete all files from this simulation that contain string
	 for directorio in directorios:
	    files=os.listdir(parentDir+'/'+directorio+'/')
	    for file in files:
	       if simulationName in file and string in file:
	          os.remove(parentDir+'/'+directorio+'/'+file)

            if(verbose): output.write("Deleted files from "+directorio+"\n")

      
   if(verbose): output.write("Clean finished from '"+string+"'\n")
   sys.exit()

if __name__ == "__main__":
   main()
