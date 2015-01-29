#!/usr/bin/python

print 'STARTING crontest.py...'

import sys

print 'Logging in ~/cronlog.txt...'
sys.stdout = open("/Users/dcoe/cronlog.txt","w")
sys.stderr = open("/Users/dcoe/cronerrors.txt","w")

sys.path.append('/data01/cipphot/pipeline')
sys.path.append('/data01/cipphot/pipeline/bpz')
sys.path.append('/data01/cipphot/pipeline/bpz/plots')
#sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages/')
sys.path.append('/Library/Python/2.6/site-packages')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/PyObjC')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/wx-2.8-mac-unicode')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python26.zip')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-mac')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-mac/lib-scriptpackages')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-tk')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-old')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload')
sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages')
sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages/matplotlib')
#sys.path.append('')

print 'adding to path...'

for p in sys.path:
    print p

#from coeplott import *
#import matplotlib

#import matplotlib
#matplotlib.use('TkAgg')
import pylab  # NO GOOD
#from pylab import *
# I HAVE A FUNCTION close IN MLab_coe WHICH CONFLICTS WITH THE FIGURE CLOSER:
#from pylab import close as closecurrentfig
#import os
#from mycolormaps import *
#from coeio import *  # NO GOOD

print 'SUCCESS!'
