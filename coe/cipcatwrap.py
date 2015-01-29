############################################
# CLASH Image Pipeline
# Photometry + Photo-z catalog generator
# -Dan Coe
############################################

"""
python $CIPPHOT/cipcat.py macs1115
cd /data02/cipphot/macs1115/mosdriz/20111202/scale_65mas/cat/120118

python $CIPPHOT/cipcat.py macs1115 -IR
cd /data02/cipphot/macs1115/mosdriz/20111202/scale_65mas/cat_IR/120118

python $CIPPHOT/bpzcolumns.py photometry

bpz photometry.cat -P $BPZPATH/bpzCLASH.param

python $CIPPHOT/bpzfinalize.py photometry

python $CIPPHOT/catfinal.py macs1115
"""

from coeio import *
import shutil
import time, datetime
from glob import glob

def older(file1, file2):
    t1 = os.stat(file1).st_mtime  # mtime better resolution than ctime
    t2 = os.stat(file2).st_mtime  # mtime better resolution than ctime
    print datetime.datetime.fromtimestamp(t1).strftime('%Y-%m-%d %H:%M'), file1
    print datetime.datetime.fromtimestamp(t2).strftime('%Y-%m-%d %H:%M'), file2
    return t1 < t2

def delifold(file1, file2):
    if exists(file1):
        if older(file1, file2):
            delfile(file1)


field   = sys.argv[1]  # a383 -or- abell_383
args = string.join(sys.argv[1:])
redo = '-redo' in sys.argv
fullfield = '-full' in sys.argv

#################################
# CATALOGS

cmd = 'python $CIPPHOT/cipcat.py %s' % args
run(cmd)

cipdir = '/data01/cipphot/pipeline'
#catdir = '/data02/cipphot/macs1115/mosdriz/20120116/scale_65mas/cat_IR/120118'
if fullfield:
    #cipoutdir = '/astro/clash5/cipphot/fullfield'
    cipoutdir = '/astro/clash1/cipphot/fullfield'
else:
    cipoutdir = '/data02/cipphot'

catdirfile = join(cipoutdir, 'catdir.txt')
catdir = loadfile(catdirfile)[0]
os.remove(catdirfile)
makedirsmode(catdir, 0775)
os.chdir(catdir)

outfile = field + '.cat'
outcatfile = outfile

if redo or not exists(outfile):
    run('python $CIPPHOT/bpzcolumns.py photometry')
    #run('bpz photometry.cat -P $BPZPATH/bpzCLASH.param')  # bpz alias not recognized
    run('python $BPZPATH/bpz.py photometry.cat -P $BPZPATH/bpzCLASH.param')
    run('python $CIPPHOT/bpzfinalize.py photometry')

    cmd = 'python $CIPPHOT/catfinal.py ' + field
    run(cmd)


#########
# UPLOAD

def copyfile(infile, outfile, verbose=1, overwrite=1):
    #shutil.copy2(infile, outfile)
    if os.path.isdir(outfile):
        outdir = outfile
        filename = os.path.basename(infile)
        outfile = join(outdir, filename)
        if exists(outfile) and not overwrite:
            return
    if verbose:
        print infile, '->'
        print outfile
        print
    run('cp -p %s %s' % (infile, outfile))
    os.chmod(outfile, 0664)

def copydir(indir, outdir, verbose=1):
    if exists(outdir):
        shutil.rmtree(outdir)
    if verbose:
        print indir, '->'
        print outdir
        print
    #shutil.copytree(indir, outdir)
    run('cp -pr %s %s' % (indir, outdir))
    os.chmod(outdir, 0775)
    #print 'outdir', 0775
    #os.chmod(join(outdir, '*'), 0664)
    run('chmod 664 %s' % join(outdir, '*'), 0)


def clonegz(infile):
    print infile
    outfile = infile + '.gz'
    print outfile
    delifold(outfile, infile)
    if not exists(outfile):
        tempfile = infile + '.copy'
        copyfile(infile, tempfile)
        run('gzip ' + tempfile)
        os.rename(tempfile+'.gz', outfile)

#copyfile('photometry.probs', 'copy.probs')
#run('gzip copy.probs')
#os.rename('copy.probs.gz', 'photometry.probs.gz')

def makedirsmode(newpath, mode=0775):
    """Make a directory path and set permissions along the way"""
    path = ''
    for dir in splitdirs(newpath):
        path = os.path.join(path, dir)
        if not exists(path):
            os.mkdir(path)
            chmod1(path, mode)

outrootdir = '/astro/clash1/ftp/outgoing/%s/HST/catalogs/mosaicdrizzle_image_pipeline/' % field
if fullfield:
    outrootdir = join(outrootdir, 'fullfield')

BPZfiles = """
photometry.cat
photometry.columns
photometry.bpz
photometry_bpz.cat
photometry_photbpz.cat
photometry.flux_comparison
photometry.probs
photometry.probs.gz
""".split('\n')[1:-1]

if '-IR' in sys.argv:
    detcam = 'IR'
else:
    detcam = 'ACS_IR'

subdir = detcam + '_detection'
outdir = join(outrootdir, subdir)
makedirsmode(outdir, 0775)

def makelink(src, lnk):
    if not exists(lnk):
        print '%s -> %s' % (lnk, src)
        os.symlink(src, lnk)
        run('chmod -h 0775 ' + lnk)
        #os.chmod(lnk, 0775)

imdir = '/astro/clash1/ftp/outgoing/%s/HST/images/mosaicdrizzle_image_pipeline' % field
lnk = join(outdir, 'images')
#makelink(imdir, lnk)

