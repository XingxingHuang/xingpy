# /astro/clash1/ftp/outgoing/galaxies/catalogs

#from coeio import *
#import urllib
from coebasics import *

#clusz = loaddict('redshifts.txt', dir='~/CLASH/program')
#clusz = loadfile('redshifts.txt', dir='~/CLASH/program')
clusz = loadfile('redshifts.txt', dir='/data01/cipphot/pipeline')

#outdir = '/astro/clash1/ftp/outgoing/galaxies/catalogs'
outdir = '/astro/clash1/ftp/outgoing/galaxies/catalogs/IR_detection'
os.chdir(outdir)

for line in clusz:
    field, z = line.split()
    #IRdir = 'http://archive.stsci.edu/pub/clash/outgoing/%s/HST/catalogs/mosaicdrizzle_image_pipeline/IR_detection/' % field
    IRdir = '/astro/clash1/ftp/outgoing/%s/HST/catalogs/mosaicdrizzle_image_pipeline/IR_detection/' % field
    #IRfile = join(IRdir, IRfile)
    IRfile = field + '_IR.cat'
    IRfilegz = IRfile + '.gz'
    if not exists(IRfile):  # in outdir
        run('cp -p %s .' % join(IRdir, IRfile))

