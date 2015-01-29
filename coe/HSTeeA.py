# ~/CLASH/data/A383/wei/v1/catalog/2/HSTee.py
# ~/CLASH/data/A383/wei/v1/catalog/2/apcors.py
# ~/CLASH/data/A383/wei/v1/catalog/2/apcor.py
# ~/CLASH/data/A383/amk/5/catalog/apcor_arcsec.py
# ~/CLASH/data/A383/amk/5/catalog/apcorradius.py
# ~/CLASH/data/A383/wei/v1/sex/apcor.py

# ~/CLASH/pipeline/apsis/notes.py
# ~/CLASH/data/A383/wei/v1/sex/notes.txt

# ~/CLASH/pipeline/apsis/apsis-4.2.5/python/apsis/colorCatalog.py

# /Users/dcoe/CLASH/pipeline/apsis/reffiles/aperData/newWFC_0803.ee_new_csky.dat
# /Users/coe/CLASH/pipelines/Wei/wfex/reffiles/aperData/newIR_0803.ee_new_csky.dat
# /Users/coe/CLASH/pipelines/Wei/wfex/reffiles/aperData/wfc3_filter.dat

#from coeplottk import *
#from coetools import *
from coeio import *

#################################

import socket
def onclashdms1():
    hostname = socket.gethostname()
    return (len(hostname) >= 9) and (hostname[:9] == 'clashdms1')

if onclashdms1():
    indir = '/data01/cipphot/pipeline/'
else:
    indir = '~/CLASH/pipeline/photometry/'

# ACS
ACSeecat = loadsexcat0('newWFC_0803.ee_new_csky.dat', indir)

# WFC3/IR
IReecat = loadcat2d('wfc3ir_ee_circle.dat', indir)

# WFC3/UVIS
UVISeecat = loadcat2d('wfc3uvis_ee_circle.dat', indir)

#eecat.z = eecat.z / eecat.z[-1]  # Normalize to maximum (that's what APSIS does)

#lamdict = loaddict('filtlam.dict')

#################################

# The WFC3 encircled energy tables only give 0.1" < r < 2.0"
minradius = 0.1  # arcsec
maxradius = 2.0  # arcsec

#################################

def ACSee(filt, radii):  # aperture radii in arcsec
    """IRapcor('g', radii_in_arcsec)"""
    FILT = string.upper(filt)
    label = 'EE_'+FILT
    if label not in ACSeecat.labels:
        print label, 'not found in', ACSeecat.name
        return None
    else:
        tabradii = ACSeecat.radius_asec
        tabee = ACSeecat.get(label)
        radii = clip(radii, minradius, maxradius)
        ee = interp(radii, tabradii, tabee)
        ee = ee / 100.
        #apcor = 2.5 * log10(ee)
        return ee

#################################

def IRee(lam, radii):  # aperture radii in arcsec
    """IRapcor(1100, radii_in_arcsec)"""
    lam = lam / 10.  # Angstroms -> nanometers
    radii = clip(radii, minradius, maxradius)
    ee = IReecat.get(lam, radii, dointerp=1)
    #apcor = 2.5 * log10(ee)
    return ee

#################################

def UVISee(lam, radii):  # aperture radii in arcsec
    """UVISapcor(336, radii_in_arcsec)"""
    lam = lam / 10.  # Angstroms -> nanometers
    radii = clip(radii, minradius, maxradius)
    ee = UVISeecat.get(lam, radii, dointerp=1)
    #apcor = 2.5 * log10(ee)
    return ee
