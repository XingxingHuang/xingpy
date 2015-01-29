from coeio import *
#import zeropoints
import catsave
from filttools import *
import datetime
import pdb

import socket
def onclashdms1():
    hostname = socket.gethostname()
    return (len(hostname) >= 9) and (hostname[:9] == 'clashdms1')

#################################
# FROM

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


def detM0(cat):
    M0 = cat.f775w_mag
    i1 = allfilts.index('f775w')

    filts = 'f814w f625w f606w'.split()
    for filt in filts:
        M1 = cat.get(filt+'_mag')
        det = between(0, M0, 90)
        M0 = where(det, M0, M1)
        
    filts = 'f850lp f105w f110w f125w f555w f475w f435w f140w f160w'.split()
    for filt in filts:
        M1 = cat.get(filt+'_mag')
        obs = greater(M0, 0)
        M0 = where(obs, M0, M1)

    return M0


def cipphot(files, filts, lamdict, nexposures, outdir, sexdir, detdir, cipdir, field, datestr, pixelscale=0.065, forcesec=True, forcetot=False, doapcor=True, eBV=None, apertype='iso', outname='', pruneCRs=True, detcam='ACS+IR'):
    #eBV = None  # calculate below
    #pixelscale = 0.065  # arcsec / pix
    #doapcor = '-noapcor' not in sys.argv

    #################################
    # Load in a few things from the detection image
    detcat = loadsexcat0('detectionImage.cat', dir=sexdir)

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
    #A = detcat.A_IMAGE * pixelscale
    #allcat.add('A', A, '%7.3f', 'major axis A (arcsec)')

    # flagcat = detcat.greater('FLAGS', 0)
    # The only flags present are as follows (these would all be filter specific):
    # 1 - bright neighbors
    # 2 - was deblended
    # 4 - saturated (or nearly)

    #zpdict = zeropoints.zeropoints(files, outdir, forcesec=forcesec, forcetot=forcetot)
    zpdict = loaddict(os.path.join(cipdir,'zeropoints.txt')) # by xingxing revised the direction
    #################################
    # Determine galactic dust extinction

    if not eBV:
        import pyfits
        import extinction
        if not exists('SFD_dust_4096_ngp.fits'):
            #if onclashdms1():
            #    dustdir = '/data01/cipphot/pipeline/dustmaps/'
            #else:
            #    dustdir = '~/CLASH/pipeline/apsis/reffiles/maps'
            dustdir = '/Users/xing/programs/bin'
            print 'Please check this if you are using another computer!!!!!'
            os.system('ln -s %s/SFD_dust_4096_ngp.fits' % dustdir)
            os.system('ln -s %s/SFD_dust_4096_sgp.fits' % dustdir)
            os.system('ln -s %s/SFD_mask_4096_ngp.fits' % dustdir)
            os.system('ln -s %s/SFD_mask_4096_sgp.fits' % dustdir)
        # detectionImage = 'detectionImage.fits'
        #detectionImage = '/Users/dcoe/CLASH/data/A383/wei/v1/detection.fits'
        #detectionImage = join(imdir, 'detectionImage.fits')
        #detectionImage = join(imdir, 'detectionImage_%s.fits' % datestr1)
        #detectionImage = join(detdir, 'detectionImage.fits')
        detectionImage = files[0]
        if 0: # not exists(detectionImage):
            print detectionImage, 'DOES NOT EXIST.'
            detectionImage = files[0]
            print "Instead, to determine the image coordinates and thus dust extinction, we'll use"
            print detectionImage
            
        print "To determine the image coordinates and thus dust extinction, we'll use"
        print detectionImage
        header = pyfits.open(detectionImage, memmap=1)[0].header
        ra  = header["CRVAL1"]
        dec = header["CRVAL2"]
        pdb.set_trace()
        eBV, quality = extinction.getEBV(ra,dec)
        eBV = float(eBV)

    def filterFactor(filter):
        ffactors = loaddict('extfiltfact.dict', silent=1, dir=cipdir)
        for key in ffactors.keys():
            if string.find(key, filter) > -1:  # filter is in key
                return ffactors[key]

    #################################

    allcat.add('flag5sig', 0, '%1d', '0 = probably real; 1 = probable CR; 2 = no 5-sigma detection')
    allcat.add('nf5sig',   0, '%2d', 'Number of filters with a 5-sigma detection')
    allcat.add('nfcr5sig', 0, '%2d', 'Number of CR-vulnerable filters with a 5-sigma detection')
    allcat.add('nfobs',    0, '%2d', 'Number of filters observed (not in chip gap, etc.)')

    #################################
    # Load in from the filter images and perform the aperture corrections

    nobj = allcat.len()
    if apertype == 'iso':
        detradii = sqrt(allcat.area / pi)  # pix
    else:
        aperdiams = 2,3,4,6,8,10,14,20,28,40,60,80,100,160
        aperi = apertype
        aperdiam = aperdiams[aperi]
        detradii = aperdiam / 2.
        detradii = detradii * ones(nobj)
        #area = pi * (aperdiam / 2.)**2

    radii = detradii * pixelscale  # arsec

    # Clip to minimum and maximum radii: 0.1" < r < 2.0"
    # The WFC3 tables only go between these radii
    #radii_arcsec_clipped = clip(radii_arcsec, 0.1, 2.0)
    # Do this in HSTee

    epoch = datestr2 = datestr
    if len(datestr) == 8:
        yyyy = datestr[:4]
        mm = datestr[4:6]
        dd = datestr[6:]
        datestr2 = '%s-%s-%s' % (yyyy, mm, dd)

    todaystr2 = datetime.date.today().strftime('%Y-%m-%d')  # e.g., 2011-08-06

    inroot = field + '_'
    fieldv = field + '_' + epoch
    inext  = '.cat'

    # ZP + EXTINCTION, ALL IN ONE FILE
    zpoutfile = join(outdir, 'zeropoints.txt')
    zpfout = open(zpoutfile, 'w')
    zpfout.write('# %s mosdriz %s %s\n' % (field.upper(), epoch, datestr2))
    zpfout.write('# Zeropoint (AB mag) for each filter\n')
    zpfout.write('# with and without galactic extinction included.\n')
    zpfout.write('# Extinctions derived using value from Schlegel dust maps:\n')
    zpfout.write('# E(B-V) = %.5f\n' % eBV)
    zpfout.write('#     zeropoint - extinction =\n')

    ##
    #for i in range(len(filts)):
    exptime = {}
    import pyfits
    for i in range(len(allfilts)):
        filt = allfilts[i]
        exptime[filt] = 0
        #lam = lams[i]
        lam = lamdict[filt] / 10.  # Angstroms -> nanometers - Fixed 10/6/11
        instr = getinstr(filt)
        FILT = string.upper(filt)

        if doapcor:     # by xingxing  aper correction  '-apcor'
            import HSTee
            #print lam, radii
            if instr == 'acs':
                ee = HSTee.ACSee(filt, radii)
            elif instr == 'ir':
                ee = HSTee.IRee(lam, radii)
            elif instr == 'uvis':
                ee = HSTee.UVISee(lam, radii)
        else:
            #ee = 1.
            ee = ones(nobj)



        # important   determine the units   Counts or Counts/s
        # add by xingxing
        found =0
        if filt in filts:
             for tmpfile in files:
                 if filt in tmpfile:
                      fileused = tmpfile
                      found =  1 
             if found ==1 :          
                bunit    = pyfits.open(fileused)[0].header.get('BUNIT').strip()  #  added  by xingxing
                countspersec = 1 if (bunit[-2:] <> '/S') else 0 
                exptime[filt] = pyfits.open(fileused)[0].header.get('EXPTIME')
        if found ==1 :
           zp = zpdict[filt]+2.5*log10(exptime[filt])
        else:
           zp = zpdict[filt]
        print 'Zeropint: '+filt+'  %i %10.2f   ' %(found, zp)
        #pdb.set_trace()
        #zp = zpdict[filt]


        
        # ext = extdict[filt]
        #fac = extinction.filterFactor(FILT)
        fac = filterFactor(FILT)
        #ext = fac * eBV
        extmag = -fac * eBV
        extfluxfac = 10 ** (-0.4 * extmag)      # by xx  add the extinction correction   fac * eBV
        print filt, extfluxfac, extmag

        if filt in filts:  # Observed
            #apcorfac = 10 ** (0.4 * apcor)  # convert back to a multiplicative factor
            #infile = 'a383_v1_%s_drz.cat' % filt
            #infile = 'a383_%s.cat' % filt
            #infile = 'a383_v1_%s_sci.cat' % filt
            infile = inroot + filt + inext
            cat = loadsexcat2(infile, purge=0, dir=sexdir)
            if apertype == 'iso':
                flux = cat.get('fluxiso')
                fluxerr = cat.get('fluxerriso')
            else:  # CIRCULAR APERTURE
                cat0 = loadsexcat0(infile, dir=sexdir)
                flux    = cat0.get('FLUX_APER_%d' % aperi)
                fluxerr = cat0.get('FLUXERR_APER_%d' % aperi)
            #print flux.shape
            #print ee.shape
            flux = flux / ee
            fluxerr = fluxerr / ee
            sig = flux / fluxerr
            # apcorfac here???  fluxerr too??
            #zp1 = zpdict[filt]

            flux    = flux    * extfluxfac
            fluxerr = fluxerr * extfluxfac
            #zp = zp1 - ext
            #zp1 = zp + ext

            m, dm = sex2bpzmags(flux, fluxerr, zp, sn_min=0)
            apcor = 2.5 * log10(ee)
            #m = m - apcor
            crvul = getcrvul(filt, nexposures)  # filttool.py  for acs uvis, when nexposures <4 crvul=1;  else crvul=0.5;  for ir, crvul=False
            if crvul == 1:
                crtxt = ' (* Vulnerable to cosmic rays)'
            elif crvul == 0.5:
                crtxt = ' (Edges vulnerable to cosmic rays)'
            else:
                crtxt = ''
        else:
            flux = nan
            fluxerr = inf
            m = -99
            dm = inf
            apcor = 0
            sig = nan
            crvul = False
            crtxt = ' (Not observed)'

        # zptxt = 'ZP = %6.4f = %6.4f - %6.4f extinction correction' % (zp, zp1, ext)
        zptxt = 'ZP = %6.4f' % zp
        allcat.add(filt+'_mag',    m,      '% 9.4f', FILT + ' isophotal magnitude (%s)' % zptxt)
        print filt, crtxt
        allcat.add(filt+'_magerr', dm,     '% 8.4f', FILT + ' isophotal magnitude uncertainty' + crtxt)
        allcat.add(filt+'_apcor',  apcor,  '% 7.4f', FILT + ' aperture correction')
        allcat.add(filt+'_flux',   flux,   '% 12.4f', FILT + ' isophotal flux  (multiplied by %.3f to correct for extinction (%.3f mag))' % (extfluxfac, extmag))
        allcat.add(filt+'_fluxerr',fluxerr,'% 11.4f', FILT + ' isophotal flux uncertainty    (%.3f factor applied here as well)' % extfluxfac)
        allcat.add(filt+'_sig',    sig,    '% 8.2f', FILT + ' detection significance')

        observed = greater(m, 0)      # -99 = unobserved
        detected = between(0, m, 90)  # 99 = undetected
        sig5 = greater(sig, 5)  # 5-sigma detection or better
        allcat.nfobs = allcat.nfobs + observed  # number of observed filters
        allcat.nf5sig = allcat.nf5sig + sig5    # number of observed filters with S/N>5
        #if instr == 'acs':
        if crvul:  # either 0.5 or 1
            allcat.nfcr5sig = allcat.nfcr5sig + sig5   # number of observed acs or uvis with S/N>5 and  nexposures <4. These filters are not observed with enough time.
        
        # Sign fixed 11/9/11:  extmag is negative
        zpextmag = zp + extmag
        zpfout.write('%s  %8.5f  %7.5f  %8.5f    %10.2f\n' % (filt.ljust(8), zp, -extmag, zpextmag, exptime[filt]))


    zpfout.close()

    # Now, cosmic rays are flagged also in UVIS/ACS images with 4+ exposures
    # (may be along edges)
    cr = logical_and(equal(allcat.nfcr5sig, 1), equal(allcat.nf5sig, 1))  # 1 CR filter  # cfcr5sig=1 and nf5sig=1
    #cr = equal(allcat.nf5sig - allcat.nfcr5sig, 0)  # only CR filters

    nosig5 = equal(allcat.nf5sig, 0)
    crflag = where(cr, 1, 0)
    allcat.flag5sig = where(nosig5, 2, crflag)   # 0: real; 1: probable CR; 2: no 5sig detection
    allcat.updatedata()

    M0 = detM0(allcat)
    allcat.add('M0', M0, '% 7.4f', 'Magnitude used for BPZ prior: F775W or closest observed filter')

    # flag5sig =
    #   2: no 5-sigma detection in any filter
    #   1: only 5-sigma detection is in ACS/UVIS
    #   0: multiple 5-sigma detections (or at least one 5-sigma IR detection)

    #################################

    if not outname:
        outroot = 'photometry'
        outname = outroot
        if apertype <> 'iso':
            outname += '_aper%d' % aperdiam
        #if not doapcor:
        #     outname += '_noapcor'
        if doapcor:
             outname += '_apcor'
        outname += '.cat'
        #refname = outroot+'.cat'

    refname = 'photometry.cat'
    
    print allcat.len(), 'objects before pruning cosmic rays and non-detection'

    if (outname <> refname) and exists(refname):
        print '(pruning as %s was pruned...)' % refname
        catref = loadcat(refname, dir=outdir)
        allcat = allcat.takeids(catref.id)
        print allcat.len(), 'objects after'
    else:
        if pruneCRs:
            # 1 or True to prune both cosmic rays and non-detections
            # 2 to prune non-detections but not cosmic rays
            allcat = allcat.less('flag5sig', pruneCRs-0.1)
            #allcat = allcat.equal('flag5sig', 0)
            print allcat.len(), 'objects after'
        
    print 'flag5sig total = ', total(allcat.flag5sig)
    if 0: #total(allcat.flag5sig) == 0:
        allcat.labels.remove('flag5sig')

    #################################

    # old header:
    ## 2010-11-19T09:18:29Z
    ## colorCatalog Catalog file for Observation: a383_v1
    ## This proprietary file was by the CLASH Pipeline.

    if apertype == 'iso':
        apertext = 'isophotal'
    else:
        apertext = '%d-pixel diameter circular' % aperdiam

