#!/usr/bin/env python
# Dec 03: revised for compare the catalog of Coe and Zheng.
#         The structure of Coe catalog has been motified as my style, but the Zheng catalog is different.
# Feb 11: more smooth

import os,sys,string,glob,time,math
import pdb
from pyraf import iraf
from scipy import array
import numpy as np
from pylab import *
   
   
##    1   2    3    4    5          6          7   f225w8         f275w10        f336w12        f390w14        f435w16        f475w18        f606w20        f625w22        f775w24        f814w26       f850lp28        f105w30        f110w32        f125w34        f140w36        f160w38         
## a209 nir  350    x    y         ra        dec   f225w          f275w          f336w          f390w          f435w          f475w          f606w          f625w          f775w          f814w         f850lp          f105w          f110w          f125w          f140w          f160w         
## a209   1  350 3904 3539  22.955281 -13.600110   0.0000 0.0000  0.0000 0.9386 28.1395 0.8123 27.9243 0.2774  0.0000 0.4543 27.6274 0.1724 27.2447 0.1069 27.9249 0.2993 27.7058 0.2935 27.9201 0.2084 26.8899 0.1615 27.0715 0.1395 26.9188 0.0858 26.3344 0.0990 26.6422 0.0771 28.2103 0.3150 

def readmag(cat):
  '''
  return the name and magnitudes
  '''
  r=open(cat,'r')
  lines=r.readlines()
  read_all = [line.split() for line in lines] 
  read = [i for i in read_all if i != [] ]    
  read = [i for i in read if not ('#' in i[0]) ]       # delete the elements begin with '#'
  data = []
  r.close()
  for i in range(len(read)):
     tmp = []
     for j in range(len(read[i])):
        if j>0:
          tmp.append(float(read[i][j]))
        else:
          tmp.append(read[i][j])  
     data.append(tmp)
  name = [i[:7] for i in data ]     ###
  mag  = [i[7:] for i in data ]  
  return(name,mag)
  
def readmag_zheng(cat):
  '''
  read cat with another format
  '''
  bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
  bands_used = ['f160w','f140w','f125w','f105w','f814w','f606w','f435w']
  r=open(cat,'r')
  lines=r.readlines()
  read_all = [line.split() for line in lines] 
  read = [i for i in read_all if i != [] ]    
  read = [i for i in read if not ('#' in i[0]) ]       # delete the elements begin with '#'
  data = []
  r.close()
  for i in range(len(read)):
     tmp = []
     for j in range(len(read[i])):
        if j>=0:
          tmp.append(float(read[i][j]))
        else:
          tmp.append(read[i][j])  
     data.append(tmp)
  name = [i[:4] for i in data ]     ###
  mag_all  = [i[4:] for i in data ]  
  mag=[]
  for line in mag_all:
    tmp=[99 for i in range(32)]
    for index in range(len(bands_used)):
        i = bands.index(bands_used[index]) # find the index 
        tmp[i*2] = line[index*2]
        tmp[i*2+1] = line[index*2+1]
    mag.append(tmp)    
  return(name,mag)
  
