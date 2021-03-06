# previously summarypage.py

import sys

if 1:
    print 'Logging in ~/cronlog.txt and cronerrors.txt...'
    #print 'Logging in ~/cronlog.txt...'
    #print 'Logging errors in ~/cronerrors.txt...'
    sys.stdout = open("/Users/dcoe/cronlog.txt","w")
    sys.stderr = open("/Users/dcoe/cronerrors.txt","w")

#from coeio import *
from coebasics import *
from filttools import *  # getinstr

# Check processed images and generate ASCII file with update times
#os.system('python $CIPPHOT/summary.py')

def roundhalf(x):
    return roundint(2*x) / 2.

def writeimg(imagefile, n=1, size=20):
    for i in range(n):
        fout.write('<img src=%s border=0 width=%d>' % (capfile(imagefile, 'png'), size))

colordict = {'uvis':'magenta', 'acs':'green', 'ir':'red'}

cipdir    = '/data01/cipphot/pipeline'
expectedorbits = loaddict('filterorbits.txt', dir=cipdir)
#cipoutdir = '/data02/cipphot'
#clusters = loadfile('clusters.txt', dir=cipdir)

#expfile = '/astro/clash1/ftp/test/summary/summary.txt'
#webpage = '/astro/clash1/ftp/test/summary/index.html'
#webpage = '/astro/clash1/ftp/test/summary/test.html'
expfile = '/astro/clash1/ftp/outgoing/CLASHprogress/summary.txt'
webpage = '/astro/clash1/ftp/outgoing/CLASHprogress/index.html'

txt = loadfile(expfile)
filts = txt[0].split()[1:]
modtime = os.stat(expfile).st_mtime

orbittime = 2300  # seconds

fout = open(webpage, 'w')
fout.write('<h1>CLASH HST observation progress: processed images</h1>\n')

import datetime, time
today = time.time()
todaystr = datetime.datetime.fromtimestamp(today).strftime('%Y-%m-%d %H:%M')
modstr = datetime.datetime.fromtimestamp(modtime).strftime('%Y-%m-%d %H:%M')

fout.write('Last updated %s<br>\n' % modstr)
fout.write('Total exposure times listed for each filter, then rounded:<br>\n')
fout.write('Each square = 1/2 orbit, approximating 1 orbit as %s seconds<br>\n' % orbittime)
fout.write('&bull; Bright = <b>observed *and* processed</b><br>\n')
fout.write('&bull; Dim = incomplete<br>\n')
fout.write('&bull; Yellow = bonus! (mainly archival data, sometimes spread over a larger area)<br>\n')
fout.write('Also available as an <a href=summary.txt>ASCII table</a><br>\n')
fout.write('Also see <a href=updates.txt>progress made</a> on the initial processed FLT images, final processed DRZ images (shown on this page), and catalogs<br>\n')

fout.write('Also see the CLASH schedule ')
fout.write('<a href=http://archive.stsci.edu/pub/clash/outgoing/CLASHschedule.png>plot</a>')
fout.write(' and ')
fout.write('<a href=https://docs.google.com/spreadsheet/ccc?authkey=CMTTip8K&key=0AjaeL-o31prldHFGTnhFN00yNVhQSlljTzFqZjEyUWc&authkey=CMTTip8K#gid=0>spreadsheet</a>')
fout.write('<br>\n')

print 'Creating', webpage
#print 'http://archive.stsci.edu/pub/clash/test/summary/'
print 'http://archive.stsci.edu/pub/clash/outgoing/CLASHprogress/'

no625clusters = ['macs0744', 'abell 611', 'macs1423']
no555625clusters = ['abell 611',]

fout.write('<pre>')
fout.write('           225 275 336 390 435 475 555 606 625 775 814 850 105 110 125 140 160\n')
for line in txt[1:]:
    cluster = line.split()[0]
    cluster = cluster.replace('_', ' ')
    cluster = cluster.ljust(11)
    fout.write('%s' % cluster)
    exptimes = stringsplitatoi(line[11:])
    for i in range(len(filts)):
        exptime = float(exptimes[i])
        filt = filts[i]
        
        orbits = exptime / orbittime
        # Hardwire fix for ~3900 seconds exposure time in 2 orbits
        # MUST FIX BOTH HERE AND BELOW
        if (filt in 'f814w f850lp'.split()) and (exptime > 3890) and (orbits < 2):
            orbits = 2
        # MUST HARDWIRE FIX BOTH HERE AND BELOW
        nobs = roundint(2 * orbits)
        nexpected = roundint(2 * expectedorbits[filt])
        ncomplete = min((nobs, nexpected))
        nincomplete = nexpected - ncomplete
        nextra = nobs - nexpected

        if cluster.strip() in no555625clusters:
            unexpected = filt in 'f555w f625w'.split()
        else:
            if cluster.strip() in no625clusters:
                unexpected = filt == 'f625w'
            else:
                unexpected = filt == 'f555w'

        instr = getinstr(filt)
        color = colordict[instr]
        size = 32
        if nextra > 0:
            writeimg('yellow', size=size)
        elif unexpected:
            writeimg('whitefull', size=size)
        elif ncomplete:
            if ncomplete == nexpected:
                writeimg('%son' % color, size=size)
            else:
                writeimg('%shalf' % color, size=size)
        else:
            writeimg('%soff' % color, size=size)
            
    fout.write('\n')
fout.write('</pre>')

for line in txt[1:]:
    cluster = line.split()[0]
    cluster = cluster.replace('_', ' ')
    fout.write('<h1>%s</h1>\n' % cluster)
    exptimes = stringsplitatoi(line[11:])
    for i in range(len(filts)):
        exptime = float(exptimes[i])
        filt = filts[i]
        
        orbits = exptime / orbittime
        # Hardwire fix for ~3900 seconds exposure time in 2 orbits
        # MUST HARDWIRE FIX BOTH HERE AND ABOVE
        if (filt in 'f814w f850lp'.split()) and (exptime > 3890) and (orbits < 2):
            orbits = 2
        nobs = roundint(2 * orbits)
        nexpected = roundint(2 * expectedorbits[filt])
        ncomplete = min((nobs, nexpected))
        nincomplete = nexpected - ncomplete
        nextra = nobs - nexpected

        if 0:
            print '%.1f ' % orbits,
            print '~%.1f' % roundhalf(orbits),
            print '/ %.1f ' % roundhalf(expectedorbits[filt]),
            s = ''
            s += 'X' * ncomplete
            s += 'O' * nincomplete
            s += '+' * nextra
            print s

        if nobs + nexpected == 0:
            continue

        if filt == 'f625w':
            if cluster in no625clusters:
                continue
        
        fout.write(filt)
        fout.write(' ')
        fout.write(' &nbsp; ')
        #fout.write('  %5d' % exptime)
        instr = getinstr(filt)
        color = colordict[instr]
        writeimg('%son' % color, ncomplete)
        writeimg('%soff' % color, nincomplete)
        #writeimg('%splus' % color, nextra)
        writeimg('yellow', nextra)
        if exptime:
            fout.write('%5d' % exptime)
            
        fout.write('<br>\n')

fout.close()
