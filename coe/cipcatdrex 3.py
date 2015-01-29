############################################
# CLASH Image Pipeline
# Final multiband photometry from drex image pipeline
# -Dan Coe
#
# SExtractor catalogs from drex
# Aperture corrections and dust extinction applied
# The former are derived from encircled energy tables
# Zeropoints are re-read in from images
############################################

# Run as follows:
# python /data01/cipphot/pipeline/cipcatdrex.py <field> <epoch> <datestr>
#
# Example:
# python /data01/cipphot/pipeline/cipcatdrex.py a2261 v8 110612
# python ~/CLASH/pipeline/catalog/photometry.py a2261 v8 110612
# will read in images from:
#   /data01/drex_runs/datasets/a2261/
# and create output here:
#   /data01/cipphot/a383/mosdriz/20110426/scale_065_science/
#
# These directories can be overridden with the options:
# -indir my_indir -- imports images from my_dir
# -inweightdir my_weight_dir -- imports weight images from my_weight_dir
# -outdir my_outdir -- writes output to (subdirectories in) my_outdir

###
# See also:
# ~/CLASH/pipeline/cipphot/cipcat.py
#
# Previous versions:
# ~/CLASH/pipeline/catalog/photometry.py
# ~/CLASH/data/a383/wei/v3/110101/catalog/photometry.py
# ~/CLASH/data/a383/wei/v3/101228/catalog/photometry.py
# ~/CLASH/data/A383/wei/v2/catalog/photometry.py
# ~/CLASH/data/m1149/wei/v1/catalog/photometry.py
# ~/CLASH/data/A383/wei/v1/catalog/2/photometry.py
# ~/CLASH/data/A383/wei/v1/catalog/2/bpzcat.py -- final photometry + BPZ catalg
# ~/CLASH/data/A383/wei/v1/catalog/2/crprune.py  -- deals mostly with multicolor.cat
# ~/CLASH/data/A383/amk/5/catalog/exttest.py -- calculate extinctions from dust map

# (~/CLASH/data/M1149/wei/v1/images/output)% ln m1149_v1_f475w_acs_065mas_sci_20101207.fits detectionImage.fits

from coeio import *
from glob import glob
from filttools import *
#from bpz_tools import filter_center

#datestr = '101231'
field = sys.argv[1]  # a383
epoch = sys.argv[2]  # v5
datestr = sys.argv[3]  # 110120

#indir = '~/CLASH/data/a383/wei/v3/%s/drex/' % datestr
#indir = '~/CLASH/data/a383/wei/%s/drex/' % epoch
#indir = '~/CLASH/data/a383/wei/%s/%s/drex/' % (epoch, datestr)
#indir = '~/CLASH/data/%s/wei/%s/%s/drex/' % (field, epoch, datestr)

import socket
def onclashdms1():
    hostname = socket.gethostname()
    return (len(hostname) >= 9) and (hostname[:9] == 'clashdms1')

if onclashdms1():
    inrootdir = '/data01/drex_runs/datasets/%s/' % field
    indir = join(inrootdir, 'Catalogs')
    imdir = join(inrootdir, 'Images')
    cipdir = '/data01/cipphot'
    thisdir = join(cipdir, 'pipeline')
    outrootdir = cipdir
    outrootdir = join(outrootdir, field)
    outrootdir = join(outrootdir, 'drex')
    outrootdir = join(outrootdir, epoch)
    outrootdir = join(outrootdir, datestr)
    outdir = outrootdir
    if not exists(outdir):
        os.makedirs(outdir)
    dustdir = '/data01/cipphot/pipeline/dustmaps/'
else:
    indir = '~/CLASH/data/%s/wei/%s/%s/Catalogs/' % (field, epoch, datestr)
    imdir = '~/CLASH/data/%s/wei/%s/%s/images/' % (field, epoch, datestr)
    outdir = indir
    thisdir = '~/CLASH/pipeline/catalog/'  # extfiltfact.dict
    dustdir = '~/CLASH/pipeline/apsis/reffiles/maps'

# Override with parameter inputs from command line, if any:
# For example:
# > python cipcatdrex.py ... -indir my_dir
params = params_cl()  # Parameters read in from command line
indir = params.get('indir', indir)
imdir = params.get('imdir', imdir)
inweightdir = params.get('inweightdir', indir)
outrootdir = params.get('outdir', outrootdir)

