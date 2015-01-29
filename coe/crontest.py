#!/usr/bin/python

print 'STARTING crontest.py...'

print 'Logging in ~/cronlog.txt...'
import sys
sys.stdout = open("/Users/dcoe/cronlog.txt","w")
sys.stderr = open("/Users/dcoe/cronerrors.txt","w")

#sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages')
sys.path = []
sys.path.append('/usr/stsci/pyssgx/2.7.stsci_python')
sys.path.append('/usr/stsci/pyssgx/2.7')
sys.path.append('/data01/cipphot/pipeline')
sys.path.append('/data01/cipphot/pipeline/bpz')
sys.path.append('/data01/cipphot/pipeline/bpz/plots')

for p in sys.path:
    print p

import pylab

print 'SUCCESS!'
