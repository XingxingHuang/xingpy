# ~/lp/sparse.py  -- ADDED SWAP
# ~/colorpro/current/sparse.py

## Automatically adapted for numpy Jun 08, 2006 by 

from coeio import loaddata, loadfile, capfile, decapfile, pause, savefits, census, savedata, savedata1d, loadfits, savefits
import string, os
#from Numeric import * #array, zeros, Int, ravel, resize, fromstring
from numpy import * #array, zeros, Int, ravel, resize, fromstring
from compress2 import compress2 as compress
#import fitsio
#import struct

# ALSO SEE sparsenoobj.py

# THE NEW SPARSE FORMAT WILL CONSIST OF 2 FILES
# -- fits ARRAY
# -- PIXEL LIST (ENCODED: nx * y + x)
# WILL ONLY SAVE fits FILE IF ALTERED; WILL SAVE fits HEADER

# MERGED ~/p/sparsex.py WITH ~/p/old/sparse.py

# AFTER sparse3c.py, FIXED BUG IN reid1, reid:
#   WAS REPLACING RATHER THAN CONCATENATING TO EXISTING LIST

# (SEE sparse2.py FOR BINARY FORMATSPARSE ARRAYS)
# (SEE sparse1.py FOR TEXT FORMAT SPARSE ARRAYS)

  
def osbyteswap():
    return os.uname()[0]=='OSF1' or os.uname()[4]=='i686' or os.uname()[-1]=='i386'

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
class Sparse:
    def __init__(self, input, input2=''):
        self.altered = 0
        self.name = 'anonymous'
        self.data = []
        self.assigninput(input)
        if input2:
            self.assigninput(input2)
        self.name = decapfile(self.name, 'fits')
        self.name = decapfile(self.name, 'spl')
        if self.data == []:
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
        elif self.data.any():
            if not os.path.exists(self.name+'.fits'):
                savefits(self.data, self.name+'.fits')
            self.sparsify()
        else:  # self.data WAS ASSIGNED ZEROS (BASED ON SIZE) IN assigninput
            self.spl = []
            self.objspl = [[]]
            self.npix = 0

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
		    print 'INITIALIZING SPARSE ARRAY TO ZEROS'
                    self.ny, self.nx = input
                    input = zeros(input, int)
                    ## BELOW NOT QUITE RIGHT...
                    ## ACTUALLY IT JUST TAKES LONG TO BUILD THE HUGE ARRAY
                    # TAKES TIME TO UNRAVEL
                    # LET'S JUST MAKE IT RIGHT THE FIRST TIME:
                    #input = zeros(input[0] * input[1], 'int')
                    #self.data = input
            self.data = ravel(array(input))  # ravel ADDED MUCH LATER
    def save(self, name=''):
        if self.altered:
            if name:
                self.name = name
            self.savefits()
        # savespl(self.spl, self.name)
        self.savespl()
        print max(self.data)
    def loadfits(self):
        self.data = loadfits(self.name).astype(int)
    def dataarr(self):
        return reshape(self.data, [self.ny, self.nx])
    def savefits(self, name=''):
        if name:
            self.name = name
        # data = resize(self.data, [self.ny, self.nx])
        # savefits(data, self.name)
        print 'SAVING %s...' % (self.name+'.fits')
        data = reshape(self.data, [self.ny, self.nx])
        savefits(data, self.name)
        # resize IS A HUGE PROBLEM FOR A HUGE ARRAY: TRIES TO MAKE A COPY
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
        if osbyteswap():
            self.spl = self.spl.byteswap()
        fin.close()
        self.spl = self.spl.tolist()
        self.npix = len(self.spl)
        self.buildobjspl()
    def savespl(self, name=''):
        if name:
            self.name = name
        outspl = capfile(self.name, 'spl')
        print 'SAVING %s...' % outspl
        fout = open(outspl, 'w')
        spl = array(self.spl)
        if osbyteswap():
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
        self.buildobjspl()
    def buildobjspl(self):
        print "BUILDING OBJECT PIXEL LISTS..."
        self.objspl = [[]]
        if self.data <> []:
            datac = take(self.data, self.spl)
            SI = argsort(datac)
            datacs = take(datac, SI)
            spls = take(self.spl, SI)
            hiobj = max(datacs)
            objlist = arange(hiobj+1) + 1
            census = searchsorted(datacs, objlist)
            for i in range(len(objlist)-1):
                iobj = objlist[i]
                lo = census[i]
                hi = census[i+1]
                self.objspl.append(spls[lo:hi].tolist())

    # GETTING & EDITING VALUES
    def census(self):
        cens = []
        for obj in self.objspl:
            cens.append(len(obj))
        return cens
    def reid1(self, idold, idnew):
        ncur = len(self.objspl)
        # ADD ADDITIONAL ELEMENTS IF NECESSARY
        #self.objspl[ncur:] = [[]] * (idnew - ncur + 1)
        # - ALL PREVIOUS OBJECTS GOT SET ALSO
        for i in range(idnew - ncur + 1):
            self.objspl.append([])
        nnew = len(self.objspl[idnew])
        # CONCATENATE RATHER THAN REPLACE!!
        self.objspl[idnew][nnew:] = self.objspl[idold][:]
        self.objspl[idold] = []
        put(self.data, self.objspl[idnew], idnew)
        self.altered = 1
    def swapids(self, id1, id2):
        obj1 = self.objspl[id1]
        obj2 = self.objspl[id2]
        self.objspl[id1] = obj2[:]
        self.objspl[id2] = obj1[:]
        put(self.data, self.objspl[id1], id1)
        put(self.data, self.objspl[id2], id2)
        self.altered = 1
    def reid(self, idsold, idsnew):  # NOTE: idsold-idsnew MUST CONTAIN ALL IDS
        newobjspl = [[]]
        for i in range(len(idsnew)):
            idnew = idsnew[i]
            idold = idsold[i]
            #print idold, idnew
            if idnew:
                # ADD ADDITIONAL ELEMENTS IF NECESSARY
                newobjspl[len(newobjspl):] = [[]] * (idnew - len(newobjspl) + 1)
                nnew = len(newobjspl[idnew])
                # CONCATENATE RATHER THAN REPLACE!!
                newobjspl[idnew][nnew:] = self.objspl[idold][:]
                put(self.data, newobjspl[idnew], idnew)
            else:
                nold = len(self.objspl[idold])
                put(self.data, self.objspl[idnew], 0)
                self.npix -= nold
        self.objspl = newobjspl
        self.altered = 1
    reidlist = reid
    def nval(self):
        return self.npix
    def hiobj(self):
        return len(self.objspl)-1
    def ids(self):
        ids = []
        for i in range(len(self.objspl)):
            if self.objspl[i]:
                ids.append(i)
        return ids
        #return compress(self.objspl, id)
    def nobj(self):
        n = 0
        for obj in self.objspl:
            if obj:
                n += 1
        return n
    def key2yx(self, key):
        y = key / self.nx
        x = key % self.nx
        return (y, x)
    def yx2key(self, y, x):
        key = self.nx * y + x
        return key
    def val(self, y, x):
        key = self.nx * y + x
        try:
            return self.data[key]
        except:
            print 'WARNING: (%d,%d) OUT OF RANGE' % (x,y)
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
        return compress(data, data)
    # REMOVE A WHOLE OBJECT
    def remobj(self, val):
        keys = self.objspl[val]
        put(self.data, keys, 0)
        self.altered = 1
        self.npix -= len(keys)
        self.objspl[val] = []