if indir[:2] == '~/':
    indir = join(home, indir[2:])
if imdir[:2] == '~/':
    imdir = join(home, imdir[2:])

fieldv = field + '_' + epoch
#inroot = fieldv + '_'
inroot = field + '_'  # for catalogs

print 'Input image directory:'
print imdir
print
print 'Input catalog directory:'
print indir
print
print 'Output directory:'
print outdir
print

#indir  = '~/CLASH/data/a383/wei/v2/drex'  # output catalogs
#inroot = 'a383_v2_'
#fieldv = inroot[:-1]

#imdir  = '~/CLASH/data/m1149/wei/v1/images/output'  # images
#imdir = indir
datestr1 = '20' + datestr
#fitsext = 'sci%s.fits' % datestr1
#fitsext = 'sci_%s.fits' % datestr1
#fitsext = 'sci_%s.fits' % datestr
#fitsext = '_sci.fits*'   # may be gzipped -- picks up .fits_1.cat, etc.
fitsext = '_sci.fits'
#fitsext = 'sci.fits'
#datestr1 = '20101209'
#datestr2 = '2010-12-09'
datestr2 = datestr1[:4] + '-' + datestr1[4:6] + '-' + datestr1[6:8]

#eBV = 0.03119
eBV = None  # calculate below

# ACS filters which are safe from cosmic rays
#crsafe = string.split('f555w f814w')  # macs1149
#crsafe = string.split('f850lp')  # macs1149

# Check below: cr = only 1 CR filter detection or only all CR filter detections

#indir  = '~/CLASH/data/A383/wei/v1/catalog'  # output catalogs
#indirsex = '~/CLASH/data/A383/wei/v1/sex'      # SExtractor parameter files


#################################
# Load in a few things from the detection image
detcat = loadsexcat0('detectionImage.cat', dir=indir)

pixelscale = 0.065  # arcsec / pix

allcat = VarsClass()
allcat.add('id',   detcat.NUMBER, '%5d', 'Object ID Number')
allcat.add('RA',   detcat.ALPHA_J2000, '%11.7f', 'Right Ascension in decimal degrees')
allcat.add('Dec',  detcat.DELTA_J2000, '% 11.7f', 'Declination in decimal degrees')
allcat.add('x',    detcat.X_IMAGE, '%8.3f', 'x pixel coordinate')
allcat.add('y',    detcat.Y_IMAGE, '%8.3f', 'y pixel coordinate')
#allcat.add('fwhm', detcat.FWHM_IMAGE, '%7.3f', 'Full width half maximum (pixels)')
#allcat.add('fwhm_arcsec', detcat.FWHM_WORLD, '%7.3f', 'Full width half maximum (arcsec)')
fwhm = detcat.FWHM_IMAGE * pixelscale
allcat.add('fwhm', fwhm, '%7.3f', 'Full width at half maximum (arcsec)')
allcat.add('area', detcat.ISOAREA_IMAGE, '%5d', 'Isophotal aperture area (pixels)')
allcat.add('stel', detcat.CLASS_STAR,  '%4.2f', 'SExtractor "stellarity" (1 = star; 0 = galaxy)')
allcat.add('ell',  detcat.ELLIPTICITY, '%5.3f', 'Ellipticity = 1 - B/A')

# flagcat = detcat.greater('FLAGS', 0)
# The only flags present are as follows (these would all be filter specific):
# 1 - bright neighbors
# 2 - was deblended
# 4 - saturated (or nearly)


#################################
# Zeropoints

import HSTzp

def extractfilt(name):
    words = string.split(name, '_')
    for word in words:
        if word[0] == 'f':
            good = True
            for i in 1,2,3:
                good = good and (word[i] in string.digits)
            if good:
                return word


zpdict = {}

searchstr = join(imdir, '*'+fitsext)
files = glob(searchstr)

searchstr2 = join(imdir, '*'+fitsext+'.gz')
files2 = glob(searchstr2)

files[len(files):] = files2

print searchstr
print searchstr2
print
if len(files) == 0:
    print 'NO FILES FOUND.'
    quit()
