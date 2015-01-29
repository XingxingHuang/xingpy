#import sys

if 0:
    print 'Logging in ~/cronlog.txt and cronerrors.txt...'
    #print 'Logging in ~/cronlog.txt...'
    #print 'Logging errors in ~/cronerrors.txt...'
    sys.stdout = open("/Users/dcoe/cronlog.txt","w")
    sys.stderr = open("/Users/dcoe/cronerrors.txt","w")

#from coeio import *
from coebasics import *
from filttools import *
from glob import glob
#import pyfits

#print 'summary.py now with pyfits'

allfilts = 'f225w f275w f336w f390w f435w f475w f555w f606w f625w f775w f814w f850lp f105w f110w f125w f140w f160w'.split()

def getnameinstr(filename):
    instr = strbtw(filename, 'mas_', '_f')
    instr = instr.replace('wfc3', '')
    return instr

def roundhalf(x):
    return roundint(2*x) / 2.

def writeimg(imagefile, n=1):
    for i in range(n):
        fout.write('<img src=%s border=0 width=20>' % capfile(imagefile, 'png'))

colordict = {'uvis':'magenta', 'acs':'green', 'ir':'red'}

def oldest(files):
    modtimes = []
    for file in files:
        modtime = os.stat(file).st_mtime
        modtimes.append(modtime)
    if len(modtimes):
        modtime = max(modtimes)
    else:
        modtime = None
    return modtime

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
        print file
        try:
            header = pyfits.open(file, memmap=1)[0].header
        except PermissionDenied:
            print "PERMISSION DENIED"
            break

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
        nameinstr = getnameinstr(file)
        #print instr
        #print nameinstr
        if instr <> nameinstr:
            print 'NOT INCLUDING OTHER CAMERA OBSERVATION FOR THIS FILTER'
            continue
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
    
    #for i in range(len(filts)):
    #    print drzfiles[i]
    #
    #print

    #fout = open(expfile, 'a')
    fout.write(field.ljust(10))
    
    print 'FILT  EXPTIME #EXPOSURES'
    print '-----  -----  ----------'
    for filt in allfilts:
        print filt.ljust(6),
        exptime = exptimes.get(filt, 0)
        if 0: #not exptime:
            print
            continue
        
        print '%5d ' % exptime,

        orbits = exptime / 2400
        print '%.1f ' % orbits,
        print '~%.1f' % roundhalf(orbits),
        print '/ %.1f ' % roundhalf(expectedorbits[filt]),

        sym = 'X'
        nobs = roundint(2 * orbits)
        nexpected = roundint(2 * expectedorbits[filt])
        ncomplete = min((nobs, nexpected))
        nincomplete = nexpected - ncomplete
        nextra = nobs - nexpected
        s = ''
        s += 'X' * ncomplete
        s += 'O' * nincomplete
        s += '+' * nextra
        print s

        if 0: #nobs + nexpected == 0:
            continue

        #fout.write(filt)
        #fout.write(' ')
        #fout.write(' &nbsp; ')
        fout.write('  %5d' % exptime)
        instr = getinstr(filt)
        color = colordict[instr]
        #writeimg('%son' % color, ncomplete)
        #writeimg('%soff' % color, nincomplete)
        #writeimg('%splus' % color, nextra)
        #writeimg('yellow', nextra)
        #fout.write('<br>\n')

        if 0:
            n = nexposures[filt]
            #print '%2d ' % n,
            instr = getinstr(filt)
            sym = {'uvis':'X', 'acs':'+', 'ir':'*'}[instr]
            #print sym * n

    print '-----  -----  ----------'
    print 'TOTAL', '% 5d' % totexptime

    #fout.write('<br>\n')
    fout.write('\n')
    #fout.close()

    #pause()


cipdir    = '/data01/cipphot/pipeline'
cipoutdir = '/data02/cipphot'
clusters = loadfile('clusters.txt', dir=cipdir)
expectedorbits = loaddict('filterorbits.txt', dir=cipdir)
searchstr = '*_drz*.fits*'  # allows .gz too!
#searchstr = '*_drz*.fits'  # skip compressed!

#fout = open('summary.html', 'w')
#fout = open('/astro/clash1/ftp/test/summary/index.html', 'w')
#fout = open('/astro/clash1/ftp/test/summary/summary.txt', 'w')
#expfile = '/astro/clash1/ftp/test/summary/summary.txt'
expfile = '/astro/clash1/ftp/outgoing/CLASHprogress/summary.txt'
#delfile(expfile)
if exists(expfile):
    expmodtime = os.stat(expfile).st_mtime
    expprevtxt = loadfile(expfile)
else:
    expmodtime = 0
    expprevtxt = []

fout = open(expfile, 'w')
fout.write('Cluster     f225w  f275w  f336w  f390w  f435w  f475w  f555w  f606w  f625w  f775w  f814w f850lp  f105w  f110w  f125w  f140w  f160w\n')
#fout.close()

#for field in ['macs0329']:
for iline, field in enumerate(clusters):
    print
    print field
    imdir = '/astro/clash1/ftp/outgoing/%s/HST/images/mosaicdrizzle_image_pipeline/scale_65mas' % field
    print imdir
    drzfiles = glob(join(imdir, searchstr))
    alldrzfiles = drzfiles[:]  # copy
    for drzfile in alldrzfiles:
        if 'total' in drzfile:
            drzfiles.remove(drzfile)

    #if 1: #len(drzfiles):
    #if (oldest(drzfiles) > expmodtime) or (len(expprevtxt) < iline+2):
    if iline >= 12:
        summary()
    else:
        print 'up to date'
        print 'images: ', oldest(drzfiles)
        print 'summary:', expmodtime
        line = expprevtxt[iline+1]
        print line
        fout.write(line+'\n')
        
        #fout.write('<h1>%s</h1>\n' % field)
        #fout.write(field.ljust(13))
    
fout.close()
print

#Cluster     f225w  f275w  f336w  f390w  f435w  f475w  f555w  f606w  f625w f775w f814w f850lp f105w f110w f125w f140w f160w

#abell_383    3671   3672   2434   2434   2125   2064      0   2105   2064   2042   4243   4214   3620   2514   3320   2411   5935
