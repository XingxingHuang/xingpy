# $p/hstzp.py '*_drz.fits'

from numpy import *
import glob, pyfits, sys

def HSTzp(infile, forcesec=False, forcetot=False):
    """
    Zeropoint of HST image derived from FITS keywords
    http://www.stsci.edu/hst/acs/analysis/zeropoints
    http://www.stsci.edu/hst/wfc3/phot_zp_lbn
    """
    if not (infile.endswith('.fits') or infile.endswith('.fits.gz')):
        infile = infile + '.fits'
    
    f = pyfits.open(infile, memmap=1)
    header = f[0].header
    photflam = header.get('PHOTFLAM', None)  # inverse sensitivity (erg / cm^2 / s / Ang)
    photplam = header.get('PHOTPLAM', None)  # pivot wavelength
    photplam0 = 5475.4
    pzpt     = header.get('PHOTZPT')
    bunit    = header.get('BUNIT').strip()
    exptime  = header.get('EXPTIME')
    #print infile
    #print pzpt, bunit, exptime, photflam, photplam
    #print bunit,
    #if ((bunit[-2:] <> '/S') or (forcesec == True)) and (forcetot == False):
    if ((bunit[-2:] <> '/S') or (forcetot == True)) and (forcesec == False):
        #print 'NOT SEC'
        photflam = photflam / exptime
    #zp = -21.10 - 2.5 * log10(photflam) - 5 * log10(photplam) + 18.6921
    zp = pzpt - 2.5 * log10(photflam) - 5 * log10(photplam / photplam0)
    #print infile, zp
    return zp

if __name__ == '__main__':
    infiles = glob.glob(sys.argv[1])
    forcesec = '-sec' in sys.argv
    forcetot = '-tot' in sys.argv
    # print infiles
    for infile in infiles:
        print infile, HSTzp(infile, forcesec=forcesec, forcetot=forcetot)
        print

    

"""

CONSIDER IMPLEMENTING THE FOLLOWING, MORE ROBUST, FROM APSIS utils/fUtil.zeroPoint

pzpt  = f[1].header.get('PHOTZPT')
pflam = f[1].header.get('PHOTFLAM')
pplam = f[1].header.get('PHOTPLAM')
exptime = f[1].header.get('EXPTIME')

bunit = string.strip(f[1].header.get('BUNIT'))
count_units     = ['DN','COUNTS','COUNT','ELECTRON','ELECTRONS','PHOTON','PHOTONS']
countrate_units = ['DN/S','COUNTS/S','COUNT/S','ELECTRON/S','ELECTRONS/S','PHOTON/S','PHOTONS/S']

zpt = pzpt - 2.5*math.log10(pflam/exptime) - 5.0*math.log10(pplam/5475.4)  # COUNTS
zpt = pzpt - 2.5*math.log10(pflam)         - 5.0*math.log10(pplam/5475.4)  # COUNTS / sec

"""
