## Automatically adapted for numpy Jun 08, 2006 by 

# LOADS IN A SExtractor CATALOG FILE AND CONVERTS TO A "REGIONS" FILE FOR ds9

import os,sys
import string
from coetools import params_cl, str2num, loadsexcat, savedata
#from Numeric import *
from numpy import *

def sex2xy(infile, outfile='', purge=0):

    if not outfile:
        outfile = infile[:string.rfind(infile, ".")] + ".xy"  # CHANGES EXTENSION TO .txt

    exec(loadsexcat(infile, purge=0, ma1name=''))

    outfile += '+'

    savedata(array([x,y]), outfile)


if __name__ == '__main__':
    infile = sys.argv[1]

    outfile = infile[:string.rfind(infile, ".")] + ".xy"  # CHANGES EXTENSION TO .txt
    if len(sys.argv) > 2:
        file2 = sys.argv[2]
        if file2[0] <> '-':
            outfile = file2

    params = params_cl()
    purge = ('p' in params.keys()) or ('purge' in params.keys())
    
    sex2xy(infile, outfile, purge)

