## Automatically adapted for numpy Jun 08, 2006 by 

# $p/spcensus.py segm
# NOW USING sparse3 FORMAT

# $p/compresssplist.py segm
# NOW OPERATES ON AND OUTPUTS A SPARSE ARRAY (LIST)

# $p/histeqint.py multiDet_cut.fits
# $p/histeqint.py det_cut_SEGM.fits

# LEAVING outfits=1 AND/OR outtxt=1 WILL PRODUCE THESE FILES w/ DEFAULT NAMES.  SEND IN A FILENAME, AND IT'LL BE USED INSTEAD
# MAKES NEW FITS FILE, AND RETURNS THE DECODER KEY -- OR, IF THE FITS FILE IS ALREADY SEQUENTIAL, RETURNS AN EMPTY LIST 

#from ksbtools import *
#from Numeric import *
from numpy import *
from coetools import loadfits, savefits, total, savedata
from MLab_coe import norep, isseq
from compress2 import compress2 as compress
import sys, os
from sparse import *

def spcensus(infile, outtxt=1):
    infile = sys.argv[1]
    infile = capfile(infile, 'sp')[:-3]
    inroot = capfile(infile, 'fits')[:-5]
    if outtxt == 1:
        outtxt = inroot + '_census.dat'

    sp = Sparse(infile)
    ids = sp.ids()
    census = sp.census()
    census = compress(census, census)
    #ids = arange(len(census))
    #data = array([ids, census]).astype(int)
    #datac = compress(census, data)
    savedata(array([ids, census]), outtxt+'+', labels=['id', 'area'])
    return census

if __name__ == '__main__':
    infile = sys.argv[1]
    outtxt = 1
    if len(sys.argv) > 2:
        outtxt = sys.argv[2]
    spcensus(infile, outtxt)
