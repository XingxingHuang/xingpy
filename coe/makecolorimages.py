# trilogyprep.py
# sortimages.py
# summary.py

from coeio import *
from glob import glob
from filttools import *
from im2rgbfits import im2rgbfits
import time, datetime

def fieldshorten(field):
    field = field.replace('abell_', 'a')
    return field

def fieldlengthen(field):
    if field[0] == 'a':
        if field[:5] <> 'abell':
            field = 'abell_' + field[1:]
    return field


def runtrilogy(field, imfiles, imdir, instr, redo=False, dirty=0):
    
    outroot = field
    if instr <> 'acsir':
        outroot += '_' + instr

    outfile = outroot + '.png'
    if exists(outfile):
        if not redo:
            outdir = os.getcwd()
            print join(outdir, outfile), 'EXISTS'
            return

    def writeln(s=''):
        fout.write(s+'\n')
        
    # ~/CLASH/data/m0744/trilogy/0118/notes.txt
    # ~/CLASH/data/uniform/scaling/
    chlams = None
    if instr == 'uvis':
        splits = 0, 300, 350, 400
        noiselum = 0.12
    elif instr == 'acs':
        splits = 400, 500, 700, 1000
        noiselum = 0.14
    elif instr == 'acsir':
        splits = 400, 500, 1000, 2000
        noiselum = 0.14
    elif instr == 'ir':
        splits = 1000, 1200, 1500, 2000
        noiselum = 0.20
    elif instr == 'irbright':
        #chlams = ((1100, -1400), 1250, 1600)
        #noiselum = 0.06
        chlams = ((1100, -1250), 1250, 1600)
        noiselum = 0.1
    else:
        print 'INSTRUMENT %s NOT RECOGNIZED' % instr
        return()

    lams = map(extractlam, imfiles)  # filttools

    trilogyfile = instr+'.in'
    fout = open(trilogyfile, 'w')

    if chlams <> None:
        for j in 0,1,2:
            channel = 'BGR'[j]
            writeln(channel)
            chlams1 = chlams[j]
            if type(chlams1) == type(110):
                chlams1 = [chlams1]
            for lam in chlams1:
                if abs(lam) not in lams:
                    if instr == 'irbright':
                        print 'Wavelength %dnm missing for IRbright image' % abs(lam)
                        return
                i = lams.index(abs(lam))
                if lam < 0:
                    s = '-'
                else:
                    s = ''
                writeln(s + imfiles[i])
            writeln()
    else:
        splits = array(splits)

        imagespresent = False
        prevchannel = ''
        n = len(imfiles)
        for i in range(n):
            j = splits.searchsorted(lams[i]) - 1
            if j in (0,1,2):
                imagespresent = True
                channel = 'BGR'[j]
                if channel <> prevchannel:
                    if prevchannel:
                        writeln()
                    writeln(channel)
                writeln(imfiles[i])
                prevchannel = channel

        if not imagespresent:
            print 'NO IMAGES AVAILABLE YET'
            return

    #scalingfile = '../scaling/levels_%s.txt' % instr
    scalingdir = '/astro/clash1/ftp/outgoing'
    scalingdir = join(scalingdir, 'color_images/scaling')
    scalingfile = 'levels_%s.txt' % instr
    scalingfile = join(scalingdir, scalingfile)
    
    writeln()
    writeln('indir  ' + imdir)
    writeln('outname  ' + outroot)
    writeln('noiselum  %g' % noiselum)
    writeln('scaling  ' + scalingfile)
    if dirty:
        writeln('weightimages  drz  wht')
    writeln('show  0')
    writeln('testfirst  0')
    
    fout.close()

    #run('trilogy ' + trilogyfile)
    run('python ~/trilogy/trilogy.py ' + trilogyfile)


def delifold(file1, file2):
    if exists(file1):
        t1 = os.stat(file1).st_mtime  # mtime better resolution than ctime
        t2 = os.stat(file1).st_mtime  # mtime better resolution than ctime
        if t1 < t2:
            delfile(file1)

def movefiles(searchstr, dest, pr=0):
    files = glob(searchstr)
    for file in files:
        run('mv %s %s' % (file, dest), pr)

