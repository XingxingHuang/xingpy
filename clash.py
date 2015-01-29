#!/usr/bin/env python

# need pro_tools.py
import sys,pdb
import os
from os.path import *
from pro_tools import loaddict
from pro_tools import loaddictlines


def printlog(fname,text, ptime=0):
    '''
    write the text you define 
    '''
    if os.path.exists(fname):
      f = open(fname,'a')
    else:
      f = open(fname,'w')   
      txt='#!/usr/bin/env python'
      print >> f, txt
      del txt
      print fname+' created!'
    #ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
    #format = '%s %s'  
    #print >> f, format % (ptime,text)
    if ptime==1:
        ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
        format = '#\n###  %s  ###'  
        print >> f, format % (ptime)    
    print >>  f, text
    print text
    f.close()     
   
   
   
# print the clash pipeline commands
print '______________ TIPS FOR CLASH DATA _________________'
print '\npython /Users/xing/programs/xing/coe_my/clash_pipline/cipcat_xing.py [a209]-nopatch -IR \n'
print 'param: indir outdir inweightdir  indetdir patchdir rmsdir \n '
print 'param: redosex  searchstr  searchwhtstr   useweight\n '
print '_____________________________________'
print ' TYPE:  calsh [cluster]'
print '_____________________________________'


# print the programs for one cluster
ebvfile = '/Users/xing/data/zztxt/ebv.txt'
cmdfile = '/Users/xing/data/zztxt/cmd.txt'
indir = '/Users/xing/data/clash_cat'
outdir = '/Users/xing/Desktop/clash_highz/selection'

ebvs = loaddict(ebvfile)
cmds= loaddictlines(cmdfile)
if len(sys.argv)<1:
    sys.exit()
if len(sys.argv)>1:
    cluster = sys.argv[1]
    soutdir = '%s/%s_highz' %(outdir, cluster)
    if not isdir(soutdir): os.mkdir(soutdir)    
    
    logfile = '%s/%s_highz/0%s.log' %(outdir, cluster, cluster)
    printlog( logfile, '#' )
    printlog( logfile, '*'*60 )
    printlog( logfile, '#       Please run the following commands step by step' )
    printlog( logfile, '*'*60 )
    
    printlog( logfile, '#### Make catalog ####' )
    cmd1 = '%s  -RED  -eBV  %s ' %(cmds[cluster], str(ebvs[cluster]))
    cmd2 = 'python /Users/xing/data/run/catalog.py %s' %(cluster)
    cmd3 = 'cp /Users/xing/data/clash_cat/%s/images/tmp.reg  %s/%s_highz/%s_selection.reg' %(cluster,  outdir, cluster, cluster)
    printlog( logfile, cmd1 )
    printlog( logfile, cmd2 )
    printlog( logfile, cmd3 )
    print
    
    printlog( logfile, '#### Check image ####' )
    imgdir = '%s/%s/images' %(indir, cluster)
    detfile = join(imgdir, 'detection_red.fits')
    gdetfile = join(imgdir, 'gdetection_red.fits')
    f105wfile = join(imgdir, '*_f105w_sci.fits')
    cmd1 = 'gauss_smooth %s -file %s -getscale 1 -scalefraction 0.3' %(detfile, f105wfile)
    cmd2 = 'gauss_smooth %s -file %s -scale 0.95'  %(detfile, f105wfile)
    cmd3 = 'ds9 %s %s %s %s &'   %(gdetfile, join(imgdir, '*_f140w_sci.fits'), join(imgdir, '*_f125w_sci.fits'), join(imgdir, '*_f814w_sci.fits'))
    cmd4 = 'ds9 %s %s %s %s &'   %(gdetfile, join(imgdir, '*_f160w_sci.fits'), join(imgdir, '*_f140w_sci.fits'), join(imgdir, '*_f105w_sci.fits'))
    printlog( logfile, '# cd %s' %imgdir )
    printlog( logfile, cmd1 )
    printlog( logfile, cmd2 )
    printlog( logfile, cmd3 )
    printlog( logfile, cmd4 )
    print
    
    printlog( logfile, '#Plese select the catalog and save a region file named as     *selected.reg*    with xy format' )
    printlog( logfile, '#### Select catalog ####' )
    sindir = '%s/%s/cat_RED/**/' %(indir, cluster)
    cmd1 = 'cp %s %s %s ./' %(join(sindir, '*.txt'), join(sindir, '*.cat'), join(sindir, '*.column') ) 
    cmd2 = 'selectreg photometry.cat selected.cat selected.reg -dr 3.4'
    printlog( logfile, cmd1 )
    printlog( logfile, cmd2 )
    print
    
    # plot the img for candidates. need  
    # './photo8.cat'
    #  '../images'  '*_sci.fits'  '*_drz.fits'
    # output: .
    # './img/'    
    printlog( logfile, '#### Make high Z catalog ####' )
    cmd1 = 'python /Users/xing/programs/xing/frontier_findcat.py  selected.cat  photometry.cat'
    cmd2 = 'python /Users/xing/programs/xing/frontier_speccompare.py  %s'  %(cluster)
    cmd3 = 'python /Users/xing/programs/xing/frontier_plotimg.py   %s '  %(cluster)
    printlog( logfile, cmd1 )
    printlog( logfile, cmd2 )
    printlog( logfile, cmd3 )
    print
    
    printlog( logfile, '#### Check each object ####' )
    cmd1 = 'open %s/%s_highz/img/%s.html'  %(outdir, cluster, cluster)
    cmd2 = 'ds9 %s/%s_highz/img/*_1_*.fits &'  %(outdir, cluster)
    printlog( logfile, cmd1 )
    printlog( logfile, cmd2 )
    print

    