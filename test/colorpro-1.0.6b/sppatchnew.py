## Automatically adapted for numpy Jun 08, 2006 by 

# ADD "NEW" OBJECTS TO A SEGMENTATION MAP
# python sppatchnew.py allshapes[.spl] somenewshapes[.spl] out[.spl] <newstartid> <-frac 1.5> <-r>

# newstartid =  10001 : NEW OBJECTS ARE ADDED SEQUENTIALLY STARTING WITH #10001
# newstartid = +10000 : NEW OBJECTS FROM somenewshapes HAVE 10000 ADDED TO THEIR ID NUMBERS
# newstartid = (blank): NEW OBJECTS FROM somenewshapes RETAIN THEIR ID NUMBERS

# frac (1.5 DEFAULT)
#   IF 1-(1/frac) (1/3) OF PIXELS ARE NEW, THEN ADD OBJECT
#   IF 1/frac (2/3) OF OLD OBJECT IS SMOTHERED BY NEW OBJECT,
#     THEN REMOVE THE REST OF THE OLD OBJECT


# $p/sppatchnew.py allshapes[.sp] somenewshapes[.sp] out[.sp]
# ADD BRAND-NEW OBJECTS (DON'T ALTER ANY OLD ONES)

# but I still like frac=1.5 -> 2/3 overlap still not new
# NOW CONSIDERED BRAND-NEW ONLY IF 5/6 PIXELS ARE NEW (frac = 6)
#  (IF SMALL PART (< 1/6) OVERLAPS AN ORIGINAL OBJECT, STILL CONSIDERED NEW)

# THE SLOW PART IS THE setk LOOP, BUT THAT MIGHT BE TOUGH TO SPEED UP

# sppatchnew5.py
# ADDING TO _list.txt OUTPUT
#   USED TO JUST REPORT ON OBJECTS THAT GOT MOSTLY SMOTHERED AND HENCE DELETED
#   NOW I'M ALSO REPORTING ON OBJECTS THAT GET TOTALLY SMOTHERED
#     AND THOSE THAT JUST GET A "FLESH WOUND": SOME PIXELS TAKEN OUT, BUT NOT ENOUGH TO BE DELETED

# sppatchnew4.py
# NOW GETTING RID OF OLD OBJECTS THAT GET SMOTHERED BY NEW OBJECTS
# IF 1/frac PIXELS ARE SMOTHERED, THEN GET RID OF IT!

# newstartid =  30000 -> newidseq = 1, newsegmid += 1
# newstartid = +30000 -> newidseq = 0, newsegmid = iobj + newstartid
# newstartid = ''     -> newidseq = 0, newsegmid = iobj

# $p/sppatch.py allshapes[.sp] somenewshapes[.sp] out[.sp]

# $p/reclaim.py sexsegm    segm      segmout
# $p/reclaim.py sexsegm.sp segm.fits segmout
#               OBJECTS    NUMBERING

# sppatch3
# NOW ALTERING ARRAY & SPARSE ARRAY INSTEAD OF LIST
# CAN HANDLE OVERLAPS INTO NEIGHBORING LESS POPULAR OBJECTS
# CAN MAKE NEW OBJECTS
# -- IF OBJECT SIZE IS < 1/8 SIZE OF ORIGINAL OBJECT ## SHOULD ALLOW ADJUST
#    -- IF SECTION CONTAINED IN NEW OBJECT IS < 1/8 OF ORIGINAL OBJECT
# -- IF OBJECT IS NEW (FALLS ON NO SEGMENT)

# FIX SOME SHAPES
# allshapes -- ALL ORIGINAL SHAPES
# somenewshapes -- SOME NEW SHAPES

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
from sparsenoobj import *
from spcensus import spcensus
import sys
from coetools import savefits, pause, loaddict, params_cl, pause
from numpy import arange, ravel
import string  # LOAD THIS AFTER numpy, BECAUSE numpy HAS ITS OWN string

def sppatchnew(origfile, newfile, outfile, newstartid='', frac=1.5, reportonly=0):
    if reportonly:
        print
        print "-r SELECTED"
        print 'REPORTING ONLY (to %s_list.txt)!' % outfile
        print "WON'T SAVE RESULTING SEGMENTATION MAP!"
        #print '(press Enter to continue...)'
        #pause()
    print 'PATCHING IN NEW SEGMENTS... (sppatchnew.py)'
    newidseq = 0
    if newstartid <> '':
        if newstartid[0] <> '+':
            newidseq = 1  # JUST SOME INTEGER
        newstartid = string.atoi(newstartid)
        newsegmid = newstartid
    print 'newstartid=',newstartid, ' sequential=',newidseq
    #origsp = Sparsenoobj(origfile)
    origsp = Sparse(origfile)
    newsp = Sparse(newfile)
    # GO THROUGH NEW OBJECTS
    nobj = len(newsp.objspl)
    fout = open(outfile+'_list.txt', 'w')
    for iobj in range(1,nobj):
        # obj = newsplist[iobj]
        #print 'up top...',
        newobjspl = newsp.objspl[iobj]
        newpix = len(newobjspl)
        #print 'done'
        if newpix:
            smothpix = 0
            smothcens = {}
            #print 'now ya see it...',
            for key in newobjspl:
                origid = origsp.valk(key)