else:
    for file in files:
        print file

print

zpoutfile = join(outdir, 'zp.dict')
#zpoutfile = 'zp.dict'
if exists(zpoutfile):
    print "Loading zeropoints from file:"
    zpdict = loaddict(zpoutfile)
else:
    print 'Determining zeropoints:'
    fout = open(zpoutfile, 'w')

    fout.write('# Zeropoint (AB mag) for each filter (galactic extinction not included)\n')

    for file in files:
        #print file
        zp = HSTzp.HSTzp(file)
        file = os.path.basename(file)
        filt = extractfilt(file)
        print filt, zp
        fout.write(filt.ljust(8))
        fout.write(' %8.5f\n' % zp)
        zpdict[filt] = zp

    fout.close()

#################################

def getlamname(filt):
    return int(filt[1:4])

def getlam1(filt):
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

def getcrvul(filt):
    instr = getinstr(filt)
    if instr <> 'ir':
        #if filt not in crsafe:
        if nexposures[filt] < 4:
            return True
    return False

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

# Adapted from Txitxo's bpz_tools.py:
def filter_center(filt,ccd='yes'):
    """Estimates the central wavelength of the filter"""
    filt = capfile(filt, 'res')
    xr, yr = loaddata(filt)
    if ccd=='yes':
        yr=yr*xr
    return trapz(yr*xr,xr)/trapz(yr,xr)

print 'Determining filters and number of exposures for each image.'
print '(UVIS/ACS filters with < 4 exposures are vulnerable to cosmic rays.)'
filts = []
FILTS = []
fullfilts = []
lams = []
nexposures = {}
for file in files:
    if 0:
        filt = extractfilt(file)
        filts.append(filt)
        FILTS.append(filt.upper())
        lam = getlam(filt)
        lams.append(lam)
        #nexposures[filt] = 4

    header = pyfits.open(file, memmap=1)[0].header
    #FILT = header['FILTER']
    FILT = extractfilter(header)
    filt = FILT.lower()
    FILTS.append(FILT)
    filts.append(filt)
    fullfilt = ''
    for key in 'TELESCOP INSTRUME DETECTOR'.split():
        fullfilt += header[key] + '_'
    
    #fullfilt = fullfilt[:-1]
    fullfilt += FILT
    
    fullfilts.append(fullfilt)
    #lam = filter_center(fullfilt) / 10.
    lam = getlam(filt)
    lams.append(lam)
    nexp = header['NCOMBINE']
    nexposures[filt] = nexp
    print fullfilt, lam, nexp
    #print fullfilt.ljust(19), '%7.1f' % filter_center(fullfilt)

#filts = map(string.lower, FILTS)

fullinstrdict = {
    'acs': 'HST_ACS_WFC',
    'ir':  'HST_WFC3_IR',
    'uvis':'HST_WFC3_UVIS',
    }

curdir = os.getcwd()

inext  = '_sci.cat'
inextsex  = '_sci.inpar'

if 0:
    cd(indir)
    files = glob(inroot+'*'+inext)

    filts = []
    for file in files:
        filt = strbtw(file, inroot, inext)
        filts.append(filt)

    cd(curdir)

#indir2 = '~/CLASH/data/A383/amk/5/catalog/'
#filtdict = loaddict('filters.txt', indir2)
#lamdict = loaddict('filtlam.dict', indir2)

#indirsex = '~/CLASH/data/A383/wei/v1/sex'
#zpdict = loaddict('zp.dict', indirsex)  # I believe these were calculated from the images, so no ext corr
#extdict = loaddict('extinction.dict', indir2)

#filts = filtdict.keys()

# sort filter by lambda
#lams = map(getlam, filts)
SI = argsort(lams)
filts = take(filts, SI)
lams  = take(lams, SI)
FILTS = take(FILTS, SI)
#fullfilts = take(fullfilts, SI)
files = take(files, SI)

#zpdict = {}
#for filt in filts:
#    sexfile = inroot + filt + inextsex
#    sexdict = loaddict(sexfile, dir=indirsex)
#    zpdict[filt] = sexdict['MAG_ZEROPOINT']

#################################
# Determine galactic dust extinction

os.chdir(outdir)

