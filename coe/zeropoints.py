import HSTzp
import os
from os.path import join, exists
from filttools import *  # extractfilt

def zeropoints(files, outdir, forcesec=False, forcetot=False):
    
    zpdict = {}
    zpoutfile = join(outdir, 'zp.dict')
    fout = open(zpoutfile, 'w')

    for file in files:
        #zp = HSTzp.HSTzp(file)
        zp = HSTzp.HSTzp(file, forcesec=forcesec, forcetot=forcetot)
        file = os.path.basename(file)
        filt = extractfilt(file)
        print filt.ljust(6), zp
        fout.write(filt.ljust(8))
        fout.write(' %8.5f\n' % zp)
        zpdict[filt] = zp

    fout.close()
    return zpdict
