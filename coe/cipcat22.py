############################################
# CLASH Image Pipeline
# Photometry catalog generator
# -Dan Coe
############################################

# python /data01/cipphot/pipeline/cipcat.py <field> <datestr> <subdir>
#
# Example:
# python /data01/cipphot/pipeline/cipcat.py a383 20110426 scale_065mas_science
# will read in images from:
#   /data01/amk_mosaicdrizzle/a383/20110426/scale_065_science/'
# and create output here:
#   /data01/cipphot/a383/mosdriz/20110426/scale_065_science/
#
# These directories can be overridden with the options:
# -indir my_indir -- imports images from my_dir
# -inweightdir my_weight_dir -- imports weight images from my_weight_dir
# -outdir my_outdir -- writes output to (subdirectories in) my_outdir
#
# Other options:
# -IR -- IR-based detection image
# -faint -- more aggressive SExtractor deblending & background subtraction (now default for IR)
# -apcor -- aperture corrections (now turned off by default)

#################################
# Updates
#
# 10/25/11:
#  - detection parameters modified
#    - general purpose had been optimized for arcs
#      this is now relabeled "aggressive"
#        aggressive.inpar
#      still default for IR
#      (much less aggressive than previous "aggressive")
#    - new default is better for general purpose
#        filterImage.inpar
#        (note detectionImage.inpar is not used)
#  - aperture corrections turned off by default
#  - major axis A replaces flag5sig in output catalogs (cipphot)
#
# 10/7/11:
#  - patched images to mitigate few bad pixels
#  - aperture corrections fixed (miscommuincation between cipphot-HSTee for mosdriz)
#
# 8/17/11:
# (fed in as new option to cipphot)
# IR catalogs no longer pruned of:
#  - "non-detections" (detected by SExtractor but not detected at 5-sigma in any filter)
#  - cosmic rays (aren't any: only 5-sigma detection is in ACS/UVIS)
#
# 8/16/11:
# ACS+IR detection now default
# Now using Anton's detection images and weight maps
# detection using RMS image, converted from weight image
# weight no longer clipped before converted to RMS
# new directories now have group write permission
# ...as do SExtractor parameter files

#################################

# python ~/CLASH/pipeline/catamk/cipcat.py a383 20110324 65mas gen
# python ~/CLASH/pipeline/catamk/cipcat.py a383 20110324 65mas gen -IR -faint

# ~/CLASH/pipeline/catamk/cipcat.py

# Combination of a few programs:
# ~/CLASH/pipeline/catamk/detectionimage.py
# ~/CLASH/pipeline/catamk/rmsimages.py

# ~/CLASH/data/a383/wei/v3/110101/detection/detectionimage.py
# ~/CLASH/data/A383/amk/5/catalog/images/detectionimage.py
# ~/CLASH/data/A383/amk/3/catalog/images/detectionimage.py

# Combine images as a weighted sum

# ~/CLASH/pipeline/apsis/apsis-4.2.5/python/apsis/combFilter.py
# combines images as a sum of (data - background) / noise^2

import glob, os, string, sys
import pyfits
from numpy import *
#from bpz_tools import filter_center
import cipphot
import bpzcolumns
from coeio import params_cl, decapfile
#from coeio import params_cl
from coetools import ask, pause
import scipy.signal # convolve
import datetime
from os.path import join, exists

def splitdirs(dir):
    """Splits a path into a list of directories"""
    print dir
    rootdir, basedir = os.path.split(dir)
    dirs = [basedir]
    while rootdir:
        rootdir, basedir = os.path.split(rootdir)
        dirs.append(basedir)
        if rootdir == '/':
            dirs.append('/')
            break
    
    return dirs[::-1]

def chmod1(path, mode):
    try:
        os.chmod(path, mode)
    except:  # Maybe it's not your file
        pass

def makedirsmode(newpath, mode=0775):
    """Make a directory path and set permissions along the way"""
    path = ''
    for dir in splitdirs(newpath):
        path = os.path.join(path, dir)
        if not exists(path):
            os.mkdir(path)
            chmod1(path, mode)


