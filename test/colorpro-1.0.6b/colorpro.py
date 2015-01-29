## Automatically adapted for numpy Jun 08, 2006 by convertcoords.py
## MANUALLY: B -> b

#############################################
#                 ColorPro                  #
# PSF-corrected Aperture-Matched Photometry #
#                                           #
#                by Dan Coe                 #
#############################################


from coetools import *
from pyraf.iraf import imcopy, imrename, imdelete, imexpr, psfmatch, wcsmap, geotran, wcscopy
from pyraf import iraf
iraf.set(stdgraph='stgkern')
iraf.stdgraph.device="xgterm"
from shiftWCS import shiftWCS
from sexseg import sexseg
from photcat import photcat
from wregstamp import wregstamp
from zeropadfits import zeropadfits
import popen2  # Read SExtractor output
from sppatchnew import sppatchnew
from sex2xy import sex2xy
from cat2sky import cat2sky
from prunecols import prunecols
from convertcoords import convertcoords
import string  # LOAD THIS AFTER numpy, BECAUSE numpy HAS ITS OWN string
import sys, os
# from catlabels import formats, descriptions   # DONE BELOW

colorpropath = os.environ['COLORPRO']
if colorpropath[:-1] <> '/':
    colorpropath += '/'

colorproin = 'colorpro.in'  # DEFAULT
if len(sys.argv) > 1:
    if sys.argv[1][0] <> '-':
        colorproin = sys.argv[1]

params = params_cl()  # COMMAND LINE OPTIONS: -checkalign

def getinput(category, keepstrings=0, returntext=0):
    """RETURNS DICTIONARY OF KEYS AND VALUES IN colorpro.in
    UNDER THE HEADER GIVEN BY category (e.g., IMAGES)
    keepstrings: VALUES RETURNED AS STRINGS EVEN IF THEY'RE NUMBERS
    returntext: FORGET THE DICTIONARY, JUST RETURN ALL THE LINES OF TEXT"""
    global keys, values
    txt = loadfile(colorproin, silent=1)
    d = {}
    keys = []
    iline = 0
    outlines = []
    for iline in range(iline+1, len(txt)):
        if strbegin(txt[iline], '# ' + category):
            break
    if strbegin(txt[iline], '# ' + category):  # ELSE, WASN'T FOUND, RETURN EMPTY d
        for iline in range(iline+1, len(txt)):
            line = txt[iline]
            if strbegin(line, '#####'):
                break
            if strbegin(line, '#'):
                continue
            line = string.strip(line)
            outlines.append(line)
            if line:
                words = string.split(line)
                haskey = 0
                if len(words) >= 2:
                    if not strbegin(words[1], '#'):
                        haskey = 1
                if haskey:
                    key, value = words[:2]
                    if not keepstrings:
                        value = str2num(value)
                    d[key] = value
                else:
                    key = words[0]
                    d[key] = ''
                keys.append(key)
    if returntext:
        d = outlines
    return d

# MAKE LINKS, BASED ON NICKNAMES
# IF NO NICKNAME PROVIDED, THEN NONE ASSIGNED
#   THAT IS, A LINE WITH JUST 'b' MEANS WE HAVE AN IMAGE b.fits
names = getinput('IMAGES')
filts = keys[:]

for name in keys:
    source = capfile(names[name], 'fits')
    nickname = capfile(name, 'fits')
    if source <> nickname:
        if not os.path.exists(nickname):
            os.system('ln -s %s %s' % (source, nickname))

names = getinput('RMS IMAGES')
rmsfilts = keys[:]

for name in keys:
    source = capfile(names[name], 'fits')
    nickname = capfile(name+'_rms', 'fits')
    if source <> nickname:
        if not os.path.exists(nickname):
            os.system('ln -s %s %s' % (source, nickname))

names = getinput('WEIGHT IMAGES')
weightfilts = keys[:]

for name in keys:
    source = capfile(names[name], 'fits')
    nickname = capfile(name+'_weight', 'fits')
    rmsname = capfile(name+'_rms', 'fits')
    if source <> nickname:
        if not os.path.exists(nickname):
            os.system('ln -s %s %s' % (source, nickname))
        if not os.path.exists(rmsname):
            os.system('ln -s %s %s' % (nickname, rmsname)) # WEIRD THING FOR SExSeg


# INPUT THE MAIN DETECTION IMAGE & PHOTOMETRY FRAME

lines = getinput('DETECTION IMAGES', returntext=1)
photframe2 = ''
for iline in range(len(lines)):
    line = lines[iline]
    words = stringsplitstrip(line)
    if words:
        detfilt = words[0]
        photframe = detfilt  # DEFAULT
        photframe2 = detfilt  # IN CASE IT CHANGES NEXT:
        if iline < len(lines)-2:
            if strbegin(lines[iline+1], '---'):
                words = stringsplitstrip(lines[iline+2])
                photframe = words[0]
        break

names = getinput('PHOTOMETRY FRAME')
if names:
    photframe = keys[0]

print 'PHOTOMETRY FRAME: ', photframe
        
#################################
# ALIGN IMAGES

def checkinstall(prog):
    delfile('tmp.out')
    print 'which %s > tmp.out' % prog
    os.system('which %s > tmp.out' % prog)
    txt = loadfile('tmp.out')
    delfile('tmp.out')
    return len(txt)
    #return string.find(txt[0], 'Command not found') == -1

def runmatch(fileA, fileB, matchrad=5, dx=0, dy=0):
    # CHECK FOR match INSTALLATION
    if not checkinstall('match'):
        print 'PLEASE DOWNLOAD match FROM http://spiff.rit.edu/match,'
        print 'INSTALL, THEN RERUN ColorPro'
        sys.exit(1)

    # RUN match
    delfile('match.out')
    cmd = 'match %s 1 2 3 %s 1 2 3 id1=0 id2=0 identity scale=1 matchrad=%d xsh=%.2f ysh=%.2f > match.out' % (fileA, fileB, matchrad, dx, dy)
    print cmd
    os.system(cmd)
    os.system('cat match.out')
    
    # LOAD RESULTS FROM match
    txt = loadfile('match.out')
    words = string.split(txt[0])
    
    match = {}
    for word in words:
        if string.find(word, '=') > -1:
            l, r = string.split(word, '=')
            match[l] = string.atof(r)
            
    dx = match['a']
    dy = match['d']
    xscale = match['b']
    yscale = match['f']
    print 'OFFSET: (%.1f, %.1f)' % (dx, dy)
    print 'SCALE:  (%.5f, %.5f)' % (xscale, yscale)
    print 'ROTATION:  (%.5f, %.5f)' % (match['c'], match['e'])

    return match


