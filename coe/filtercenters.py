from filttools import *
from bpz_tools import *

#allfilts = 'f225w f275w f336w f390w f435w f475w f606w f625w f775w f814w f850lp f105w f110w f125w f140w f160w'.split()
allfilts = 'f225w f275w f336w f390w f435w f475w f555w f606w f625w f775w f814w f850lp f105w f110w f125w f140w f160w'.split()

fout = open('filtercenters.dat', 'w')
fout.write('# Calculated using bpz_tools.filter_center via filtercenters.py\n')
for filt in allfilts:
    fullfilt = getfullfilt(filt)
    lam = filter_center(fullfilt)
    line = '%s %7.1f' % (filt.ljust(6), lam)
    fout.write(line+'\n')

fout.close()
