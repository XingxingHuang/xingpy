## Automatically adapted for numpy Jun 08, 2006
## BY HAND: 'float', "float" -> float; 'int' -> int

# SExSeg
# by Dan Coe
# (ACS Science Team, JHU)

# SExSeg forces a segmentation map into SExtractor for photometric analysis.
# It does this by altering your detection image given your segmentation map.
# In the new detection image, segments act as windows to the data:
#   where objects exist, you see data
#   where no objects exists, you see zeros
#   Gaps of 0's are inserted between objects.
#   And all objects come to have the same flux.
#     (Each object's image is multiplied by the necessary constant.)

# NOTES:
# INPUT: detfits, segmfits, <analfits, -C sexfile, -nobacksub, -segmout, -fences, -gapval, nooverlap>
# detfits = DETECTION IMAGE
# segmfits = SEGMENTATION MAP
# analfits = ANALYSIS IMAGE

# OUTPUT: finalcat (or analroot+'_sexseg.cat')

# FOR MORE DETAILS, SEE http://adcam.pha.jhu.edu/~coe/sexseg/
# FOR DEVELOPMENT NOTES, SEE sexsegnotes.py

# PRODUCES (WHERE 'det.fits' & 'z.fits' ARE YOUR DETECTION & ANALYSIS IMAGES)
# 'z_sexseg.cat'  FINAL CATALOG
# 'z_sexseg_sex.cat'  INTERMEDIATE CATALOG
# 'det_sexseg.fits'  FINAL SExSeg DETECTION IMAGE
# 'det_seggap.fits'  INTERMEDIATE DETECTION IMAGE (HAS GAPS, BUT NOT FLUX-NORMALIZED YET)
# ...AND WHEN LOADED INTO ds9, THESE FILES:
# 'det_segm_id_lab.reg'  LABELS ALL OBJECTS WITH THEIR ID NUMBERS
# 'det_segm.con'  DRAWS CONTOURS AROUND ALL SEGMENTS
#
# 'det_segmcutflag.dat'  FLAGS WHICH OBJECTS HAD PIXELS DROPPED (MUCH BETTER INFO IN z_sexseg.cat)

# FUTURE:
# A COMMAND LINE OPTION FOR NO "ANALYSIS THRESHOLD" (CAN ALSO SET ANALYSIS_MINAREA 0)
# *** NO WAY TO INPUT "finalcat" NAME YET FROM COMMAND LINE
# SHOULD HAVE OPTION TO NOT SUBTRACT BACKGROUND (JUST LINK G-back.fits -> G.fits)
# WHEN INPUTTING .sex FILE, SHOULD STILL BE ABLE TO SUBTRACT BACKGROUND
# SHOULD HAVE 2 "area" COLUMNS: area & isoarea, THE LATTER BEING THE AREA ABOVE THE ANALYSIS THRESHOLD (CURRENTLY MY ONLY "area" COLUMN)
#   THE NEW (FULL) AREA CAN BE GLEANED FROM [ker_]segm.sp (ESPECIALLY WHEN LOADED AS splist)  BUT I DON'T ALWAYS LOAD segm.sp AS AN splist BUT DO I HAVE TO LOAD IT JUST FOR THIS, OR SHOULD I CREATE A area.txt FILE
#  COULD BE DONE AS PART OF compresssplist
#  HOWEVER, WHEN CONVOLVING, SHOULD YOU HAVE 3 "area"'s, INCLUDING ONE FOR THE ORIGINAL UNCONVOLVED SEGMENTS?

# 2DO:
# INPUT OTHER SEXTRACTOR-CALCULATED VALUES (RADIUS, ETC.)
# -- I THINK THIS INVOLVES AN OVERHAUL OF loadsexcat: MAKE IT SAVE A DICTIONARY AND RETURN AN EXECUTABLE STRING THAT LOADS THE DICTIONARY, PLUS ALL THE VARIABLES

# sexsegy:
# !! mag=99  dmag=ZP !!
# ADDED POST-PRODUCTION (AFTER SExtractor)
# USER INPUTS ANALYSIS_MINAREA & ANALYSIS_THRESH INTO .sexseg FILE
# ANALYSIS THRESH -> .sex -> ISOAREA_IMAGE (ABOVE THRESH)
# SExSeg TAKES OBJECTS w/o ENOUGH PIXELS ABOVE THRESH, SETS mag=99, dmag=ZP
# WARN: IF YOU MAKE SMALL SEGMENTS AND LARGE ANALYSIS_MINAREA...
# ALSO, IT DOESN'T ERASE OTHER SHAPE MEASUREMENTS LIKE fwhm, ell (SExtractor SETS THESE TO ZERO)
#   YOU'RE ENCOURAGED TO USE THE area COLUMN TO SORT OUT THE DETECTED OBJECTS

