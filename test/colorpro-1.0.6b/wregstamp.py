## Automatically adapted for numpy Jun 08, 2006 by 

# $p/wregstamp.py inwcs instamp outwcs outstamp

# REMAPS A POSTAGE STAMP TO A NEW COORDINATE SYSTEM
# CENTER PIXEL SHOULD BE CENTERED IN NEW IMAGE
# (GOOD FOR REMAPPING PSFs!)
# LIKE IRAF'S WREGISTER...
# BUT INPUT POSTAGE STAMP DOESN'T HAVE WCS!

from coetools import savedata, loaddata, capfile, decapfile, delfile, fpart, odd, pause, fitssize
#from Numeric import *
from numpy import *
#import fitsio
from convertcoords import convertcoords
from shiftWCS import shiftWCS
from pyraf.iraf import imcopy, wcsmap, geotran, wcscopy, imdelete, imrename, wcsmap, geotran
import os, sys

def oddbox(x):
    """ENCLOSES x IN A RANGE OF ODD LENGTH"""
    xmin = min(x)
    xmax = max(x)
    xlo = int(floor(xmin))
    xhi = int(ceil(xmax))
    if odd(xhi - xlo):  # EVEN NUMBER OF PIXELS
        if fpart(xmax) > (1 - fpart(xmin)): # RHS CLOSER TO EDGE
            xhi += 1
        else:
            xlo -= 1
    return xlo, xhi


