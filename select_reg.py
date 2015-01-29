#!/usr/bin/env python
#
# selected the objects contained in the region file. So it will be more convenient to select sources.
# if the region file does not exit, it will create a region file for all of the objects.
#
from readcol import readcol
import pdb,os,sys

# the x y must be in the column m and n
ifile = 'F140W_all.cat'
m=2
n=3
ofile = 'F140W.cat'
region = 'reg_xy.reg'
oregion = 'region.reg'
# set to 1, if you want to select catalogs with the region file.
# set to 0, if you only want to create a file that could be read by ds9.

f=open(ifile)
icat=f.readlines()
f.close()
ocat=[]

if os.path.isfile(region):
    regx=readcol(region).getcol(1)
    regy=readcol(region).getcol(2)
else:
    print 'WARNING: region file does not exit! create the region.py without selection'
    pdb.set_trace()
    f=open(oregion,'w')
    for i_cat in range(len(icat)):
        if '#' in icat[i_cat]:
             continue
        tmp=icat[i_cat].split()
        ra=float(tmp[m-1])
        dec=float(tmp[n-1])
        text='%7.2f  %7.2f' %(ra,dec)
        print >> f,text
    f.close()
    pdb.set_trace()
    sys.exit(oregion+' created!')


count=0
for i_cat in range(len(icat)):
    yes=0
    if '#' in icat[i_cat]:
        continue
    for i_reg in range(len(regx)):
        tmp=icat[i_cat].split()
        ra=float(tmp[m-1])
        dec=float(tmp[n-1])
        if regx[i_reg]-ra<1. and regy[i_reg]-dec<1.:
            yes=1
    if yes==1:
        ocat.append(icat[i_cat][0:-1])
    else:
        count+=1
        tmp=icat[i_cat].split()
        num=tmp[0]
        ra=tmp[m-1]
        dec=tmp[n-1]
        print '%2i del %3i: %6.1f %6.1f' %(count,float(num),float(ra),float(dec))

f=open(ofile,'w')
for text in ocat:
    print >> f,text
f.close()
pdb.set_trace()