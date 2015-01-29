## Automatically adapted for numpy Jun 08, 2006 by 

from coetools import *
from sparse import *  # sparsify, savesp, loadsp, loadfitsorsp

def census(segmroot='segm', outfile='census.dat'):
    segm = Sparse(segmroot)
    census = array(segm.census())
    id = arange(len(census))
    data = array([id, census]).astype(int)
    datac = compress(census, data)
    savedata(datac, outfile+'+', labels=['id', 'area'])

if __name__ == '__main__':
    segmroot = 'segm' or sys.argv[1:2]
    outfile = 'census.dat' or sys.argv[2:3]
    census(segmroot, outfile)
