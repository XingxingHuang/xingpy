
#!/usr/bin/env python


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


########################### by xingxing ###################################
# global param
#    global sexcmds, sexcats
#    global drzfiles, lams, filts, FILTS, fullfilts, exptimes, nexposures
#    global imdatestr
#    global drzfile, whtfile, datatot, weightsum, totexptime

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

def run(cmd, pr=1):
    if pr:
        print cmd
    os.system(cmd)

def getintr(files):
    header = pyfits.open(files)[0].header
    intr = header['INSTRUME']
    if string.lower(intr) == 'wfc3':
        det = header['DETECTOR']
        intr = intr+string.lower(det)
    return(intr)


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


def findimages(searchstr, indir, imcopydir, silent=1, keeptotal=0, keepcln=0, detdate=0):
    global imdatestr
    if not silent:
        print 'Searching:', join(indir, searchstr)
    allfiles = glob.glob(join(indir, searchstr))
    
    if not silent:
        print "Found:"
    files = []
    if detdate:
        imdatestr = 0
    if imcopydir:  # add by xingxing
        if not exists(imcopydir):
             makedirsmode(imcopydir, 0775)
    for file in allfiles:
        if keepcln or ('_cln' not in file):
            if keeptotal or ('total' not in file):
                if file[-3:] == '.gz':
                    if imcopydir:
                        filebase = os.path.basename(file)
                        filecopy = join(imcopydir, filebase)
                        newfile = filecopy[:-3]
                        if not exists(newfile):
                            #print '[xingxing] Do not Copying and Only decompressing %s...' % file
                            print 'Copying and decompressing %s...' % file
                            makedirsmode(imcopydir, 0775)
                            os.system('cp -p %s %s' % (file, filecopy))
                            os.system('chmod 664 %s' % filecopy)
                            os.system('gunzip ' + filecopy)
                        file = newfile
                        #print 'Decompressing %s...' % file
                        #os.system('gunzip ' + file)
                    else:
                        file = file[:-3]
                if not silent:
                    print file
                files.append(file)
                #datestr = int(file.split('_')[-1][:-5])
                datestr = 20139999 # by xingxing
                #print datestr, imdatestr
                if detdate:
                    if datestr > imdatestr:
                        imdatestr = datestr
                            

    if not len(files):
        print join(indir, searchstr)
        print 'WARNING :  NO FILES FOUND!!!!'
        #quit()

    if detdate:
        imdatestr = '%d' % imdatestr
        print 'Latest date:', imdatestr
        #pause()
    
    if not silent:
        print
    return files

#def loadfitsfiles(searchstr, instr='', indir=''):
def loadfitsfiles(instrs='',drzstr = '_sci', whtstr = '_sci_weight'):  # by xingxing
    #global drzfile, whtfile, datasum, weightsum, totexptime
    global drzfile, whtfile, rmsfile, datatot, weightsum, rmssum, totexptime
    
    print
    datasum = 0
    weightsum = 0 
    rmssum = 0
    rms2sum = 0  # by xingxing  calculate the sum data based on the 1/rms2 as weight
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
            if instr == string.lower(getintr(drzfile)):  # by xingxing
                chosen = 1
        
        if not chosen:
            print 'skipping ', drzfile
            continue
        
        #whtfile = drzfile[:-9] + '_wht.fits'
        #whtfile = drzfile.replace(drzstr, whtstr)
        whtfile = whtfiles[where(drzfiles==drzfile)][0]  # by xingxing
        rmsfile = rmsfiles[where(drzfiles==drzfile)][0]

        print 'drzfile  ',drzfile
        print 'whtfile  ',whtfile
        print 'rmsfile  ',rmsfile

        data = pyfits.open(drzfile, memmap=1)[0].data
        weight = pyfits.open(whtfile, memmap=1)[0].data
        rms = pyfits.open(rmsfile, memmap=1)[0].data
        exptime = pyfits.open(drzfile, memmap=1)[0].header['EXPTIME']
        if countspersec ==1:
             datasum = datasum + data * weight 
        elif countspersec==0:
             datasum = where(rms, datasum + data * exptime**2/ rms**2,datasum)   
        else:
              print 'countspersec ???'
              pause() 
        weightsum = weightsum + weight
        rms2sum = where(rms, rms2sum +exptime**2/rms**2, rms2sum)
        totexptime += exptime
    #datatot = where(weightsum, datasum/weightsum, 0)
    datatot = where(rms2sum, datasum/rms2sum, 0)
    rmssum = 1./sqrt(rms2sum)*totexptime
    pdb.set_trace()