if 'checkalign' in params:
    # FIRST CHECK THAT WCS HEADERS GET ALIGNMENT RIGHT!
    # REQUIRES match PROGRAM
    print 'NOW CHECKING THAT WCS HEADERS GET ALIGNMENT RIGHT'
    print 'BRIGHT OBJECTS WILL BE DETECTED IN EACH IMAGE AND ALIGNED BASED ON THE WCS HEADERS'
    print 'ColorPro WILL ATTEMPT TO CORRECT ANY MISALIGNMENT BEFORE THE IMAGES THEMSELVES ARE ACTUALLY ALIGNED'

    # RUN SExtractor, DETECT BRIGHT OBJECTS
    for filt in filts:
        outcat = filt + 'bright.cat'
        delfileifempty(outcat)
        if not os.path.exists(outcat):
            if not os.path.exists(filt+'bright.sex'):
                sexdict = loadsexdict(colorpropath+'bright.sex')
                sexdict['PARAMETERS_NAME'] = colorpropath+'bright.param'
                sexdict['CATALOG_NAME'] = outcat
                if filt in weightfilts:
                    sexdict['WEIGHT_TYPE'] = 'MAP_WEIGHT'
                    sexdict['WEIGHT_IMAGE'] = filt+'_weight.fits'
                elif filt in rmsfilts:
                    sexdict['WEIGHT_TYPE'] = 'MAP_RMS'
                    sexdict['WEIGHT_IMAGE'] = filt+'_rms.fits'
                savesexdict(sexdict, filt+'bright.sex')

            cmd = 'sex %s.fits -c %sbright.sex' % (filt, filt)

    ##         cmd = 'sex %s.fits' % filt
    ##         cmd += ' -c %sbright.sex' % colorpropath
    ##         cmd += ' -PARAMETERS_NAME %sbright.param' % colorpropath
    ##         cmd += ' -CATALOG_NAME ' + outcat
    ##         if filt in weightfilts:
    ##             cmd += ' -WEIGHT_TYPE MAP_WEIGHT  -WEIGHT_IMAGE %s_weight.fits' % filt
    ##         elif filt in rmsfilts:
    ##             cmd += ' -WEIGHT_TYPE MAP_RMS     -WEIGHT_IMAGE %s_rms.fits' % filt
            print cmd
            os.system(cmd)

    # photframe .xy
    photcatb = photframe+'bright.cat'  # "photcat" is a procedure
    photxy = photframe+'brightpurged.xy'
    photwcs = photframe+'brightpurged.wcs'
    if not os.path.exists(photxy):
        sex2xy(photcatb, photxy, purge=1)

    # REMAP photframe's OBJECTS TO EACH OTHER FILTER
    # CORRECT ALIGNMENT AS NECESSARY
    for filt in filts:
        if filt <> photframe:
            if not os.path.exists(filt+'s.fits'):
                # CONVERT photframe COORDS TO THIS FILTER'S FRAME
                phot2filt = '%s2%sbright' % (photframe, filt)
                delfile(photwcs)
                convertcoords(photframe, photxy, filt, phot2filt+'.xy')

                # filt .ixym
                exec(loadsexcat(filt+'bright.cat', ma1name=''))  # purge YES
                data = array([id, x, y, mag])
                savedata(data, filt+'bright.ixym+')

                # photframe .ixym
                exec(loadsexcat(photframe+'bright.cat', purge=0, ma1name=''))  # WOULD BE NICE TO PURGE, BUT 2A WASN'T
                x, y = loaddata(phot2filt+'.xy+')
                #print len(id), len(x), len(y), len(mag)
                data1 = array([id, x, y, mag])
                exec(loadsexcat(photcatb, ma1name=''))
                id = array(id)
                data = takeids(data1, id)
                savedata(data, phot2filt+'.ixym+')

                # RUN match (A COUPLE TIMES TO GET IT RIGHT
                phot2filtixym = phot2filt+'.ixym'
                filtixym = filt+'bright.ixym'

                match = runmatch(phot2filtixym, filtixym, matchrad=30)
                match = runmatch(phot2filtixym, filtixym, dx=match['a'], dy=match['d'])
                match = runmatch(phot2filtixym, filtixym, dx=match['a'], dy=match['d'])

                dx = match['a']
                dy = match['d']
                xscale = match['b']
                yscale = match['f']

                if (abs(xscale - 1) > 0.01) or (abs(yscale - 1) > 0.01) or (abs(match['c']) > 0.01) or (abs(match['e']) > 0.01):
                    print
                    print "WARNING!"
                    print "THIS TRANSFORMATION COULD BE MORE COMPLICATED THAN A SIMPLE x,y OFFSET!"
                    print "ALL I CAN DO IS CORRECT FOR THE OFFSET"
                    print "IF IT DOESN'T DO A GOOD ENOUGH JOB, PLEASE CONSIDER CORRECTING THE WCS HEADER YOURSELF"

                # SHIFT THE WCS HEADER OF THIS FILTER
                shiftWCS(filt, filt+'s', dx=dx, dy=dy)

    pause('WCS ALIGNMENT CHECK COMPLETE')
    pause('NEXT WILL ALIGN IMAGES')
    pause('Press <Enter> to continue...')

#########

print 'NOW ALIGNING IMAGES TO THE PHOTOMETRY FRAME, AS NECESSARY'
print 'IRAF WINDOWS SHOULD POP UP' # SHOWING THE ALIGNMENT'
print 'JUST KEEP HITTING q TO CONTINUE...'