def oldest(files):
    global datestr
    modtimes = []
    for file in files:
        modtime = os.stat(file).st_mtime
        modtimes.append(modtime)
        
        if file[-3:] == '.gz':
            file2 = file[:-3]
        else:
            file2 = file
        if file2[-5:] <> '.fits':
            continue
        datestr = int(file2.split('_')[-1][:-5])
        
    if len(modtimes):
        modtime = max(modtimes)
    else:
        modtime = None
    return modtime

def findimages(imdir, searchstr):
    imfiles = glob(join(imdir, searchstr))
    
    allimfiles = imfiles[:]  # copy
    for imfile in allimfiles:
        if 'total' in imfile:
            imfiles.remove(imfile)

    if len(imfiles):
        lams = map(extractlam, imfiles)  # filttools
        SI = argsort(lams)
        lams = take(lams, SI)
        imfiles = take(imfiles, SI)

    return imfiles

def makecolorimages(field=None, params=None):
    fullfield = 'full' in params.keys()

    searchstr = '*_drz*.fits*'  # allows .gz too!
    #searchstr = '*_drz*.fits'  # skip compressed!

    field = fieldlengthen(field)

    if (field == 'macs1149') and not fullfield:
        imdir = '/astro/clash1/ftp/outgoing/%s/HST/images/mosaicdrizzle_image_pipeline/old/20110314/65mas/clnpix_cosmetic' % field
        imfiles = findimages(imdir, searchstr)
        dirty = 0
        immodtime = oldest(imfiles)
    else:
        #imdir = '/astro/clash1/ftp/outgoing/%s/HST/images/mosaicdrizzle_image_pipeline/scale_65mas/clnpix_cosmetic' % field
        imdir = '/astro/clash1/ftp/outgoing/%s/HST/images/mosaicdrizzle_image_pipeline' % field
        if fullfield:
            imdirtydir = join(imdir, 'fullfield')
        else:
            imdirtydir = join(imdir, 'scale_65mas')

        imdir = join(imdirtydir, 'clnpix_cosmetic')
        
        imfiles = findimages(imdir, searchstr)
        imdirtyfiles = findimages(imdirtydir, searchstr)

        immodtime = oldest(imfiles)
        imdirtymodtime = oldest(imdirtyfiles)

        if len(imdirtyfiles):
            print 'Dirty images last modified:'
            print datetime.datetime.fromtimestamp(imdirtymodtime).strftime('%Y-%m-%d %H:%M')
        else:
            print 'No dirty FITS images found in'

        if len(imfiles):
            print 'Clean images last modified:'
            print datetime.datetime.fromtimestamp(immodtime).strftime('%Y-%m-%d %H:%M')
        else:
            print 'No clean FITS images found in'
            print imdir

        if len(imdirtyfiles):
            if len(imfiles):
                immoddiff = (immodtime - imdirtymodtime) / 3600. / 24.  # days
                if immoddiff < -1:
                    print 'Using dirty images which are newer by %d days' % -immoddiff
                    dirty = 1
                else:
                    print 'Using cleaned images'
                    dirty = 0
            else:
                print "Using dirty images since cleaned images aren't available"
                dirty = 1

    if dirty:
        imfiles = imdirtyfiles
        immodtime = imdirtymodtime
    
    if len(imfiles) == 0:
        print 'No FITS images found in'
        print imdir
        return

    if strend(imfiles[0], '.gz'):
        #datestr = datetime.datetime.fromtimestamp(immodtime).strftime('%Y%m%d')
        shortfield = fieldshorten(field)
        if fullfield:
            #newimdir = '/astro/clash5/cipphot/%s/mosdriz/%s/fullfield/images' % (shortfield, datestr)
            #newimdir = '/astro/clash5/cipphot/fullfield/%s/mosdriz/%s/fullfield/images' % (shortfield, datestr)
            newimdir = '/astro/clash1/cipphot/fullfield/%s/mosdriz/%s/fullfield/images' % (shortfield, datestr)
        else:
            newimdir = '/data02/cipphot/%s/mosdriz/%s/scale_65mas/images/clnpix_cosmetic' % (shortfield, datestr)
        
        newimfiles = []
        for imfile in imfiles:
            #newimdir = '/data02/cipphot/a2261/mosdriz/20110604/scale_65mas'
            if not exists(newimdir):
                makedirsmode(newimdir, 0775)
            
            imbase = os.path.basename(imfile)
            newimfile = join(newimdir, imbase)
            if not exists(newimfile):
                if not exists(newimfile[:-3]):  # gunzipped
                    run('cp -p %s %s' % (imfile, newimfile))

            if dirty:  # wht images too!
                whtfile    = imfile.replace('_drz', '_wht')
                newwhtfile = newimfile.replace('_drz', '_wht')
                if not exists(newwhtfile):
                    if not exists(newwhtfile[:-3]):  # gunzipped
                        run('cp -p %s %s' % (whtfile, newwhtfile))
                if strend(newwhtfile, '.gz'):
                    run('gunzip ' + newwhtfile)

            if strend(newimfile, '.gz'):
                run('gunzip ' + newimfile)
                newimfile = newimfile[:-3]
            newimfiles.append(newimfile)

        imfiles = newimfiles
    
    #outdir = '/astro/clash1/ftp/outgoing/color_images/'
    #outdir = join(outdir, field)
    #mkdir(outdir, 0775)
    outdir = '/astro/clash1/ftp/outgoing'
    outdir = join(outdir, field)
    outdir = join(outdir, 'HST/color_images/mosaicdrizzle_image_pipeline')
    if fullfield:
        outdir = join(outdir, 'fullfield')
    if not exists(outdir):
        makedirsmode(outdir, 0775)
    cd(outdir)

    print
    print imdir
    print 'Images last modified:'
    print datetime.datetime.fromtimestamp(immodtime).strftime('%Y-%m-%d %H:%M')

    colorimages = glob('*.png')
    if len(colorimages):
        colormodtime = oldest(colorimages)

        print
        print outdir
        print 'Color images last modified:'
        print datetime.datetime.fromtimestamp(colormodtime).strftime('%Y-%m-%d %H:%M')
    else:
        colormodtime = 0
    
    #print time.strftime('%Y%m%d%H%M', colormodtime)
    #print immodtime
    #print colormodtime
    REDO = 'REDO' in params.keys()
    redo = 'redo' in params.keys()
    print 'REDO', REDO
    print 'redo', redo
    redo = redo or REDO
    print 'redo', redo
    if (immodtime > colormodtime) or redo:
        # ARCHIVE COLOR IMAGES TO old/datetimestamp
        # as in cipcatwrap.py
        # '201201241106' = 2012 Jan 24 11:06AM
        datetimestr = datetime.datetime.fromtimestamp(colormodtime).strftime('%Y-%m-%d_%H%M')
        #datetimestr = time.strftime('%Y%m%d%H%M', colormodtime)
        olddir = join('old', datetimestr)
        print 'Archiving old color images to:'
        print olddir
        makedirsmode(olddir, 0775)
        run('mv %s/* %s/' % (outdir, olddir))
    else:
        print 'Up to date'

    print
    
    #instrs = 'acsir acs ir uvis'.split()
    instrs = 'acsir acs ir irbright uvis'.split()
    instrs = params.get('instr', instrs)
    if type(instrs) == str:
        instrs = [instrs]
    
    for instr in instrs:
        print 'Instrument', instr
        runtrilogy(field, imfiles, imdir, instr, dirty=dirty)

    rgbfitsfile = field+'_RGB.fits'
    delifold(rgbfitsfile,       field+'.png')
    delifold(rgbfitsfile+'.gz', field+'.png')
    if exists(rgbfitsfile) or exists(rgbfitsfile+'.gz'):
        print rgbfitsfile, 'EXISTS'
    else:
        im2rgbfits(field+'.png', headerfile=imfiles[0])
    
    run('chmod 664 *.*', 0)
    mkdir('log', 0775)
    run('chmod 775 log', 0)  # in case it was made already
    movefiles('%s_*_filters.txt' % field, 'log/')
    movefiles('*.in', 'log/')
    #run('mv %s_*_filters.txt log/' % field)
    #run('mv *.in log/')
    if exists('log/trilogyfilterlog.txt'):
        os.rename('log/trilogyfilterlog.txt', 'color_filters.txt')
    if glob('*.fits'):
        run('gzip *.fits')

   
def makeallcolorimages(params=None):
    cipdir    = '/data01/cipphot/pipeline'
    clusters = loadfile('clusters.txt', dir=cipdir)
    for field in clusters:
        makecolorimages(field, params)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        field = sys.argv[1]
        makecolorimages(field, params_cl())
    else:
        makeallcolorimages(params_cl())