def updatefitsfile(infile, outfile, newdata, totexptime):
    hdulist = pyfits.open(infile, memmap=1)
    hdulist.info()
    hdulist[0].data = newdata
    header = hdulist[0].header
    oldkeys = header.ascard.keys()
    #newkeys = loadlist('keywordkeepers.txt', dir=thisdir)
    
    delkey = []
    for key in oldkeys:
        if key not in keywords and key!='': # by xingxing
            if key not in delkey:
                delkey.append(key)
    for key in delkey:
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

def makedetectionimage(instr, outfile, outwhtfile, over=0,drzstr = '_drz', whtstr = '_wht'):
    #outfile = join(outdir, outfile)
    #outwhtfile = join(outdir, outwhtfile)
    if fileintheway(outfile, over):
        return
    
    print 'To create %s...' % outfile
    #loadfitsfiles(searchstr, instr, indir)
    loadfitsfiles(instr,drzstr = drzstr, whtstr = whtstr)
    updatefitsfile(drzfile, outfile,    datatot, totexptime)
    updatefitsfile(whtfile, outwhtfile, weightsum, totexptime)
    outrmsfile = outfile.replace(drzstr, '_rms')
    outrmsfile = redir(outrmsfile, rmsdir)
    updatefitsfile(rmsfile, outrmsfile, rmssum, totexptime) # by xingxing
    #makermsimage(outwhtfile,outfile)

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

def makermsimage(whtfile, drzfile, over=0,searchstr='_wht'):
    if 1:
        #rmsfile = os.path.basename(whtfile[:-9]) + '_rms.fits'
        rmsfile = os.path.basename(whtfile).replace(searchstr, '_rms')
        if not exists(rmsdir):  # by xingxing
              makedirsmode(rmsdir)
        rmsfile = join(rmsdir, rmsfile)
        if fileintheway(rmsfile, over):
            return
        
        print
        print 'whtfile  ',whtfile
        print 'drzfile  ',drzfile
        print 'rmsfile  ',rmsfile
        
        hdulist = pyfits.open(join(inweightdir, whtfile), memmap=1)
        wht = hdulist[0].data
        wht = clip(wht, 1e-44, 1e99)

        if 1 :
            # create the rms based on the combDither in APSIS
            _rnVarSuppFac_ = 1.38                  # boost N*rn^2 by this factor for RMS images
            _exVarPerSec_  = 0.02222               # add this much extra var per sec for RMS ims            
            area_ratio = 1.
            
            scifits = pyfits.open(drzfile)
            scidata = scifits[0].data
            header = scifits[0].header
            skyval  = header['ALIGNSKY']  # this rescaled below
            skyval *= area_ratio
            exptime =header['EXPTIME']
            Ncombed = header['NCOMBINE']           # gain and read noise
            scifits.close()
            
            gain = header['CCDGAIN']
            try: 
                amps   = header['CCDAMP']
            except KeyError:
                amps = []
                sys.exit("WARNING: No CCDAMP keyword found.")

            rnvals = []
            try:    rnvals.append(header['READNSE'])
            except: pass

            for amp in amps:
                try:    rnvals.append(header['READNSE'+amp])
                except: pass    
            if len(rnvals) < 1:
                print "WARNING: No readnoise found in header!"
                pause()
            else:    
                rn = max(rnvals)
            #print 'exptime, Ncombed, rn, gain: %7.1f  %3.0f    %4.1f %4.1f' %(exptime, Ncombed, rn, gain)    
            print   drzfile+":  gain,rn = "+str(gain)+","+str(rn)+"  NCOMBINE = "+str(Ncombed)+"  EXPTIME = "+str(exptime)
            readVariance = Ncombed*(rn/gain)*(rn/gain)
            totInstVar =  (_rnVarSuppFac_ * readVariance) + (_exVarPerSec_ * exptime)
            print "adjusted instrumental variance = "+str(totInstVar)+" which was  "+str(readVariance)
            print "skyval   "+str(skyval)
            totInstVar *= area_ratio       
            
            #pdb.set_trace()

            # calculate the weight
            if countspersec==1:
                newDat  = (skyval/gain + scidata/gain + totInstVar) * (exptime * area_ratio)
            elif countspersec==0: 
                newDat  = ((skyval/gain+ totInstVar)*exptime+ scidata/gain )*area_ratio
            else:
                print 'countspersec ???'
                pause()    
            newDat /=  wht
            newDat = where(logical_or(greater_equal(newDat,1e60),\
                                                      less_equal(newDat,0.)),4e60,newDat)
            rms =  sqrt(newDat).astype(float32)


        ####################################################################################
        #pdb.set_trace()
        #sizetotal = size(wht)
        #sizeuse = size(wht[where(wht>1)])
        #rms = 1 / sqrt(wht)*std(wht[where(wht>1.)])*sqrt(sizetotal/sizeuse)  
        #sqrt(mean(wht**2))  
        #*std(wht[where(wht>1.)])*sqrt(sizetotal/sizeuse)     # by xingxing  important. use rms
        ####################################################################################
        hdulist[0].data = rms
        hdulist.writeto(rmsfile)

