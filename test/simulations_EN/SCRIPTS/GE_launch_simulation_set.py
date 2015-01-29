#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Script to launch a simulation set
# CREATED: 20070518 davidabreu@users.sourceforge.net
# This script launch a simulation set with GE_galaxy_photometry_simulator.py
#
# Usage: GE_launch_simulation_set.py -p simulationParameterFile numberOfIter
#

"""Script to launch a simulation set"""

import sys
from optparse import OptionParser
import os
import signal
import time
import commands
import datetime

estatus=0
simulationsDir='/net/zipi/scratch/DOCTORADO/GROTHERR/simulations/SIMU/WORK/'

# Function to read simulation parameters
def readParams(file):
   """readParams(file) -> return dictionary with parameter file data and values
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
	 if len(trozos[1:])>1: # more than one value
	    parametros[trozos[0]]=trozos[1:] # return list
	 else:
	    parametros[trozos[0]]=trozos[1]

   return parametros

def main():

   # To catch the SIGTERM and delete the lockFile
   def signal_handler(signal, frame):
      """signal_handler(signal, frame) -> To catch the SIGTERM and delete the
					lockfile

         To catch, call it as:
         signal.signal(signal.SIGTERM, signal_handler)"""

      output.write("SIGTERM received (launch_simulation_set talking)\n")
      try:
         os.remove(lockFileName)
         output.write("lockfile deleted\n")
      except:
         output.write("Fail trying to delete the lockfile\n")
         pass
      
      sys.exit(1)

   signal.signal(signal.SIGTERM, signal_handler)

   def secureCompute(nombrePaso,doneFileName,lockFileName,comando,outFileName):
      """secureCompute(nombrePaso,doneFileName,lockFileName,comando,outFileName)
      
   			   nombrePaso = only for verbose
   			   doneFileName = "done" file name
   			   lockFileName = "lock" file name
   			   comando = command to send if everything is OK
   			   outFileName = output file name for comando"""
   
      doneFile=0; lockFile=0
   
      doneFile=os.access(doneFileName,os.F_OK)
      if not(doneFile): # Step not done
   	 if verbose: output.write("Not done "+nombrePaso+"\n")
   	 lockFile=os.access(lockFileName,os.F_OK)
   	 if not(lockFile): # Not doing
   	    os.system("touch "+lockFileName)
	    lockFile=os.access(lockFileName,os.F_OK)
	    if verbose: output.write("lockFile: "+str(lockFile)+"\n")
   	    if verbose: output.write(lockFileName+"\n")            
   	    if verbose: output.write("Not doing "+nombrePaso+"\n")
   	    (estatus, salida)=commands.getstatusoutput(comando)
   	    if verbose: output.write(salida)
   	    if estatus == 0: # Step finished OK
   	       if verbose: output.write("\nStatus 0\n")
   	       if(os.access(outFileName,os.F_OK)):
   		  os.system("touch "+doneFileName)
   		  os.remove(lockFileName)
   	       else: # Apparently finished but no outFile
   		  if verbose: output.write("No outFile "+outFileName+"\n")
   		  os.remove(lockFileName)
   		  return 1
   	    else: # Bad step
   	       if verbose: output.write("Fail from "+nombrePaso+"\n")
	       output.write("=== "+lockFileName+"\n")
   	       os.remove(lockFileName)
   	       return 1
   	    
   	 else: # Step is running
   	    if verbose: output.write(nombrePaso+" is running\n")
   	    return 1 # next step in for
   	    
      else: # Step done
   	 if verbose: output.write(nombrePaso+" done\n")
   
      return 0 # everything was OK

   # main starts here
   usage = "usage: %prog [options] Iter"
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                     help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-p", "--par", dest="param", default="default.par",
                 help="Parameter filename (from WORK dir) [default : %default]",
                     metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", default="1",
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   (options, args) = parser.parse_args()

   if len(args)<1:
      print "Error in args. Type --help for help\n"
      sys.exit(1)

   simulationNumber=int(args[0])
   simulationParameterFile=options.param
   verbose=options.verbose
      
   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")
      
   #parameterFile=simulationsDir+"ParamFiles/"+simulationParameterFile
   parameterFile=simulationParameterFile
   paramValues=readParams(parameterFile)

   #totaliters = int(paramValues['TOTITERS'])
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
   kernelImage = paramValues['KERNELIMAGE']
   entorno     = paramValues['ENTORNO']

   # Uncompress local files
   os.system('tar -xzf '+entorno)

   re1   = str(reff[0])
   re2   = str(reff[1])
   eb1   = str(elipt[0])
   eb2   = str(elipt[1])
   mag1  = str(mag[0])
   mag2  = str(mag[1])
   n1    = str(sersic[0])
   n2    = str(sersic[1])
   nsim1 = str(simulationNumber*step+1)
   nsim2 = str(simulationNumber*step+step)

   inputName=inputImage.split('/')[-1]

   Name = "galsim_"+inputName
   Name+= "_r_"+re1+"_"+re2+"_e_"+eb1+"_"+eb2+"_m_"
   Name+= mag1+"_"+mag2+"_n_"+n1+"_"+n2+"_i_"
   Name+= nsim1+"_"+nsim2

   #Names of files
   simulatedCatalogFile=simulationsDir+"Catalogs/"+Name+".cat"
   doneFileName=simulationsDir+"LockFiles/"+Name+".done"
   lockFileName=simulationsDir+"LockFiles/"+Name+".lock"
      
   #doneFile=os.access(doneFileName,os.F_OK)
   #if not(doneFile): # old style, now using secureCompute
   dir="/net/zipi/scratch/DOCTORADO/GROTHERR/simulations/SIMU/SCRIPTS/"
   comando =dir+"GE_galaxy_photometry_simulator.py -r "+re1+" "+re2+" -e "+eb1
   comando+=" "+eb2+" -m "+mag1+" "+mag2+" -s "+n1+" "+n2+" -i "+nsim1+" "
   comando+=nsim2+" -x "+" "+sexFile+" -g "+galSexFile+" "+inputImage+" "
   comando+=psfImage+" "+simulatedCatalogFile+" "+rmsImage+" "+rmsPsfImage
   comando+=" "+kernelImage

   if verbose: output.write('Comand: '+comando+'\n')

   estatus=secureCompute('catalog',doneFileName,lockFileName,comando,simulatedCatalogFile)
   if estatus==1:
      if verbose: output.write("Problems with catalog\n")
   else:
      if verbose: output.write("Everything OK with catalog\n")
      if verbose: output.write("Writing the done\n")
      os.system('touch '+doneFileName)

   if verbose: output.write("\nLF_launch_simulations_set.py ends here\n")
   if verbose: output.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
   output.close()
   sys.exit(0)
   
if __name__ == "__main__":
   main()