##                 if origid == 108:
##                     print origsp.objspl[origid]
                if origid:
                    smothpix += 1
                    # orig census -- CHECK FOR SMOTHERING
                    nnn = smothcens.get(origid, 0)
                    smothcens[origid] = nnn + 1
            #print 'done'
            if not newidseq:
                if newstartid:
                    newsegmid = iobj + newstartid
                else:
                    newsegmid = iobj
            if smothpix < (newpix / frac):
                print smothcens
                origcens = {}
                for origid in smothcens.keys():
                    origcens[origid] = len(origsp.objspl[origid])
                print origcens
                # ADD OBJECT
                #print iobj, newsegmid
                #print 'adding object...',
                newobjspl = newsp.objspl[iobj]
                # this part probably takes a little while, but it'd be hard to get around it
                # need to adjust all object lists when pixels get taken out...
##                 for key in newobjspl:
##                     origsp.setk(key,newsegmid)
                origsp.setkeys(newobjspl, newsegmid)
                # CONVERT SMOTHERED OBJECTS
                # ALSO, REPORT ON OBJECTS LESS SMOTHERED
                for origid in smothcens.keys():
                    # IF SMOTHERED MORE THAN 2/3 OF THE ORIGINAL PIXELS (frac=1.5)
                    smothpix1 = smothcens[origid]
                    if smothpix1:
                        origpix1 = origcens[origid]
                        if smothpix1 == origpix1:  # ALL WERE SMOTHERED, SO ALL WERE CONVERTED
                            outline = 'SMOTHERED OBJECT %d -> %d' % (origid, newsegmid)
                            #print '%d, %d pixels smothered' % (smothpix1, origpix1)
                        else:  # ALL WEREN'T SMOTHERED
                            if smothpix1 > (origpix1 / frac):  # BUT MOST WERE SMOTHERED  # or (origpix1 - smothpix1) < 9
                                # SO CONVERT THE REST
                                outline = 'CONVERTING SMOTHERED OBJECT %d -> %d:  %d / %d = %.2f' % (origid, newsegmid, smothpix1, origpix1, smothpix1/float(origpix1))
                                origsp.reid1(origid, newsegmid)
                                # origsp.reid([origid], [newsegmid])
                                # origsp.remobj(origid)
                            else:  # FLESH WOUND
                                outline = 'OBJECT LOST A FEW PIXELS %d -> %d:  %d / %d = %.2f' % (origid, newsegmid, smothpix1, origpix1, smothpix1/float(origpix1))
                        print outline
                        fout.write(outline+'\n')
                fout.write('%d -> %d' % (iobj, newsegmid))  # newsegm
                print '%d -> %d' % (iobj, newsegmid)
                fout.write('*')  # newsegm
                print '*',
                # THE FOLLOWING USED TO GO 4 LINES UP, BEFORE THE fout.write's ABOVE
                # AM I DOING THE RIGHT THING BY MOVING IT?
                if newidseq:
                    newsegmid += 1
            else:
                fout.write(' ')
                print ' ',
                #print 'done'
            #print 'writing...',
            #else:
                #print iobj, 'objhere'
            if smothpix:
                outline = '%5d %5d %5d %4.2f' % (iobj, newpix, smothpix, (newpix * 1. / smothpix))
            else:
                outline = '%5d %5d %5d inf' % (iobj, newpix, smothpix)
##             if smothpix:
##                 outline = '%5d %5d %5d %4.2f' % (newsegmid, newpix, smothpix, (newpix * 1. / smothpix))
##             else:
##                 outline = '%5d %5d %5d inf' % (newsegmid, newpix, smothpix)
            print outline
            fout.write(outline+'\n')
            #print 'done'

    fout.close()

    if not reportonly:
        origsp.save(outfile)

if __name__ == '__main__':
    origfile, newfile, outfile = sys.argv[1:4]
    newstartid = ''
    if len(sys.argv) > 4:
        if sys.argv[4][0] <> '-':
            newstartid = sys.argv[4]
##             if sys.argv[4][0] == '+':
##                 newstartid = sys.argv[4]
##             else:
##                 newstartid = string.atoi(sys.argv[4])
    params = params_cl()
    frac = params.get('frac', 1.5) * 1.0
    reportonly = 'r' in params
    sppatchnew(origfile, newfile, outfile, newstartid, frac, reportonly)
