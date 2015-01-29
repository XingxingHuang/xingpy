from coeio import *
from glob import glob

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

os.chdir('/astro/clash2/cipcal_archive/macs0647/flt/macs0647')
files = glob('*_flt.fits')

for infile in files:
    #print infile
    hdulist = pyfits.open(infile)
    
    header = hdulist[0].header
    target = header['TARGNAME']  # MACS0647+7015
    if target.find('PAR') > -1:
        targ = 'PAR'
    else:
        targ = 'CORE'
    instrument = string.strip(header['INSTRUME'])  # WFC3
    detector = string.strip(header['DETECTOR'])  # IR
    filt = extractfilter(header)  # F160W
    proposid = header['PROPOSID']  # 12101
    linenum = string.strip(header['LINENUM'])  # B1.007

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

    data = hdulist[1].data
    datasorted = sort(data.flat)
    datasorted = compress(datasorted, datasorted)
    s = meanstd_robust(datasorted,sortedalready=True)
    s.run()
    m = s.mean
    r = s.std
    #print m, r

    line = string.join(
        (infile[:-9].ljust(22), target.strip().ljust(15), string.ljust(targ, 4),
         string.ljust(filt, 6), string.ljust(instrument, 4), string.ljust(detector, 4), 
        '%5d' % proposid, linenum, '%6.2f' % angle,
        #'%6.2f' % sunangle, '%6.2f' % moonangle, '% 7.2f' % sunalt, '%6.2f' % earthlimb,
        dateobs, timeobs,
        '%11.6f' % expstart,
        #'%11.6f' % expend,
        '%4d' % exptime,
        '% 10.6f' % m,
        '% 10.6f' % r,
        ), '  ')
    
    print line
    
    if 1:
        fout = open('/Users/dcoe/backfltlog.txt', 'a')
        #fout = open('backgrounds.txt', 'a')
        fout.write('%s  %g  %g\n' % (infile, m, r))
        fout.close()

# cd /astro/clash1/ftp/outgoing/macs0647/HST/images/mosaicdrizzle_image_pipeline/scale_65mas/single_drz/
