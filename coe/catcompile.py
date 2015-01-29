#from coeplottk import *
from coeio import *
from glob import glob

files = glob('*.cat*')

for file in files:
    if strbegin(file, 'macs1149'):
        files.remove(file)
        files.insert(0, file)

for file in files:
    if strbegin(file, 'CLASH'):
        files.remove(file)

def clus2num(file):
    istart = 0
    for i in range(len(file)):
        if file[i] in string.digits:
            if istart == 0:
                istart = i
            iend = i
    num = file[istart:iend+1]
    return int(num)

#map(clus2num, files)

cat = loadcat(files[0])
cat.assign('clusnum', clus2num(files[0]))
for file in files[1:]:
    newcat = loadcat(file)
    newcat.assign('clusnum', clus2num(file))
    for label in cat.labels:
        #print label
        if label not in newcat.labels:
            if strend(label, 'mag'):
                val = -99
            if strend(label, 'magerr'):
                val = inf
            if strend(label, 'apcor'):
                val = 0
            if strend(label, 'flux'):
                val = nan
            if strend(label, 'fluxerr'):
                val = inf
            if strend(label, 'sig'):
                val = nan
            newcat.assign(label, val)
    newcat.labels = cat.labels
    cat = cat.append(newcat)

# 25066
#cat.save('CLASH_IR.cat')

#################################
# ~/CLASH/pipeline/cipphot/catfinal.py

from coeio import *
from catsave import catsave
#import re
from fnmatch import fnmatch

oldlabelspecs = """
 id     '%5d'       Object ID Number
 clusnum '%04d'      Cluster Number
 RA     '%11.7f'    Right Ascension in decimal degrees
 Dec    '% 11.7f'   Declination in decimal degrees
 x      '%8.3f'     x pixel coordinate
 y      '%8.3f'     y pixel coordinate
 fwhm   '%7.3f'     Full width at half maximum (arcsec)
 area   '%5d'       Isophotal aperture area (pixels)
 stel   '%4.2f'     SExtractor "stellarity" (1 = star; 0 = galaxy)
 ell    '%5.3f'     Ellipticity = 1 - B/A

 flag5sig '%1d'  0 = probably real; 1 = probable CR; 2 = no 5-sigma detection
 nf5sig   '%2d'  Number of filters with a 5-sigma detection
 nfcr5sig '%2d'  Number of CR-vulnerable filters with a 5-sigma detection
 nfobs    '%2d'  Number of filters observed (not in chip gap, etc.)

 *_mag     '% 9.4f'  FILT + ' isophotal magnitude (%s)' % zptxt
 *_magerr  '% 8.4f'  FILT + ' isophotal magnitude uncertainty' + crtxt
 *_apcor   '% 7.4f'  FILT + ' aperture correction'
 *_flux    '% 12.4f' FILT + ' isophotal flux'
 *_fluxerr '% 11.4f' FILT + ' isophotal flux uncertainty'
 *_sig     '% 8.2f'  FILT + ' detection significance'
"""

newlabelspecs = """
 zb	'%6.3f'	    BPZ most likely redshift
 tb	'%4.2f'	    BPZ most likely spectral type
 zbmin	'%6.3f'	    Lower limit (95% confidence)
 zbmax	'%6.3f'	    Upper limit (95% confidence)
 odds	'%5.3f'	    P(z) contained within zb +/- 2*0.02*(1+z)
 zml	'%5.2f'	    Maximum Likelihood most likely redshift
 tml	'%4.2f'	    Maximum Likelihood most likely spectral type
 chisq	'%7.3f'	    Poorness of BPZ fit: observed vs. model fluxes
 M0	'% 9.4f'    Magnitude used as BPZ prior: F775W or closest available filter
 chisq2	'%7.3f'	    Modified chisq: model fluxes given error bars
"""

zptxt = 'multiplied by X.XXX to correct for extinction (-Y.YYY mag)'
crtxt = 'X.XXX factor applied here as well'

def printdict(d, sortkeys=True):
    keys = d.keys()
    if sortkeys:
        keys = sort(keys)
    for k in keys:
        print k, d[k]

# Crappy version: RA is a match to A
def starmatch1(query, name):
    words = query.split('*')
    for word in words:
        i = name.find(word)
        if i == -1:
            break
        name = name[i+len(word):]
    return (i > -1) and (name == '')

# Fails on *_magerr = mag
def starmatch2(pattern, s):
    p = pattern.replace('*', '.*')
    return re.match(p, s)

def starmatch(pattern, s):
    return fnmatch(s, pattern)

def applylabelspecs(cat, labelspecs, applyformats=1, applydescriptions=1):
    lines = labelspecs.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            # Split around ' surrounding format
            # But allow for ' in description (by only splitting 2x)
            label, format, description = line.split("'", 2)
            label = label.strip()
            description = description.strip()
            
            for catlabel in cat.labels:
                #print label, catlabel, starmatch(label, catlabel)
                if starmatch(label, catlabel):
                    #print label, catlabel
                    if applyformats:
                        cat.formats[catlabel] = format
                    
                    if applydescriptions:
                        cat.descriptions[catlabel] = description

cat.header = loadfile('CLASH_IR_header.txt', dir='/data01/cipphot/pipeline')
cat.header.append('.')  # SPECIAL CODE TO REFRAIN FROM ADDING TO HEADER

applylabelspecs(cat, newlabelspecs)
#applylabelspecs(cat, oldlabelspecs, applydescriptions=0)
applylabelspecs(cat, oldlabelspecs)
outname = 'CLASH_IR.cat'
catsave(cat, outname)

#printdict(cat.formats)

