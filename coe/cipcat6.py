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
# -faint -- aggressive SExtractor background subtraction

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
from os.path import join, exists
import pyfits
from numpy import *
#from bpz_tools import filter_center
import cipphot
import bpzcolumns
from coeio import params_cl
from coetools import ask, pause

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


def findimages(searchstr, indir, silent=1):
    if not silent:
        print 'Searching:', join(indir, searchstr)
    allfiles = glob.glob(join(indir, searchstr))
    
    if not silent:
        print "Found:"
    files = []
    for file in allfiles:
        if '_cln' not in file:
            if 'total' not in file:
                if file[-3:] == '.gz':
                    print 'Decompressing %s...' % file
                    os.system('gunzip ' + file)
                    file = file[:-3]
                if not silent:
                    print file
                files.append(file)

    if not len(files):
        print join(indir, searchstr)
        print 'NO FILES FOUND!'
        quit()

    if not silent:
        print
    return files

#def loadfitsfiles(searchstr, instr='', indir=''):
def loadfitsfiles(instr=''):
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
        if instr not in drzfile:
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

def fileintheway(file, over):
    if exists(file):
        if over:
            print "Deleting previous copy of ", outfile
            os.remove(file)
        else:
            print file, 'EXISTS'
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
    if 0:
        i = sexcmddir.find('bin')
        sexcmddir = sexcmddir[:i]
        sexconfigdir = join(sexcmddir, 'config')
    sexcmddir = os.path.realpath(sexcmddir)  # Follows links
    sexcmddir = os.path.dirname(sexcmddir)   # directory
    sexconfigdir = os.path.split(sexcmddir)[0]  # one level up
    sexconfigdir = join(sexconfigdir, 'config')    # then config/
    # /Applications/ST_sci/SEXTRACTOR/
    os.remove('sexdirtemp.txt')
    ######

    cmdfile = join(sexdir, 'sexcmds')
    foutcmd = open(cmdfile, 'w')

    if '-IR' in sys.argv:
        detimage = join(detdir, 'IR_detectionImage.fits')
    elif '-ACS' in sys.argv:
        detimage = join(detdir, 'ACS_detectionImage.fits')
    elif '-ACSIR' in sys.argv:
        detimage = join(detdir, 'ACSIR_detectionImage.fits')
    else:
        detimage = join(detdir, 'detectionImage.fits')

    if '-faint' in sys.argv:
        inparfile = 'aggressive.inpar'
    else:
        inparfile = 'filterImage.inpar'

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
    pardict['WEIGHT_TYPE']     = 'NONE'
    pardict['CHECKIMAGE_TYPE']     = 'SEGMENTATION,APERTURES'
    pardict['CHECKIMAGE_NAME'] = 'detectionImage_SEGM.fits,detectionImage_APER.fits'

    dirp = os.path.dirname(pardict['PARAMETERS_NAME'])
    pardict['PARAMETERS_NAME'] = join(dirp, 'detectionImage.param')

    del pardict['WEIGHT_IMAGE']
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

    sexline = 'sex %s -c %s' % (detimage, sexfile)

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
                val = 'null.fits,' + rmsimage
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

        sexline = 'sex %s %s -c %s' % (detimage, filtimage, sexfile)

        print sexline
        foutcmd.write(sexline+'\n')
        sexcmds.append(sexline)
        #sexcats.append(pardict['CATALOG_NAME'])
        print
        #os.system(sexline)

    foutcmd.close()
    # os.chmod(cmdfile, 755)
    os.system('chmod 755 %s' % cmdfile)
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
    datestr = sys.argv[2]  # 20110324
    if len(sys.argv) > 3:
        subdir  = sys.argv[3]  # 65mas
    else:
        subdir = ''
    #outsubdir = sys.argv[4]  # faint

    if onclashdms1():
        cipdir = '/data01/cipphot'
        
        # indir = /astro/clash1/ftp/outgoing/abell_2261/HST/amk_mosaicdrizzle/20110324/65mas/
        #indir = '/astro/clash1/ftp/outgoing/'
        indir = '/data01/amk_mosaicdrizzle'
        indir = join(indir, field)
        #indir = join(indir, datestr)
        indir = join(indir, subdir)
        
        # outdir = clashdms1:/data01/cipcat/abell_2261/mosdriz/20110324/65mas/
        #outrootdir = '/data01/cipcat'
        outrootdir = cipdir
        outrootdir = join(outrootdir, field)
        outrootdir = join(outrootdir, 'mosdriz')
        outrootdir = join(outrootdir, datestr)
        outrootdir = join(outrootdir, subdir)
        
        cipdir = join(cipdir, 'pipeline')
    else:
        home = os.environ.get('HOME', '')
        cipdir = join(home, 'CLASH/pipeline/catamk/')  # keywordkeepers.dict
        rootdir = 'CLASH/data/%s/amk/%s' % (field, datestr)
        rootdir = join(home, rootdir)
        indir = join(rootdir, 'images')
        indir = join(indir, subdir)
        outrootdir = rootdir

    params = params_cl()  # Parameters read in from command line

    # Replace parameters with any values input on command line
    # for example:
    # > python cipcat.py ... -indir my_dir
    
    indir = params.get('indir', indir)
    inweightdir = params.get('inweightdir', indir)
    outrootdir = params.get('outdir', outrootdir)

    thisdir = cipdir  # for compatibility with some portions of code
    
    #################################
    # DETECTION IMAGES
    
    outdir = detdir = join(outrootdir, 'det')

    # Try this first to make sure it's there before processing all the images!
    keywords = loadlist('keywordkeepers.txt', dir=cipdir)
    
    if not exists(outdir):
        os.makedirs(outdir)

    #searchstr = '*_drz.fits*'  # amk
    searchstr = '*_drz*.fits*'  # amk
    drzfiles = findimages(searchstr, indir)
    summary()
    
    #searchstr = '*_wht.fits*'  # amk
    searchstr = '*_wht*.fits*'  # amk
    #whtfiles = findimages(searchstr, indir)
    whtfiles = findimages(searchstr, inweightdir)
    
    #searchstr = '*065mas*_drz.fits'  # amk
    # searchstr = '*065mas*cln_drz.fits'  # amk
    # searchstr = '*065mas_sci_%s.fits' % datestr  # wei
    
    print 'Creating detection images'
    makedetectionimage('', 'detectionImage.fits')
    makedetectionimage('wfc3ir', 'IR_detectionImage.fits')
    makedetectionimage('_acs_', 'ACS_detectionImage.fits')

    detimages = 'ACS_detectionImage.fits', 'IR_detectionImage.fits'
    adddetectionimages(detimages, 'ACSIR_detectionImage.fits')

    print
    
    #################################
    # RMS FILES
    
    outdir = rmsdir = join(outrootdir, 'rms')
    if not exists(outdir):
        os.makedirs(outdir)
    
    makermsimages()


    #################################
    # SEXTRACTOR SETUP & RUN

    if '-nosex' not in sys.argv:
        print 'SExtractor setup & run'
        #sexdir = join(outrootdir, 'cat/sex')
        catsubdir = 'cat'
        
        if '-IR' in sys.argv:
            catsubdir += '_IR'
        elif '-ACS' in sys.argv:
            catsubdir += '_ACS'
        elif '-ACSIR' in sys.argv:
            catsubdir += '_ACSIR'
        
        if '-faint' in sys.argv:
            catsubdir += '_faint'

        catdir = join(outrootdir, catsubdir)
        sexdir = join(catdir, 'sex')

        if not exists(sexdir):
            os.makedirs(sexdir)

        sexsetup()
        os.chdir(sexdir)

        print
        
        redosex = None
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
    
    print 'PHOTOMETRY: combining into multiband catalog'
    filter_centers = loaddict0('filtercenters.dat', dir=thisdir, numconv=1)
    cipphot.cipphot(drzfiles, filts, filter_centers, nexposures, catdir, sexdir, detdir, cipdir, field, datestr, pixelscale=0.065, forcesec=True, forcetot=False, doapcor=True, eBV=None)

    catroot = join(catdir, 'photometry')
    bpzcolumns.bpzcolumns(catroot)

# python ~/CLASH/pipeline/catamk/cipcat.py a383 20110324 65mas gen