###
# FIRST, THERE MAY BE IMAGES THAT THE USER INSISTS ARE ALIGNED:
getinput('ALIGNED')
alignedforsure = keys[:]
#print 'ALIGNED', alignedforsure
#pause()


def aligned(dbname):
    db = loaddict(dbname, silent=1)
    good = 1
    good = good * (abs(db['xshift']) < 0.5)
    good = good * (abs(db['yshift']) < 0.5)
    good = good * (abs(db['xmag'] - 1) < 1e-4)
    good = good * (abs(db['ymag'] - 1) < 1e-4)
    good = good * ((abs(db['xrotation']) < 0.01) or (abs(db['xrotation'] - 360) < 0.01))
    good = good * ((abs(db['yrotation']) < 0.01) or (abs(db['yrotation'] - 360) < 0.01)) 
    return good

# NOTE, THIS FUNCTION NO LONGER NEEDED
def inAframe(filt):
    if filt == photframe:
        good = True
    else:
        good = aligned(filt+'2A.db')
    return good

mapped2Afilts = []
for name in filts:
    if name <> photframe:
        if name in alignedforsure:
            print "YOU SAY %s IS ALIGNED TO %s.  I'LL TRUST YOU." % (name, photframe)
            continue
        dbname = name+'2A.db'
        if not os.path.exists(dbname):
            wcsmap(name, photframe, dbname, interactive='no')
        if aligned(dbname):
            print 'IMAGE %s IS ALREADY ALIGNED TO THE PHOTOMETRY FRAME (IMAGE %s)' % (name, photframe)
        else:
            mapped2Afilts.append(name)
            if not os.path.exists(name+'2A.fits'):
                print 'IMAGE %s WILL NOW BE REMAPPED AND ALIGNED TO THE PHOTOMETRY FRAME (IMAGE %s)' % (name, photframe)
                geotran(name, name+'2A', dbname, name, boundary='constant', interp='spline3')
            else:
                print 'IMAGE %s HAS ALREADY BEEN REMAPPED AND ALIGNED TO THE PHOTOMETRY FRAME (IMAGE %s)' % (name, photframe)
            if name in rmsfilts: #os.path.exists(name+'_rms.fits'):
                if not os.path.exists(name+'2A_rms.fits'):
                    geotran(name+'_rms', name+'2A_rms', dbname, name, boundary='constant', interp='spline3')
            elif name in weightfilts:  # os.path.exists(name+'_weight.fits'):
                if not os.path.exists(name+'2A_weight.fits'):
                    geotran(name+'_weight', name+'2A_weight', dbname, name, boundary='constant', interp='spline3')
                    print 'ln -s %s2A_weight.fits %s2A_rms.fits' % (name, name)
                    os.system('ln -s %s2A_weight.fits %s2A_rms.fits' % (name, name))  # WEIRD THING NEEDED FOR SExSeg

print '...IMAGE ALIGNMENT COMPLETE'


#################################
# CREATE DETECTION IMAGE FROM RECIPE IN colorpro.in

#names = getinput('DETECTION IMAGES')
#detfilt = keys[0]
# imexpr('b / 1.128 + v / 2.182 + i / 2.252 + z / 1.644', 'det', b='b', v='v', i='i', z='z')
# imexpr('b / 1.128 + v / 2.182 + i / 2.252 + z / 1.644', 'det_weight', b='b_weight', v='v_weight', i='i_weight', z='z_weight')
lines = getinput('DETECTION IMAGES', returntext=1)
detfilt = ''
detfilt1 = ''
detfilts = []
detfiltsexes = {} # .sex FILE USED FOR THIS DETECTION IMAGE
detfiltfilts = {} # FILTERS USED TO CREATE THIS IMAGE
exprs = []
for iline in range(len(lines)):
    line = lines[iline]
    line = string.strip(line)
    if line:
        if not detfilt:
            words = string.split(line)
            detfilt = words[0]
            detfilts.append(detfilt)
            if len(words) == 2:  # det  det_bviz1.sex
                detfiltsexes[detfilt] = words[1]
            exprs = []
            if not detfilt1:
                detfilt1 = detfilt[:]
        elif not strbegin(line, '---'):
            exprs.append(line)
    if (not line) or (iline == len(lines) - 1):
        if exprs and detfilt:
            for suffix in ['', '_rms', '_weight']:
                exprstr = string.join(exprs, ' + ')
                s = "imexpr("
                s += "'%s'" % exprstr
                s += ", '%s%s'" % (detfilt, suffix)
                filtsindet = []
                for expr in exprs:
                    filt = string.split(expr)[0]
                    filtsindet.append(filt)
                    s += ", %s='%s%s'" % (filt, filt, suffix)  # b='b' OR b='b_weight'
                s += ')'
                filename = detfilt[:]
                allthere = 1  # ALL filts HAVE WEIGHT IMAGE
                if suffix:
                    filename += suffix
                    ss = 'suffixfilts = %sfilts' % suffix[1:]  # = weightfilts
                    exec(ss)
                    for filt in filtsindet:
                        if filt not in suffixfilts:
                            allthere = 0
                if not os.path.exists(capfile(filename, 'fits')) and allthere:
                    print s
                    exec(s)
                if not suffix:
                    detfiltfilts[detfilt] = filtsindet # SAVE FOR LATER
            if os.path.exists(detfilt+'_weight.fits') and not os.path.exists(detfilt+'_rms.fits'):
                os.system('ln -s %s_weight.fits %s_rms.fits' % (detfilt, detfilt)) # WEIRD THING FOR SExSeg
        detfilt = ''

# NOTE I ALREADY READ IN detfilt WAY EARLIER (BEFORE THE IMAGE ALIGNMENT),
#  BUT I UNDID THAT IN THIS LOOP HERE, SO I REDO IT:
detfilt = detfilt1[:]  # FIRST DETECTION IMAGE IS THE ONE!

#################################
# SHOULD WE RUN SExSeg OR STRAIGHT SExtractor?

#straightsex = 0  # RUN SExSeg UNLESS...
reasons = []
if len(detfilts) > 1:
    reasons.append('Multiple detections requested.')
