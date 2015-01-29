# checkforupdates.py
# summary.py

import sys

if 0:
    print 'Logging in ~/cronlog.txt and cronerrors.txt...'
    #print 'Logging in ~/cronlog.txt...'
    #print 'Logging errors in ~/cronerrors.txt...'
    sys.stdout = open("/Users/dcoe/cronlog.txt","w")
    sys.stderr = open("/Users/dcoe/cronerrors.txt","w")

#from coeio import *
import os
from os.path import join, exists
from glob import glob
import time
import datetime

cipdir    = '/data01/cipphot/pipeline'
cipoutdir = '/data02/cipphot'

def stripnewline(line):
    if line[-1] == '\n':
        line = line[:-1]
    return line

def loadfile1(infile, dir=''):
    file = join(dir, infile)
    f = open(file, 'r')
    txt = f.readlines()
    txt = map(stripnewline, txt)
    return txt

clusters = loadfile1('clusters.txt', dir=cipdir)
#file = join(cipdir, 'clusters.txt')
#f = open(file, 'r')
#clusters = f.readlines()

updatefile = '/astro/clash1/ftp/outgoing/CLASHprogress/updates.txt'

def writeln(s=''):
    print s
    fout.write(s+'\n')

def fwrite(s=''):
    print s,
    fout.write(s)

#today = datetime.date.today()
today = time.time()
#print today
#today = float(today)

fout = open(updatefile, 'w')

todaystr = datetime.datetime.fromtimestamp(today).strftime('%Y-%m-%d %H:%M')
#writeln('Automatically updated every minute')
#writeln('Last updated ' + todaystr)
writeln('Automatically updated every minute (last update %s)' % todaystr)
writeln('')

writeln('Cluster       FLT images last updated:            Reduced images last updated:        Catalogs last updated:')

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


def timestr(modtime):
    if modtime == None:
        return ' ' * 34
    
    modtimestr = '  '
    modtimestr += datetime.datetime.fromtimestamp(modtime).strftime('%Y-%m-%d %H:%M')
    
    secondsago = today - modtime
    daysago = secondsago / 60. / 60. / 24.
    daysago = int(daysago)  # rounding down
    if daysago > 1:
        modtimestr += '   %3d days ago' % daysago
    elif daysago == 1:
        modtimestr += '   Yesterday'
    else:
        hoursago = secondsago / 60. / 60.
        modtimestr += '   %3d hours ago' % hoursago

    return modtimestr

def fieldshorten(field):
    field = field.replace('abell_', 'a')
    return field

def fieldlengthen(field):
    if field[0] == 'a':
        if field[:5] <> 'abell':
            field = 'abell_' + field[1:]
    return field


def modcompstr(mod1, mod2):
    if mod1 > mod2:
        return '*'
    else:
        return ' '

debug = '-debug' in sys.argv

#for field in ['macs0329']:
for field in clusters:
    shortfield = fieldshorten(field)
    fltdir1 = '/astro/clash2/cipcal_archive/%s/flt/%s' % (shortfield, shortfield)
    fltdir2 = '/data02/cipcal/%s/flt/%s' % (shortfield, shortfield)
    if debug:
        print fltdir1
        print fltdir2
    imdir  = '/astro/clash1/ftp/outgoing/%s/HST/images/mosaicdrizzle_image_pipeline/scale_65mas' % field
    catdir = '/astro/clash1/ftp/outgoing/%s/HST/catalogs/mosaicdrizzle_image_pipeline/ACS_IR_detection' % field
    if debug:
        print imdir
    fltfiles1 = glob(join(fltdir1,  '*_fl?*.fits*'))  # NOW SEARCHING FOR flc FILES AS WELL
    fltfiles2 = glob(join(fltdir2,  '*_fl?*.fits*'))  # NOW SEARCHING FOR flc FILES AS WELL
    if debug:
        print len(fltfiles1)
        print len(fltfiles2)
    fltfiles = fltfiles1 + fltfiles2
    imfiles   = glob(join(imdir,  '*_drz*.fits*'))
    catfiles  = glob(join(catdir, '*.cat*'))
    if debug:
        print 'imfiles', len(imfiles)
    allimfiles = imfiles[:]  # copy
    modtimes = []
    for imfile in allimfiles:
        if 'total' in imfile:
            imfiles.remove(imfile)

    fwrite(field.ljust(12))

    fltmod = oldest(fltfiles)
    immod = oldest(imfiles)
    catmod = oldest(catfiles)
    
    if len(fltfiles):
        fwrite(timestr(fltmod).ljust(36))

        s = timestr(immod) + modcompstr(fltmod, immod)
        fwrite(s.ljust(36))
        
        fwrite(timestr(catmod))
        fwrite(modcompstr(immod, catmod))

    writeln()
    if debug:
        print

fout.close()

print
print 'Uploaded to:'
print 'http://archive.stsci.edu/pub/clash/outgoing/CLASHprogress/updates.txt'