# APSIS utils/pUtil.py
import time
def ptime():
    """returns the current date/time in ISO 8601 standard format."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))

def loadlist(infile, dir=''):
    #dir = dir.replace('~/', home)
    infile = join(dir, infile)
    f = open(infile, 'r')
    lines = f.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i][:-1]  # Remove trailing \n
    
    f.close()
    return lines


def findimages(searchstr, indir, silent=1, keeptotal=0, keepcln=0, detdate=0):
    global imdatestr
    if not silent:
        print 'Searching:', join(indir, searchstr)
    allfiles = glob.glob(join(indir, searchstr))
    
    if not silent:
        print "Found:"
    files = []
    if detdate:
        imdatestr = 0
    for file in allfiles:
        if keepcln or ('_cln' not in file):
            if keeptotal or ('total' not in file):
                if file[-3:] == '.gz':
                    print 'Decompressing %s...' % file
                    os.system('gunzip ' + file)
                    file = file[:-3]
                if not silent:
                    print file
                files.append(file)
                datestr = int(file.split('_')[-1][:-5])
                #print datestr, imdatestr
                if detdate:
                    if datestr > imdatestr:
                        imdatestr = datestr

    if not len(files):
        print join(indir, searchstr)
        print 'NO FILES FOUND!'
        quit()

    if detdate:
        imdatestr = '%d' % imdatestr
        print 'Latest date:', imdatestr
        #pause()
    
    if not silent:
        print
    return files

#def loadfitsfiles(searchstr, instr='', indir=''):
def loadfitsfiles(instrs=''):
    #global drzfile, whtfile, datasum, weightsum, totexptime
    global drzfile, whtfile, datatot, totexptime
    
    print
    datasum = 0
    weightsum = 0 
    totexptime = 0
    #print join(indir, searchstr)
    #print drzfiles
    print 'Adding the following images multiplied by their weight images:'
    for drzfile in drzfiles:
        #if string.find(drzfile, instr) == -1:
        if type(instrs) == type(''):
            instrs = [instrs]

        chosen = 0
        for instr in instrs:
            if instr in drzfile:
                chosen = 1
        
        if not chosen:
            print 'skipping ', drzfile
            continue
        
        #whtfile = drzfile[:-9] + '_wht.fits'
        whtfile = drzfile.replace('_drz', '_wht')
        print drzfile
        print whtfile
        data = pyfits.open(drzfile, memmap=1)[0].data
        weight = pyfits.open(whtfile, memmap=1)[0].data
        datasum = datasum + data * weight
        weightsum = weightsum + weight
        totexptime += pyfits.open(drzfile, memmap=1)[0].header['EXPTIME']

    datatot = where(weightsum, datasum/weightsum, 0)


def updatefitsfile(infile, outfile, newdata, totexptime):
    hdulist = pyfits.open(infile, memmap=1)
    hdulist.info()
    hdulist[0].data = newdata
    header = hdulist[0].header
    
    oldkeys = header.ascard.keys()
    #newkeys = loadlist('keywordkeepers.txt', dir=thisdir)
    
    for key in oldkeys:
        if key not in keywords:
            del header.ascard[key]
            
    header.update('FILENAME', outfile)
    header.update('EXPTIME', totexptime)
    header.update('ORIGIN','CLASH Image Pipeline')  # Add version number!
    header.update('DATE',ptime())        
        
    print "Saving ", outfile
    hdulist.writeto(outfile)

def delfile(file1):
    if exists(file1):
        os.remove(file1)

def fileintheway(file, over, checkzip=1):
    if exists(file):
        if over:
            print "Deleting previous copy of ", outfile
            os.remove(file)
        else:
            print file, 'EXISTS'
            return True
    elif checkzip:
        zipfile = file + '.gz'
        if exists(zipfile):
            print 'Decompressing', zipfile
            os.system('gunzip ' + zipfile)
            return True
    return False

def makedetectionimage(instr, outfile, over=0):
    outfile = join(outdir, outfile)
    if fileintheway(outfile, over):
        return
    
    print 'To create %s...' % outfile
    #loadfitsfiles(searchstr, instr, indir)
    loadfitsfiles(instr)
    updatefitsfile(drzfile, outfile, datatot, totexptime)

def adddetectionimages(images, outfile):
    datasum = 0
    totexptime = 0
    print 'Adding detection images...'
    for image in images:
        image = join(detdir, image)
        print image
        data = pyfits.open(image, memmap=1)[0].data
        totexptime += pyfits.open(image, memmap=1)[0].header['EXPTIME']
        datasum = datasum + data

    datasum = datasum / float(len(images))
    image0 = join(detdir, images[0])
    outfile = join(detdir, outfile)
    updatefitsfile(image0, outfile, datasum, totexptime)

    
import socket
def onclashdms1():
    hostname = socket.gethostname()
    return (len(hostname) >= 9) and (hostname[:9] == 'clashdms1')

def makermsimages(over=0):
    print "Converting wht files into rms files",
    print "(rms = 1 / sqrt(wht))"
    for whtfile in whtfiles:
        #rmsfile = os.path.basename(whtfile[:-9]) + '_rms.fits'
        rmsfile = os.path.basename(whtfile).replace('_wht', '_rms')
        rmsfile = join(rmsdir, rmsfile)
        if fileintheway(rmsfile, over):
            continue
        
        print whtfile
        print rmsfile
        hdulist = pyfits.open(join(inweightdir, whtfile), memmap=1)
        wht = hdulist[0].data
        wht = clip(wht, 1e-44, 1e99)
        rms = 1 / sqrt(wht)
        hdulist[0].data = rms
        hdulist.writeto(rmsfile)

def patchimages(over=0):
    print "Patching over bad pixels by interpolating within 3x3 boxes..."
    print
    ker = array([
        [0.5, 1,   0.5],
        [1,   0,   1  ],
        [0.5, 1,   0.5]])
    ker = ker / sum(ker.flat)
    block = ones((3,3)) / 9.

    #for drzfile in drzfiles:
    for whtfile in whtfiles:  # includes "total" images
        # Input
        drzfile = os.path.basename(whtfile).replace('_wht', '_drz')
        drzfile = join(indir, drzfile)
        hdu_drz = pyfits.open(drzfile, memmap=1)
        data = hdu_drz[0].data

        #whtfile = os.path.basename(drzfile).replace('_drz', '_wht')
        #whtfile = join(inweightdir, whtfile)
        hdu_wht = pyfits.open(whtfile, memmap=1)
        weight = hdu_wht[0].data

        # Output
        outdrzfile = redir(drzfile, patchdir)
        rmsfile = os.path.basename(drzfile).replace('_drz', '_rms')
        rmsfile = join(rmsdir, rmsfile)

        if fileintheway(outdrzfile, over):
            if fileintheway(rmsfile, over):
                print
                continue

        print drzfile
        print whtfile
        print outdrzfile
        print rmsfile
        print

        # Convolve
        #mode = 1
        mode = 'same'
        # doesn't work: set old_behavior flag just to suppress the warning
        #dataconv   = scipy.signal.convolve(data,   ker, mode, old_behavior=False)
        #weightconv = scipy.signal.convolve(weight, ker, mode, old_behavior=False)
        eps = 1e-8
        weighteps = weight+eps
        weight_block = scipy.signal.convolve(weighteps,        block, mode, old_behavior=False)
        dataconv     = scipy.signal.convolve(weighteps * data,   ker, mode, old_behavior=False) / weight_block
        weightconv   = scipy.signal.convolve(weighteps * weight, ker, mode, old_behavior=False) / weight_block

        # Only use convolved where data is bad (weight = 0)
        good = greater(weight, 0)
        datainterp   = where(good, data,   dataconv)
        weightinterp = where(good, weight, weightconv)

        wht = clip(weightinterp, 1e-44, 1e99)
        rms = 1 / sqrt(wht)

        hdu_drz[0].data = datainterp
        hdu_wht[0].data = rms
        
        if not fileintheway(outdrzfile, over):
            hdu_drz.writeto(outdrzfile)
        
        if not fileintheway(rmsfile, over):
            hdu_wht.writeto(rmsfile)
        
#################################
# SEXTRACTOR SETUP

import pyfits
from numpy import sort
import HSTzp
from filttools import *

def redir(file, newdir):
    file = os.path.basename(file)
    file = join(newdir, file)
    return file

def loadfile(infile, indir='', silent=0):
    infile = join(indir, infile)
    if not silent:
        print 'Loading', infile
        
    fin = open(infile, 'r')
    lines = fin.readlines()
    fin.close()
    
    for i in range(len(lines)):
        lines[i] = lines[i][:-1]
        
    return lines

def loaddict0(filename, dir="", silent=0, numconv=0):
    #global sortedkeys
    lines = loadfile(filename, dir, silent)
    dict = {}
    sortedkeys = []
    for line in lines:
        if line[0] <> '#':
            key, val = line.split()
            if numconv:
                try:
                    val = float(val)
                except:
                    pass
            dict[key] = val
            sortedkeys.append(key)
    dict['keys'] = sortedkeys
    return dict

def sexsetup():
    global sexcmds, sexcats
    sexcmds = []
    sexcats = []
    
    ######
    # Find SExtractor configuration files on this computer
    os.system('which sex > sexdirtemp.txt')
    # /Applications/ST_sci/SEXTRACTOR/bin/sex
    sexcmddir = loadfile('sexdirtemp.txt')[0]
    if onclashdms1():  # /Applications/ST_sci/bin/sex link messes this up
        #sexcmddir = '/Applications/ST_sci/sextractor2.8.6/bin/'
        sexcmddir = '/usr/local/scisoft/packages/sextractor/src/'
    #print sexcmddir
    #pause()
    if 0:
        i = sexcmddir.find('bin')
        sexcmddir = sexcmddir[:i]
        sexconfigdir = join(sexcmddir, 'config')
    sexcmddir = os.path.realpath(sexcmddir)  # Follows links
    #sexcmddir = os.path.dirname(sexcmddir)   # directory
    sexconfigdir = os.path.split(sexcmddir)[0]  # one level up
    #print sexconfigdir
    sexconfigdir = join(sexconfigdir, 'config')    # then config/
    #print sexconfigdir
    #print sexcmddir
    #pause()
    # /Applications/ST_sci/SEXTRACTOR/
    os.remove('sexdirtemp.txt')
    ######

    cmdfile = join(sexdir, 'sexcmds')
    foutcmd = open(cmdfile, 'w')

    detimage    = detfiles[detcam]
    detrmsimage = detrmsfiles[detcam]

    ## if '-IR' in sys.argv:
    ##     detimage    = IRdetimage
    ##     detrmsimage = IRdetrmsimage
    ## elif '-ACS' in sys.argv:
    ##     detimage    = ACSdetimage
    ##     detrmsimage = ACSdetrmsimage
    ## else:  # ACS+IR default
    ##     detimage    = ACSIRdetimage
    ##     detrmsimage = ACSIRdetrmsimage

    ## if '-IR' in sys.argv:
    ##     detimage = join(detdir, 'IR_detectionImage.fits')
    ## elif '-ACS' in sys.argv:
    ##     detimage = join(detdir, 'ACS_detectionImage.fits')
    ## elif '-ACSIR' in sys.argv:
    ##     detimage = join(detdir, 'ACSIR_detectionImage.fits')
    ## else:
    ##     detimage = join(detdir, 'detectionImage.fits')

    #if '-faint' in sys.argv:
    if ('-faint' in sys.argv) or ('-IR' in sys.argv):
        inparfile = 'aggressive.inpar'
        # New "aggressive" is now less aggressive than before
        # Deblending is the same as previous general catalogs,
        # optimized for the arcs / high-z objects
    else:
        inparfile = 'filterImage.inpar'
        # Now better for general purpose
        # Previously was optimized for the arcs

    commondict = loaddict0(inparfile, dir=thisdir)

    #################################
    # DETECTION IMAGE

    pardict = commondict.copy()

    #detfile = 'detectionImage.fits'
    sexfile = '%s_det.inpar' % field
    sexline = 'sex %s -c %s' % (detimage, sexfile)

    pardict['PARAMETERS_NAME'] = redir(pardict['PARAMETERS_NAME'], thisdir)
    pardict['FILTER_NAME']     = redir(pardict['FILTER_NAME'],     sexconfigdir)
    pardict['STARNNW_NAME']    = redir(pardict['STARNNW_NAME'],    sexconfigdir)

    pardict['CATALOG_NAME']    = 'detectionImage.cat'
    #pardict['WEIGHT_TYPE']     = 'NONE'
    pardict['WEIGHT_IMAGE']     = detrmsimage
    pardict['WEIGHT_TYPE']     = 'MAP_RMS'
    pardict['CHECKIMAGE_TYPE']     = 'SEGMENTATION,APERTURES'
    pardict['CHECKIMAGE_NAME'] = 'detectionImage_SEGM.fits,detectionImage_APER.fits'

    dirp = os.path.dirname(pardict['PARAMETERS_NAME'])
    pardict['PARAMETERS_NAME'] = join(dirp, 'detectionImage.param')

    #del pardict['WEIGHT_IMAGE']
    del pardict['WEIGHT_THRESH']

    sexfile = '%s_det.inpar' % field
    sexfile = join(sexdir, sexfile)
    print sexfile

    fout = open(sexfile, 'w')
    for key in sort(pardict.keys()):
        if key == 'keys':
            continue
        val = pardict[key]
        line = key.ljust(20)
        #print line, val
        line += val
        #print line
        fout.write(line+'\n')

    fout.close()
    chmod1(sexfile, 0664)

    #sexline = 'sex %s -c %s' % (detimage, sexfile)
    sexline = '%s/sex %s -c %s' % (sexcmddir, detimage, sexfile)

    print sexline
    foutcmd.write(sexline+'\n')
    sexcmds.append(sexline)
    sexcats.append(pardict['CATALOG_NAME'])
    print
    #os.system(sexline)


    #################################
    # FILTER IMAGES

    for filtimage in drzfiles:
        filt = extractfilt(filtimage)
        #sexfile = '%s_%s_drz.inpar' % (field, filt)
        sexfile = '%s_%s.inpar' % (field, filt)
        sexfile = join(sexdir, sexfile)
        fout = open(sexfile, 'w')
        print sexfile

        #rmsimage = os.path.basename(filtimage)[:-9] + '_rms.fits'
        rmsimage = os.path.basename(filtimage).replace('_drz', '_rms')
        #print rmsdir
        #print rmsimage
        rmsimage = join(rmsdir, rmsimage)
        #print rmsimage
        #pause()

        instr = getinstr(filt)

        #filtimage = '/Users/koekemoe/pipeline/datasets/a383/5/a383_065mas_%s_%s_drz.fits' % (instr, filt)
        #filtimage = '/Users/koekemoe/pipeline/datasets/a383/5/a383_065mas_%s_%s_cln_drz.fits' % (instr, filt)
        #filtimage = 'a383_065mas_%s_%s_cln_drz.fits' % (instr, filt)
        #filtimage = '%s_mosaic_%s_%s_%s_drz.fits' % (field, res, instr, filt)
        #filtimage = join(imdir, filtimage)
        #gain = getgain(filtimage)

        pardict = commondict.copy()

        pardict['PARAMETERS_NAME'] = redir(pardict['PARAMETERS_NAME'], thisdir)
        pardict['FILTER_NAME']     = redir(pardict['FILTER_NAME'],     sexconfigdir)
        pardict['STARNNW_NAME']    = redir(pardict['STARNNW_NAME'],    sexconfigdir)

        #del pardict['WEIGHT_THRESH']
        
        #pardict['CHECKIMAGE_TYPE'] = '-BACKGROUND'
        #pardict['CHECKIMAGE_NAME'] = 'something to be changed below'
        
        for key in sort(pardict.keys()):
            if key == 'keys':
                continue
            val = pardict[key]
            if key == 'CHECKIMAGE_NAME':
                #val = '%s_%s_drz_BACK.fits' % (field, filt)  # a383_amkv5 ?
                #val = '%s_%s_BACK.fits' % (field, filt)  # a383_amkv5 ?
                val = '%s_%s-BACK.fits' % (field, filt)  # a383_amkv5 ?
            elif key == 'WEIGHT_IMAGE':
                #val = 'ones.fits,../det/%s_%s_%s_%s_rms.fits' % (field, res, instr, filt)
                #val = 'null.fits,' + rmsimage
                val = '%s,%s' % (detrmsimage, rmsimage)
            elif key == 'WEIGHT_TYPE':
                val = 'MAP_RMS,MAP_RMS'
            elif key == 'CATALOG_NAME':
                #val = '%s_%s_drz.cat' % (field, filt)  # a383_amkv5?
                val = '%s_%s.cat' % (field, filt)  # a383_amkv5?
                sexcats.append(val)
            elif key == 'MAG_ZEROPOINT':
                #val = '%.9f' % zpdict[filtkey]
                #val = zpdict[filtkey]
                val = '%.9f' % HSTzp.HSTzp(filtimage, forcesec=True)  # zeropoint
            elif key == 'SEEING_FWHM':
                val = '%.3f' % getseeing(instr)
            elif key == 'GAIN':
                val = '%g' % getgain(filtimage)
            line = key.ljust(20)
            line += val
            #print line
            fout.write(line+'\n')

        fout.close()
        chmod1(sexfile, 0664)
        
        if runpatches:
            filtimage = redir(filtimage, patchdir)

        #sexline = 'sex %s %s -c %s' % (detimage, filtimage, sexfile)
        sexline = '%s/sex %s %s -c %s' % (sexcmddir, detimage, filtimage, sexfile)
        #sexline = '%s/sex %s -c %s' % (sexcmddir, detimage, sexfile)
        
        print sexline
        foutcmd.write(sexline+'\n')
        sexcmds.append(sexline)
        #sexcats.append(pardict['CATALOG_NAME'])
        print
        #os.system(sexline)

    foutcmd.close()
    # chmod1(cmdfile, 755)
    #os.system('chmod 755 %s' % cmdfile)
    chmod1(cmdfile, 0775)
    #print 'Now run SExtractor by running ./'+cmdfile

#allfilts = 'f225w f275w f336w f390w f435w f475w f606w f625w f775w f814w f850lp f105w f110w f125w f140w f160w'.split()
allfilts = 'f225w f275w f336w f390w f435w f475w f555w f606w f625w f775w f814w f850lp f105w f110w f125w f140w f160w'.split()

# hijacked from bpz_tools.py
def filter_center(filt):
    return filter_centers[filt]

def summary():
    global drzfiles, lams, filts, FILTS, fullfilts, exptimes, nexposures
    filts = []
    FILTS = []
    fullfilts = []
    lams = []
    exptimes = {}
    nexposures = {}
    totexptime = 0
    for file in drzfiles:
        #print file
        header = pyfits.open(file, memmap=1)[0].header
        #FILT = header['FILTER']
        FILT = extractfilter(header)
        filt = FILT.lower()
        FILTS.append(FILT)
        filts.append(filt)
        fullfilt = ''
        #for key in 'TELESCOP INSTRUME DETECTOR FILTER'.split():
        for key in 'TELESCOP INSTRUME DETECTOR'.split():
            fullfilt += header[key] + '_'
            
        #fullfilt = fullfilt[:-1]
        fullfilt += FILT
        
        fullfilts.append(fullfilt)
        lam = getlam(filt)
        #lam = filter_center(fullfilt) / 10.
        lams.append(lam)
        #nexp = header['NCOMBINE']
        nexp = header['NDRIZIM']
        instr = getinstr(filt)
        exptime = header['EXPTIME']
        if instr in ('acs', 'uvis'):
            nexp = nexp / 2
            exptime = exptime / 2
        nexposures[filt] = nexp
        exptimes[filt] = exptime
        totexptime += exptime
        #print fullfilt, lam, nexp
        #print fullfilt.ljust(19), '%7.1f' % filter_center(fullfilt)

    SI = argsort(lams)
    filts = take(filts, SI)
    lams  = take(lams, SI)
    FILTS = take(FILTS, SI)
    fullfilts = take(fullfilts, SI)
    drzfiles = take(drzfiles, SI)

    print
    
    for i in range(len(filts)):
        print drzfiles[i]

    print

    print 'FILT  EXPTIME #EXPOSURES'
    print '-----  -----  ----------'
    for filt in allfilts:
        print filt.ljust(6),
        exptime = exptimes.get(filt, 0)
        if not exptime:
            print
            continue
        
        print '%5d ' % exptime,
        n = nexposures[filt]
        instr = getinstr(filt)
        sym = {'uvis':'X', 'acs':'+', 'ir':'*'}[instr]
        print sym * n

    print '-----  -----  ----------'
    print 'TOTAL', '% 5d' % totexptime

    if 0:
        #for i in range(len(filts)):
        print filts[i].ljust(6),
        print '%5d ' % exptimes[filts[i]],
        n = nexposures[filts[i]]
        instr = getinstr(filts[i])
        sym = {'uvis':'X', 'acs':'+', 'ir':'*'}[instr]
        print sym * n
        #print '*' * n
        #s = '*' * (n-1)
        #s = s + '%d' % n
        #print s
        #print string.digits[1:n+1]
        #for j in range(1,n+1):
        #    print '%1d' % j,
        #print
        #fmt = '%%%dd' % n
        #print fmt % n
        #print '%2d' % nexposures[filts[i]]
        #print filts[i].ljust(6), '%4d' % lams[i], '%5d' % exptimes[filts[i]], '%4.1f' % nexposures[filts[i]]
    
    print

#################################

if __name__ == '__main__':
    
    field   = sys.argv[1]  # a383 -or- abell_383

    #todaystr20 = datetime.date.today().strftime('%Y%m%d')  # e.g., 20110806
    #datestr = todaystr20
    datestr = 'datestr'
    if len(sys.argv) > 2:
        if sys.argv[2][0] <> '-':
            datestr = sys.argv[2]  # 20110324
    
    #subdir = ''
    subdir = 'scale_65mas'
    if len(sys.argv) > 3:
        if sys.argv[3][0] <> '-':
            subdir  = sys.argv[3]  # 65mas

    #outsubdir = sys.argv[4]  # faint

    if onclashdms1():
        cipdir    = '/data01/cipphot'
        cipoutdir = '/data02/cipphot'
        
        # indir = /astro/clash1/ftp/outgoing/abell_2261/HST/amk_mosaicdrizzle/20110324/65mas/
        #indir = '/astro/clash1/ftp/outgoing/'
        indir = '/data01/amk_mosaicdrizzle'
        indir = join(indir, field)
        #indir = join(indir, datestr)
        indir = join(indir, subdir)
        
        cipdir = join(cipdir, 'pipeline')
    else:
        home = os.environ.get('HOME', '')
        cipdir = join(home, 'CLASH/pipeline/catamk/')  # keywordkeepers.dict
        rootdir = 'CLASH/data/%s/amk/%s' % (field, datestr)
        rootdir = join(home, rootdir)
        indir = join(rootdir, 'images')
        indir = join(indir, subdir)

    params = params_cl()  # Parameters read in from command line

    # Replace parameters with any values input on command line
    # for example:
    # > python cipcat.py ... -indir my_dir
    
    indir = params.get('indir', indir)
    inweightdir = params.get('inweightdir', indir)
    indetdir = params.get('indetdir', indir)

    #################################
    # IMAGES

    detdir = None  # still input by cipphot but not used
    #outdir = detdir = join(outrootdir, 'det')
    #if not exists(outdir):
    #    makedirsmode(outdir)

    # Try this first to make sure it's there before processing all the images!
    keywords = loadlist('keywordkeepers.txt', dir=cipdir)
    
    #searchstr = '*_drz.fits*'  # amk
    searchstr = '*_drz*.fits*'  # amk
    drzfiles = findimages(searchstr, indir, detdate=1)
    if datestr == 'datestr':
        datestr = imdatestr
    summary()
    
    #searchstr = '*_wht.fits*'  # amk
    searchstr = '*_wht*.fits*'  # amk
    #whtfiles = findimages(searchstr, indir)
    #whtfiles = findimages(searchstr, inweightdir)
    whtfiles = findimages(searchstr, inweightdir, keeptotal=1)

    if '-IR' in sys.argv:
        detcam = 'IR'
    elif '-ACS' in sys.argv:
        detcam = 'ACS'
    else:  # ACS+IR default
        detcam = 'ACSIR'
    
    #################################
    # OUTPUT DIRECTORIES
    
    if onclashdms1():
        # outdir = clashdms1:/data01/cipcat/abell_2261/mosdriz/20110324/65mas/
        #outrootdir = '/data01/cipcat'
        #outrootdir = '/data01/cipphot'
        outrootdir = cipoutdir
        outrootdir = join(outrootdir, field)
        outrootdir = join(outrootdir, 'mosdriz')
        outrootdir = join(outrootdir, datestr)
        outrootdir = join(outrootdir, subdir)
    else:
        outrootdir = rootdir

    outrootdir = params.get('outdir', outrootdir)
        
    runpatches = 'nopatch' not in params.keys()
    patchdir = join(outrootdir, 'patch')
    patchdir = params.get('patchdir', patchdir)
    
    if runpatches:
        rmsdir = join(outrootdir, 'rms_patch')
    else:
        rmsdir = join(outrootdir, 'rms')
    rmsdir = params.get('rmsdir', rmsdir)

    thisdir = cipdir  # for compatibility with some portions of code

    #################################
    # IMAGES cont.
    
    detfiles = {}
    detrmsfiles = {}
    searchstr = '*_total*.fits*'  # amk
    allfiles = glob.glob(join(indetdir, searchstr))
    for detfile in allfiles:
        if detfile.find('acs_wfc3ir_total_drz') > -1:
            detfiles['ACSIR'] = detfile
            rmsfile = detfile.replace('drz', 'rms')
            rmsfile = redir(rmsfile, rmsdir)
            detrmsfiles['ACSIR'] = rmsfile
        elif detfile.find('wfc3ir_total_drz') > -1:
            detfiles['IR'] = detfile
            rmsfile = detfile.replace('drz', 'rms')
            rmsfile = redir(rmsfile, rmsdir)
            detrmsfiles['IR'] = rmsfile
        elif detfile.find('acs_total_drz') > -1:
            detfiles['ACS'] = detfile
            rmsfile = detfile.replace('drz', 'rms')
            rmsfile = redir(rmsfile, rmsdir)
            detrmsfiles['ACS'] = rmsfile

    ## detfiles = findimages(searchstr, indetdir, keeptotal=1)
    ## for detfile in detfiles:
    ##     if detfile.find('acs_wfc3ir') > -1:
    ##         if detfile.find('wht'):
    ##             ACSIRdetrmsfile = detfile
    ##         else:
    ##             ACSIRdetfile = detfile
    ##     elif detfile.find('wfc3ir') > -1:
    ##         if detfile.find('wht'):
    ##             IRdetrmsfile = detfile
    ##         else:
    ##             IRdetfile = detfile
    ##     elif detfile.find('acs') > -1:
    ##         if detfile.find('wht'):
    ##             ACSdetrmsfile = detfile
    ##         else:
    ##             ACSdetfile = detfile

    #searchstr = '*065mas*_drz.fits'  # amk
    # searchstr = '*065mas*cln_drz.fits'  # amk
    # searchstr = '*065mas_sci_%s.fits' % datestr  # wei

    if 0:
        print 'Creating detection images'
        makedetectionimage('', 'detectionImage.fits')
        makedetectionimage('wfc3ir', 'IR_detectionImage.fits')
        makedetectionimage('_acs_', 'ACS_detectionImage.fits')
        makedetectionimage(['_acs_', 'wfc3ir'], 'ACSIR_detectionImage.fits')

    #detimages = 'ACS_detectionImage.fits', 'IR_detectionImage.fits'
    #adddetectionimages(detimages, 'ACSIR_detectionImage.fits')

    print
    

    #################################
    # RMS FILES
        
    if not exists(rmsdir):
        makedirsmode(rmsdir)
    if runpatches:
        if not exists(patchdir):
            makedirsmode(patchdir)
        patchimages()
    else:
        #outdir = rmsdir
        makermsimages()


    #################################
    # SEXTRACTOR SETUP & RUN

    if '-nosex' not in sys.argv:
        print 'SExtractor setup & run'
        #sexdir = join(outrootdir, 'cat/sex')
        catsubdir = 'cat'

        catsubdir = catsubdir + '_' + detcam
        
        if '-faint' in sys.argv:
            catsubdir += '_faint'

        todaystr = datetime.date.today().strftime('%y%m%d')  # e.g., 110806
        catsubdir = join(catsubdir, todaystr)

        catdir = join(outrootdir, catsubdir)
        #print 'Output directory:', catdir
        sexdir = join(catdir, 'sex')

        if not exists(sexdir):
            makedirsmode(sexdir)

        sexsetup()
        os.chdir(sexdir)

        print
        
        #redosex = None
        redosex = params.get('redosex', None)
        for i in range(len(sexcmds)):
            sexcmd = sexcmds[i]
            sexcat = sexcats[i]
            print
            print sexcmd
            #print '...to produce', sexcat
            print '...to produce', join(os.getcwd(), sexcat)
            print
            if exists(sexcat):
                if redosex == None:
                    line = sexcat + ' EXISTS.  Would you like to rerun SExtractor on this image and all other images? (y/n) '
                    redosex = ask(line)
                if not redosex:
                    continue
                
            #print 'Okay, really now, about to produce', join(os.getcwd(), sexcat)
            #pause()
            os.system(sexcmd)
        
        #os.system('./sexcmds')
        #sexcmds = loadfile("sexcmds")
        #for sexcmd in sexcmds:
        #    print sexcmd
        #    os.system(sexcmd)

    #################################
    # PHOTOMETRY
    
    #doapcor = 'noapcor' not in params.keys()
    doapcor = 'apcor' in params.keys()
    apertype = params.get('aper', 'iso')
    
    print 'PHOTOMETRY: combining into multiband catalog'
    filter_centers = loaddict0('filtercenters.dat', dir=thisdir, numconv=1)

    pruneCRs = '-IR' not in sys.argv
    
    outfile = cipphot.cipphot(drzfiles, filts, filter_centers, nexposures, catdir, sexdir, detdir, cipdir, field, datestr, pixelscale=0.065, forcesec=True, forcetot=False, doapcor=doapcor, eBV=None, apertype=apertype, pruneCRs=pruneCRs, detcam=detcam)

    if exists('photometry.cat'):
        catroot = join(catdir, 'photometry')
    else:
        catroot = decapfile(outfile)
        catroot = join(catdir, catroot)
    bpzcolumns.bpzcolumns(catroot)

    print
    print 'Output saved to:'
    print outrootdir

    print
    print 'Output catalogs saved to:'
    print catdir

# python ~/CLASH/pipeline/catamk/cipcat.py a383 20110324 65mas gen
