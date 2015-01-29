## Automatically adapted for numpy Jun 08, 2006 by 

from sexsegtools import loaddata, loadfile, capfile, pause, savefits, loadfits
import string, os
#from Numeric import * #array, zeros, Int, ravel, resize, fromstring
from numpy import * #array, zeros, Int, ravel, resize, fromstring
from compress2 import compress2 as compress
#import fitsio
#import struct

# sparse array w/o objspl
# val NOW RETURNING 0 WHEN x OR y ARE OUT OF RANGE

# THE NEW SPARSE FORMAT WILL CONSIST OF 2 FILES
# -- fits ARRAY
# -- PIXEL LIST (ENCODED: ny * y + nx)
# WILL ONLY SAVE fits FILE IF ALTERED; WILL SAVE fits HEADER

# (SEE sparse2.py FOR BINARY FORMATSPARSE ARRAYS)
# (SEE sparse1.py FOR TEXT FORMAT SPARSE ARRAYS)

  

# KEEP, I GUESS
def loadsp(input):
    sp = Sparse(input)
    return sp

# NOW, USE sp.save()
## def savesp(sp, outroot):
##     data = resize(sp.data, [sp.ny, sp.nx])
##     savefits(data, outroot)
##     savespl(sp.spl, outroot)

# sp. data(unraveled - after ravel is performed),
# spl, objspl, name, nx, ny, npix, nobj()
# IF altered, WILL SAVE FITS ON OUTPUT
# NEW sp3 FORMAT!!
# FITS IMAGE + PIXEL LIST
class Sparsenoobj:
    def __init__(self, input, input2=''):
        self.altered = 0
        self.name = 'anonymous'
        self.data = []
        self.assigninput(input)
        if input2:
            self.assigninput(input2)
        self.name = capfile(self.name, 'fits')[:-5]
        self.name = capfile(self.name, 'spl')[:-4]
        if self.data <> []:
            if not os.path.exists(self.name+'.fits'):
                savefits(self.data, self.name+'.fits')
            self.sparsify()
        else:
            self.loadfits()
            self.spl = []  # sparse pixel list
            if os.path.exists(self.name+'.spl'):
                if os.path.getmtime(self.name+'.spl') >= os.path.getmtime(self.name+'.fits'):
                    self.loadspl()
                else:
                    print 'YOUR %s IS NOT UP TO DATE.  WILL RE-BUILD...' % self.name+'.spl'
            if not self.spl:
                self.sparsify()
                self.savespl()

    # INPUT / OUTPUT
    def assigninput(self, input):
        """input MAY BE A FILENAME, AN ARRAY, OR A SIZE (TO START WITH AN ALL-ZERO ARRAY)"""
        if type(input) == str: # string type
            self.name = input
        else:  # array, list, tuple
            if len(input) == 2:
                print input[0], 'input0'
                try:
                    n = len(input[0])
                except:
                    n = 1
                if n == 1:
                    self.ny, self.nx = input
                    input = zeros(input, int)
            self.data = array(input)
    def save(self, name=''):
        if self.altered:
            if name:
                self.name = name
            self.savefits()
        # savespl(self.spl, self.name)
        self.savespl()
    def loadfits(self):
        self.data = loadfits(self.name).astype(int)
    def savefits(self):
        # data = resize(self.data, [self.ny, self.nx])
        print 'SAVING %s...' % (self.name+'.fits')
        savefits(self.data, self.name)
        self.altered = 0
    def loadspl(self):
        if len(self.data.shape) > 1:
            self.ny, self.nx = self.data.shape
            self.data = ravel(self.data)
        inspl = capfile(self.name, 'spl')
        print "LOADING %s..." % inspl
        fin = open(inspl, 'r')
        self.spl = fin.read()
        self.spl = fromstring(self.spl,int32)
        if os.uname()[0]=='OSF1' or os.uname()[4]=='i686':
            self.spl = self.spl.byteswap()
        fin.close()
        self.spl = self.spl.tolist()
        self.npix = len(self.spl)
    def savespl(self):
        outspl = capfile(self.name, 'spl')
        print 'SAVING %s...' % outspl
        fout = open(outspl, 'w')
        spl = array(self.spl)
        if os.uname()[0]=='OSF1' or os.uname()[4]=='i686':
            fout.write(spl.byteswap().tostring())
        else:
            fout.write(spl.tostring())
        fout.close()

    # SPARSIFYING
    def sparsify(self):
        print "BUILDING SPARSE PIXEL LIST..."
        if len(self.data.shape) > 1:
            self.ny, self.nx = self.data.shape
            self.data = ravel(self.data)
        self.spl = arange(len(self.data))
        self.spl = compress(self.data, self.spl)
        self.spl = self.spl.tolist()
        self.npix = len(self.spl)

    # GETTING & EDITING VALUES