if not eBV:
    import pyfits
    import extinction
    if not exists('SFD_dust_4096_ngp.fits'):
        #line = 'ln -s %s/SFD_dust_4096_ngp.fits' % dustdir
        #print line
        #os.system('ln -s /data01/cipphot/pipeline/dustmaps/*_?gp.fits .' % dustdir)
        os.system('ln -s %s/*_?gp.fits .' % dustdir)
        #os.system('ln -s %s/SFD_dust_4096_ngp.fits' % dustdir)
        #os.system('ln -s %s/SFD_dust_4096_sgp.fits' % dustdir)
        #os.system('ln -s %s/SFD_mask_4096_ngp.fits' % dustdir)
        #os.system('ln -s %s/SFD_mask_4096_sgp.fits' % dustdir)
    # detectionImage = 'detectionImage.fits'
    #detectionImage = '/Users/dcoe/CLASH/data/A383/wei/v1/detection.fits'
    detectionImage = join(imdir, 'detectionImage.fits')
    #detectionImage = join(imdir, 'detectionImage_%s.fits' % datestr1)
    if not exists(detectionImage):
        print detectionImage, 'DOES NOT EXIST.'
        detectionImage = join(imdir, 'detectionImage.fits.gz')
        print 'Trying', detectionImage, '...'
        if not exists(detectionImage):
            print detectionImage, 'DOES NOT EXIST.'
            detectionImage = files[0]
            print "Instead, to determine the image coordinates and thus dust extinction,"
            print "we'll use", detectionImage
    header = pyfits.open(detectionImage, memmap=1)[0].header
    ra  = header["CRVAL1"]
    dec = header["CRVAL2"]
    
    eBV, quality = extinction.getEBV(ra,dec)
    eBV = float(eBV)

def filterFactor(filter):
    ffactors = loaddict('extfiltfact.dict', silent=1, dir=thisdir)
    for key in ffactors.keys():
        if string.find(key, filter) > -1:  # filter is in key
            return ffactors[key]

#################################

allcat.add('flag5sig', 0, '%1d', '0 = probably real; 1 = probable CR; 2 = no 5-sigma detection')
allcat.add('nf5sig',    0, '%2d', 'Number of filters with a 5-sigma detection')
allcat.add('nfcr5sig', 0, '%2d', 'Number of CR-vulnerable filters with a 5-sigma detection')
allcat.add('nfobs', 0, '%2d', 'Number of filters observed (not in chip gap, etc.)')

#################################
# FROM Txitxo's bpz_tools.py

def sex2bpzmags(f,ef,zp=0.,sn_min=1.):
    """
    This function converts a pair of flux, error flux measurements from SExtractor
    into a pair of magnitude, magnitude error which conform to BPZ input standards:
    - Nondetections are characterized as mag=99, errormag=+m_1sigma
      - corrected error in previous version: was errormag=-m_1sigma
    - Objects with absurd flux/flux error combinations or very large errors are
      characterized as mag=-99 errormag=0.
    """

    nondetected=less_equal(f,0.)*greater(ef,0) #Flux <=0, meaningful phot. error
    nonobserved=less_equal(ef,0.) #Negative errors
    #Clip the flux values to avoid overflows
    nonobserved+=greater(ef, 100*abs(f)) # the old APSIS colorCatalog.py way
    f=clip(f,1e-100,1e10)
    ef=clip(ef,1e-100,1e10)
    #nonobserved+=equal(ef,1e10)  # the new way
    nondetected+=less_equal(f/ef,sn_min) #Less than sn_min sigma detections: consider non-detections
    
    detected=logical_not(nondetected+nonobserved)

    m=zeros(len(f), float)
    em=zeros(len(ef), float)

    m = where(detected,-2.5*log10(f)+zp,m)
    m = where(nondetected,99.,m)
    m = where(nonobserved,-99.,m)

    em = where(detected,2.5*log10(1.+ef/f),em)
    #em = where(nondetected,2.5*log10(ef)-zp,em)
    em = where(nondetected,zp-2.5*log10(ef),em)
    #print "NOW WITH CORRECT SIGN FOR em"
    em = where(nonobserved,0.,em)
    return m,em

#################################
# Load in from the filter images and perform the aperture corrections

