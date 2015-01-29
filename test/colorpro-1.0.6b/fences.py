## Automatically adapted for numpy Jun 08, 2006 by 

# ~/p/fences.py infits outcon

# WILL ATTEMPT TO DRAW "FENCES" BETWEEN NEIGHBORING REGIONS IN A SEGMENTATION MAP
# THE RESULTING FILE CAN BE INPUT AS CONTOURS INTO ds9

# PROBLEMS w/ sparse3:
# CAN'T HAVE NEGATIVE VALUES IN SPARSE ARRAY (OR AT LEAST IF YOU'RE MAKING AN OBJECT LIST.  THAT'S WHY I SWITCHED TO sparsenoobj.py)
# val OF OUT OF RANGE x OR y NEEDS TO = 0

# HORIZONTAL & VERTICAL GRIDS ASSIGNED CURL OF DATA

# fences5 USES THE sparse3 FORMAT
# fences4 USES SPARSE MATRICES WITH THE NEW CLASS DEFINITION
# fences3 WILL USE SPARSE MATRICES

#from Numeric import *
from numpy import *
import sys
from sexsegtools import loadfits, pause, capfile, params_cl, flipud, between
from sparsenoobj import *
from sparse import *

global fout, format, horiz, vert, goval, ny, nx, lastlevel, debug

sys.setrecursionlimit(50000)  # DEFAULT IS 1000

goval = {'right':1, 'left':-1, 'up':1, 'down':-1, 'nowhere':0}
horizword = ['nowhere', 'right', 'left']
vertword = ['nowhere', 'up', 'down']
oneornone = [0, 1, 0]
lastlevel = 0

debug = 0
def pause1():
    if debug:
        pause()

def follow(iy, ix, gooldname, level):
    global fout, format, horiz, vert, goval, ny, nx, lastlevel, debug
    if debug:
	print "LEVEL = ", level
	print gooldname, ix, iy,
    if gooldname in ['left', 'right']:
        go = horiz.val(iy, ix)
        go1 = oneornone[go]
        if debug:
            print go, horizword[go], go1
            pause1()
        if go == goval[gooldname]:
            if level < lastlevel:
                fout.write('\n')
                fout.write(format % (ix + 1 - 0.5 * go, iy + 0.5))
            fout.write(format % (ix + 1 + 0.5 * go, iy + 0.5))
            #horiz.rem(iy, ix)
            horiz.set(iy,ix,0)
            lastlevel = level
            follow(iy, ix+go, horizword[go], level+1)
            follow(iy, ix+go1, 'up', level+1)
            follow(iy-1, ix+go1, 'down', level+1)
    else:
        go = vert.val(iy, ix)
        go1 = oneornone[go]
        if debug:
            print go, vertword[go], go1
            pause1()
        if go == goval[gooldname]:
            if level < lastlevel:
                fout.write('\n')
                fout.write(format % (ix + 0.5, iy + 1 - 0.5 * go))
            fout.write(format % (ix + 0.5, iy + 1 + 0.5 * go))
            #vert.rem(iy, ix)
            vert.set(iy,ix,0)
            lastlevel = level
            follow(iy+go, ix, vertword[go], level+1)
            follow(iy+go1, ix, 'right', level+1)
            follow(iy+go1, ix-1, 'left', level+1)
    if debug:
	print


def fences(infile, outfile, idlist=''):
    global fout, format, horiz, vert, goval, ny, nx, lastlevel
    #data = loadfitsorsp(infile)
    if idlist:
        data = Sparse(infile)
    else:
        data = Sparsenoobj(infile)
    ny = data.ny
    nx = data.nx
    vert = Sparsenoobj((ny,nx+1))
    horiz = Sparsenoobj((ny+1,nx))
    if idlist:
        if type(idlist) == str:
            idlist = ravel(loaddata(idlist)).astype(int)
    if debug:
        print data.arr()
    # for key in data.keys():
    # EXPAND SEGMENTS