# DIRECTORY OF VARIABLES:
# -------------------------
# segmspfile = 'segm.sp'
# if no analfits, analfits = detfits (Single image mode)
#      detfits = detfits/objsconvfits
#      segmfits = segmidfits/segmconvfits
##     sexcat = analroot+'_sexseg_sex.cat'
##     regfile = analroot+'_segm_lab.reg'
##     seggapfits = detroot/analroot + "_seggap.fits"  # INTERMEDIATE FILE
##     sexsegfits = detroot/analrool + '_sexseg.fits'  # OUTPUT FILE TO RUN SEXTRACTOR ON
##     segmcon = detroot + "_segm_id.con"  # INPUT SEGMENTATION MAP CONTOURS
##     data = []
##     segm = []
##     segmsp = {}
##     segmlist = []
#   segmsp = load(segmfits)
# INSERT GAPS.  segmsp, data -> out -> seggapfits
#   data = load(detfits/objsconvfits)
#   out = zeros
#   area (of each obj) <- segmsp
#   data, segmsp -> out (DATA ONLY ON SEGMENTS, W/ GAPS INSERTED)
#   out -> seggapfits
# NORMALIZE FLUXES.  segmsp, seggapfits  -> sexsegfits
#   data = out / seggapfits
#   nobj, fluxlist, flux <- segmsp, data
#   segmlist = load(segmspfile)
#   MULTIPLY data BY FACTOR, SAVE AS sexseg

import sys, os
#from sexsegtools import loadfits, savefits, capfile, pause, total, params_cl, loaddata, savedata, clip2, loadsexcat, savelabels, loaddict, delfile, getanswer, loadsexdict, census
from sexsegtools import *
#from Numeric import *
from numpy import *
#from MLab_coe import min, isseq, close
#from histeqint import histeqint
from compresssplist import compresssplist
from pyraf.iraf import imcopy, psfmatch, imdelete
from fences import fences
from sparse import *  # sparsify, savesp, loadsp, loadfitsorsp
from sexsegconfig import sexsegconfig, defaultsexfile
from sexsegconfiganalthresh import sexsegconfiganalthresh
from reclaim import reclaim
from coeio import fitssize
#from fitsio import gethead, getimport
import popen2  # Read SExtractor output
from compress2 import compress2 as compress
import string

#global detfits, segmfits, analfits, seggapfits, sexsegfits, sexfile, finalcat, options, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmroot, segmspfile, analroot, finalcat, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile

debug = 0

def objbox(data, xind=[], yind=[]):
    """DETERMINES EXTENT OF OBJECT IN IMAGE"""
    ny, nx = data.shape
    if not xind:
        xind = arange(nx)+1

    if not yind:
        yind = arange(ny)+1

    xsum = add.reduce(data)
    ysum = add.reduce(data, 1)
    xindobj = compress(xsum, xind)
    yindobj = compress(ysum, yind)
    return xindobj[0], xindobj[-1], yindobj[0], yindobj[-1]


def addmags(m1, m2, dm1=0, dm2=0):
    # F = 10 ** (-0.4 * m)
    # dF = -0.4 * ln(10) * 10 ** (-0.4 * m) * dm = -0.921034 * F * dm
    if (m1 >= 99 and m2 >= 99) or (dm1 >= 99 and dm2 >= 99):
        m = 99
        dm = 99
    elif m1 >= 99: # or dm1 >= 99:
        m = m2
        dm = dm2
    elif m2 >= 99: # or dm2 >= 99:
        m = m1
        dm = dm1
    else:  # NORMAL SITUATION
        F1 = 10 ** (-0.4 * m1)
        F2 = 10 ** (-0.4 * m2)
        F = F1 + F2
        m = -2.5 * log10(F)
        #dF1 = 0.921034 * F1 * dm1
        #dF2 = 0.921034 * F2 * dm2
        #dF = sqrt(dF1 ** 2 + dF2 ** 2)
        #dm = dF / F / 0.921034
        if dm1 >= 99 or dm2 >= 99:
            dm = 99
        else:
            dm = sqrt( (F1 * dm1) ** 2 + (F2 * dm2) ** 2 ) / F
    output = (m, dm)
##     if dm1 or dm2:
##         output = (m, dm)
##     else:
##         output = m
    
    return output

def addfluxes(F1, F2, dF1=0, dF2=0):
    F = F1 + F2
    dF = sqrt(dF1 ** 2 + dF2 ** 2)
    output = (F, dF)
##     if dF1 or dF2:
##         dF = sqrt(dF1 ** 2 + dF2 ** 2)
##         output = (F, dF)
##     else:
##         output = F
    
    return output