##     def remobj(self, val):
##         keys = self.objspl[val][:]
##         for key in keys:
##             self.remk(key)
    # ALTERNATIVE PROCEDURES, IF YOU WANT TO USE KEYS AS INPUT
    def valk(self, key):
        try:
            return self.data[key]
        except:
            print 'WARNING: key=%d OUT OF RANGE in sparse array %s' % (key, self.name)
            return 0
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
                for iapp in range(val-self.hiobj()):
                    self.objspl.append([])
                self.objspl[val] += [key]
                self.npix += 1
    def remk(self, key):
        val = self.data[key]
        if val:
            self.altered = 1
            self.data[key] = 0
            self.spl.remove(key)
            self.objspl[val].remove(key)
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
            # print 'oldval =', oldval
            # print self.objspl[oldval]
            self.objspl[oldval].remove(key)
            for iapp in range(val-self.hiobj()):
                self.objspl.append([])
            self.objspl[val] += [key]
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
    def setkeys(self, keys, val):  # ASSUMES val > 0
        oldvals = take(self.data, keys)
        cens = census(oldvals)
        for oldval in cens.keys():
            oldvalkeys = compress(equal(oldval, oldvals), keys)
            for oldvalkey in oldvalkeys:
                if oldval:
                    self.objspl[oldval].remove(oldvalkey)  # WAS SOMETHING THERE, REMOVE THIS PIXEL FROM THAT OBJECT'S PIXEL LIST
                else:
                    self.spl += [oldvalkey]  # WAS NOTHING THERE, ADD THIS PIXEL TO THE OVERALL SPARSE PIXEL LIST
        for iapp in range(val-self.hiobj()):
            self.objspl.append([])
        self.objspl[val] = keys
        put(self.data, keys, val)
        if 0 in cens.keys():
            self.npix += cens[0]
        self.altered = 1
    def addkeys(self, keys, val):  # CAN APPEND INSTEAD OF JUST ADDING KEYS
        oldvals = take(self.data, keys)
        cens = census(oldvals)
        for oldval in cens.keys():
            oldvalkeys = compress(equal(oldval, oldvals), keys)
            for oldvalkey in oldvalkeys:
                if oldval:
                    self.objspl[oldval].remove(oldvalkey)  # WAS SOMETHING THERE, REMOVE THIS PIXEL FROM THAT OBJECT'S PIXEL LIST
                else:
                    self.spl += [oldvalkey]  # WAS NOTHING THERE, ADD THIS PIXEL TO THE OVERALL SPARSE PIXEL LIST
        for iapp in range(val-self.hiobj()):
            self.objspl.append([])
        ncur = len(self.objspl[val])
        self.objspl[val][ncur:] = keys
        put(self.data, keys, val)
        if 0 in cens.keys():
            self.npix += cens[0]
        self.altered = 1
    # ALTERNATIVE PROCEDURES, IF YOU WANT TO USE INDEX AS INPUT
    def vali(self, i):
        return self.spl[i]

