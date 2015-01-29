# from cipcat.py

from coetools import *
import pyfits
from glob import glob

def fileintheway(file, over):
    if exists(file):
        if over:
            print "Deleting previous copy of ", outfile
            os.remove(file)
        else:
            print file, 'EXISTS'
            return True
    return False

def makermsimages(over=0):
    print "Converting wht files into rms files",
    print "(rms = 1 / sqrt(wht))"
    for whtfile in whtfiles:
        #rmsfile = os.path.basename(whtfile[:-9]) + '_rms.fits'
        rmsfile = os.path.basename(whtfile).replace('_wht', '_rms')
        rmsfile = join(outdir, rmsfile)
        if fileintheway(rmsfile, over):
            continue
        
        print whtfile
        print rmsfile
        hdulist = pyfits.open(join(indir, whtfile), memmap=1)
        wht = hdulist[0].data
        wht = clip(1e-20, wht, 1e99)
        rms = 1 / sqrt(wht)
        hdulist[0].data = rms
        hdulist.writeto(rmsfile)

indir = ''
whtfiles = glob(join(indir, '*_wht*.fits'))
print whtfiles
#outdir = '../../rms'
outdir = '../rms'
makermsimages()