def makermsimages(over=0,rmsstr='_sci_weight'):
    print "Converting wht files into rms files",
    print "(rms = 1 / sqrt(wht)) but now rms = 1 / sqrt(xing_wht))"
    #for whtfile in whtfiles:
    for i in range(len(whtfiles)):
        makermsimage(whtfiles[i],drzfiles[i], over=over,searchstr=rmsstr)


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
        print whtfile
        # Input
        drzfile = whtfile.replace('_wht', '_drz')
        if not exists(drzfile):
            print drzfile, 'does not exist'
            drzfile = os.path.basename(whtfile).replace('_wht', '_drz')
            drzfile = join(indir, drzfile)
            print 'Trying', drzfile
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
        bunit    = pyfits.open(drzfile, memmap=1)[0].header.get('BUNIT').strip()  #  added  by xingxing
        if (bunit[-2:] <> '/S'):
            print 'in units of Counts/s'
            countspersec = 1
        else:
            countspersec = 0     
        # Convolve
        #mode = 1
        mode = 'same'
        # doesn't work: set old_behavior flag just to suppress the warning
        #dataconv   = scipy.signal.convolve(data,   ker, mode, old_behavior=False)
        #weightconv = scipy.signal.convolve(weight, ker, mode, old_behavior=False)
        eps = 1e-8
        weighteps = weight+eps
        weight_block = scipy.signal.convolve(weighteps,        block, mode)  # by xingxing old_hehavior
        tmp = weighteps * data  if countspersec == 1 else data   # add by xingxing
        dataconv     = scipy.signal.convolve(tmp ,   ker, mode) / weight_block
        weightconv   = scipy.signal.convolve(weighteps * weight, ker, mode) / weight_block

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
            print key
            if numconv:
                try:
                    val = float(val)
                except:
                    pass
            dict[key] = val
            sortedkeys.append(key)
    dict['keys'] = sortedkeys
    return dict

