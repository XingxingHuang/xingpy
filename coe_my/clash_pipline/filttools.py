import string
try:
    import pyfits
except:
    print 'Could not import pyfits.'

allfilts = 'f225w f275w f336w f390w f435w f475w f555w f606w f625w f775w f814w f850lp f105w f110w f125w f140w f160w'.split()

def getlamname(filt):
    return int(filt[1:4])

def getlam(filt):
    lam = getlamname(filt)
    if lam < 200:
        lam = 10 * lam
    return lam

def getinstr(filt):
    lam = getlamname(filt)
    if lam < 200:
        instr = 'ir'
    elif lam < 400:
        instr = 'uvis'
    else:
        instr = 'acs'
    return instr

def getinstr2(filt):
    lam = getlam(filt)
    if lam < 200:
        instr = 'wfc3ir'
    elif lam < 400:
        instr = 'wfc3uvis'
    else:
        instr = 'acswfc'
    return instr

fullinstrdict = {
    'acs': 'HST_ACS_WFC',
    'ir':  'HST_WFC3_IR',
    'uvis':'HST_WFC3_UVIS',
    }

def getfullinstr(filt):
    return fullinstrdict[getinstr(filt)]

def getfullfilt(filt):
    instr = getinstr(filt)
    fullinstr = fullinstrdict[instr]
    FILT = filt.upper()
    fullfilt = fullinstr + '_' + FILT
    return fullfilt

def extractfilt(name):
    words = name.split('_')
    for word in words:
        if word[0] == 'f':
            good = True
            for i in 1,2,3:
                good = good and (word[i] in string.digits)
            if good:
                return word

def extractlam(name):
    filt = extractfilt(name)
    lam = getlam(filt)
    return lam

def extractfilter(header):
    """Extracts filter from a FITS header"""
    filt = header.get('FILTER', None)
    if filt == None:
        filt1 = header.get('FILTER1', None)
        if filt1[:5] == 'CLEAR':
            filt2 = header.get('FILTER2', None)
            filt = filt2
        else:
            filt = filt1
    return filt

# Approximate HST PSF FWHM for use in SExtractor stellarity determinations
#UVIS ~ 0.07" - 0.08"
#ACS: ~ 0.10"
#IR:  ~ 0.13" - 0.15"
#http://www.stsci.edu/hst/wfc3/documents/handbooks/currentIHB/c06_uvis07.html#391844
#http://www.stsci.edu/hst/wfc3/documents/handbooks/currentIHB/c07_ir07.html#401685
def getseeing(instr):
    if instr == 'uvis':
        fwhm = 0.075
    elif instr == 'acs':
        #fwhm = 0.105
        fwhm = 0.10
    elif instr == 'ir':
        #fwhm = 0.125
        fwhm = 0.14
    else:
        print instr, 'NOT FOUND IN filttools.getseeing'
        quit()
    return fwhm

def getseeing2(instr):
    if instr == 'wfc3uvis':
        fwhm = 0.075
    elif instr == 'acswfc':
        #fwhm = 0.105
        fwhm = 0.10
    elif instr == 'wfc3ir':
        #fwhm = 0.125
        fwhm = 0.14
    else:
        print instr, 'NOT FOUND IN filttools.getseeing'
        quit()
    return fwhm

# 1) drex          images [electrons]:     g = 1
# 2) MosaicDrizzle images [electrons/sec]: g = EXPTIME
# 3) other         images [DN/sec]:        g = EXPTIME * CCDGAIN
# - 2 yields slightly higher uncertainties than 3 (a few millimag)
def getgain(image, persecond=True, DN=False):
    hdulist = pyfits.open(image, memmap=1)
    header = hdulist[0].header
    ccdgain = header['CCDGAIN']
    exptime = header['EXPTIME']
    if persecond:
        gain = exptime
    else:
        gain = 1
    if DN:
        gain = gain * exptime
    print image, ccdgain, exptime, gain
    return gain

def getcrvul(filt, nexposures):
    instr = getinstr(filt)
    if instr in ('acs', 'uvis'):
        if nexposures[filt] < 4:
            return 1
        else:
            return 0.5
        #if filt not in crsafe:
            #return True
    
    return False