##     def reid(self, idsold, idsnew):
##         for i in range(len(idsnew)):
##             idnew = idsnew[i]
##             idold = idsold[i]
##             if idsnew[i]:
##                 for iapp in range(idnew-self.hiobj()):  # ADD ADDITIONAL ELEMENTS IF NECESSARY
##                     self.objspl.append([])
##                 self.objspl[idnew] = self.objspl[idold]
##                 self.objspl[idold] = []
##                 put(self.data, self.objspl[idnew], idnew)
##             else:
##                 nold = len(self.objspl[idold])
##                 put(self.data, self.objspl[idnew], 0)
##                 self.objspl[idold] = []
##                 self.objspl.npix -= nold
##         self.altered = 1
##     reidlist = reid
    def nval(self):
        return self.npix
    def hiobj(self):
        return max(self.data)
##     def nobj(self):
##         n = 0
##         for obj in self.objspl:
##             if obj:
##                 n += 1
##         return n
    def yx2key(self, y, x):
        key = self.nx * y + x
        return key
    def key2yx(self, key):
        y = key / self.nx
        x = key % self.nx
        return (y, x)
    def val(self, y, x):
        if (0 <= y < self.ny) and (0 <= x < self.nx):
            key = self.nx * y + x
            return self.data[key]
        else:
            return 0
    def add(self, y, x, val):
        key = self.nx * y + x
        self.addk(key, val)
    def rem(self, y, x):
        key = self.nx * y + x
        self.remk(key)
    def alt(self, y, x, val):  # JUST CHANGE VALUE
        key = self.nx * y + x
        self.altk(key, val)
    def set(self, y, x, val):  # JUST CHANGE VALUE
        key = self.nx * y + x
        self.setk(key, val)
    def keys(self):
        return self.spl
    def values(self):
        return compress(self.data, self.data)
    def arr(self):
        return resize(self.data, (self.ny, self.nx))
    # ALTERNATIVE PROCEDURES, IF YOU WANT TO USE KEYS AS INPUT
    def valk(self, key):
        return self.data[key]
    def addk(self, key, val):
        if val:
            self.altered = 1
            oldval = self.data[key]
            if oldval:
                print 'WARNING: YOU "added" VALUE TO A PIXEL THAT ALREADY HAD A VALUE.  NEXT TIME, USE "alt" OR "set" INSTEAD.'
                self.altk(key, val)
            else:
                self.data[key] = val
                self.spl += [key]  # SHOULD I PUT IT IN SORTED ORDER?
                self.npix += 1
    def remk(self, key):
        val = self.data[key]
        if val:
            self.altered = 1
            self.data[key] = 0
            self.spl.remove(key)
            self.npix -= 1
        else:
            print "Missing key:", key
    def altk(self, key, val):  # JUST CHANGE VALUE
        oldval = self.data[key]
        if oldval and val:
            self.altered = 1
            self.data[key] = val
            #print key, 'k'
            self.spl.remove(key)
            self.spl += [key]
        elif not oldval:
            print 'Nothing there to begin with.  Need to "add" or "set".'
        else: # not val
            print 'To alter to zero, use "rem" or "set"'
    def setk(self, key, val):  # JUST CHANGE VALUE
        oldval = self.data[key]
        if oldval or val:
            if not oldval:
                self.addk(key, val)
            elif not val:
                self.remk(key)
            else:
                self.altk(key, val)
    # ALTERNATIVE PROCEDURES, IF YOU WANT TO USE INDEX AS INPUT
    def vali(self, i):
        return self.spl[i]