def extractinstrcam(infile):
    instrcams = 'wfc3uvis acs wfc3ir'.split()
    for instrcam in instrcams:
        instr = pyfits.open(infile)[0].header['INSTRUME']
        dete = pyfits.open(infile)[0].header['DETECTOR']
        if string.lower(instr) =='acs':
            return 'acs'
        if string.lower(dete) in instrcam and string.lower(instr) in instrcam:
           return instrcam

    print 'instrcam not found in ', infile
    return None

def extractinstr(infile):
    instrcam = extractinstrcam(infile)
    instrs = 'uvis acs ir'.split()
    for instr in instrs:
        if instr in instrcam:
            return instr
    print 'instr not found in ', infile
    return None

def sexsetup():
    global sexcmds, sexcats
    sexcmds = []
    sexcats = []
    sexused = '/opt/local/bin/sex'  #sex2.8
    #sexused = 'sex '   #sex2.5
    
    ######
    # Find SExtractor configuration files on this computer
    os.system('which sex > sexdirtemp.txt')
    # /Applications/ST_sci/SEXTRACTOR/bin/sex
    sexcmddir = loadfile('sexdirtemp.txt')[0]
    if onclashdms1():  # /Applications/ST_sci/bin/sex link messes this up
        #sexcmddir = '/Applications/ST_sci/sextractor2.8.6/bin/'
        sexcmddir = '/usr/local/scisoft/packages/sextractor/src/'
    sexcmddir = '/usr/local/scisoft/packages/sextractor/src/'    # by xingxing
    #print sexcmddir
    #pause()
    if 0:
        i = sexcmddir.find('bin')
        sexcmddir = sexcmddir[:i]
        sexconfigdir = join(sexcmddir, 'config')
    sexcmddir = os.path.realpath(sexcmddir)  # Follows links
    sexcmddir = os.path.dirname(sexcmddir)   # directory
    sexconfigdir = sexcmddir# os.path.split(sexcmddir)[0]   # by xingxing  # one level up
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
    detwhtimage = detwhtfiles[detcam]

    #if '-faint' in sys.argv:
    if ('-faint' in sys.argv) or ('-IR' in sys.argv) or ('-RED' in sys.argv) :
        inparfile = 'aggressive.inpar'
        # New "aggressive" is now less aggressive than before
        # Deblending is the same as previous general catalogs,
        # optimized for the arcs / high-z objects
    elif ('-REDg' in sys.argv):
        inparfile = 'gaggressive.inpar'
        # only used for 'detection-F105W' image.
        print
        print 'Using ',inparfile,' ??'
        print 
        pdb.set_trace()
    else:
        print
        print 'Are you sure?  using filterImage.inpar'
        print
        pdb.set_trace()
        inparfile = 'filterImage.inpar'
        # Now better for general purpose
        # Previously was optimized for the arcs

    commondict = loaddict0(inparfile, dir=thisdir)

    #################################
    # DETECTION IMAGE

    pardict = commondict.copy()

    #detfile = 'detectionImage.fits'
    sexfile = '%s_det.inpar' % field
    #sexline = '%s %s -c %s' % (sexused,detimage, sexfile)
    pardict['PARAMETERS_NAME'] = redir(pardict['PARAMETERS_NAME'], thisdir)
    pardict['FILTER_NAME']     = redir(pardict['FILTER_NAME'],     sexconfigdir)
    pardict['STARNNW_NAME']    = redir(pardict['STARNNW_NAME'],    sexconfigdir)
   
    pardict['CATALOG_NAME']    = 'detectionImage.cat'
    #pardict['WEIGHT_TYPE']     = 'NONE'
    pardict['WEIGHT_IMAGE']     = detwhtimage
    pardict['WEIGHT_TYPE']     = 'MAP_WEIGHT'
    pardict['CHECKIMAGE_TYPE']     = 'SEGMENTATION,APERTURES,BACKGROUND'  #,FILTERED
    pardict['CHECKIMAGE_NAME'] = 'detectionImage_SEGM.fits,detectionImage_APER.fits,detectionImage_BACK.fits' #,detectionImage_FILT.fits
    pardict['PHOT_APERTURES'] = '4'  # add by xingxing.  So you can use the detectionImage_APER.fits now
    dirp = os.path.dirname(pardict['PARAMETERS_NAME'])
    pardict['PARAMETERS_NAME'] = join(dirp, 'detectionImage.param')
    #del pardict['WEIGHT_IMAGE']
    pardict['WEIGHT_THRESH']

    sexfile = '%s_det.inpar' % field
    sexfile = join(sexdir, sexfile)
    print sexfile

    fout = open(sexfile, 'w')
    for key in sort(pardict.keys()):
        if key == 'keys':
            continue
        val = pardict[key]
        line = key.ljust(20)
        print line, val
        line += val
        #print line
        fout.write(line+'\n')
    chmod1(sexfile, 0664)

    #sexline = 'sex %s -c %s' % (detimage, sexfile)
    #sexline = '%s/src/sex %s -c %s' % (sexcmddir, detimage, sexfile)
    sexline = '%s %s -c %s' % (sexused, detimage, sexfile)
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
        instr = getinstr(filt)
        instr2 = extractinstr(filtimage)

        print filtimage
        print 'instr in name  :', instr2
        print 'instr should be:', instr
        if instr <> instr2:
            print 'wrong instrument for', filt
            print 'skipping...'
            #pause()
            continue
        
        #pause()
        
        #sexfile = '%s_%s_drz.inpar' % (field, filt)
        sexfile = '%s_%s.inpar' % (field, filt)
        sexfile = join(sexdir, sexfile)
        fout = open(sexfile, 'w')
        print sexfile
        
        '''
        #rmsimage = os.path.basename(filtimage)[:-9] + '_rms.fits'
        if  '_sci' in os.path.basename(filtimage):
            rmsimage = os.path.basename(filtimage).replace('_sci', '_rms')  # by xingxing
        elif  '_drz' in os.path.basename(filtimage):
            rmsimage = os.path.basename(filtimage).replace('_drz', '_rms')  # by xingxing
        else:   
            print '_drz or _sci are not detected in '+filtimage
        #print rmsdir
        #print rmsimage
        rmsimage = join(rmsdir, rmsimage)
        #print rmsimage
        #pause()
        '''
        rmsimage = rmsfiles[where(drzfiles==filtimage )][0]
        whtimage = whtfiles[where(drzfiles==filtimage )][0]

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
                val = '%s,%s' % (detwhtimage, rmsimage)
            elif key == 'WEIGHT_TYPE':
                val = 'MAP_WEIGHT,MAP_RMS'     
            elif key == 'CATALOG_NAME':
                #val = '%s_%s_drz.cat' % (field, filt)  # a383_amkv5?
                val = '%s_%s.cat' % (field, filt)  # a383_amkv5?
                sexcats.append(val)
            elif key == 'MAG_ZEROPOINT':
                #val = '%.9f' % zpdict[filtkey]
                #val = zpdict[filtkey]
                val = '%.9f' % HSTzp.HSTzp(filtimage, forcesec=False)  # zeropoint
            elif key == 'SEEING_FWHM':
                val = '%.3f' % getseeing(instr)
            elif key == 'GAIN':
                val = '%g' % getgain(filtimage, persecond = countspersec)    # add the countspersec by xingxing
            line = key.ljust(20)
            line += val
            #print line
            fout.write(line+'\n')

        fout.close()
        chmod1(sexfile, 0664)
        

        #sexline = 'sex %s %s -c %s' % (detimage, filtimage, sexfile)
        #sexline = '%s/src/sex %s %s -c %s' % (sexcmddir, detimage, filtimage, sexfile)
        sexline = '%s %s %s -c %s' % (sexused, detimage, filtimage, sexfile)

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
    global drzfiles, whtfiles,rmsfiles,lams, filts, FILTS, fullfilts, exptimes, nexposures
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
    whtfiles = take(whtfiles, SI)
    rmsfiles = take(rmsfiles, SI)

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

