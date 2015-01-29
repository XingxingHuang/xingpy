from coetools import *
from glob import glob

#files = glob('*.fits')
#files = glob('*065mas*_drz.fits')
#files = glob('*_drz.fits')

if len(sys.argv) > 1:
    searchstr = sys.argv[1]
else:
    searchstr = '*_drz.fits'

files = glob(searchstr)

def extractlam(name):
    words = string.split(name, '_')
    for word in words:
        if word[0] == 'f':
            good = True
            for i in 1,2,3:
                good = good and (word[i] in string.digits)
            if good:
                filt = word
                lam = int(filt[1:4])
                if lam < 200:
                    lam = lam * 10
                return lam

splits = 0, 400, 1000, 2000
#splits = 400, 600, 700, 1000
if 0:
    splits = sys.argv[1:]
    if len(splits) == 0:
        splits = 0, 400, 1000, 2000
    else:
        splits = stringsplitatoi(splits)
        if len(splits) == 2:
            splits = 0, splits[0], splits[1], 2000

splits = array(splits)
print splits

lams = map(extractlam, files)
SI = argsort(lams)
lams = take(lams, SI)
files = take(files, SI)

n = len(lams)

prevchannel = ''
for i in range(n):
    j = splits.searchsorted(lams[i]) - 1
    if j in (0,1,2):
        channel = 'BGR'[j]
        if channel <> prevchannel:
            print
            print channel
        print files[i]
        prevchannel = channel


if 0: #for file in files:
    lam = extractlam(file)
    i = splits.searchsorted(lam) - 1
    print lam, i, 'BGR'[i]

