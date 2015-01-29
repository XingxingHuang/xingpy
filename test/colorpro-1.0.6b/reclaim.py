## Automatically adapted for numpy Jun 08, 2006 by 

# $p/reclaim.py segm data segmout
#               sp3  fits sp3
# segm = OBJECTS
# data = NUMBERING

# NOW USING sparse3 FORMAT
# MUCH MORE EFFICIENT (ARRAY-BASED) ALGORITHM


# $p/reclaim.py sexsegm    segm      segmout
# $p/reclaim.py sexsegm.sp segm.fits segmout
#               OBJECTS    NUMBERING

# NOTE: I JUST ALLOWED DIFFERENCES TO SLIP BY IN THE CASE WHEN THERE'S A VALUE = 0

# ALLOWS SEXTRACTOR SEGMENTATION MAP TO "RECLAIM" OBJECTS THAT HAVE BROKEN OFF

# sexsegmlist IS A list[nobj] OF XYList's -- FOR EACH OBJECT, THERE'S A LIST OF POSITIONS
# segm IS AN ARRAY -- SEGMENT MAP
# FOR EACH OBJECT IN sexsegmlist, SEE WHICH OBJECT IT SHOULD BE ON segm
#   IF THERE ARE MULTIPLE segm SEGMENTS ASSOCIATED WITH THAT sexsegmlist OBJECT, THEN CHOOSE THE MOST POPULAR, AND RAISE THE FLAG
# SO IF A sexsegmlist OBJECT IS BROKEN IN segm, IT'LL BE PUT BACK TOGETHER IN THE OUTPUT IMAGE segmoutfile

# THAT IS, segmoutfile WILL FOLLOW sexsegmlist's OBJECTS, BUT segm's NUMBERING.
#   IF THERE'S EVER A DISPUTE AS TO THE NUMBER (THERE'S MORE THAN ONE segm NUMBER FOR A sexsegmlist OBJECT,
#    THEN THE MOST POPULAR NUMBER WILL BE CHOSEN, RECLAIMING THE DEVIANT PIXELS, AND THE FLAG WILL BE RAISED.


from sparse import *
import sys
from sexsegtools import savefits, pause, loadfits
from numpy import arange
from sys import exit

# RETOOLED FOR sparse3
# ALSO SEE sppatch.py

# CURRENTLY, MAY ASSIGN SAME VALUE TO MULTIPLE SEGMENTS

def reclaim(segm, newdata, segmoutfile):
    print 'RECLAIMING PIXELS... (reclaim.py)'
    if (segm.ny, segm.nx) <> newdata.shape:
        print "segm & newdata SIZES DON'T MATCH!  KILLING PROGRAM."
        print "segm: %d, %d" % (segm.ny, segm.nx)
        print 'newdata: ', newdata.shape
        exit()
    newdata = ravel(newdata)
    newsegm = max(newdata) + 1
    raiseflag = 0
    hiobj = segm.hiobj()
    #segmout = Sparse((segm.ny, segm.nx), segmoutfile)  # JUST ALTER segm
    idsold = []
    idsnew = []
    for iobj in arange(hiobj)+1:
        obj = segm.objspl[iobj]
        if obj:
            vals = take(newdata, obj)
            vals = sort(vals)
            izero = searchsorted(vals, 1)
            vals = vals[izero:]
            popval = 0
            if vals.any():
                lo = vals[0]
                hi = vals[-1]
                if lo == hi:
                    popval = lo
                else:
                    objlist = arange(lo, hi+2)
                    census = searchsorted(vals, objlist)
                    census = census[1:] - census[:-1]
                    objlist = objlist[:-1]
                    imax = argmax(census)
                    popval = objlist[imax]
                    # hicount = census[imax]
            if popval == 0:
                popval = newsegm
                newsegm += 1
                print 'CREATING NEW SEGMENT:',
            #print iobj, popval
            idsold.append(iobj)
            idsnew.append(popval)
    segm.reid(idsold, idsnew)
    segm.name = segmoutfile
    segm.save()
    return raiseflag
##     if raiseflag:
##         print 'RECLAIMING WAS NECESSARY!'
            

if __name__ == '__main__':
    infile = sys.argv[1]
    segm = Sparse(infile)
    newdata = loadfits(sys.argv[2])
    segmoutfile = sys.argv[3]
    print newdata.shape, 'before'
    reclaim(segm, newdata, segmoutfile)
    print newdata.shape, 'after'