detradii = sqrt(allcat.area / pi)  # pix
radii = detradii * pixelscale  # arsec

# Clip to minimum and maximum radii: 0.1" < r < 2.0"
# The WFC3 tables only go between these radii
#radii_arcsec_clipped = clip(radii_arcsec, 0.1, 2.0)
# Do this in HSTee

import HSTee

extdict = {}

#for filt in filts:
for i in range(len(filts)):
    filt = filts[i]
    lam = lams[i]
    instr = getinstr(filt)
    FILT = string.upper(filt)
    
    if instr == 'acs':
        ee = HSTee.ACSee(filt, radii)
    elif instr == 'ir':
        #lam = lamdict[filt]
        #lam = getlam(filt)
        ee = HSTee.IRee(lam, radii)
    elif instr == 'uvis':
        #lam = lamdict[filt]
        #lam = getlam(filt)
        ee = HSTee.UVISee(lam, radii)
        
    #apcorfac = 10 ** (0.4 * apcor)  # convert back to a multiplicative factor
    #infile = 'a383_v1_%s_drz.cat' % filt
    #infile = 'a383_%s.cat' % filt
    #infile = 'a383_v1_%s_sci.cat' % filt
    infile = inroot + filt + inext
    cat = loadsexcat2(infile, purge=0, dir=indir)
    flux = cat.get('fluxiso')
    fluxerr = cat.get('fluxerriso')
    flux = flux / ee
    fluxerr = fluxerr / ee
    sig = flux / fluxerr
    # apcorfac here???  fluxerr too??
    #zp1 = zpdict[filt]
    zp = zpdict[filt]

    # ext = extdict[filt]
    #fac = extinction.filterFactor(FILT)
    fac = filterFactor(FILT)
    extmag = -fac * eBV
    extfluxfac = 10 ** (-0.4 * extmag)
    extdict[filt] = extmag
    print filt, extfluxfac, extmag
    flux    = flux    * extfluxfac
    fluxerr = fluxerr * extfluxfac
    #zp = zp1 - ext
    #zp1 = zp + ext
    
    m, dm = sex2bpzmags(flux, fluxerr, zp, sn_min=0)
    apcor = 2.5 * log10(ee)
    #m = m - apcor
    
    #zptxt = 'ZP = %6.4f = %6.4f - %6.4f extinction correction' % (zp, zp1, ext)
    zptxt = 'ZP = %6.4f' % zp
    allcat.add(filt+'_mag',    m,      '% 9.4f', FILT + ' isophotal magnitude (%s)' % zptxt)
    crvul = getcrvul(filt)
    if crvul:
        crtxt = ' (* Vulnerable to cosmic rays)'
    else:
        crtxt = ''
    print filt, crtxt
    allcat.add(filt+'_magerr', dm,     '% 8.4f', FILT + ' isophotal magnitude uncertainty' + crtxt)
    allcat.add(filt+'_apcor',  apcor,  '% 7.4f', FILT + ' aperture correction')
    allcat.add(filt+'_flux',   flux,   '% 12.4f', FILT + ' isophotal flux  (multiplied by %.3f to correct for extinction (%.3f mag))' % (extfluxfac, extmag))
    allcat.add(filt+'_fluxerr',fluxerr,'% 11.4f', FILT + ' isophotal flux uncertainty    (%.3f factor applied here as well)' % extfluxfac)
    allcat.add(filt+'_sig',    sig,    '% 8.2f', FILT + ' detection significance')

    observed = greater(m, 0)      # -99 = unobserved
    detected = between(0, m, 90)  # 99 = undetected
    sig5 = greater(sig, 5)  # 5-sigma detection or better
    allcat.nfobs = allcat.nfobs + observed
    allcat.nf5sig = allcat.nf5sig + sig5
    #if instr == 'acs':
    if crvul:
        allcat.nfcr5sig = allcat.nfcr5sig + sig5

cr = logical_and(equal(allcat.nfcr5sig, 1), equal(allcat.nf5sig, 1))  # 1 CR filter
#cr = equal(allcat.nf5sig - allcat.nfcr5sig, 0)  # only CR filters

nosig5 = equal(allcat.nf5sig, 0)
crflag = where(cr, 1, 0)
crflag = where(nosig5, 2, crflag)
allcat.flag5sig = crflag

