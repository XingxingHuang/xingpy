## Automatically adapted for numpy Jun 08, 2006 by 

# CONVERTS COORDS FROM ONE COORDINATE SYSTEM TO THE OTHER USING WCS INFO
# GIVEN AN INPUT WCS & (x,y) LIST AND NEW WCS, OUTPUTS (x,y) LIST IN THE NEW WCS

# USAGE: python convertcoords.py <infits> <inxy> <outfits (new WCS)> <outxy>

# USAGE EXAMPLE: python convertcoords.py K Istars.xy G Gstars.xy
#   You can use my abbreviations for images in 3 coordinate systems:
#     A = ACS
#     K = Keck
#     G = GMOS
#     L = VLT

import os, sys, string
#from ksbtools import prunecols
from coetools import capfile

def prunecols(infile, cols, outfile, separator=" ", splitdef=0):
    """TAKES CERTAIN COLUMNS FROM infile AND OUTPUTS THEM TO OUTFILE
    COLUMN NUMBERING STARTS AT 1!
    ALSO AVAILABLE AS STANDALONE PROGRAM prunecols.py"""
    fin = open(infile, 'r')
    sin = fin.readlines()
    fin.close()

    fout = open(outfile, 'w')
    for line in sin:
        line = string.strip(line)
        if splitdef:
            words = string.split(line)
        else:
            words = string.split(line, separator)
        for col in cols:
            fout.write(words[col-1] + separator)
        fout.write("\n")
    fout.close()

def convertcoords(infits, inxy, outfits, outxy):
# acs3    fitsdict = {'A':'/home/coe/A1689/ACS/r3.fits', 'K':'/home/coe/A1689/KECK/R.fits', 'G':'/home/coe/Gemini/GMOS/r.fits', 'L':'/home/coe/A1689/KECK/L/L.fits', 'Anew':'/home/coe/A1689/ACS/new/newWCS.fits', 'Aold1':'/home/coe/A1689/ACS/newWCS.fits', 'Anew1':'/home/coe/A1689/ACS/new/phot/take1-shwag/newWCS.fits'}
    #fitsdict = {'A':'/home/coe/A1689/ACS/r3.fits', 'K':'/home/coe/A1689/KECK/R.fits', 'G':'/home/coe/Gemini/GMOS/r.fits', 'L':'/home/coe/A1689/KECK/L/L.fits', 'Anew':'/home/coe/A1689/ACS/new/newWCS.fits', 'Aold1':'/home/coe/A1689/oldWCS1', 'Anew1':'/home/coe/A1689/newWCS1.fits'}
    fitsdict = {'A':'/home/coe/A1689/ACS/r3.fits', 'K':'/home/coe/A1689/KECK/R.fits', 'G':'/home/coe/Gemini/GMOS/r.fits', 'L':'/home/coe/A1689/KECK/L/L.fits', 'Anew':'/home/coe/A1689/ACS/new/newWCS.fits', 'Aold1':'/home/coe/A1689/ACS/oldWCS1.fits', 'Anew1':'/home/coe/A1689/ACS/newWCS1.fits'}
    # Aold1 & Anew1 match -- see /export/data1/coe/A1689/ACS/new/phot/take1-shwag/README.txt
    infits = fitsdict.get(infits, infits)
    outfits = fitsdict.get(outfits, outfits)

    infits = capfile(infits, 'fits')
    outfits = capfile(outfits, 'fits')

    inroot = string.join(string.split(inxy, '.')[:-1], '.')
    inwcs = inroot + '.wcs'
    outtemp = 'temp.txt'

    if os.path.exists(inwcs):
        print inwcs, 'EXISTS. QUITTING.'
        sys.exit()
    if os.path.exists(outtemp):
        os.remove(outtemp)

    oss = os.system
    # ENOUGH DECIMAL PLACES, VERY IMPORTANT!
    print 'xy2sky -n 10 %s @%s > %s' % (infits, inxy, inwcs)
    oss('xy2sky -n 10 %s @%s > %s' % (infits, inxy, inwcs))
    print 'sky2xy %s @%s > %s' % (outfits, inwcs, outtemp)
    oss('sky2xy %s @%s > %s' % (outfits, inwcs, outtemp))
    prunecols(outtemp, (5, 6), outxy, splitdef=1)

if __name__ == '__main__':
    infits, inxy, outfits, outxy = sys.argv[1:]
    convertcoords(infits, inxy, outfits, outxy)

