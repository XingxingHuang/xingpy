from coeio import *
from catsave import catsave
#import re
from fnmatch import fnmatch

oldlabelspecs = """
 id     '%5d'       Object ID Number
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


field = sys.argv[1]  # a383 = output file name
#epoch = sys.argv[2]  # v5

if len(sys.argv) > 2:
    root = sys.argv[2]
else:
    root = 'photometry'

cat = loadcat(root + '.cat')
#print cat.header
#pause()

for i in range(len(cat.header)):
    if cat.header[i][:2] <> '##':
        break

cat.header = cat.header[:i]
#cat.header[0] = cat.header[0].replace('Photometric', 'Photometric + BPZ')
cat.header[0] = cat.header[0].replace('Photometric', 'Photometric + photo-z (BPZ)')
line = "## Note: photo-z estimates are intended for galaxies only\n"
line += "## Stars may be identified as having higher values of SExtracor stellarity\n"
cat.header.insert(1, line)
#cat.header.insert(1, '## BPZ v1.99.3 results obtained using CR-free filters only\n')

#cat.descriptions

bpzcat = loadcat(root+'_bpz.cat')
#bpzcat.labels = string.split('id zb   zbmin  zbmax     tb    odds    zml    tml    chisq      M0      chisq2')
if 'M0' in cat.labels:
    cat.labels.remove('M0')
bpzcat.labels = string.split('id zb   zbmin  zbmax     tb    odds    chisq   chisq2  M0    zml    tml')
cat.merge(bpzcat)

applylabelspecs(cat, newlabelspecs)
applylabelspecs(cat, oldlabelspecs, applydescriptions=0)

#for label in cat.labels:
#    print label, cat.formats[label], cat.descriptions[label]

print cat.len()
if 'flag5sig' in cat.labels:
    nflag = total(cat.flag5sig)
    print '%d' % nflag, 'total object flags (pruned for ACS but not IR)'
else:
    nflag = 0

#cat = cat.equal('flag5sig', 0)
#print cat.len()

for i, line in enumerate(cat.header):
    if 'runed' in line:
        if nflag:
            cat.header[i] = '## Not pruned: a few < 5-sigma detections may remain (flagsig > 0)\n'
        else:
            cat.header[i] = line.replace('Please prune', 'Pruned')

cat.header.append('##\n')

#cat.save('macs1149_v1.cat')
#cat.header = None
#catsave(cat, 'macs1149_v1.cat')
#catsave(cat, 'a383_v6amk.cat')

#fieldv = field + '_' + epoch
#outname = fieldv + 'amk.cat'
outname = field + '.cat'
catsave(cat, outname)