if detfilt in mapped2Afilts:
    reasons.append('Detection image is not in Photometry frame.')
if getinput('SEGMENTATION'):
    reasons.append('External segmentation map to be used.')


print
print '*' * 77

if reasons:
    straightsex = 0
    print 'SExSeg WILL NEED TO BE RUN (INSTEAD OF STRAIGHT SExtractor)'
    print ' FOR THE FOLLOWING REASONS:'
    for reason in reasons:
        print reason
else:
    straightsex = 1
    print 'SExSeg WILL NOT BE REQUIRED FOR THIS PHOTOMETRIC ANALYSIS'
    print 'SExtractor WILL BE RUN WITHOUT IT'

print '*' * 77
print
#pause()

#################################
# CREATE SEGMENTATION MAPS, AS NEEDED

if not straightsex:
    for filt in detfilts:
        if filt in detfiltsexes.keys():
            outsegm = filt+'segm.fits'
            outcat  = filt+'_detection.cat'
            if not os.path.exists(outsegm):
                looksgood = 0
                while not looksgood:
                    sexfile = detfiltsexes[filt]
                    outsexfile = sexfile[:-4] + '_final.sex'
                    detfiltsexes[filt] = sexfile  # (not that this variable is ever used again...)
                    sexc = loadsexdict(sexfile)
                    # VALUES RETURNED AS STRINGS/NUMBERS
                    # NOW: WANT TO MAKE SURE WE RETURN A SEGMENTATION IMAGE
                    # (AND CONTROL ITS NAME, ALONG WITH THAT OF THE OUTPUT IMAGE)
                    # BUT I WANT TO CONTINUE TO ALLOW THE USER TO PRODUCE ANY OTHER
                    #  CHECKIMAGES THEY WANT
                    if 'CHECKIMAGE_TYPE' in sexc.keys():
                        #segmname = ''
                        checkimagetypes = stringsplitstrip(sexc['CHECKIMAGE_TYPE'], ',')
                        checkimagenames = stringsplitstrip(sexc['CHECKIMAGE_NAME'], ',')
                        for ic in range(len(checkimagetypes)):
                            checkimagetype = checkimagetypes[ic]
                            if string.strip(checkimagetype) == 'SEGMENTATION':
                                checkimagenames[ic] = outsegm
                        checkimagetype = string.join(checkimagetypes, ',') # NO SPACES ALLOWED
                        checkimagename = string.join(checkimagenames, ',') #   ON COMMAND LINE
                    else:
                        checkimagetype = 'SEGMENTATION'
                        checkimagename = outsegm
                    sexc['CHECKIMAGE_TYPE'] = checkimagetype
                    sexc['CHECKIMAGE_NAME'] = checkimagename
                    sexc['CATALOG_NAME'] = outcat
                    savesexdict(sexc, outsexfile)
                    cmd = 'sex %s.fits -c %s' % (filt, outsexfile)
                    #cmd += ' -CHECKIMAGE_TYPE ' + checkimagetype
                    #cmd += ' -CHECKIMAGE_NAME ' + checkimagename
                    #cmd += ' -CATALOG_NAME ' + outcat
                    print cmd
                    os.system(cmd)
                    print 'Take a minute to look at the output segmentation map (%s) and catalog (%s).' % (outsegm, outcat)
                    looksgood = getanswer('Are you satisfied with the results? (y/n) ')
                    if not looksgood:
                        delfile(outsegm)
                        delfile(outcat)
                        pause('Edit the parameters in %s,\n and press Enter when ready to run SExtractor again.' % sexfile)


#################################
# COMBINE SEGMENTATION MAPS

#$p/sppatchnew.py STisegm STzsegm STizsegm +11000
#sppatchnew(origfile, newfile, outfile, newstartid='', frac=1.5, reportonly=0):

# READ IN AND CLEAN UP
lines1 = getinput('SEGMENTATION', returntext=1)
lines = []
for line in lines1:
    if line:
        if not strbegin(line, '#'):
            lines.append(line)

# 4 INPUT OPTIONS:
# BLANK -> ('segm' DEFAULT)
# SEGMNAME / NICKNAME
# SEGMNAME / NICKNAME, FOLLOWED BY '---' THEN COMBINATION
# COMBINATION -> ('segm' DEFAULT)

segmname = 'segm'  # DEFAULT
if lines:
    if len(lines) == 1:
        lines.append('---')
    if lines[1] == '---':  # (OR IF THERE WAS ONLY WAS LINE)
        words = stringsplitstrip(lines[0])
        segmname = decapfile(words[0], 'fits')
        if len(words) == 2:  # NICKNAME PROVIDED
            source = capfile(words[1], 'fits')
            nickname = capfile(segmname, 'fits')
            if source <> nickname:
                if not os.path.exists(nickname):
                    os.system('ln -s %s %s' % (source, nickname))
        # FOR LATER, I TRIM TO THE LIST OF IMAGES THAT MAKE UP THE SEGMENTATION MAP (IF APPLICABLE)
        lines = lines[2:]
# SPECIAL CASE: ONE DETECTION IMAGE CREATED, AND NO FURTHER INSTRUCTIONS GIVEN
# THEN THAT MUST BE OUR SEGMENTATION MAP!
elif len(detfilts) == 1:
    if not straightsex:
        os.system('ln -s %ssegm.fits segm.fits' % detfilts[0])

