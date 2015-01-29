# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# http://docs.python.org/library/os.html

# cd /data02/cipphot
# python $CIPPHOT/compressfiles.py
# python $CIPPHOT/compressfiles.py fits probs

from coeio import *

# Compress all files ending in:
#exts = 'fits cat probs'.split()
exts = 'fits probs'.split()
if len(sys.argv) > 1:
    exts = sys.argv[1:]

print exts

#KB = 1024.
KB = 1000.
def bsize(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < KB:
            return "%3.1f%s" % (num, x)
        num /= KB

from os.path import join, getsize, exists, islink

totalsize = 0
totalcsize = 0

# walk does not follow symbolic links by default
for root, dirs, files in os.walk('.'):
    for file in files:
        fullfile = join(root, file)
        if not exists(fullfile):
            continue
        if islink(fullfile):
            continue
        cfile = file + '.gz'
        cfullfile = join(root, cfile)
        if exists(cfullfile):
            continue
        for ext in exts:
            if strend(file, '.'+ext):
                filesize = getsize(fullfile)
                print bsize(filesize), fullfile
                
                os.system('gzip %s' % fullfile)
                if not exists(cfullfile):
                    continue  # hard link won't gzip?
                
                cfilesize = getsize(cfullfile)
                print bsize(cfilesize), cfullfile
                
                totalsize += filesize
                totalcsize += cfilesize
                print bsize(totalsize - totalcsize), 'SAVED SO FAR'
                print

print bsize(totalsize)
print bsize(totalcsize)