def wregstamp(inwcs, instamp, outwcs, outstamp):
    inwcs = capfile(inwcs, 'fits')
    instamp = capfile(instamp, 'fits')
    outwcs = capfile(outwcs, 'fits')
    outstamp = capfile(outstamp, 'fits')
    
    # CLEAN UP!
    delfile('temp.txt', silent=1)
    delfile('box.xy', silent=1)
    delfile('box.wcs', silent=1)
    delfile('box2A.xy', silent=1)
    delfile('center.xy', silent=1)
    delfile('center.wcs', silent=1)
    delfile('center2A.xy', silent=1)
    delfile('center2A.wcs', silent=1)

    # NEW: FIGURE OUT A GOOD xc, yc
    nyoutwcs, nxoutwcs = fitssize(outwcs)
    x2Ac = nxoutwcs/2 + 1
    y2Ac = nyoutwcs/2 + 1
    print 'center:'
    print x2Ac, y2Ac
    center = array([[x2Ac], [y2Ac]])
    savedata(center, 'center2A.xy+')
    #delfile('temp.txt')
    #print inroot+'wcs', outroot+'wcs1'
    convertcoords(outwcs, 'center2A.xy', inwcs, 'center.xy')
    xc, yc = loaddata('center.xy')
    print xc, yc

    nyinwcs, nxinwcs = fitssize(inwcs)
    #xc = nxinwcs / 2
    #yc = nyinwcs / 2
    nyinstamp, nxinstamp = fitssize(instamp)

    xlo = xc - nxinstamp/2 - 1
    ylo = yc - nyinstamp/2 - 1
    xhi = xc + nxinstamp/2 + 1
    yhi = yc + nyinstamp/2 + 1
    #print xc, yc, nxinstamp, nxinstamp/2, nyinstamp, nyinstamp/2
    #print xlo, xhi, ylo, yhi

    box = array([[xlo, ylo],
                 [xhi, ylo],
                 [xlo, yhi],
                 [xhi, yhi]])

    savedata(box, 'box.xy')

    convertcoords(inwcs, 'box.xy', outwcs, 'box2A.xy')

    x, y = loaddata('box2A.xy+')
    # NOW TO GET THE RANGE OF THESE POINTS
    # BUT MAKE SURE THE SIDES HAVE AN ODD NUMBER OF PIXELS!
    xloout, xhiout = oddbox(x)
    yloout, yhiout = oddbox(y)

    # SHOULDN'T NEED TO CHECK THIS NOW THAT I FOUND GOOD xc, yc FROM THE START
    nyoutwcs, nxoutwcs = fitssize(outwcs)
    if (0 < xloout < xhiout < nxoutwcs) and (0 < yloout < yhiout < nyoutwcs):
        pass
    else:
        print 'NEED TO FIND DIFFERENT POINT TO REMAP!'
        print 'EXITING PROGRAM.'
        sys.exit()

    instamprange = '[%d:%d,%d:%d]' % (xlo+1,xhi-1,ylo+1,yhi-1)
    inroot = os.path.split(instamp)[1]
    inroot = decapfile(inroot, 'fits')
    imdelete(inroot+'temp')
    imcopy(instamp, inroot+'temp')
    imdelete(inroot+'wcs')
    imcopy(inwcs+instamprange, inroot+'wcs')
    wcscopy(inroot+'temp', inroot+'wcs')
    imdelete(inroot+'wcs')
    imrename(inroot+'temp', inroot+'wcs')
    # inroot+'wcs' IS THE ORIGINAL PSF IMAGE WITH WCS INFO
    # (FROM A RANDOM STAMP FROM THE FULL IMAGE)

    # CREATE STAMP IN OUTPUT FRAME (FOR ITS WCS)
    outstamprange = '[%d:%d,%d:%d]' % (xloout+1,xhiout-1,yloout+1,yhiout-1)
    outroot = os.path.split(outstamp)[1]
    outroot = decapfile(outroot, 'fits')
    imdelete(outroot+'wcs1')
    imcopy(outwcs+outstamprange, outroot+'wcs1')

    # NOW SEE WHERE THE CENTER WILL FALL,
    # AND ADJUST THE WCS SO IT WILL LAND ON THE NEW CENTER
    delfile('center.xy', silent=1)
    delfile('center2A.xy', silent=1)
    xcs = nxinstamp/2 + 1
    ycs = nyinstamp/2 + 1
    center = array([[xcs], [ycs]])
    savedata(center, 'center.xy+')
    delfile('temp.txt')
    print inroot+'wcs', outroot+'wcs1'
    convertcoords(inroot+'wcs', 'center.xy', outroot+'wcs1', 'center2A.xy')
    x2Ac, y2Ac = loaddata('center2A.xy')
    #print x2Ac, y2Ac
    dx = fpart(x2Ac)  # 3.1 -> 0.1
    dy = fpart(y2Ac)
    if dx > 0.5:  # 2.9 -> 0.9 -> -0.1
        dx = dx - 1
    if dy > 0.5:
        dy = dy - 1
    print dx, dy
    shiftWCS(outroot+'wcs1', outroot+'wcs', dx=-dx, dy=-dy)
    
    # wregister ISN'T WORKING ON MY MACHINE, SO I'LL DO IT IN 2 STEPS:
    print "PRESS 'q' IN EACH OF THE 2 IRAF WINDOWS THAT POP UP..."
    delfile(outroot+'.db')
    print inroot+'wcs', outroot+'wcs', outroot+'.db'
    wcsmap(inroot+'wcs', outroot+'wcs', outroot+'.db')
    geotran(inroot+'wcs', outroot, outroot+'.db', inroot+'wcs', boundary='constant', interp='spline3')

    # CLEAN UP!
    delfile('temp.txt')
    delfile('box.xy')
    delfile('box.wcs')
    delfile('box2A.xy')
    delfile('center.xy')
    delfile('center.wcs')
    delfile('center2A.xy')
    delfile('center2A.wcs')
    delfile(inroot+'wcs.fits') # THIS ONE'S GOOD TO HAVE SOMETIMES
    delfile(outroot+'wcs1.fits')
    delfile(outroot+'wcs.fits')
    delfile(outroot+'.db')


if __name__ == '__main__':
    inwcs, instamp, outwcs, outstamp = sys.argv[1:]
    wregstamp(inwcs, instamp, outwcs, outstamp)