#oldoutfiles = glob(join(outdir, '*'))
#if len(oldoutfiles):

# '201201241106' = 2012 Jan 24 11:06AM
#datetimestr = time.strftime('%Y%m%d%H%M')
datetimestr = time.strftime('%Y-%m-%d_%H%M')
oldsubdir = join('old', datetimestr)

indir = os.getcwd()
catfile = field + '.cat'
outname = field + '_' + detcam + '.cat'
infile = join(indir, catfile)
outfile = join(outdir, outname)
if exists(outfile):
    #if older(outname, infile):
    if redo or older(outfile, infile):
        # ARCHIVE EVERYTHING TO outdir/old/datetimestamp
        olddir = join(outdir, oldsubdir)
        print 'Archiving old catalogs to:'
        print olddir
        makedirsmode(olddir, 0775)
        run('mv %s/* %s/' % (outdir, olddir))

if redo or not exists(outfile):
    copyfile(infile, outfile)
    clonegz(outfile)

    # SExtractor
    outdir2 = join(outdir, 'SExtractor')
    copydir(join(indir, 'sex'), outdir2)
    copyfile(join(indir, 'zeropoints.txt'), outdir2)
    copyfile(join(cipdir, 'filterImage.param'), outdir2)
    outfile2 = join(outdir2, 'detectionImage_SEGM.fits')
    clonegz(outfile2)
    #run('gzip %s/*.fits' % outdir2)

    # Photo-z
    clonegz(join(indir, 'photometry.probs'))
    outdir2 = join(outdir, 'PhotoZ')
    #os.remove(outdir2)
    mkdir(outdir2, 0775)
    for infile in BPZfiles:
        infile2 = join(indir, infile)
        copyfile(infile2, outdir2)


#################################
# LABELED COLOR IMAGES
# setenv PYTHONPATH {$PYTHONPATH}:{$CIPPHOT}:{$BPZPATH}:{$BPZPATH/plots}

"""
#ln /data01/trilogy/best/rxj1347.png
python $CIPPHOT/segmoutline.py rxj1347.png sex/detectionImage_SEGM rxj1347_segm.png photometry.cat
python $CIPPHOT/imlabel.py rxj1347_segm.png photometry.cat rxj1347_segm_id.png id 0 -COLOR yellow

python $CIPPHOT/bpzlabel.py rxj1347_segm.png rxj1347.cat rxj1347_segm_bpz.png
python $CIPPHOT/bpzlabel.py rxj1347.png rxj1347.cat rxj1347_bpz.png

python $CIPPHOT/bpzlabelcolor.py rxj1347.png rxj1347.cat rxj1347_bpzcolor.png
python $CIPPHOT/bpzlabelcolor.py rxj1347_segm.png rxj1347.cat rxj1347_segm_bpzcolor.png
"""

colordir = '/astro/clash1/ftp/outgoing/%s/HST/color_images/mosaicdrizzle_image_pipeline' % field
if fullfield:
    colordir = join(colordir, 'fullfield')

lnk = join(outdir, 'color_images')
#makelink(colordir, lnk)

# CREATE LABELED COLOR IMAGE IN THIS CIPPHOT DIRECTORY
outfile = field + '_bpzcolor.png'
if redo or not exists(outfile):
    #colordir = '/data01/trilogy/best/'
    colorimage = '%s.png' % field
    colorimagefull = join(colordir, colorimage)

    if exists(colorimagefull):
        print 'MAKING LABELED COLOR IMAGES'
        if not exists(colorimage):
            print os.getcwd()
            makelink(colorimagefull, colorimage)
            #os.symlink(colorimagefull, colorimage)

        if 1:
            run('python $CIPPHOT/imlabel.py %s.png photometry.cat %s_id.png id 0 -COLOR yellow' % (field, field))
            run('python $CIPPHOT/segmoutline.py %s.png sex/detectionImage_SEGM %s_segm.png photometry.cat' % (field, field))
            run('python $CIPPHOT/imlabel.py %s_segm.png photometry.cat %s_segm_id.png id 0 -COLOR yellow' % (field, field))
            
            run('python $CIPPHOT/bpzlabel.py %s.png %s.cat %s_bpz.png' % (field, field, field))
            run('python $CIPPHOT/bpzlabel.py %s_segm.png %s.cat %s_segm_bpz.png' % (field, field, field))

        print 'These next lines require: setenv PYTHONPATH {$PYTHONPATH}:{$CIPPHOT}:{$BPZPATH}:{$BPZPATH/plots}'
        run('python $CIPPHOT/bpzlabelcolor.py %s.png %s.cat %s_bpzcolor.png' % (field, field, field))
        run('python $CIPPHOT/bpzlabelcolor.py %s_segm.png %s.cat %s_segm_bpzcolor.png' % (field, field, field))
        
    else:
        print colorimagefull, 'NOT FOUND'


# UPLOAD
outdir2 = join(outdir, 'labeled_images')
mkdir(outdir2, 0775)
outfile2 = join(outdir2, outfile)
if exists(outfile2):
    if redo or older(outfile2, outcatfile):
        # ARCHIVE EVERYTHING TO outdir/old/datetimestamp
        olddir = join(outdir2, oldsubdir)
        makedirsmode(olddir, 0775)
        run('mv %s/* %s/', outdir2, olddir)

infiles = glob(join(indir, '*.png'))
for infile in infiles:
    #print 'Uploading', infile, 'to', outdir2
    copyfile(infile, outdir2, overwrite=False)