def fieldshorten(field):
    field = field.replace('abell_', 'a')
    return field

def fieldlengthen(field):
    if field[0] == 'a':
        if field[:5] <> 'abell':
            field = 'abell_' + field[1:]
    return field

def timestamp(file):
    return os.stat(file).st_mtime  # mtime better resolution than ctime

def oldest(files):
    if len(files):
        times = map(timestamp, files)
        return max(times)
    else:
        return 0

def writefile(infile, txt):
    fout = open(infile, 'a')
    if txt[-1] <> '\n':
        txt += '\n'
    fout.write(txt)
    fout.close()





if __name__ == '__main__':
    import pdb
    ###################################
    # set input para
    # field
    field   = sys.argv[1]  # a383 -or- abell_383
    field = fieldshorten(field)
    longfield = fieldlengthen(field)
    fullfield = '-full' in sys.argv
    datestr = 'datestr'
    if len(sys.argv) > 2:
        if sys.argv[2][0] <> '-':
            datestr = sys.argv[2]  #20110324

    # dir
    #indir = os.getcwd() # by xingxing
    #datadir = '/Users/xing/data/clash'    
    #output = 'clash_cat'
    
    datadir = '/Users/xing/data/frontier'    
    output = 'frontier_cat'
    
    indir = join(datadir,field,'Images')         
    cipdir = '/Users/xing/programs/xing/coe_my/cipdir' # parameter file 
    params = params_cl()  # coeio: Parameters read in from command line. You can change some parameters from command line. [-indir ./]
    indir = params.get('indir', indir)
    inweightdir = params.get('inweightdir', indir)

    #################################
    # OUTPUT DIRECTORIES
    rootdir = join(os.path.dirname(datadir), 'frontier_cat' ,field)   
    cipoutdir = join(os.path.dirname(datadir), 'frontier_cat','cipphot')
    outrootdir = rootdir
    outrootdir = params.get('outdir', outrootdir)
    indetdir = params.get('indetdir', join(outrootdir, 'images'))
    imcopydir = join(outrootdir, 'images')  # save the untar files 

    #################################
    # IMAGES
    rmsstr = '_sci_weight'
    rmsstr = params.get('rmsstr',rmsstr)
    searchwhtstr = '*_weight.fits*'       # 
    searchwhtstr = params.get('searchwhtstr',searchwhtstr)
    searchrmsstr = '*_RMS.fits.gz'
    searchrmsstr = params.get('searchrmsstr',searchrmsstr)
    keywords = loadlist('keywordkeepers.txt', dir=cipdir)       #cipcat: read each line
    searchstr = '*_sci.fits*'  # amk  notice here
    searchstr = params.get('searchstr',searchstr)
    drzfiles = findimages(searchstr, indir, imcopydir, detdate=1, keeptotal=1) # copy all .gz
    whtfiles = findimages(searchwhtstr, inweightdir, imcopydir, keeptotal=1)    
    tempdrzfiles = findimages(searchstr, indir, None, detdate=1)  #cipcat get datestr
    rmsfiles = findimages(searchrmsstr, inweightdir, imcopydir, keeptotal=1)    
    if len(rmsfiles)!=len(whtfiles) or len(whtfiles)!=len(drzfiles):
        print rmsfiles
        print whtfiles
        print drzfiles
        print 'Something Wrong! The length of rms wht drz do not match'
        print
        pdb.set_trace()

    # counts/s or counts
    bunit    = pyfits.open(drzfiles[-1], memmap=1)[0].header.get('BUNIT').strip()  #  added  by xingxing
    if (bunit[-2:] == '/S'):
            print 'in units of Counts/s'
            countspersec = 1
    else:
            countspersec = 0  
    countstr = 'yes' if countspersec ==1 else 'no'
 

    #################################
    # CHECK IF drz IMAGE FILES ARE NEWER THAN MOST RECENT CATALOG
    # does not work here by xingxing
    if '-IR' in sys.argv:
        detcam = 'IR'
    elif '-ACS' in sys.argv:
        detcam = 'ACS'
    elif '-RED' in sys.argv:
        detcam = 'RED'
    else:  # ACS+IR default
        detcam = 'ACSIR'
    drztime = oldest(drzfiles)  # cipcat
    catdirfile = join(cipoutdir, 'catdir.txt')
    catsubdir = 'cat_' + detcam
    catdir = join(outrootdir, catsubdir)
    if '-REDg' in  sys.argv:
        detcam = 'RED'
        catsubdir = 'cat_REDg' 
        catdir = join(outrootdir, catsubdir)



    redocat = ('-redo' in sys.argv) or ('-redocat' in sys.argv)
    todaystr = datetime.date.today().strftime('%y%m%d')  # e.g., 110806
    catdir = join(outrootdir, catsubdir, todaystr)   # './output/cat_ACSIR/140128'
    
    makedirsmode(catdir)
    if '-nosex' in sys.argv:
        prevcatdir = join(outrootdir, catsubdir, catdatestr)
        run('ln -s ../%s/sex %s' % (catdatestr, catdir))

    thisdir = cipdir  # for compatibility with some portions of code

    # print to check 
    print 
    print 'Check the files and dirs here! You can change the program to revise! [ print tempdrzfiles ]'
    print 
    print  'Counts/s         :  '+countstr
    print 
    print 'indir              : '+indir
    print 'inweightdir     : '+inweightdir
    print 'indetdir          : '+indetdir
    print 'outrootdir       : '+outrootdir
    print 'searchstr        : '+searchstr
    print 'rmsstr            : '+rmsstr
    print 'searchwhtstr   : '+searchwhtstr
    print 'imcopydir       : '+imcopydir
    print 'cipdir             : '+cipdir
    print 'cipoutdir        : '+cipoutdir
    print 
    print 
    summary()  #cipcat: check
    print


    #################################
    # IMAGES cont.
    # by xingxing different kind of detection image
    detfiles = {}
    detrmsfiles = {}
    detwhtfiles = {}
    segfiles = {}
    #if 'IR' not in detfiles.keys() and detcam=='IR':
    if detcam=='IR':
        print 'Creating IR detection image'
        #outdrz = imroot + '_wfc3ir_total_drz' + imext
        #detfiles['IR'] = join(imcopydir,outdrz)
        #rmsfile = outdrz.replace('drz', 'rms') # by xingxing
        #rmsfile = redir(rmsfile, rmsdir)
        #detrmsfiles['IR'] = join(rmsdir,rmsfile)
        #outwht = outdrz.replace('_drz', '_wht')
        #outdir = imcopydir
        #outdrz = join(outdir,outdrz)
        #outwht = join(outdir,outwht)
        #detwhtfiles['IR'] = outwht
        #makedetectionimage(['wfc3ir'], outdrz, outwht,drzstr = drzstr, whtstr = whtstr)        
        detfiles['IR'] = findimages('detection_nir.fits*', indir, imcopydir, keeptotal=1)[0]   
        detrmsfiles['IR']  = findimages('detection_nir_wht.fits*', indir, imcopydir, keeptotal=1)[0]   
        detwhtfiles['IR']  = findimages('detection_nir_wht.fits*', indir, imcopydir, keeptotal=1)[0]  

    if detcam=='RED':
        print 'Creating RED detection image'
        detfiles['RED'] = findimages('detection_red.fits*', indir, imcopydir, keeptotal=1)[0]   
        detrmsfiles['RED']  = findimages('detection_red_wht.fits*', indir, imcopydir, keeptotal=1)[0]   
        if '-REDg' in sys.argv:  detfiles['RED'] = findimages('gdetection_red.fits', imcopydir, imcopydir, keeptotal=1)[0]   
        try:
          detwhtfiles['RED']  = findimages('detection_red_wht.fits*', indir, imcopydir, keeptotal=1)[0]  
          segfiles['RED'] = findimages('detection_red_SEGM.fits*', indir, imcopydir, keeptotal=1)[0]  
        except Exception:
          print
          print 'No Seg or Det'
          pass
    print
    pdb.set_trace()