#def initialize(detfits, segmfits, analfits, sexfile, finalcat, options):
#def initialize():
def initialize(detroot, segmroot, analroot='', sexfile=defaultsexfile, finalcat='', options=[]):
    global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    # global detfits, segmfits, analfits, seggapfits, sexsegfits, sexfile, finalcat, options, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmroot, segmspfile, analroot, finalcat, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile

    detfits = capfile(detroot, 'fits')  # INPUT DATA FITS FILE
    detroot = detfits[:-5]

    segmfits = capfile(segmroot, 'fits')
    segmroot = segmfits[:-5]

    analroot = analroot or detroot
    analfits = capfile(analroot, 'fits')
    analroot = analfits[:-5]

    segmspfile = segmroot+'.sp'

    sexcat = analroot+'_sexseg_sex.cat'
    finalcat = finalcat or analroot+'_sexseg.cat'

    cmd = "sexseg %s %s" % (detfits, segmfits)
    if analfits:
        cmd += ' '+analfits
    if sexfile <> defaultsexfile:
        cmd += ' -c '+sexfile
    print cmd
    print options
    print

    #global ny, nx
    #regfile = analroot+'_segm_id_lab.reg'
    regfile = analroot+'_segm_lab.reg'
    seggapfits = detroot + "_seggap.fits"  # INTERMEDIATE FILE
    sexsegfits = detroot + '_sexseg.fits'  # OUTPUT FILE TO RUN SEXTRACTOR ON
    segmcon = capfile(segmroot, 'con')  # SEGMENTATION MAP CONTOURS
    segmoutroot = segmroot + '_out'
    if 'segmout' in options:  # SO YOU CAN SEE THE GAPS
        segmsexoutfits = capfile(segmoutroot, 'fits')
    else:
        segmsexoutfits = ''
    segmcutflagfile = detroot+'_segmcutflag.dat'
    analbackfile = analroot+'_back.txt'
    if type(options) == str: #type('aa'):
        options = [options]
    nooverlap = 'nooverlap' in options


    if ('fences' in options) and not os.path.exists(segmcon):
        print "DRAWING FENCES AROUND SEGMENTS..."
        print 'CREATING '+segmcon
        fences(segm.spl, segmcon)
        # fences(segmsp, segmcon)

    gapval = 1.e-6  # INSTEAD OF 0!
    if 'gapval' in options:
        gapval2 = gapval
    else:
        gapval2 = 0
    #print 'gapval2 = ', gapval2

    data = []
    datar = []
    segm = []
    segmsp = {}
    segmlist = []

    #nx, ny = getimport(gethead(analfits))[2]
    ny, nx = fitssize(analfits)
    print analfits, (ny, nx)

    segmcutflags = []

    out = []

    return detroot, segmroot, analroot, sexfile, finalcat, options

def insertgaps(): # data, segm, detfits, segmfits, ny, nx, seggapfits, segmcutflagfile
    #global detfits, segmfits, analfits, seggapfits, sexsegfits, sexfile, finalcat, options, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmroot, segmspfile, analroot, finalcat, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    if not segm:
        segm = Sparse(segmfits)

    #os.system('date')
    print "INSERTING GAPS BETWEEN OBJECTS..."
    if not data:
        data = loadfits(detfits)

    out = zeros((ny, nx), float)

    # FIRST COUNT AREA COVERED BY EACH OBJECT

    print "Counting Area covered by each object..."
    area = [0]
    lenarea = 0
    area = segm.census()
    if segmcutflags == []:
        segmcutflags = zeros(segm.hiobj()+1, int)  # A FLAG THAT WILL BE RAISED IF ANY PIXELS ARE KILLED

    #os.system('date')
    print "Inserting Gaps..."
    if nooverlap:
        for key in segm.spl:
            iy, ix = segm.key2yx(key)
            out[iy,ix] = data[iy,ix]
    else:
        #gapflag = segm.data * 0
        gapflag = zeros(segm.ny * segm.nx, int8) # 1-BYTE TYPE (ONLY 1's OR 0's HERE)
        pass  ## #gapflag.savespace(1)  # MAINTAIN TYPE (ONLY NECESSARY IF ADDING, NOT SETTING)
        for key1 in segm.spl:
            iy, ix = segm.key2yx(key1)
            id1 = segm.valk(key1)
            if not gapflag[key1]:
                if debug:
                    #print id1, out[iy,ix], gapval, (out[iy,ix] <> gapval)
                    pause()
                out[iy,ix] = data[iy,ix]
                # CHECK HALF OF THE SURROUNDING PIXELS, IN THIS ORDER:
                # 123
                # -*0
                # ---
                # THIS LOOP NOT CLEANED UP UNTIL sexsegz
                dylist = [0, 1, 1, 1]
                dxlist = [1,-1, 0, 1]
                for ilist in range(4):
                    dy = dylist[ilist]
                    dx = dxlist[ilist]
                    if (0 < iy+dy < ny-1) and (0 < ix+dx < nx-1):
                        key2 = segm.yx2key(iy+dy,ix+dx)
                        if not gapflag[key2]:
                            id2 = segm.val(iy+dy, ix+dx)
                            if id2:
                                if id2 <> id1:  # KILL THE OBJECT WITH MORE AREA
                                    if area[id1] > area[id2]:
                                        out[iy,ix] = gapval  # KILL THIS PIXEL
                                        area[id1] -= 1
                                        segmcutflags[id1] += 1
                                        gapflag[key1] = 1
                                        break
                                        #print 'KILL THIS PIXEL'
                                    else:
                                        out[iy+dy,ix+dx] = gapval  # KILL THIS NEIGHBOR
                                        area[id2] -= 1
                                        segmcutflags[id2] += 1
                                        gapflag[key2] = 1
            if debug:
                savefits(out, seggapfits)
                pause()

        savedata(array(segmcutflags), segmcutflagfile)
    #os.system('date')
    print "Saving Gaps..."
    del data  # SHOULD FREE UP MEMORY
    del gapflag  # SHOULD FREE UP MEMORY
    savefits(out, seggapfits)
    segmcutflags = segmcutflags[1:]
    #print 'SEGMCUTFLAGS, LEN=', len(segmcutflags)
    savedata(segmcutflags, segmcutflagfile, format='%1d\n')
    #os.system('date')