if not os.path.exists(segmname+'.fits'):
    segmnames = []
    for iline in range(len(lines)):
        line = lines[iline]
        words = stringsplitstrip(line)
        newsegm = words[0]
        segmnames.append(newsegm)
        segmdetfilt = words[1]
        if segmdetfilt in detfilts:
            segmdetfilt = detfiltfilts[segmdetfilt][0]
        if segmdetfilt in mapped2Afilts:
            #print 'ALIGNING SEGMENTATION MAP %s TO THE PHOTOMETRY FRAME' % (newsegm+'segm')
            #print 'IRAF WINDOWS SHOULD POP UP SHOWING THE ALIGNMENT'
            #print 'JUST KEEP HITTING q TO CONTINUE...'
            if not os.path.exists(newsegm+'2Asegm.fits'):
                geotran(newsegm+'segm', newsegm+'2Asegm', segmdetfilt+'2A.db', segmdetfilt, boundary='constant', interp='nearest', fluxconserve='no')
            newsegm += '2A'
            # wregister det_jh_sexsegm det det_jh2A_sexsegm boundary=constant interp=nearest nxblock=2000 nyblock=2000 interactive- fluxconserve-
        if iline: # AFTER FIRST LINE, ADD OTHERS
            newstartid = words[2]
            #print segmnames
            oldsegm = string.join(segmnames[:-1], '') + 'segm'
            newsegm += 'segm'
            sumsegm = string.join(segmnames, '') + 'segm'
            #print oldsegm, newsegm, sumsegm, newstartid
            if not os.path.exists(sumsegm+'.fits'):
                if len(words) == 4:
                    frac = num2str(words[3])
                    #print frac
                    sppatchnew(oldsegm, newsegm, sumsegm, newstartid=newstartid, frac=frac)
                else:
                    sppatchnew(oldsegm, newsegm, sumsegm, newstartid=newstartid)

    finalsegm = string.join(segmnames, '') + 'segm'
    if finalsegm <> 'segm':
        os.rename(finalsegm+'.fits', segmname+'.fits')
        os.system('ln -s %s.fits %s.fits' % (segmname, finalsegm)) # LINK BACK, IN CASE YOU CARE
        os.rename(finalsegm+'.spl', segmname+'.spl')
        os.system('ln -s %s.spl %s.spl' % (segmname, finalsegm)) # LINK BACK, IN CASE YOU CARE
        #os.system('ln -s %s.fits segm.fits' % finalsegm)
##         if os.path.exists('segm.fits'):
##             if os.realpath('segm.fits') <> os.realpath(finalsegm+'.fits'):
##                 print 'YOU ALREADY HAVE A segm.fits'

#################################
# SELECT STARS, DETERMINE PSFs (OF EACH IMAGE, INCL. PHOTFRAME)

allpsfsequal = None
# PREDEFINED PSF IMAGES
names = getinput('PSF')

if 'FWHM' in keys:
    allpsfsequal = float(names['FWHM'])  # in arcsec!

# OR IF IT WAS DEFINED ON THE COMMAND LINE:
if 'psffwhm' in params:
    allpsfsequal = float(params['psffwhm'])  # in arcsec!

if allpsfsequal:
    print
    print "YOU SAY THAT THE PSFs OF ALL IMAGES ARE EQUAL."
    print 'AND THAT THEY HAVE A FWHM = %.3f"' % allpsfsequal
    print

for name in keys:
    if allpsfsequal:
        break
    source = capfile(names[name], 'fits')
    nickname = capfile(name+'psf', 'fits')
    if source <> nickname:
        if not os.path.exists(nickname):
            os.system('ln -s %s %s' % (source, nickname))

#################################
# DETERMINE WHICH IMAGES ARE BLURRY AND WHICH AREN'T !!

# IF DETECTION IMAGE HAD TO BE CREATED,
#  RETURN IT NOW TO ITS RIGHTFUL PLACE AS photframe
if photframe2:
    photframe = photframe2
    print 'Now that the detection image has been made, we reassign:'
    print 'PHOTOMETRY FRAME: ', photframe

# MISSING PSFs: EQUAL TO DETECTION IMAGE??
for filt in filts:
    if allpsfsequal:
        break
    if not os.path.exists(filt+'psf.fits'):
        if filt in mapped2Afilts:
            if not os.path.exists(filt+'2Apsf.fits'):
                print filt+'psf.fits NOT FOUND.  (NOR WAS '+filt+'2Apsf.fits)'
                print "DEFINE THE PSF FOR IMAGE %s, AND THEN GET BACK TO ME" % filt
                sys.exit()
        else:
            print
            print filt+'psf.fits NOT FOUND'
            if filt == photframe:
                print "DEFINE THE PSF FOR IMAGE %s, AND THEN GET BACK TO ME" % photframe
                sys.exit()
            else:
                delfile(filt+'psf.fits', silent=1) # IN CASE WE HAVE A BROKEN LINK
                print "SHOULD WE ASSUME THE PSF FOR IMAGE %s IS THE SAME AS FOR %s? (y/n)" % (filt, photframe)
                if getanswer():
                    os.system('ln -s %spsf.fits %spsf.fits' % (photframe, filt))
                else:
                    print "DEFINE THE PSF FOR IMAGE %s, AND THEN GET BACK TO ME" % filt
                    sys.exit()


# REMAP PSFs AS NEEDED
for filt in mapped2Afilts:
    if allpsfsequal:
        break
    if not os.path.exists(filt+'2Apsf.fits'):
        wregstamp(filt, filt+'psf', photframe, filt+'2Apsf')
        # inwcs, instamp, outwcs, outstamp

# RUN SExtractor ON PSF IMAGES TO SEE HOW WIDE THEY ARE
filts2 = filts[:]
filts2.insert(0, photframe)
blurryfilts = []

configdict = getinput('CONFIGURATION')
pixelscale = configdict.get('PIXEL_SCALE', loadpixelscale(photframe))
#print 'PIXEL SCALE = %.3f' % pixelscale

if not allpsfsequal:
    print
    print "DETERMINING PSF FWHMs USING SExtractor..."
