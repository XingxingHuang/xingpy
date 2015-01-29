from coeio import *
from coeim import *

colors = 255 * loaddata('50krandom.lut+', dir='/data01/cipphot/pipeline', silent=1)

def segmcolor(infile):
    segm = loadfits(infile)
    R, G, B = colors[:]
    R = R.take(segm)
    G = G.take(segm)
    B = B.take(segm)
    RGB = array([R, G, B])
    im = rgb2im(RGB)
    return im

infile = sys.argv[1]
infile = capfile(infile, 'fits')

if len(sys.argv) > 2:
    outfile = sys.argv[2]
else:
    outfile = recapfile(infile, 'png')

print 'Converting %s to %s...' % (infile, outfile)
im = segmcolor(infile)
#print 'Saving ', outfile
im.save(outfile)