#################################
# EXTINCTION

zpoutfile = join(outdir, 'extinction.dict')
fout = open(zpoutfile, 'w')
fout.write('# Extinction in AB magnitudes for each filter\n')
fout.write('# to be subtracted from reported magnitudes\n')
fout.write('# using value from Schlegel dust maps E(B-V) = %.5f\n' % eBV)

for filt in filts:
    ext = extdict[filt]
    fout.write(filt.ljust(8))
    fout.write(' %8.5f\n' % -ext)

fout.close()


# ZP + EXTINCTION
zpoutfile = join(outdir, 'zpext.dict')
fout = open(zpoutfile, 'w')
fout.write('# Zeropoint (AB mag) for each filter\n')
fout.write('# using value from Schlegel dust maps E(B-V) = %.5f\n' % eBV)

for filt in filts:
    zp = zpdict[filt]
    ext = extdict[filt]
    zpext = zp + ext
    fout.write(filt.ljust(8))
    fout.write(' %8.5f\n' % zpext)

fout.close()


# ZP + EXTINCTION, ALL IN ONE FILE
zpoutfile = join(outdir, 'zeropoints.txt')
fout = open(zpoutfile, 'w')
fout.write('# %s drex %s %s\n' % (field.upper(), epoch, datestr2))
fout.write('# Zeropoint (AB mag) for each filter\n')
fout.write('# with and without galactic extinction included.\n')
fout.write('# Extinctions derived using value from Schlegel dust maps:\n')
fout.write('# E(B-V) = %.5f\n' % eBV)
fout.write('#     zeropoint - extinction =\n')

for filt in filts:
    zp = zpdict[filt]
    ext = extdict[filt]
    zpext = zp + ext
    fout.write('%s  %8.5f  %7.5f  %8.5f\n' % (filt.ljust(8), zp, -ext, zpext))

fout.close()


#################################

# old header:
## 2010-11-19T09:18:29Z
## colorCatalog Catalog file for Observation: a383_v1
## This proprietary file was by the CLASH Pipeline.

# new header:
header = """
## Photometric catalog for observation %s (%s)
## Based on images produced by the CLASH drex pipeline
## Pruned by selecting flag5sig = 0 (more likely real)
##
## Position, aperture, and shape measurements determined in the detection image
## For each filter, we provide:
##  - magnitude & uncertainty
##  - aperture correction used
##  - flux & uncertainty
##  - detection significance
## Both fluxes and magnitudes have been corrected for:
##  - galactic extinction: E(B-V) = %.5f
##  - finite apertures (from encircled energy tables)
## mag, magerr =  99, 1-sigma limit: non-detection (flux < 0)
## mag, magerr = -99, 0: unobserved (outside FOV, in chip gap, etc.)
## This proprietary file was created by the CLASH Pipeline.
##
""" % (fieldv, datestr2, eBV)

# flux < 0: see sn_min above

## Both fluxes and magnitudes have been corrected for both galactic extinction and finite apertures
## mag =  99: non-detection (flux < 0)
## mag = -99, 0: unobserved (outside FOV, chip gap, etc.)

header = string.split(header[1:-1], '\n')
#print header

allcat.header = header
#print allcat.header

#################################

# Lengthen formats as necessary to allow labels to fit

#for label in allcat.labels:
if 0:
    print label, allcat.formats[label],
    fmt = allcat.formats[label]
    if 'd' in fmt:
        nstr = strbtw(fmt, '%', 'd')
    else:        
        nstr = strbtw(fmt, '%', '.')
    print nstr
    if int(nstr) < len(label):
        #fmt = fmt.replace(nstr, '%d'%len(label), 1)  # 1 at end means only replace 1st instance
        n = len(label)
        nextra = n - int(nstr)
        nl = nextra / 2
        nr = nextra - nl
        fmt = ' '*nl + fmt + ' '*nr
        allcat.formats[label] = fmt
        print 'being lengthened: |' + fmt + '|'

#################################

import catsave
catsave.catsave(allcat, 'photometry.cat', dir=outdir)

# Clean up: remove links to dust maps
os.system('\\rm SFD*gp.fits')

#allcat.save('photometry.cat', header=header)

