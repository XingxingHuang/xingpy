from coeio import *
import HSTzp

filt = 'f850lp'
filt = 'f775w'
filt = 'f625w'
filt = 'f225w'
filt = 'f110w'
filt = 'f814w'
filt = 'f435w'
filt = sys.argv[1]

for root, dirs, files in os.walk('.'):
    for file in files:
        if filt+'_drz' in file:
            #print file
            fullfile = join(root, file)
            print HSTzp.HSTzp(fullfile, forcesec=True), file