## Photometric catalog (%s) for observation %s (%s)

    if detcam == 'ACSIR':
        detcam = 'ACS+IR'

    # new header:
    header = """
## Photometric catalog (produced %s) for %s (processed %s)
## Based on 0.065"/pix images produced by AMK's mosaicdrizzle
## Objects detected in a weighted sum of %s images
## Pruned by selecting flag5sig = 0 (gets rid of cosmic rays and < 5-sigma detections)
##
## Position, aperture, and shape measurements determined in the detection image
## Photometry measured in %s apertures
## For each filter, we provide:
##  - magnitude & uncertainty
##  - flux & uncertainty
##  - detection significance
##  - aperture correction used
## Both fluxes and magnitudes have been corrected for:
##  - galactic extinction: E(B-V) = %.5f
##  - finite apertures (from encircled energy tables)
## mag, magerr =  99, 1-sigma limit: non-detection (flux < 0)
## mag, magerr = -99, 0: unobserved (outside FOV, in chip gap, etc.)
## This catalog was created by the CLASH Image Pipeline
## 
""" % (todaystr2, field, datestr2, detcam, apertext, eBV)
#""" % (fieldv, datestr2, apertext, eBV)

    # flux < 0: see sn_min above

    ## Both fluxes and magnitudes have been corrected for both galactic extinction and finite apertures
    ## mag =  99: non-detection (flux < 0)
    ## mag = -99, 0: unobserved (outside FOV, chip gap, etc.)

    #header = string.split(header[1:-1], '\n')
    header = string.split(header[1:-2], '\n')
    #print header
    
    for i, line in enumerate(header):
        if not pruneCRs:
            if 'Pruned' in line:
                header[i] = '## Not pruned: a few < 5-sigma detections may remain (flagsig > 0)\n'

        if not doapcor:
            if ('aperture correction' in line) or \
                ('encircled energy' in line):
                header.remove(line)

    allcat.header = header
    #print allcat.header

    #################################

    catsave.catsave(allcat, outname, dir=outdir)

    # Clean up: remove links to dust maps
    os.system('\\rm SFD*gp.fits')

    #allcat.save('photometry.cat', header=header)

    return outname