fwhmdict = {} # arcsec (")
fout = open('psffwhms.txt', 'w')
for ifilt in range(len(filts2)):
    filt = filts2[ifilt]
    if filt in filts2[:ifilt]:
        continue  # DON'T DO THE PHOTOMETRY FRAME TWICE
    filt2 = filt
    if filt in mapped2Afilts:
        filt2 += '2A'
    if allpsfsequal:
        fwhm = allpsfsequal / pixelscale
    else:  # GET PSF FWHM FROM SExtractor
        cmd = 'sex %spsf.fits -c %spsf.sex -PARAMETERS_NAME %spsf.param' % (filt2, colorpropath, colorpropath)
        #cmd += ' > sex.txt'
        delfile('psf.cat', silent=1) # IF SEx HAS AN ERROR, DON'T WANT TO RE-READ THIS!
        #os.system(cmd)
        subproc = popen2.Popen4(cmd)
        sexout = subproc.fromchild.readlines()  # SExtractor output
        # (IN THIS CASE I JUST WANT TO SWALLOW IT, SO IT DOESN'T GET PRINTED TO THE SCREEN)
        if not os.path.exists('psf.cat'):
            print
            print 'SExtractor CRASHED TRYING TO CALCULATE PSF OF %s!' % filt2
            print
            print cmd
            for sexline in sexout:  # in case there's an error
                print sexline
            sys.exit()
        cat = loadsexcat2('psf.cat', purge=0, silent=1)
        #print 'WARNING: psf2.cat'
        cat.sort('mag')
        fwhm = cat.fwhm[0]
        #pause()
    #print string.rjust(filt2, 10), ' %5.2f pix =' % cat.fwhm[0], '%.3f"' % (cat.fwhm[0] * pixelscale)
    line = '%s  %5.2f pix = %.3f"' % (string.rjust(filt2, 10), fwhm, fwhm * pixelscale)
    print line
    fout.write(line+'\n')
    fwhmdict[filt] = fwhm * pixelscale # arcsec (")
    if ifilt == 0:
        photframefwhm = fwhm
    else:
        if fwhm / photframefwhm > 1.1:
            blurryfilts.append(filt)

fout.close()
print 'SAVED AS psffwhms.txt'
print
delfile('psf.cat', silent=1)
print 'Blurry Filters:', blurryfilts

#################################
# CALCULATE DEGRADING KERNELS (ONE PSF TO OTHER)
# NOTE THAT THEY COME OUT NORMALIZED

for filt in blurryfilts:
    if filt in mapped2Afilts:
        filt += '2A'
    outker = 'ker%sto%s' % (photframe, filt)
    if not os.path.exists(outker+'.fits'):
        zeropadfits(photframe+'psf', filt+'psf', photframe+'psf0')
        psfmatch(photframe+'psf0', filt+'psf', photframe+'psf0', outker, convolution='psf', background='none')
        imdelete(photframe+'psf0')

#################################
# DEGRADE ACS IMAGES TO MATCH BLURRY IMAGES

for name in blurryfilts:
    if name in mapped2Afilts:
        suffix2A = '2A'
    else:
        suffix2A = ''
    kernelname = 'ker%sto%s%s' % (photframe, name, suffix2A)
    outname = '%sto%s%s' % (photframe, name, suffix2A)
    if not os.path.exists(outname+'.fits'):
        psfmatch(photframe, 'shwag', 'shwag', kernelname, convolution='kernel', output=outname)

#################################
# PHOTOMETRY!
# RUN SExSeg! (OR STRAIGHT SExtractor)

def extractsexseg():
    """EXTRACTS THE SExSeg PARAMETERS FROM colorpro.in
       CREATING A FILE common.sexseg"""
    txt = loadfile(colorproin, silent=1)
    fout = open('common.sexseg', 'w')
    copyon = 0
    for line in txt:
        if strbegin(line, '# '):
            if strbegin(line, '# CONFIGURATION'):
                fout.write('# ----- CONFIGURATION -----\n')
                copyon = 1
            elif strbegin(line, '# PARAMETERS'):
                fout.write('\n# ----- PARAMETERS -----\n')
                copyon = 1
            else:
                copyon = 0
        elif line and not strbegin(line, '#####'):
            if copyon:
                fout.write(line+'\n')
    fout.close()

if not straightsex:
    extractsexseg()

zpstrdict = getinput('ZEROPOINTS', keepstrings=1)
getinput('BACKGROUND')
backpresub = keys[:]

satdict = getinput('SATURATION', keepstrings=1)
gaindict = getinput('GAIN', keepstrings=1)

def sexsegsetup(image, filt='', degraded=0):
    print 'PREPARING', image+'.sexseg'
    if not filt:
        filt = image
    sexc = loadsexsegconfig(colorpropath+'default.sexseg')
    sexc.merge('common.sexseg')
    
    sexc.config['CATALOG_NAME'] = image+'_sexseg.cat'
    if (filt not in filts) and (filt in detfilts):
        sexc.config['MAG_ZEROPOINT'] = '30'
    else:
        sexc.config['MAG_ZEROPOINT'] = zpstrdict[filt]
    if degraded:  # RMS IMAGE WILL BE CONSTRUCTED FROM SCRATCH
        sexc.config['WEIGHT_TYPE'] = 'NONE, MAP_RMS'
        sexc.config['WEIGHT_IMAGE'] = image+'_rms.fits'
    else:
        if filt in rmsfilts:
            sexc.config['WEIGHT_TYPE'] = 'NONE, MAP_RMS'
            sexc.config['WEIGHT_IMAGE'] = image+'_rms.fits'
        elif filt in weightfilts:
            sexc.config['WEIGHT_TYPE'] = 'NONE, MAP_WEIGHT'
            sexc.config['WEIGHT_IMAGE'] = image+'_weight.fits'

    sexc.config['PIXEL_SCALE'] = '%.3f' % pixelscale
    sexc.config['SEEING_FWHM'] = '%.3f' % fwhmdict[filt]
    sat = satdict.get(filt, '')
    if sat:
        sexc.config['SATUR_LEVEL'] = sat

    gain = gaindict.get(filt, '')
    if gain:
        sexc.config['GAIN'] = gain
        #sexc['GAIN'] = gain  Alberto changed it to this?
        
    sexc.save(image+'.sexseg')