##     keys = data.spl[:]
##     for key in keys:
##         y, x = data.key2yx(key)
##         if y:
##             if not data.val(y-1, x):
##                 data.add(y-1, x, data.val(y,x))
##         if x:
##             if not data.val(y, x-1):
##                 data.add(y, x-1, data.val(y,x))
    nkeys = len(data.spl)
    ikey = 0
##     print len(horiz.data)
##     print horiz.yx2key(3661, 1073)
##     print horiz.ny, horiz.nx
    if idlist:
        for id in idlist:
            for key in data.objspl[id]:
                y, x = data.key2yx(key)
                val = data.val(y, x)
                vert.set(y, x+1, cmp(val, data.val(y, x+1)))  # RIGHT
                horiz.set(y+1, x, -cmp(val, data.val(y+1, x)))  # UP
                vert.set(y, x, -cmp(val, data.val(y, x-1)))  # LEFT
                horiz.set(y, x, cmp(val, data.val(y-1, x)))  # DOWN
    else:
        for key in data.spl:
            if not (ikey % 10000):
                print '%d / %d' % (ikey, nkeys)
            ikey += 1
            y, x = data.key2yx(key)
            val = data.val(y, x)
            goahead = 1
            if idlist:
                goahead = (val in idlist)
            if goahead:
                if debug:
                    print 'val=', val
                    print '(x, y) = ', (x, y)
        ##             # CHANGED add TO set HERE
        ##             print cmp(val, data.val(y, x+1))
        ##             print vert.val(y, x+1)
        ##             print y, x+1
        ##             print 'vert:'
        ##             print vert.arr()
        ##             print vert.spl
        ##             # print vert.objspl
                vert.set(y, x+1, cmp(val, data.val(y, x+1)))  # RIGHT
                horiz.set(y+1, x, -cmp(val, data.val(y+1, x)))  # UP
                vert.set(y, x, -cmp(val, data.val(y, x-1)))  # LEFT
                horiz.set(y, x, cmp(val, data.val(y-1, x)))  # DOWN
                if debug:
                    print vert.arr()
                    print horiz.arr()
                    pause1()
    
    if debug:
        print vert.arr()
        print horiz.arr()
        pause1()
    if outfile:
        outfile = capfile(outfile, '.con')
    else:
 	outfile = capfile(infits,'.fits')[:-5] + '.con'
    fout = open(outfile, 'w')
    format = '%.1f %.1f\n'
    
    # while horiz.keys():
    while horiz.spl:
        # key = horiz.keys()[0]
        key = horiz.vali(0)
        go = horiz.valk(key)  # NO NEED TO LOOK AT vert.  YOU CAN'T HAVE A CONTOUR MADE OUT OF JUST vert (OR JUST horiz).
        iy, ix = horiz.key2yx(key)
        if debug:
            print ix, iy, go, horizword[go], 'MAIN LOOP'
            pause1()
        fout.write(format % (ix + 1 - 0.5 * go, iy + 0.5))
        fout.write(format % (ix + 1 + 0.5 * go, iy + 0.5))
        horiz.remk(key)  # DON'T TRACE THIS PART OF THE PATH AGAIN
        go1 = oneornone[go]
        follow(iy, ix+go, horizword[go], 0)
        follow(iy, ix+go1, 'up', 0)
        follow(iy-1, ix+go1, 'down', 0)
        fout.write('\n')
        # FOLLOW IT
        # AFTER YOU USE EACH ONE, TURN IT OFF
        
    fout.close()
    

if __name__ == '__main__':
    infits = sys.argv[1]
    outcon = ''
    if len(sys.argv) >= 3:
	outcon = sys.argv[2]
        if outcon[0] == '-':
            outcon = ''
    params = params_cl()
    idlist = params.get('i', '')
    fences(infits, outcon, idlist)

