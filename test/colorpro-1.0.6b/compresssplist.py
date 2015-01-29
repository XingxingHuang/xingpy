## Automatically adapted for numpy Jun 08, 2006 by 

# $p/compresssplist.py segm
# NOW OPERATES ON AND OUTPUTS A SPARSE ARRAY (LIST)
# ALSO SEE spcensus.py

# $p/histeqint.py multiDet_cut.fits
# $p/histeqint.py det_cut_SEGM.fits

# LEAVING outfits=1 AND/OR outtxt=1 WILL PRODUCE THESE FILES w/ DEFAULT NAMES.  SEND IN A FILENAME, AND IT'LL BE USED INSTEAD
# MAKES NEW FITS FILE, AND RETURNS THE DECODER KEY -- OR, IF THE FITS FILE IS ALREADY SEQUENTIAL, RETURNS AN EMPTY LIST 

#from Numeric import *
from numpy import *
from sexsegtools import loadfits, savefits, total, savedata, norep, isseq
import sys, os
from sparse import *

def compresssplist(infile, outsp=1, outtxt=1):

    #data = loadfits(infits).astype(int)
    #data = loadfits(infits)
    splist = loadfitsorsplist(infile)
    infile = capfile(infile, 'sp')[:-3]
    inroot = capfile(infile, 'fits')[:-5]
    insp = inroot + '.sp'

    if outsp == 1:
        outsp = inroot + '_id.sp'
    
    print "sorting..."
    nobj = len(splist) - 1
    outsplist = [splist[0]]  # nx, ny, nval
    vals = []
    isseq = 1
    
    for iobj in range(1, nobj+1):
        if splist[iobj].x:  # IF ANYTHING IN THERE (ANY PIXELS ASSIGNED TO THIS # OBJECT)
            if outsp:
                outsplist.append(splist[iobj])
            if iobj:
                vals.append(iobj)
        else:
            isseq = 0
    
    if isseq:
        os.system("ln -s %s %s" % (insp, outsp))
        infits = insp[:-3] + '.fits'
        outfits = outsp[:-3] + '.fits'
        os.system("ln -s %s %s" % (infits, outfits))
    else:
        if outtxt:
            if outtxt == 1:
                outtxt = 'histeqint.txt'
            print vals
            print 'Saving ' + outtxt + '...'
            savedata(array(vals), outtxt)
        
        if outsp:
            print "Saving %s..." % outsp
            savesplist(outsplist, outsp)

    return(vals)


if __name__ == '__main__':
    compresssplist(sys.argv[1])