def sexsetup(image, filt='', degraded=0):
    print 'PREPARING', image+'.sex'
    if not filt:
        filt = image
    sexfile = detfiltsexes[detfilt]
    sexc = loadsexdict(sexfile)
    sexc['CATALOG_NAME'] = image + '_sex.cat'
    sat = satdict.get(filt, '')
    if sat:
        sexc['SATUR_LEVEL'] = sat
    gain = gaindict.get(filt, '')
    if gain:
        sexc.config['GAIN'] = gain
    if (filt not in filts) and (filt in detfilts):
        sexc['MAG_ZEROPOINT'] = '30'
    else:
        sexc['MAG_ZEROPOINT'] = zpstrdict[filt]
    if 'WEIGHT_IMAGE' in sexc.keys():
        detweightimage = string.split(sexc['WEIGHT_IMAGE'], ',')[0]
        detweighttype  = string.split(sexc['WEIGHT_TYPE'],  ',')[0]
    else:
        detweightimage = 'det_weight.fits'
        detweighttype  = 'NONE'
    if degraded:  # RMS IMAGE WILL BE CONSTRUCTED FROM SCRATCH
        sexc['WEIGHT_TYPE']  = detweighttype
        sexc['WEIGHT_IMAGE'] = detweightimage
    else:
        if filt in rmsfilts:
            sexc['WEIGHT_TYPE'] = '%s, MAP_RMS' % detweighttype
            sexc['WEIGHT_IMAGE'] = '%s, %s_rms.fits' % (detweightimage, image)
        elif filt in weightfilts:
            sexc['WEIGHT_TYPE'] = '%s, MAP_WEIGHT' % detweighttype
            sexc['WEIGHT_IMAGE'] = '%s, %s_weight.fits' % (detweightimage, image)

    sexc['SEEING_FWHM'] = '%.3f' % fwhmdict[filt]

    savesexdict(sexc, image+'.sex')


if straightsex:
    # STRAIGHT SEX
    for filt in filts2:
        if filt not in mapped2Afilts:
            image = filt
        else:
            image = filt+'2A'

        sexcat = image+'_sex.cat'
        finalcat = image+'.cat'
        delfileifempty(finalcat)
        if not os.path.exists(finalcat):
            sexsetup(image, filt)
            if filt == detfilt:
                cmd = 'sex %s.fits -c %s.sex' % (image, image)
            else:
                cmd = 'sex %s.fits %s.fits -c %s.sex' % (detfilt, image, image)
            print cmd
            os.system(cmd)

            cat = loadsexcat2(sexcat, purge=0, silent=1, magname="MAG_ISO")
            cat.save(finalcat)

        if filt == detfilt:
            if not os.path.exists('census.dat'):
                if 'area' in cat.labels:
                    cat.labels = ['id', 'area']
                    cat.save('census.dat')

        # HANDLE DEGRADED IMAGE (photframe DEGRADED TO filt)
        if filt in blurryfilts:
            image = '%sto%s' % (photframe, image)
            sexcat = image+'_sex.cat'
            finalcat = image+'.cat'
            delfileifempty(finalcat)
            if not os.path.exists(finalcat):
                sexsetup(image, photframe, degraded=1)
                cmd = 'sex %s.fits %s.fits -c %s.sex' % (detfilt, image, image)
                print cmd
                os.system(cmd)
                cat = loadsexcat2(sexcat, purge=0, silent=1, magname="MAG_ISO")
                cat.save(finalcat)

else:
    # SExSeg
    for filt in filts2:
        options = []
        if filt not in rmsfilts:
            if filt in weightfilts:
                options.append('weightback') # NO LONGER SUPPORTED BY SExSeg!
        if (filt in backpresub):  # or (filt in detfilts): 
            options.append('nobacksub') # WHY WAS I DOING THIS?: DON'T SUBTRACT FROM DETECTION IMAGE

        if filt not in mapped2Afilts:
            image = filt
            finalcat = image+'_sexseg.cat'
            if not os.path.exists(finalcat):
                sexsegsetup(image)
                cmd = 'sexseg %s %s %s -C %s.sexseg' % (photframe, segmname, image, image)
                if 'weightback' in options:
                    pass # cmd += ' -weightback'
                if 'nobacksub' in options:
                    cmd += ' -nobacksub'
                print cmd
                sexseg(photframe, segmname, image, image+'.sexseg', finalcat, options)
        else:
            image = filt+'2A'
            finalcat = image+'_sexseg.cat'
            if not os.path.exists(finalcat):
                sexsegsetup(image, filt)
                cmd = 'sexseg %s %s %s -C %s.sexseg' % (photframe, segmname, image, image)
                if 'nobacksub' in options:
                    cmd += ' -nobacksub'
                print cmd
                sexseg(photframe, segmname, image, image+'.sexseg', finalcat, options)


        if not os.path.exists(image+'.cat'):
            os.system('ln -s %s %s' % (finalcat, image+'.cat'))

        # HANDLE DEGRADED IMAGE (photframe DEGRADED TO filt)
        if filt in blurryfilts:
            image = '%sto%s' % (photframe, image)
            finalcat = image+'_sexseg.cat'
            if not os.path.exists(finalcat):
                sexsegsetup(image, photframe, degraded=1)
                cmd = 'sexseg %s %s %s -C %s.sexseg' % (photframe, segmname, image, image)
                print cmd
                sexseg(photframe, segmname, image, image+'.sexseg', finalcat, ['nobacksub'])
                # DON'T SUBTRACT FROM DEGRADED VERSION OF DETECTION IMAGE EITHER (BE CONSISTENT)

        if not os.path.exists(image+'.cat'):
            os.system('ln -s %s %s' % (finalcat, image+'.cat'))



#################################
# WCS CATALOG

if not os.path.exists(photframe+'.wcs'):
    if loadpixelscale(photframe):  # ELSE NO WCS IN HEADER
	photframe+'.cat'
	delfile(photframe+'.wcs')  # THE FILE TO BE CREATED:
	cat2sky(photframe, photframe+'.cat', '-d -n 8')
	prunecols(photframe+'.wcs', [1, 2], photframe+'.wcs')


#################################
# COMPILE PHOTOMETRY: APPLY SEGMENTATION

zpdict = getinput('ZEROPOINTS')
extdict = getinput('EXTINCTION')

# A DETECTION IMAGE CREATED AS A SUM OF OTHER IMAGES
#  CAN BE ASSIGNED AN ARBITRARY ZEROPOINT
if photframe not in filts:
    zpdict[photframe] = 30
    extdict[photframe] = 0

## OUTPUT FILE NAME...
# DEFAULT
outroot = decapfile(colorproin)
colorproout = outroot+'.cat'

