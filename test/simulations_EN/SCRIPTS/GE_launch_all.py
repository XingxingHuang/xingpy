#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Pytho script to launch all the simulations
# CREATED: 20070622 davidabreu@users.sourceforge.net
# Small script to launch all the simulations
#
"""Small script to launch all the simulations"""

import sys
from optparse import OptionParser # to parse options
import os
import datetime
import commands

def main():

   usage = "usage: %prog [options] launchOption1 launchOption2 ...\n\n"
   usage+= "launchOption is the number of the field (01, 02, ..., 11)"
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                     help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", default=1,
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   parser.add_option("-f", "--filter", dest="filter", default="all",
                     type="choice", choices=["ks","j","all"],
                     help="Filter [default : %default]",
                     metavar="OPT")
   parser.add_option("-t", "--tipo", dest="tipo", default="all",
                     type="choice", choices=["main","refuerzo","all"],
                     help="Tipo [default : %default]",
                     metavar="OPT")
   
   (options, args) = parser.parse_args()
   
   if len(args)<1:
      print "Error in args. Type --help for help\n"
      sys.exit(1)

   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")

   verbose=options.verbose
 
   if options.filter=="all":
      filters=["ks","j"]
   else:
      filters=[options.filter] 

   if options.tipo=="all":
      tipos=["main","refuerzo"]
   else:
      tipos=[options.tipo]

   campos=["01","02","03","04","05","06","07","08","09","10","11"]
   DF={"ks":"K","j":"J"}
   DT={"main":"","refuerzo":"R"}
   T={"main":".submit","refuerzo":"_mag_19_21.submit"}

   dir='/net/zipi/scratch/DOCTORADO/GROTHERR/simulations/SIMU/WORK/Initial/'      
   for filter in filters:
      for tipo in tipos:
         for campo in args:
            if not(campo in campos):
               output.write("Field "+campo+"is not valid\n")
               sys.exit()
            initDir=dir+DF[filter]+campo+DT[tipo]
            try:
               os.chdir(initDir) # changed to initial dir
            except:
               output.write("Problems with dir "+initDir+"\n")
               sys.exit()
            submitFile='../../CondorFiles/GE_groth_wi'+campo+'-'+filter+T[tipo]
            cmnd='condor_submit '+submitFile
            output.write("Send: "+cmnd+"\n")
            outCon=commands.getoutput(cmnd)
            if verbose: output.write(outCon+'\n')
            jobNumber=outCon.split()[-1]
            os.system('touch '+jobNumber+'job')

   output.write("\nAhí va el mogollón\n")    
   output.close()
   sys.exit()

if __name__ == "__main__":
   main()
