# rsync ~/CLASH/pipeline/fltcatalog.py clashdms1.stsci.edu:~/pipeline/

import glob, os, string, sys
import pyfits
from numpy import argsort

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

indir = ''

exposures = {}

#searchstr = '*_flt.fits'
searchstr = '*_fl?.fits'
if len(sys.argv) > 1:
    searchstr = sys.argv[1]

fltfiles = glob.glob(searchstr)
lines = []
expends = []
print '*_fl?.fits                  filt   instr/cam    targ  prop visit.exp rollPAV3 sunang moonang  sunalt earthlimb exp(s)  date       time'
for fltfile in fltfiles:
    infile = os.path.join(indir, fltfile)
    hdulist = pyfits.open(infile)
    #hdulist.info()
    header = hdulist[0].header
    #header.ascardlist()
    filt = extractfilter(header)
    instrument = string.strip(header['INSTRUME'])
    detector = string.strip(header['DETECTOR'])
    proposid = header['PROPOSID']
    linenum = string.strip(header['LINENUM'])
    angle = header['PA_V3']
    sunangle = header['SUNANGLE']
    moonangle = header['MOONANGL']
    sunalt = header['SUN_ALT']
    earthlimb = sunangle + sunalt
    if earthlimb > 90:
        earthlimb = 180 - earthlimb
    visit = string.split(linenum,'.')[0]
    exposure = string.split(linenum,'.')[1]
    dateobs = string.strip(header['DATE-OBS'])
    timeobs = string.strip(header['TIME-OBS'])
    exptime = header['EXPTIME']
    expstart = header['EXPSTART']
    expend = header['EXPEND']
    target = header['TARGNAME']
    if target.find('PAR') > -1:
        targ = 'PAR'
    else:
        targ = 'CORE'
    #
    #rint 'ibeya0drq  F125W   WFC3  IR  PAR   12065  A0.002  231.99   702  2010-11-18  21:43:23
    #fltfile[:-9].ljust(22)
    line = string.join((fltfile[:-5].ljust(26), string.ljust(filt, 6), string.ljust(instrument, 4), string.ljust(detector, 4), string.ljust(targ, 4), '%5d' % proposid, linenum, '%6.2f' % angle, '%6.2f' % sunangle, '%6.2f' % moonangle, '% 7.2f' % sunalt, '%6.2f' % earthlimb,  '%4d' % exptime, dateobs, timeobs), '  ')
    lines.append(line)
    expends.append(expend)

    #exposure = int(exposure)
    if filt in exposures.keys():
        exposures[filt].append(exptime)
    else:
        exposures[filt] = [exptime]
    
    #print line

SI = argsort(expends)
for i in SI:
    print lines[i]

print

def filt2lam(filt):
    lam = int(filt[1:4])
    if lam < 200:
        lam = 10 * lam
    return lam

filts = exposures.keys()
lams = map(filt2lam, filts)
SI = argsort(lams)
#filts = take(filts, SI)
#for filt in filts:
print 'filt  nexp totexp'
for i in SI:
    filt = filts[i]
    print '%6s %2d  %5d' % (filt.ljust(6), len(exposures[filt]), sum(exposures[filt]))