def equalizefluxes():  # segm, data, out, 
    global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    if not segm:
        print 'loading ', segmfits
        segm = Sparse(segmfits)

    #os.system('date')
    print "EQUALIZING FLUXES..."
    flux = 1.  # WILL BE SET = MAX FLUX LATER

    if out <> []:
        data = out
        del out  # SHOULD FREE UP MEMORY USED BY out
    else:
        data = loadfits(seggapfits)

    print "DETERMINE MAX FLUX..."

    # sexsegw: CLIPPING NEGATIVE data -> 100 * gapval.  SEE HOW THAT WORKS OUT...

    data = ravel(data)
    fluxlist = []
    for obj in segm.objspl:
        objdata = take(data, array(obj).astype(int))
        fluxlist.append(sum(objdata))
    data = resize(data, (segm.ny, segm.nx))
    #os.system('date')
    #print 'fluxlist', len(fluxlist)
    #print shape(fluxlist)
    #pause()
    flux = max(fluxlist)# / 100.
    #os.system('date')

    print "Equalize..."
    # YES, PIXEL-BY-PIXEL: SUPPOSED TO BE MUCH FASTER THAN USING where
    #print "(sparing you the gory details)"
    hiobj = segm.hiobj()
    for iobj in arange(hiobj)+1:  # 1 to n
        if not (iobj % 1000):
            print '%5d / %5d' % (iobj, hiobj)
        obj = segm.objspl[iobj]
        for key in obj:
            y, x = segm.key2yx(key)
            if data[y,x] < 0:
                if gapval:
                    data[y,x] = 100 * gapval  # sexsegw: CLIPPING NEGATIVE data -> 100 * gapval.  SEE HOW THAT WORKS OUT...
                else:
                    data[y,x] = 1e-4
            elif close(data[y,x], gapval, rtol=1.e-3, atol=0):  # NOT ADDED TILL sexsegu!
                data[y,x] = gapval2
            else:
                if fluxlist[iobj] > 0: # sexsegx
                    #print type(data), type(flux), type(fluxlist)
                    #print flux
                    ##print len(data), len(flux), len(fluxlist[iobj])
                    #print data[y,x], flux, fluxlist[iobj]
                    if not singlevalue(flux):
                        flux = flux[0]
                    data[y,x] = data[y,x] * flux / fluxlist[iobj]

    #os.system('date')

    savefits(data, sexsegfits)
    #print sexsegfits, 'READY FOR VIEWING!'
    if os.path.exists(seggapfits):
        print "REMOVING INTERMEDIATE FILE ", seggapfits, "..."
        print '...NOT!!'
        #os.remove(seggapfits)
    #os.system('date')


def runsextractor(analroot, sexfile, options):
    global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    # CREATE BACKGROUND IMAGES (IF NECESSARY)
    analrmsfits = analroot + '_rms.fits'
    if os.path.exists(analrmsfits):
        analrmsfits = ''
    analbacksubfits = analroot + '-back.fits'
    if 'nobacksub' in options:
        os.system('ln -s %s %s' % (analroot+'.fits', analbacksubfits))
    if os.path.exists(analbacksubfits):
        analbacksubfits = ''
    backsexfile = analroot + '_back.sex'
##     if not analrmsfits and not analbacksubfits:
##         backsexfile = ''
    sexfile = sexsegconfig(sexfile, analroot, segmsexoutfits, backsexfile, analrmsfits, analbacksubfits)
    rms = 0
    if os.path.exists(analbackfile):
        txt = loadfile(analbackfile)[1]
        rms = string.atof(string.split(txt)[-1])
    if analrmsfits or analbacksubfits or not rms:
        print 'CALCULATING RMS'
        if analrmsfits or analbacksubfits:
            print 'AND CREATING BACKGROUND RMS AND/OR BACKGROUND-SUBTRACTED IMAGES...'
        cmd = 'sex %s -c %s' % (analfits, backsexfile)
        print cmd
        if not os.path.exists(analfits):
            print analfits + ' DOES NOT EXIST.'
            print 'QUITTING SExSeg'
            sys.exit(1)
        #os.system(cmd)
        subproc = popen2.Popen4(cmd)
        sexout = subproc.fromchild.readlines()  # SExtractor output
        for sexline in sexout:  # in case there's an error
            print sexline
        for sexline in sexout:
            if string.find(sexline,'(M+D) Background:') != -1:
                linef = string.split(sexline)
                back, rms = linef[2], linef[4]
                print "Image background (M+D) = " + back
                print "Image noise (RMS) = " + rms
                fout = open(analbackfile, 'w')
                fout.write("Image background (M+D) = " + back + '\n')
                fout.write("Image noise (RMS) = " + rms + '\n')
                fout.close()

    sexsegconfiganalthresh(sexfile, rms, sexsegfile)

    analrmsfits = analroot + '_rms.fits'  # IN CASE ITS NAME GOT DELETED ABOVE
    analbacksubfits = analroot + '-back.fits'  # IN CASE ITS NAME GOT DELETED ABOVE
    print "RUN SEXTRACTOR..."
    print "(Ignore the warning about constant data...)"
    cmd = 'sex %s %s -c %s -WEIGHT_IMAGE %s -CATALOG_NAME %s' % (sexsegfits, analbacksubfits, sexfile, analrmsfits, sexcat)
    print cmd
    os.system(cmd)
    #os.system('date')
    #print 'fa_segm_sexout.fits READY FOR VIEWING!'
    #pause()


