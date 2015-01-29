#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Pytho script to make simulations
# CREATED: 20060913 davidabreu@users.sourceforge.net
# Small script to make simulations that calls N times a command and manage the
# SIGTEM (very useful for condor)
#
# MODIFIED: 20061004 davidabreu@users.sourceforge.net
# TIMEOUT added to catch a too long process and kill it properly
#
# MODIFIED: 20070521 davidabreu@users.sourceforge.net
# Adaptación para las simulaciones de errores en Groth
#
"""Script to make simulations"""

import sys
from optparse import OptionParser
import os
try:
   import pexpect
except ImportError:
   print 'pexpect import error'
   sys.exit(2)
import signal
import datetime

import time
import random

def main():

   def signal_handler(signal, frame):
      """signal_handler(signal, frame) -> To catch the SIGTERM and kill the
					process.

         To catch be performed, call as:
         signal.signal(signal.SIGTERM, signal_handler)"""
      output.write("SIGTERM received (launch_simulations talking)\n")
      p.kill(15)
      sys.exit(1)

   signal.signal(signal.SIGTERM, signal_handler)

   # Aquí empieza main
   usage = "usage: %prog [options] nIter"
   parser = OptionParser(usage)
   parser.add_option("-o", "--out", dest="outfilename", default="stdout",
                     help="Output to FILE [default : %default]", metavar="FILE")
   parser.add_option("-v", "--verbose", dest="verbose", default=1,
                     help="Set verbose level to INT [default : %default]",
                     metavar="INT")
   parser.add_option("-p", "--par", dest="param", default="default.par",
                 help="Parameter filename (from WORK dir) [default : %default]",
                 metavar="FILE")
   
   (options, args) = parser.parse_args()
   
   if len(args)<1:
      print "Error in args. Type --help for help\n"
      sys.exit(1)

   nIter=int(args[0])
   parFile=options.param
   verbose=options.verbose

   if options.outfilename=="stdout":
      output=sys.stdout
   else:
      output=open(options.outfilename, "w")
   
   # To avoid problems with too many machines
   time.sleep(random.random()*30)

   for iter in range(nIter):
      if verbose: output.write('Inside loop. '+str(datetime.datetime.today())+'\n')
      dir='/net/zipi/scratch/DOCTORADO/GROTHERR/simulations/SIMU/SCRIPTS/'      
      comando=dir+"GE_launch_simulation_set.py -p "+parFile+" "+str(iter)
      if verbose: output.write("Before pexpect.spawn of "+comando+"\n")
      p=pexpect.spawn(comando, timeout=3600)
      
      queHaPasado=p.expect([pexpect.EOF,pexpect.TIMEOUT])
      
      if queHaPasado==0:
         estatus=os.getenv("status")
         if verbose: output.write(p.before)
         if verbose: output.write("After p.expect\n")
      if queHaPasado==1:
         if verbose: output.write("TIMEOUT\n")
	 if verbose: output.write(p.before)
         p.kill(15)

   output.write("\nOK\n")    
   output.close()
   sys.exit()

if __name__ == "__main__":
   main()