"""
ib6o05w4q  F125W   WFC3  IR  11359  05.001  119.09   802  2009-10-04  11:30:18
ib6o05w6q  F125W   WFC3  IR  11359  05.003  119.09   902  2009-10-04  11:44:54
ib6o05waq  F125W   WFC3  IR  11359  05.005  119.09   802  2009-10-04  12:01:10
ib6o05wsq  F125W   WFC3  IR  11359  05.007  119.09   802  2009-10-04  13:02:07
ib6o05wwq  F125W   WFC3  IR  11359  05.009  119.09   902  2009-10-04  13:16:43
ib6o05wzq  F125W   WFC3  IR  11359  05.011  119.09   802  2009-10-04  13:32:59

ib6o05xjq  F160W   WFC3  IR  11359  05.013  119.09   802  2009-10-04  14:37:59
ib6o05xmq  F160W   WFC3  IR  11359  05.015  119.09   802  2009-10-04  14:52:35
ib6o05xqq  F160W   WFC3  IR  11359  05.017  119.09   902  2009-10-04  15:07:11
ib6o05xuq  F160W   WFC3  IR  11359  05.019  119.09   802  2009-10-04  16:13:50
ib6o05xyq  F160W   WFC3  IR  11359  05.021  119.09   802  2009-10-04  16:28:26
ib6o05y1q  F160W   WFC3  IR  11359  05.023  119.09   902  2009-10-04  16:43:02

ib6o15y6q  F098M   WFC3  IR  11359  15.001  119.09   802  2009-10-04  17:53:16
ib6o15y8q  F098M   WFC3  IR  11359  15.003  119.09   902  2009-10-04  18:07:52
ib6o15ycq  F098M   WFC3  IR  11359  15.005  119.09   802  2009-10-04  18:24:08
ib6o15yfq  F098M   WFC3  IR  11359  15.007  119.09   802  2009-10-04  19:25:33
ib6o15yjq  F098M   WFC3  IR  11359  15.009  119.09   902  2009-10-04  19:40:09
ib6o15ymq  F098M   WFC3  IR  11359  15.011  119.09   802  2009-10-04  19:56:25

---

j8e616mbq  F435W   ACS  WFC   9425  16.016   70.05  1200  2002-08-23  20:54:35
j8e616meq  F435W   ACS  WFC   9425  16.016   70.05  1200  2002-08-23  21:17:31
j8e616miq  F435W   ACS  WFC   9425  16.016   70.05  1200  2002-08-23  22:28:21
j8e616mmq  F435W   ACS  WFC   9425  16.016   70.05  1200  2002-08-23  22:51:17
j8e616mqq  F435W   ACS  WFC   9425  16.016   70.05  1200  2002-08-24  00:13:55
j8e616n9q  F435W   ACS  WFC   9425  16.016   70.05  1200  2002-08-24  01:57:54

j8e631e5q  F606W   ACS  WFC   9425  31.063   70.05   520  2002-08-04  05:50:33
j8e631e9q  F606W   ACS  WFC   9425  31.063   70.05   520  2002-08-04  06:02:09
j8e631eeq  F775W   ACS  WFC   9425  31.064   70.05   520  2002-08-04  06:14:25
j8e631ejq  F775W   ACS  WFC   9425  31.064   70.05   520  2002-08-04  06:26:01
j8e631ffq  F850LP  ACS  WFC   9425  31.065   70.05   530  2002-08-04  07:24:46
j8e631fkq  F850LP  ACS  WFC   9425  31.065   70.05   530  2002-08-04  07:36:32
j8e631fpq  F850LP  ACS  WFC   9425  31.065   70.05   530  2002-08-04  07:48:18
j8e631fuq  F850LP  ACS  WFC   9425  31.065   70.05   530  2002-08-04  08:00:04

j8e662otq  F606W   ACS  WFC   9425  62.243  159.98   480  2002-11-02  10:20:44
j8e662oxq  F606W   ACS  WFC   9425  62.243  159.98   480  2002-11-02  10:31:40
j8e662p2q  F775W   ACS  WFC   9425  62.244  159.98   480  2002-11-02  10:43:16
j8e662p7q  F775W   ACS  WFC   9425  62.244  159.98   480  2002-11-02  10:54:12
j8e662pdq  F850LP  ACS  WFC   9425  62.245  159.98   510  2002-11-02  11:54:19
j8e662piq  F850LP  ACS  WFC   9425  62.245  159.98   510  2002-11-02  12:05:45
j8e662pnq  F850LP  ACS  WFC   9425  62.245  159.98   510  2002-11-02  12:17:11
j8e662psq  F850LP  ACS  WFC   9425  62.245  159.98   510  2002-11-02  12:28:37

j8e693ezq  F606W   ACS  WFC   9425  93.443  249.95   520  2003-02-05  14:18:03
j8e693f3q  F606W   ACS  WFC   9425  93.443  249.95   520  2003-02-05  14:29:19
j8e693f8q  F775W   ACS  WFC   9425  93.444  249.95   520  2003-02-05  14:41:15
j8e693fdq  F775W   ACS  WFC   9425  93.444  249.95   520  2003-02-05  15:57:11
j8e693fhq  F850LP  ACS  WFC   9425  93.445  249.95   530  2003-02-05  16:08:53
j8e693foq  F850LP  ACS  WFC   9425  93.445  249.95   530  2003-02-05  17:38:14
j8e693ftq  F850LP  ACS  WFC   9425  93.445  249.95   530  2003-02-05  17:49:40
j8e693g0q  F850LP  ACS  WFC   9425  93.445  249.95   530  2003-02-05  19:19:49

j92qifz7q  F775W   ACS  WFC  10340  IF.001   70.05   398  2004-07-30  18:20:18
j92qifzgq  F850LP  ACS  WFC  10340  IF.003   70.05   398  2004-07-30  19:24:24
j92qifzjq  F850LP  ACS  WFC  10340  IF.005   70.05   398  2004-07-30  19:33:38
j92qifzmq  F850LP  ACS  WFC  10340  IF.007   70.05   398  2004-07-30  19:42:52

j92qifzpq  F850LP  ACS  WFC  10340  IF.009   70.05   398  2004-07-30  19:52:06
j92qkfpwq  F775W   ACS  WFC  10340  KF.001  159.98   400  2004-11-03  10:48:01
j92qkfpyq  F850LP  ACS  WFC  10340  KF.003  159.98   400  2004-11-03  10:57:23
j92qkfq1q  F850LP  ACS  WFC  10340  KF.005  159.98   400  2004-11-03  11:06:39
j92qkfq4q  F850LP  ACS  WFC  10340  KF.007  159.98   400  2004-11-03  11:15:55
j92qkfqeq  F850LP  ACS  WFC  10340  KF.009  159.98   400  2004-11-03  12:19:27

j92qmfvwq  F606W   ACS  WFC  10340  MF.001  249.95   140  2005-02-04  03:21:39
j92qmfvyq  F775W   ACS  WFC  10340  MF.003  249.95   350  2005-02-04  03:26:57
j92qmfw1q  F850LP  ACS  WFC  10340  MF.005  249.95   360  2005-02-04  03:35:29
j92qmfw4q  F850LP  ACS  WFC  10340  MF.007  249.95   360  2005-02-04  03:44:05
j92qmfw7q  F850LP  ACS  WFC  10340  MF.009  249.95   360  2005-02-04  03:52:41
j92qmfwaq  F850LP  ACS  WFC  10340  MF.011  249.95   360  2005-02-04  04:01:17
"""