def assignresults(finalcat):
    global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    # FIX CATALOG TO REFLECT ORIGINAL SEGMENTS
    print "ASSIGN RESULTS TO ORIGINAL SEGMENTS..."

    #os.system('date')
    exec(loadsexcat(sexcat, magname='MAG_ISO', ma1name='', purge=0))
    #os.system('date')
    id = id.astype(int)
    nobj = id[-1]

    napers = 0
    #print id
    #print x
    #print mag
    #print magaper
    if 'magaper' in params:
        napers = len(magaper.shape)
        if napers == 2:
            napers = magaper.shape[0]

    #os.system('date') #***
    # print "LOAD SEGM YET AGAIN..."
    # segm = loadfits(segmfits).astype(int)  # NOW DONE JUST A FEW LINES EARLIER!
    #os.system('date')
    sid = []
    xrlist = []
    yrlist = []
    #print 'I used to print all objects here...'
    for i in range(nobj):
        xr = int(round(xpeak[i]))
        yr = int(round(ypeak[i]))
        xrlist.append(xr)
        yrlist.append(yr)
        #             print '%2d' % id[i]
        #             print '%5.1f %5.1f' % (x[i], y[i])
        #             print '%3d %3d' % (xr, yr)
        #             print xr
        #             print yr
        #             print '%2d' % segm[yr-1][xr-1]
        # print '%2d %5.1f %5.1f %3d %3d %2d' % (id[i], x[i], y[i], xr, yr, segm.val(yr-1, xr-1))
        sid.append(segm.val(yr-1, xr-1))

    savelabels(x, y, sid, regfile, precision=0)

    #nsegm = max(sid)  # BUG: PROBLEM IF HIGHEST NUMBERED SEGMENTS ARE NOT DETECTED
    nsegm = segm.hiobj()

    #print sid

    # PUT TOGETHER FULL CATALOG, HANDLING SPLIT OBJECTS:
    #   POSITION SET TO POSITION OF BIGGEST CHUNK
    #   MAGS OF CHUNKS ADDED
    id = array(id).astype(float)
    sid = array(sid).astype(float)
    area = array(area).astype(float)
    SI = argsort(sid)
    params.insert(1, 'sid')
    # area, id, sid AREN'T AFFECTED BY locals
    for param in params:
        print param, string.find(param, 'aper'), napers
        if (string.find(param, 'aper') > -1) and (napers > 1):
            exec('%s = take(%s, SI, 1)' % (param, param))
        else:
            #print param, len(eval(param)), eval(param).shape, len(SI)
            exec('%s = take(%s, SI)' % (param, param))

    # CREATE ARRAYS THAT CORRESPOND TO THE SEGMENT IDS
    #  EACH PARAMETER WILL APPEND AN 's' TO ITS NAME: xs, ys, areas, mags, magerrapers, etc.
    sid = array(sid).astype(int)
    lastisegm = -1
    maxareas = zeros(nsegm, int)
    #xs = zeros(nsegm)  -- CREATED BELOW IN exec STATEMENT
    #ys = zeros(nsegm)
    #mags = ones(nsegm) * -99.99  # mag = -99.99 : "UNRESOLVED"
    areas = zeros(nsegm, int)
    #segmcutflags = zeros(nsegm)
    for param in params:
        #print param
        if param[:3] == 'mag':
            exec('%ss = ones(nsegm) * -99.99' % param)
        else:
            exec('%ss = zeros(nsegm, float)' % param)
    if napers > 1:
        magapers = zeros((napers, nsegm), float)
        magerrapers = zeros((napers, nsegm), float)
    for i in range(nobj):
        isegm = sid[i] - 1
        #print i, isegm, lastisegm
        if isegm > lastisegm:  # NEW SEGMENT
            for param in params:
                if (string.find(param, 'aper') > -1) and (napers > 1):
                    exec('%ss[:,%d] = %s[:,%d]' % (param, isegm, param, i))
                else:
                    exec('%ss[%d] = %s[%d]' % (param, isegm, param, i))
            maxareas[isegm] = area[i]
            lastisegm = isegm
            #segmcutflags[isegm] = segmcutflag[i]
        else:  # ANOTHER PIECE OF THE SAME SEGMENT
            #print 'ANOTHER PIECE OF THE SAME SEGMENT', isegm, lastisegm
            #  id      x         y      xpeak  ypeak   area  fluxmax  magauto  magerrauto  magaper  magerraper    mag     magerr  magprof  magerrprof  fluxauto  fluxerrauto  fluxiso   fluxerriso   fwhm       rf       rk     a       b     theta  stellarity  flags   ell    pixelsdropped  
            # HOW TO "ADD" SEGMENTS:
            # FROM BIGGER SEGMENT (DEFAULT):
            #    POSITION: x, y, xpeak, ypeak
            #    magaper, fluxaper
            #    SHAPE: rf, rk, a, b, theta, stellarity, (ell)
            # ADD:
            #    area
            #    mag, flux  (except aper)
            # MAX: fluxmax
            # SPECIAL: id (GETS SET)
            # DETERMINED EARLIER: pixelsdropped (DEFINED ON ORIGINAL SEGMENTS.  NOT CALCULATED BY SEXTRACTOR, SO DOESN'T NEED TO BE ADDED)
            if area[i] > maxareas[isegm]:  # THIS PIECE IS BIGGER, USE IT TO DEFINE POSITION, SHAPE, FLUX/MAGAPER, etc.
                xs[isegm] = x[i]
                ys[isegm] = y[i]
                maxareas[isegm] = area[i]
                # APERTURE MAGNITUDES CAN'T BE ADDED.  YOU ONLY GET ONE APERTURE (PUT IT AROUND THE BIGGEST OBJECT):
                if napers > 1:
                    magapers[:,isegm] = magaper[:,i]
                    magerrapers[:,isegm] = magerraper[:,i]
                elif napers == 1:
                    magapers[isegm] = magaper[i]
                    magerrapers[isegm] = magerraper[i]
                if 'fluxaper' in params:
                    if napers > 1:
                        fluxapers[:,isegm] = fluxaper[:,i]
                        fluxerrapers[:,isegm] = fluxerraper[:,i]
                    elif napers == 1:
                        fluxapers[isegm] = fluxaper[i]
                        fluxerrapers[isegm] = fluxerraper[i]
                # SET MOST PARAMETERS TO BIGGER SEGMENT
                for param in params:
                    if (param not in ['x', 'y', 'area']) and (param[:3] <> 'mag') and (param[:4] <> 'flux'):
                        exec('%ss[%d] = %s[%d]' % (param, isegm, param, i))
            # SET fluxmax
            fluxmaxs[isegm] = max([fluxmax[i], fluxmaxs[isegm]])
            # ADD FLUXES (EXCEPT APER)
            for param in params:
                if (param[:4] == 'flux') and (param[4:7] <> 'err') and (param[4:7] <> 'max') and (param[:8] <> 'fluxaper'):
                    # ESTABLISH fluxerr
                    paramerr = list(param)
                    paramerr.insert(4, 'err')
                    paramerr = string.join(paramerr, '')
                    # print paramerr
                    # print params
                    if paramerr not in params:
                        paramerr = ''
                    paramstrdict = {'param':param, 'paramerr':paramerr}
                    # print param, paramerr
                    if paramerr:
                        exec('%(param)ss[isegm], %(paramerr)ss[isegm] = addfluxes(%(param)ss[isegm], %(param)s[i], %(paramerr)ss[isegm], %(paramerr)s[i])' % paramstrdict)
                    else:
                        exec('%(param)ss[isegm] = addfluxes(%(param)ss[isegm], %(param)s[i])' % paramstrdict)
            # ADD MAGNITUDES (EXCEPT APER)
            for param in params:
                if (param[:3] == 'mag') and (param[3:6] <> 'err') and (param[:7] <> 'magaper'): # MAG_AUTO / ISO / PROF
                    paramerr = list(param)
                    paramerr.insert(3, 'err')
                    paramerr = string.join(paramerr, '')
                    if paramerr not in params:
                        paramerr = ''
                    paramstrdict = {'param':param, 'paramerr':paramerr}
                    if paramerr:
                        try:
                            exec('%(param)ss[isegm], %(paramerr)ss[isegm] = addmags(%(param)ss[isegm], %(param)s[i], %(paramerr)ss[isegm], %(paramerr)s[i])' % paramstrdict)
                        except:
                            print isegm, param
                            exec('print %(param)ss[isegm], %(paramerr)ss[isegm]' % paramstrdict)
                            exec('print addmags(%(param)ss[isegm], %(param)s[i], %(paramerr)ss[isegm], %(paramerr)s[i])' % paramstrdict)
                            print "SOMETHING'S WRONG HERE. SHUTTING DOWN."
                            die()
                    else:
                        exec('%(param)ss[isegm] = addmags(%(param)ss[isegm], %(param)s[i])' % paramstrdict)
            areas[isegm] += area[i]
            #segmcutflags[isegm] = segmcutflag[i] or segmcutflags[isegm]

    outlist = []
    outparams = []
    outfullparams = []
    params = params[1:]  # GET RID OF SEXTRACTOR ID

    #ANALYSIS THRESHOLD
    sexsegdict = loadsexdict(sexsegfile)
    analarea = sexsegdict.get('ANALYSIS_MINAREA', 0)
    zeropoint = sexsegdict['MAG_ZEROPOINT']
    aboveanalthresh = greater_equal(areas, analarea)
    print total(aboveanalthresh), '/', len(aboveanalthresh), 'OBJECTS MEET ANALYSIS THRESHOLD OF area > ', analarea
    print '(REST WILL HAVE MAGNITUDES ASSIGNED = 99, MAGNITUDE UNCERTAINTIES = ZEROPOINT)'
    if napers > 1:
        aboveanalthreshnapers = resize(aboveanalthresh, (napers, nsegm))

    for iparam in range(len(params)):
        param = params[iparam]
        if param[:3] == 'mag':
            # I THINK ALL THESE PARAMS WERE MEANT TO HAVE 's' ADDED TO THEIR END, SO I DID IT --sexsegy
            if param[:6] <> 'magerr':  # mag
                exec('%ss = clip2(%ss, None, 99)' % (param, param))  # mag = clip2(mag, None, 99)
                if (string.find(param, 'aper') > -1) and (napers > 1):
                    exec('%ss = where(aboveanalthreshnapers, %ss, 99)' % (param, param))  # mag = where(aboveanalthreshnapers, mag, 99)
                else:
                    exec('%ss = where(aboveanalthresh, %ss, 99)' % (param, param))  # mag = where(aboveanalthresh, mag, 99)
            else:  # magerr
                # BUG FIX: IF zeropoint = 0, THEN ALL magerr's GET SET = 0!!
                #exec('%ss = clip2(%ss, None, zeropoint)' % (param, param))  # magerr = clip2(magerr, None, zeropoint)
                exec('%ss = clip2(%ss, None, 99)' % (param, param))  # magerr = clip2(magerr, None, zeropoint)
                if (string.find(param, 'aper') > -1) and (napers > 1):
                    exec('%ss = where(aboveanalthreshnapers, %ss, zeropoint)' % (param, param))  # magerr = where(aboveanalthreshnapers, magerr, zp)
                else:
                    exec('%ss = where(aboveanalthresh, %ss, zeropoint)' % (param, param))  # magerr = where(aboveanalthresh, magerr, zp)
        exec('psh = %s.shape' % param)
        plen = len(psh)
        if plen == 1:
            exec('outlist.append(%ss)' % param)
            outparams.append(param)
            outfullparams.append(fullparamnames[iparam])
        else:
            plen = psh[0]
            for ii in range(plen):
                exec('outlist.append(%ss[%d])' % (param, ii))
                outparams.append(param+`ii+1`)
                outfullparams.append(fullparamnames[iparam]+'[%d]'%(ii+1))
    outlist.insert(1, sids)    # SEQUENTIAL ID's

    if segmcutflags == []:
        if os.path.exists(segmcutflagfile):
            segmcutflags = ravel(loaddata(segmcutflagfile).astype(int))
            print 'segmcutflags len=', len(segmcutflags)
        else:
            print segmcutflagfile + ' NOT FOUND.  OH WELL.  NO DROPPED PIXEL STATS!'
            #         print len(areas), len(segmcutflags), 'len'
            #         print areas.shape, segmcutflags.shape
            #         print type(areas[0]), type(segmcutflags[0])
    #segmcutflag = zeros(3)  # JUST A LITTLE SOMETHING TO HUMOR psh!  (SEES THAT SHAPE IS 1-D)
    if segmcutflags <> []:
        print len(segmcutflags), len(outlist[0])
        if len(segmcutflags) <> len(outlist[0]):
            print 'WRONG LENGTH!'
            print 'segmcutflags: len=', len(segmcutflags)
            print 'object data:  len=', len(outlist[0])
        outlist.insert(len(outlist), array(segmcutflags).astype(float))
        outparams.append('pixelsdropped')
        outfullparams.append('PIXELS DISCARDED FROM SEGMENT')

    del outlist[0]  # REMOVE SEx ids
    outparams[0] = 'id'  # CHANGE NAME
    itemlen1 = 0
    for item in outlist:
        #print item.shape, type(item[0])
        itemlen = len(item)
        if not itemlen1:
            itemlen1 = itemlen
        if not itemlen:
            print 'EMPTY ITEM!'
        elif itemlen <> itemlen1:
            print 'WRONG LENGTH!'
            #         for i in range(outlist):
            #             print outlist[i].shape, type(item[0]), outparams[i]
    outcat = array(outlist)
    print finalcat
    #print outcat.shape
    #print outcat[0].shape
    outcat = compress(outcat[0], outcat)  # GET RID OF EMPTY ROWS
    #print outparams
    #print outcat.shape
    #pause()
    savedata(outcat, finalcat+'+', labels=outparams, descriptions=outfullparams) # pf=1
    #print 'MANUAL FORMATTING...'
    #savedata(outcat, finalcat+'+', labels=outparams, descriptions=outfullparams, format=' %5d  %8.3f  %8.3f  %5d  %5d  %5d  % 7.4f  %7.4f  %10.4f  %7.4f  %10.4f  %7.4f  %7.4f  %7.4f  %10.4f  %10.8f  %11.8f  %10.8f  %11.8f  %6.2f  % .3e  %4.2f  %6.3f  %6.3f  % 5.1f  %10.2f  %5d  %6.4f  %13d\n')
    #savedata(outcat, finalcat+'+', labels=outparams, descriptions=outfullparams, format=' %5d  %8.3f  %8.3f  %5d  %5d  %5d  % 7.4f  %7.4f  %10.4f  %7.4f  %10.4f  %7.4f  %7.4f  %7.4f  %10.4f  %8.4f  %11.4f  %8.4f  %11.4f  %6.2f  % .3e  %4.2f  %6.3f  %6.3f  % 5.1f  %10.2f  %5d  %6.4f  %13d\n')


