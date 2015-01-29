#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Script to collect simulation results
# CREATED: 20070524 davidabreu@users.sourceforge.net
# This script collects results from simulations and put them all in a file 
#

"""Script to collect simulation results"""

import sys
from optparse import OptionParser
import os
try:
   import sexcat
except:
   import catg as sexcat

parentDir='/net/zipi/scratch/DOCTORADO/GROTHERR/simulations/SIMU/WORK/'

# Function to read simulation parameters
def readParams(file):
   """readParams(file) -> returns dictionary with parameter file data and values
			as string or list"""
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
	 if len(trozos[1:])>1: # More than one value
	    parametros[trozos[0]]=trozos[1:] # Return a list
	 else:
	    parametros[trozos[0]]=trozos[1]

   return parametros

# Function to obtain simulation name
def getName(file):
   """def getName(file) -> return simulation name"""

   paramValues=readParams(file)

   step        = int(paramValues['STEPSIZE'])   
   reff        = [float(i) for i in paramValues['REFF']]
   elipt       = [float(i) for i in paramValues['ELIPT']]
   mag         = [float(i) for i in paramValues['MAG']]
   sersic      = [float(i) for i in paramValues['SERSIC']]
   inputImage  = paramValues['INPUTIMAGE']

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

   return simulationName

def main():
   usage = "usage: %prog [options] parFileName"
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                     help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", default=1,
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   parser.add_option("-n", "--noheader", dest="noheader", default=False,
                     help="If TRUE do not prints header [default : %default]",
                     metavar="BOOL")
#   parser.add_option("-p", "--par", dest="param", default=None,
#                     help="Parameter filename [default : %default]",
#                     metavar="FILE")
   
   (options, args) = parser.parse_args()

   verbose=options.verbose

   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")

   if len(args)<1 or len(args)>2:
      output.write('No param file received. Call with "--help"\n')
      sys.exit()
   else:
      parameterFileName=args[0]

   catDir=parentDir+'Catalogs/'
  
   name=getName(parameterFileName)

   todos=os.listdir(parentDir+'LockFiles')
   dones=[]
   for i in todos:
      if (name in i and '.done' in i): dones.append(i)

   catFileNames=[catDir+i[:-5]+'.cat' for i in dones]

   head=sexcat.readcat(catFileNames[0],l=1)
   largo=len(head[1])   
   if not(options.noheader): # if noheader == TRUE do not prit header
      for i in head[1]:
         output.write(i)   
   for i in catFileNames:
      file=open(i)
      lineas=file.readlines()
      for linea in lineas:
         if linea[0]!='#':
            if len(linea.split())==largo: output.write(linea)
            else:
               sys.stderr.write('Problems with line: '+linea)
               sys.stderr.write('From: '+i+'\n')
   
   sys.exit()

if __name__ == "__main__":
   main()
