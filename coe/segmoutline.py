# python segmoutline.py COLOR_IMAGE SEGMENTATION_MAP OUTPUT_IMAGE <INPUT_CATALOG>
# (The input catalog is optional.
#    If input, then objects in the segmentation map but pruned from the catalog will be outlined in magenta.)
#
# python segmoutline.py ../trilogy/m1206_acsir.png detectionImage_SEGM m1206_segm.png macs1206.cat

from coeio import *
from PIL import Image, ImageDraw
from sparse import Sparse

inimage  = sys.argv[1]  # trilogy/m1206_acsir.png
insegm   = sys.argv[2]  # detectionImage_SEGM
outimage = sys.argv[3]  # m1206_segm.png
if len(sys.argv) > 4:
    incat = sys.argv[4]
    outcatsegm = os.path.basename(incat)
    outcatsegm = outcatsegm.replace('.', '_') + '_segm'
else:
    incat = None

segm = loadfits(insegm)
ny, nx = segm.shape
print (ny, nx)

#########

colordict = {
    'white'  : (1,1,1),
    'red'    : (1,0,0),
    'green'  : (0,1,0),
    'blue'   : (0,0,1),
    'cyan'   : (0,1,1),
    'magenta': (1,0,1),
    'yellow' : (1,1,0),
    'black'  : (0,0,0),
    }

def color2rgb(color):
    return tuple(255 * array(colordict[color]))

params = params_cl()  # other options: FONT, MIN, MAX

color = params.get('COLOR', 'white')
prunecolor = params.get('PRUNECOLOR', 'magenta')

color = color2rgb(color)
prunecolor = color2rgb(prunecolor)

if 'COLOR' in params:
    color = color2rgb(params['COLOR'])

#########

def segmoutline1(RGBin, segm, color):
    diff = segm[1:,:] - segm[:-1,:]
    diff = logical_not(equal(diff,0))
    dd[1:,:] = logical_or(dd[1:,:], diff)

    diff = segm[:,1:] - segm[:,:-1]
    diff = logical_not(equal(diff,0))
    dd[:,1:] = logical_or(dd[:,1:], diff)

def segmoutline(RGBin, segm, color):
    """Pixels outside segments will be marked
    At segment boundaries, put marks in lower numbered segment"""
    dd = zeros(segm.shape)

    diff = segm[1:,:] - segm[:-1,:]
    dd[1:,:]  = logical_or(dd[1:,:],  less(diff,0))
    dd[:-1,:] = logical_or(dd[:-1,:], greater(diff,0))
    
    diff = segm[:,1:] - segm[:,:-1]
    dd[:,1:]  = logical_or(dd[:,1:],  less(diff,0))
    dd[:,:-1] = logical_or(dd[:,:-1], greater(diff,0))

    R, G, B = RGBin

    R0, G0, B0 = color
    R = where(dd, R0, R)
    G = where(dd, G0, G)
    B = where(dd, B0, B)
    RGB = R, G, B
    
    return RGB

RGB = loadrgb(inimage)

segmcat = zeros(segm.shape)
bad = zeros(segm.shape)
if incat:
    RGB = segmoutline(RGB, segm, prunecolor)  # will get left for bad objects

    if exists(outcatsegm+'.fits'):
        segmcat = loadfits(outcatsegm)
    else:
        cat = loadcat(incat)
        catids = cat.id.astype(int)
        segmids = norep(segm.flat)
        prunedids = set(segmids) - set(catids) - set([0])
        prunedids = array(list(prunedids))
        print len(segmids), len(catids), len(prunedids)
        npruned = len(prunedids)
        sp = Sparse(insegm)
        for i in range(npruned):
            id = prunedids[i]
            #print '%4d  %d/%d' % (id, i+1, npruned)
            #bad = bad + equal(segm, id)
            sp.remobj(id)

        sp.save(outcatsegm)
        segmcat = sp.data
        segmcat.shape = segm.shape
        #savefits(segmcat, 'segmcat')

    RGB = segmoutline(RGB, segmcat, color)  # white for good ones

else:
    RGB = segmoutline(RGB, segm, color)  # make all white

savergb(RGB, outimage)