if __name__ == '__main__':  
  #################### param ####################
  cat = ['./cat/obj_frontier.cat']
  name = ['spec']
  color = ['black','green','red']

  try:
      field   = sys.argv[1]
      saveprefix = field
  except :
      saveprefix ='obj'
  savefile  = './img'


  # read
  plot_cat=[]
  plot_name=[]
  for catfile in cat:
    print 'read catalog Done: ',catfile
    catname,catmag = readmag(catfile)
    plot_cat.append(catmag)
    plot_name.append(catname)

  if not os.path.isdir(savefile): os.mkdir(savefile)


  # plot
  width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
       [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]    
  bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
  xx=[]
  xxerr=[]
  for i in range(len(width)):
    xx.append(math.log10(width[i][0]))    
    #xxerr.append(math.log10(width[i][1]/2.)) 



  for index in range(len(plot_cat[0])):
    print '************* '+saveprefix+' '+str(index+1)+' ***************'
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    for cati in range(len(plot_cat)):
       if len(plot_cat[cati]) != len(plot_cat[0]):
           sys.exit('check the length of '+name[cati])
       ylimit = 25.3   # this is the upper limit for y axis
       wave=[]
       x = []
       xe = []
       y = []
       ye = []      
       for key in bands:
         i = bands.index(key)
         # i 
         x.append( width[i][0] )
         wave.append(x)
         xe.append(width[i][1]/2)
         # y 
         yt = plot_cat[cati][index][i*2]
         yet = plot_cat[cati][index][i*2+1]
         y1 = yt
         y0 = yet*2.
         if abs(yt) > 30.0 : y1 = 30.1;y0 = 0.5
         if y1-0.4 < ylimit and y1>20: ylimit = y1-0.5
         if abs(yt) > 50.0 : yt = 35;yet = 0.1
         y.append(yt)
         ye.append(yet)
       if cati == 0:
           aa=ax.errorbar(array(x), array(y),xerr=array(xe), yerr=array(ye), fmt='s',color='black',markeredgecolor='black',ecolor='0.6',alpha=0.85,label=name[cati])  
           #mag1.append(y)
       else:
           aa=ax.errorbar(array(x), array(y), yerr=array(ye), fmt='o',label=name[cati],markersize=5,color = color[cati],alpha=0.5)  
        #elif cati == 1:
        #  bb=ax.errorbar(array(x), array(y),xerr=[array(0)], yerr=[array(ye)], fmt='s',color='red',markeredgecolor='red',ecolor='red',alpha=0.5,markersize=4)   
        #   mag2.append(y)
        #elif cati == 2: 
        #   cc=ax.errorbar(array(x), array(y),xerr=[array(0)], yerr=[array(ye)], fmt='o',color='green',markeredgecolor='green',ecolor='green',alpha=0.5,markersize=4)  
        #   mag3.append(y)
        #
      #
    # plot line
    ax.set_xscale('log')
    ax.set_xticks([235.9,270.4,335.5,392.1,432.5,477.3,588.7,624.2,764.7,802.4,916.6,1055.2,1153.4,1248.6,1392.3,1536.9,268.3])
    ax.set_xticklabels(['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w'],fontsize=8)
    ax.set_xlabel('wavelength')
    ax.set_ylabel('magnitude')
    ax.set_xlim(200,1700)
    ax.set_ylim(31.5,ylimit)
    leg = ax.legend(loc='lower right')
    #leg = ax.legend([aa[0],bb[0]],[name1,name2,name3],loc='lower right',bbox_to_anchor=(0.9,0.1), bbox_transform=gcf().transFigure)  
    leg.get_frame().set_alpha(0)
    #leg.draw_frame(False)
    for label in ax.get_xticklabels():
       label.set_rotation(45)
    #pdb.set_trace()
    # cluster name
    txt = 'obj: %5s' %(plot_name[0][index][0])
    #text(0.5,0.9,txt,ha='left',va='center',transform=ax.transAxes)
    title(txt)
    # ra dec
    txt1 = 'RA  : %10.6f' %(plot_name[0][index][5])
    txt2 = 'DEC: %10.6f' %(plot_name[0][index][6])
    txt3 = 'X    : %6.1f' %(plot_name[0][index][3])
    txt4 = 'Y    : %6.1f' %(plot_name[0][index][4])
    text(0.2,0.95,txt1,ha='left',va='center',transform=ax.transAxes)
    text(0.2,0.90,txt2,ha='left',va='center',transform=ax.transAxes)
    text(0.2,0.85,txt3,ha='left',va='center',transform=ax.transAxes)
    text(0.2,0.80,txt4,ha='left',va='center',transform=ax.transAxes)
    savename = saveprefix+'_'+str(index+1)+'_'+str(plot_name[0][index][0])+'_spec.jpg'
    output = os.path.join(savefile,savename)
    print '  Saveing  %s'  %(output)
    savefig(output)      


   