#def sexseg(detfits, segmfits, analfits='', sexfile=defaultsexfile, finalcat='', options=['saveobjs']):
#def sexseg():
def sexseg(detroot, segmroot, analroot='', sexfile=defaultsexfile, finalcat='', options=[]):
    global detfits, segmfits, analfits, seggapfits, sexsegfits, ny, nx, data, segm, segmcutflags, nooverlap, gapval, gapval2, segmcutflagfile, out, segmspfile, sexcat, regfile, segmcon, segmoutroot, segmsexoutfits, analbackfile, sexsegfile
    detroot, segmroot, analroot, sexfile, finalcat, options = initialize(detroot, segmroot, analroot, sexfile, finalcat, options)
    #initialize(detfits, segmfits, analfits, sexfile, finalcat, options)
    # $p/compresssplist.py
    # $p/histeqint.py
    #histeqint('segm.fits', 0, 1)


    #################################
    # INSERT GAPS
    if not (os.path.exists(seggapfits) or os.path.exists(sexsegfits)):
        insertgaps()

    #################################
    # NORMALIZE FLUXES
    #  EVERY OBJECT WILL HAVE THE SAME FLUX = THE HIGHEST FLUX OF ANY OBJECT
    #   (ALL OTHERS ARE MULTIPLIED UP TO MEET IT)
    # NEW STREAMLINED IMPLEMENTATION (AFTER sexsegd.py) DOESN'T RELY ON SO MANY CALLS TO where
    # $p/equalflux_seggap_test2.py

    if os.path.exists(sexsegfits):
        print sexsegfits, 'ALREADY EXISTS!'
    else:
        equalizefluxes()

    #################################
    # RUN SEXTRACTOR!!

    sexsegfile = sexfile  # NEED IT LATER FOR ANALYSIS_THRESH
    #os.system('date')
    if os.path.exists(sexcat):  # FIRST CHECK IF THERE'S AN EMPTY CATALOG (RUN-TIME ERROR)
        fin = open(sexcat, 'r')
        line = 'x'
        gotdata = 0
        while line and not gotdata:
            line = fin.readline()
            if line:
                if line[0] <> '#':
                    gotdata = 1
        if not gotdata:
            print 'No data in ', sexcat, '.  Removing...'
            os.remove(sexcat)
    
    if not os.path.exists(sexcat):
        runsextractor(analroot, sexfile, options)

    # CHECK IF OUTPUT SEGMENT IMAGE MATCHES INPUT
    # print "LOAD SEGM YET AGAIN?... NO!"
    # segm = loadfits(segmfits).astype(int)
    if not segm:
        segm = Sparse(segmfits)

    if 'segmout' in options:
        sexoutsegm = Sparse(segmsexoutfits)
        #print 'ABOUT TO RECLAIM...'
        #print 'COMPARING %s & %s (may be a link to a "backin" image)...' % (segmsexoutfits, segmfits)
        print 'RECLAIMING PIXELS IN SEXTRACTOR OUTPUT SEGMENTATION MAP...'
        print 'COMPARING %s & %s...' % (segmsexoutfits, segmfits)
        # CREATE segmoutfits = sexoutsegmlist OBJECTS w/ segm NUMBERING
        #needtoredo = reclaim(sexoutsegm, resize(segm.data, [segm.ny, segm.nx]), segmoutroot)  # segm -> segm.data AFTER z2
        nnn = reclaim(sexoutsegm, resize(segm.data, [segm.ny, segm.nx]), segmoutroot)  # segm -> segm.data AFTER z2

    #################################
    # ASSIGN RESULTS TO ORIGINAL SEGMENTS
    assignresults(finalcat)


if __name__ == '__main__':
    detroot = sys.argv[1]
    segmroot = sys.argv[2]
    analroot = detroot  # UNLESS...
    if len(sys.argv) >= 4:
        if sys.argv[3][0] <> '-':
            analroot = sys.argv[3]
    params = params_cl()
    sexfile = params.get('c', params.get('C', defaultsexfile))
    finalcat = ''
    # params['fences'] = ''  # JUST NEED TO ADD KEY
    options = params.keys()
    #sexseg(detfits, segmfits, analfits, sexfile, finalcat, params.keys())
    #sexseg()
    sexseg(detroot, segmroot, analroot, sexfile, finalcat, options)
