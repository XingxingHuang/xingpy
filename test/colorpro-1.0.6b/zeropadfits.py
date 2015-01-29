## Automatically adapted for numpy Jun 08, 2006 by 

#from fitsio import getsize
from pyraf.iraf import imarith, imcopy
import sys
from coetools import capfile, fitssize

def zeropadfits(smfits, bigfits, padfits):
    """PADS smfits WITH ZEROS TO MATCH SIZE OF bigfits
    RESULT IS padfits, CENTERED AS WAS smfits
    ASSUMES smfits & bigfits ARE SQUARES w/ ODD # OF PIXELS ACROSS
    GREAT FOR PSFs!"""
    NY, NX = fitssize(bigfits)
    ny, nx = fitssize(smfits)
    center = (NY+1)/2
    border = ny / 2
    lo = center - border
    hi = center + border
    croprange = '[%d:%d,%d:%d]' % (lo,hi,lo,hi)
    
    imarith(bigfits, '*', 0, padfits)
    imcopy(smfits, padfits+croprange)
    

if __name__ == '__main__':
    smfits, bigfits, padfits = sys.argv[1:4]
    zeropadfits(smfits, bigfits, padfits)
