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
print ny, nx

def segmoutline(RGBin, segm, color):
    dd = zeros(segm.shape)

    diff = segm[1:,:] - segm[:-1,:]
    diff = logical_not(equal(diff,0))
    dd[1:,:] = logical_or(dd[1:,:], diff)

    diff = segm[:,1:] - segm[:,:-1]
    diff = logical_not(equal(diff,0))
    dd[:,1:] = logical_or(dd[:,1:], diff)

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
    RGB = segmoutline(RGB, segm, (255,0,255))  # will get left for bad objects

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

    RGB = segmoutline(RGB, segmcat, (255,255,255))  # white for good ones

else:
    RGB = segmoutline(RGB, segm, (255,255,255))  # make all white

savergb(RGB, outimage)
