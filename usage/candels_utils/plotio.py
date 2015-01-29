###
# some program related to clash data
from os.path import *
import numpy as np
from glob import glob
import pdb
import string,sys,os
import pyfits
from pyraf import iraf
from pylab import *

from readcol import fgetcols
from readcol import fgetcols2
from program import printlog

######################################################################
###   make sure the following are right
######################################################################

HST_bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
HST_center= [2359.0, 2704.0, 3355.0, 3921.0, 4325.0, 4773.0, 5887.0, 6242.0, 7647.0, 8024.0, 9166.0, 10552.0, 11534.0, 12486.0, 13923.0, 15369.0]
HST_width = [467.0, 398.0, 511.0, 896.0, 618.0, 1344.0, 2182.0, 1463.0, 1171.0, 1536.0, 1182.0, 2650.0, 4430.0, 2845.0, 3840.0, 2683.0]

CFHT_bands = 'u b g v r i z Rp Ip rp'.split()

def read_band(field,HST=0,CFHT=0):
    '''
    read the band informations
    '''
    file_info = join(os.path.dirname(os.path.realpath(__file__)), 'band_%s.dat' %field)
    column = [1,2,3]
    bands,centers,widths = fgetcols2(file_info,column)
    info_center = {}
    info_width = {}
    info_bands=[]
    index_HST=[]
    index_CFHT=[]
    for i,band in enumerate(bands):
        if string.lower(band) in HST_bands:
            index_HST.append(i)
        if string.lower(band) in CFHT_bands:
            index_CFHT.append(i)
        info_center[string.lower(band)] = centers[i]*10000.
        info_width[string.lower(band)] = widths[i]*10000.
        info_bands.append(string.lower(band))
    if HST!=0:
        if CFHT ==0:
          return(info_bands,info_center,info_width, index_HST)
        else:
          return(info_bands,info_center,info_width,index_HST, index_CFHT)    
    else:
        return(info_bands,info_center,info_width) 
    
def read_cosmos_large_band():
    '''
    read the band informations
    '''
    file_info = join(os.path.dirname(os.path.realpath(__file__)), 'band_cosmos_large.dat')
    column = [1,2,3]
    bands,centers,widths = fgetcols2(file_info,column)
    info_center = {}
    info_width = {}
    info_bands=[]
    index_HST=[]
    index_CFHT=[]
    for i,band in enumerate(bands):
        info_center[band] = centers[i]*10000.
        info_width[band] = widths[i]*10000.
        info_bands.append(band)
    return(info_bands,info_center,info_width) 
            

def plotspec(ax,ID,x,xe,y,ye,color = 'black',text_mag=0,yscale=1):
    #y,ye = data_review(y,ye)
    aa=ax.errorbar(np.array(x), np.array(y),xerr=np.array(xe), yerr=np.array(ye), fmt='s',color=color,markeredgecolor=color,ecolor='0.6',alpha=0.85)   
    #limit
    ylimit = 24.
    ylimit_low = 28.2    
    y = np.array(y)
    tmpy = np.where((y<0.) & (ye<1.),99,y)
    miny = np.min(tmpy)
    if miny<ylimit:
        ylimit = miny-0.3
    tmpy = np.where((y<0.) | (y>31),-99,y)
    maxy = np.max(tmpy) 
    if maxy>ylimit_low:
        ylimit_low = maxy+0.1   
    
    for i in range(len(y)):
        if y[i]>90:
            ax.plot(x[i],ye[i],'v',color='red',markersize=16,alpha=0.7)
        if y[i]<-90:
            ax.plot(x[i],[ylimit_low-0.05],'^',color='blue',markersize=10,alpha=0.7)   
    if text_mag!=0 :
      for i in range(len(x)):
        txt = r'%5.2f$\pm$%5.2f' %(y[i],ye[i])
        ax.text(x[i],ylimit_low-0.5,txt,fontsize=10.,rotation='vertical',ha='center',va='bottom')
    ax.set_xticks([2359,2704,3355,3921,4325,4773,5887,6242,7647,8024,9166,10552,11534,12486,13923,15369])
    ax.set_xticklabels(['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w'],fontsize=8)
    ax.set_xlabel('wavelength')
    ax.set_ylabel('magnitude')
    ax.set_xlim(2000,17000)
    if yscale==1:
       ax.set_ylim(ylimit_low,ylimit)   
    #leg = ax.legend(loc='lower right')
    #leg.get_frame().set_alpha(0)
    for label in ax.get_xticklabels():
       label.set_rotation(45)
    # cluster name
    txt = 'obj: %5s' %(ID)
    #text(0.5,0.9,txt,ha='left',va='center',transform=ax.transAxes)
    #pdb.set_trace()
    title(txt)
    return(ax)
    
def data_review(y,ye):
    d=[]
    de= []

              