#    global sexcmds, sexcats
#    global drzfiles, lams, filts, FILTS, fullfilts, exptimes, nexposures
#    global imdatestr
#    global drzfile, whtfile, datatot, weightsum, totexptime
     # print to check 
    print 
    print 'Check the files and dirs here! You can change the program to revise! '
    print 'detrmsfiles         : '
    print detrmsfiles
    print 'drzfiles               : '
    print drzfiles
    print 'detfiles               : '
    print detfiles
    print 'whtfiles               : '
    print whtfiles
    print 'rmsfiles               : '
    print rmsfiles
    print 
    print 



    #################################
    # SEXTRACTOR SETUP & RUN
    print 'Sending catalog output to',catdir
    sexdir = join(catdir, 'sex')

    if '-nosex' not in sys.argv:
        print 'SExtractor setup & run'

        if not exists(sexdir):
            makedirsmode(sexdir)

        os.chdir(sexdir)
        sexsetup()   #cipcat: global sexcmds, sexcats

        #redosex = None
        redosex = params.get('redosex', None)
        for i in range(len(sexcmds)):
            sexcmd = sexcmds[i]
            sexcat = sexcats[i]
            print
            print sexcmd
            print '...to produce', join(os.getcwd(), sexcat)
            print
            if exists(sexcat):
                if redosex == None:
                    line = sexcat + ' EXISTS.  '
                    print line,
                    line = 'Would you like to rerun SExtractor on this image and all other images? (y/n) '
                    redosex = ask(line)  # coetools
                    #redosex = False
                if not redosex:
                    continue
            #print 'Okay, really now, about to produce', join(os.getcwd(), sexcat)
            #pause()
            ###############################################################################
            os.system(sexcmd)
            ###############################################################################
        #os.system('./sexcmds')
        #sexcmds = loadfile("sexcmds")
        #for sexcmd in sexcmds:
        #    print sexcmd
        #    os.system(sexcmd)

    #################################
    # PHOTOMETRY
    eBV = 0.01140  # for a2744
    eBV = params.get('eBV',eBV)    
    print 'Do you want to use eBV  = '+str(eBV)
    print 'You can use -eBV to set the eBV value. OR install the dust_getval.'
    print
    pause()
    
    photfile = join(catdir, 'photometry.cat')
    if not exists(photfile) or redocat or ('-rerun' in sys.argv):
        doapcor = 'apcor' in params.keys()
        apertype = params.get('aper', 'iso')
        print 'PHOTOMETRY: combining into multiband catalog'
        #print os.getcwd()
        #print catdir
        #print exists('photometry.cat'), ('-redocat' in sys.argv), ('-rerun' in sys.argv)
        #quit()
        filter_centers = loaddict0('filtercenters.dat', dir=thisdir, numconv=1)

        pruneCRs = ('-IR' not in sys.argv) and ('-noprune' not in sys.argv)

        outfile = cipphot.cipphot(drzfiles, filts, filter_centers, nexposures, catdir, sexdir, indetdir, cipdir, field, datestr, pixelscale=0.065, forcesec=False, forcetot=False, doapcor=doapcor, eBV=eBV, apertype=apertype, pruneCRs=pruneCRs, detcam=detcam)   # by xingxing  do not use extinction correction eBV = None

        #if exists('photometry.cat'):
        if exists(photfile):
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
    
    if not exists( cipoutdir):
         makedirsmode(cipoutdir)
    catdirfile = join(cipoutdir, 'catdir.txt')
    writefile(catdirfile, catdir)
    chmod1(catdirfile, 0664)
    print "Congratulations! Xingxing!"
    #fout = open(catdirfile, 'w')
    #fout.write(catdir+'\n')
    #fout.close()

# python ~/CLASH/pipeline/catamk/cipcat.py a383 20110324 65mas gen
