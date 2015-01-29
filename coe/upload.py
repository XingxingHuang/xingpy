from coeio import *
import shutil
from glob import glob

field = 'macs1115'
outrootdir = '/astro/clash1/ftp/outgoing/%s/HST/catalogs/mosaicdrizzle_image_pipeline/' % field

detcams = 'ACS_IR IR'.split()

def copyfile(infile, outfile, verbose=1):
    if verbose:
        print infile, '->'
        print outfile
        print
    shutil.copy2(infile, outfile)
    if os.path.isdir(outfile):
        outdir = outfile
        filename = os.path.basename(infile)
        outfile = join(outdir, filename)
    os.chmod(outfile, 0664)

def copydir(indir, outdir, verbose=1):
    if exists(outdir):
        shutil.rmtree(outdir)
    if verbose:
        print indir, '->'
        print outdir
        print
    shutil.copytree(indir, outdir)
    os.chmod(outdir, 0775)
    #print 'outdir', 0775
    #os.chmod(join(outdir, '*'), 0664)
    run('chmod 664 %s' % join(outdir, '*'), 0)

BPZfiles = """
photometry.cat
photometry.columns
photometry.bpz
photometry_bpz.cat
photometry_photbpz.cat
photometry.flux_comparison
photometry.probs
""".split('\n')[1:-1]

for detcam in detcams:
    subdir = detcam + '_detection'
    outdir = join(outrootdir, subdir)
    mkdir(outdir, 0775)
    detcam2 = detcam.replace('_', '')
    indir = '/data02/cipphot/macs1115/mosdriz/20120116/scale_65mas/cat_%s/120118' % detcam2

    catfile = field + '.cat'
    outname = field + '_' + detcam + '.cat'
    infile = join(indir, catfile)
    outfile = join(outdir, outname)
    copyfile(infile, outfile)

    # SExtractor
    outdir2 = join(outdir, 'SExtractor')
    copydir(join(indir, 'sex'), outdir2)
    copyfile(join(indir, 'zeropoints.txt'), outdir2)
    #run('gzip %s/*.fits' % outdir2)
    
    # Photo-z
    outdir2 = join(outdir, 'PhotoZ')
    #os.remove(outdir2)
    mkdir(outdir2, 0775)
    for infile in BPZfiles:
        infile2 = join(indir, infile)
        copyfile(infile2, outdir2)
    #run('gzip %s/photometry.probs' % outdir2)

    # Labeled color images
    outdir2 = join(outdir, 'labeled_images')
    mkdir(outdir2, 0775)
    infiles = glob(join(indir, '*.png'))
    for infile in infiles:
        #print 'Uploading', infile, 'to', outdir2
        copyfile(infile, outdir2)