# OR FROM colorproin
outdict = getinput('OUTPUT')
if outdict:
    colorproout = keys[0]

# OR FROM THE COMMAND LINE, THIS TRUMPS EVERYTHING
if len(sys.argv) > 2:
    if sys.argv[2][0] <> '-':
        colorproout = sys.argv[2]

#colorproout = recapfile(colorproout, 'cat')
#outroot = decapfile(colorproout)
outroot = decapfile(colorproout)
colorproout = outroot+'.cat'  # ALSO SEE ABOVE, NOW THIS NAME IS BEING REDONE BASED ON INPUT
bpzout = outroot+'_bpz.cat'
colorprobpzout = outroot+'_photbpz.cat'

# NOW, PRODUCE THE FINAL ColorPro CATALOG:
if os.path.exists(colorproout):
    print 'FINAL ColorPro CATALOG ALREADY EXISTS:', colorproout
else:
    photcat(filts, photframe, mapped2Afilts, blurryfilts, zpdict, extdict, colorproout)


#################################
# BPZ!

filtnames = getinput('FILTERS')
if not filtnames:
    sys.exit()
    # USER DIDN'T PUT BPZ SETUP IN colorproin,
    # SO WE FIGURE THEY DIDN'T WANT TO RUN BPZ

#################################
# BPZ COLUMNS FILE

if not os.path.exists(outroot+'.columns'):
    maxlen = len('# Filter')
    for filtname in filtnames.values():
        if len(filtname) > maxlen:
            maxlen = len(filtname)


    catheader = loadheader(colorproout)
    catlabels = string.split(catheader[-1][1:])

    vegafilts = getinput('VEGA')

    zperror = getinput('ZEROPOINT UNCERTAINTIES')

    priorfilt = getinput('PRIOR')
    if priorfilt:
        priorfilt = priorfilt.keys()[0]
    else:
        print 'NO FILTER SET FOR BPZ PRIOR'
        print 'FILTER WILL BE SELECTED BASED ON MOST DETECTIONS'
        cat = loadcat(colorproout)
        maxndet = 0
        print 'FILTERS AND # DETECTIONS:'
        for filt in filts:
            ndet = total(between(-99, cat.get(filt), 99))
            print filt, ndet
            if ndet > maxndet:
                maxndet = ndet
                priorfilt = filt

    print
    print 'THUS, BPZ WILL GET ITS PRIOR MAGNITUDES FROM THE %s FILTER' % priorfilt

    print
    print 'BUILDING %s.columns' % outroot
    print
    fout = open(outroot+'.columns', 'w')

    line = string.ljust('# Filter', maxlen+2)
    line += 'columns  AB/Vega  zp_error  zp_offset\n'
    fout.write(line)
    print line[:-1]

    for filt in filts:
        # FILTER
        line = string.ljust(filtnames[filt], maxlen+3)
        # MAG
        magcol = catlabels.index(filt)+1
        dmagcol = catlabels.index('d'+filt)+1
        line += '%2d,%2d   ' % (magcol, dmagcol)
        # AB / Vega
        if filt in vegafilts:
            line += 'Vega      '
        else:
            line += 'AB        '
        # ZP UNCERTAINTY
        zperrorstr = '%.4f' % zperror.get(filt, 0.01)
        while zperrorstr[-1] == '0':  # TRIM TRAILING ZEROS
            zperrorstr = zperrorstr[:-1]
        zperrorstr = string.ljust(zperrorstr, 10)
        line += zperrorstr
        # ZP OFFSET
        line += '0.0\n'
        fout.write(line)
        print line[:-1]


    line = string.ljust('M_0', maxlen+3)
    line += '%2d\n' % (catlabels.index(priorfilt)+1)
    fout.write(line)
    print line[:-1]

    line = string.ljust('ID', maxlen+3)
    line += '%2d\n' % (catlabels.index('id')+1)
    fout.write(line)
    print line[:-1]

    fout.close()
    print


#################################
# RUN BPZ!

if os.path.exists(outroot+'.bpz'):
    print 'FINAL BPZ CATALOG ALREADY EXISTS:', outroot+'.bpz'
    #sys.exit()

else:

    print
    if not ask('CONTINUE NOW AND RUN BPZ? (y/n)'):
        print 'OKAY, BYE.'
        print 'YOU CAN RERUN ColorPro ANY TIME TO RUN BPZ'
        sys.exit()

    bpzoptions = getinput('BPZ OPTIONS')

    cmd = 'python %s/bpz.py' % os.environ['BPZPATH']
    cmd += ' %s' % colorproout
    cmd += ' -COLUMNS %s.columns' % outroot

    if 'PROBS_LITE' in keys:
        if not bpzoptions['PROBS_LITE']:
            bpzoptions['PROBS_LITE'] = outroot+'.probs'

    for key in keys:
        cmd += ' -%s %s' % (key, bpzoptions[key])

    print cmd
    os.system(cmd)  # RUN BPZ!


if os.path.exists(outroot+'.bpz') and not os.path.exists(bpzout):
    #################################
    # FINALIZE THE CATALOG...
    cmd = 'python %s/bpzfinalize.py' % os.environ['BPZPATH']
    cmd += ' '+outroot

    print cmd
    os.system(cmd)


#################################
# FINAL PHOTOMETRY + BPZ CATALOG
photcat = loadcat(colorproout)
bpzcat = loadcat(bpzout)

photcat.merge(bpzcat)
allcat = photcat
allcat.labels.remove('M0')

from catlabels import formats, descriptions

format = formats
allcat.descriptions = descriptions

#filtnames['det'] = 'Detection Image ' + string.join(detfiltfilts[detfilt])

for filt in filts:
    format[filt] = format['mag']
    format['d'+filt] = format['dmag']
    descriptions[filt] = filtnames[filt] + ' ' + descriptions['mag']
    descriptions['d'+filt] = descriptions['dmag'] + ' ' + filt
    
header = ['# ColorPro + BPZ catalog\n#\n']

print 'FINAL ColorPro + BPZ catalog:'
allcat.save(colorprobpzout, header=header, format=format)
