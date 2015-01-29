#!/usr/bin/env python
# Dec 03: revised for compare the catalog of Coe and Zheng.
#         The structure of Coe catalog has been motified as my style, but the Zheng catalog is different.

import os,sys,string,glob,time,math
import pdb
from pyraf import iraf
from scipy import array
import numpy as np
from pylab import *


# analyze the beta with mpfit
def myfunct(p, fjac=None, x=None, y=None, err=None):
    # Parameter values are passed in "p"
    # If fjac==None then partial derivatives should not be
    # computed.  It will always be None if MPFIT is called with default
    # flag.
    model = func(x, p)
    # Non-negative status value means MPFIT should continue, negative means
    # stop the calculation.
    status = 0
    return([status, (y-model)/err] )

def func(x, p):
   a,b=p
   f= a + b*x
   return(f)
   
def getbeta(mag=None,mage=None,choosedbands=[4,5,6,7,8,9]):
   '''
    data include the magnitudes and errors for all 16 bands.
    choose the band between the index defined in the 'index' and delete the point with 0 value and too faint value
   '''
   wave = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
    	 [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]   
   wavelength = []
   for i in range(len(wave)):
      wavelength.append(math.log10(wave[i][0]*10.))                       
   

   x = [wavelength[i] for i in choosedbands]        			# choose the ACS/WFC bands   F336W >> F814W
   y 	  = [mag[i] for i in choosedbands]
   yerr   = [mage[i] for i in choosedbands]
   
   #x = [x[j] for j in range(len(ytmp))  if ytmp[j] != 0 and ytmp[j] < 28.5]
   #y = [y[j] for j in range(len(ytmp))  if ytmp[j] != 0 and ytmp[j] < 28.5]   # delete the value 0 and lower than 28.5
   #yerr = [yerr[j] for j in range(len(ytmp))  if ytmp[j] != 0 and ytmp[j] < 28.5]
   

   #test = [i for i in y if i !=0]
   #if test == [] or len(y)<4:
   #   print 'Not enough detection in all bands'
   #   return(0,0,0)
 
   from mpfit import mpfit
   x = array(x)
   y = array(y)
   err=array(yerr)
   p = [26.,0.1]
   fa = {'x':x, 'y':y, 'err':err}
   try:
     m = mpfit(myfunct, p, functkw=fa)
   except:
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     pdb.set_trace()
     sys.exit()
       
   beta = m.params[1]/2.5+2.
   beta_error =  m.perror[1] /2.5
   con = m.params[0]
   
   print 'status = ', m.status
   if (m.status <= 0):
      print 'error message = ', m.errmsg 
      pdb.set_trace()
   print 'parameters = ', m.params
   print 'para error = ', m.perror
   print 'beta       = ',beta , ' + ' ,beta_error
   
   return( con,beta, beta_error)
   
   
   
##    1   2    3    4    5          6          7   f225w8         f275w10        f336w12        f390w14        f435w16        f475w18        f606w20        f625w22        f775w24        f814w26       f850lp28        f105w30        f110w32        f125w34        f140w36        f160w38         
## a209 nir  350    x    y         ra        dec   f225w          f275w          f336w          f390w          f435w          f475w          f606w          f625w          f775w          f814w         f850lp          f105w          f110w          f125w          f140w          f160w         
## a209   1  350 3904 3539  22.955281 -13.600110   0.0000 0.0000  0.0000 0.9386 28.1395 0.8123 27.9243 0.2774  0.0000 0.4543 27.6274 0.1724 27.2447 0.1069 27.9249 0.2993 27.7058 0.2935 27.9201 0.2084 26.8899 0.1615 27.0715 0.1395 26.9188 0.0858 26.3344 0.0990 26.6422 0.0771 28.2103 0.3150 

def readmag(cat):
  r=open(cat,'r')
  lines=r.readlines()
  read_all = [line.split() for line in lines] 
  read = [i for i in read_all if i != [] ]    
  read = [i for i in read if not ('#' in i[0]) ]     	# delete the elements begin with '#'
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
  name = [i[:7] for i in data ] 		###
  mag  = [i[7:] for i in data ]  
  return(name,mag)
  
def readmag_zheng(cat):
  bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
  bands_used = ['f160w','f140w','f125w','f105w','f814w','f606w','f435w']
  r=open(cat,'r')
  lines=r.readlines()
  read_all = [line.split() for line in lines] 
  read = [i for i in read_all if i != [] ]    
  read = [i for i in read if not ('#' in i[0]) ]     	# delete the elements begin with '#'
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
  name = [i[:4] for i in data ] 		###
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
  
#################### read magnitude
cat1 = 'a2744_zheng.cat'
cat2 = 'a2744_runresults.log'
cat0 = 'a2744_bright_runresults.log'




'''
cat1_name,cat1_mag = readmag_zheng(cat1)
print 'read Zheng catalog DONE!'
cat2_name,cat2_mag = readmag(cat2)
print 'read Coe catalog Done!'i
'''
cat_name, cat_mag = readmag(cat0)

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


plot_cat = [cat_mag,cat_mag]
plot_name = [cat_name,cat_name]
saveprefix= 'a2744'
   
for index in range(len(plot_cat[0])):
    print '************* '+saveprefix+' '+str(index+1)+' ***************'
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    ylimit = 25.3   # this is the upper limit for y axis
    wave=[]
    mag1=[]
    mag2=[]
    mag3=[]
    for key in bands:
      i = bands.index(key)
      x = width[i][0]
      wave.append(x)
      xe = width[i][1]/2
      for cati in range(len(plot_cat)):
        y = plot_cat[cati][index][i*2]
        ye = plot_cat[cati][index][i*2+1]
        y1 = y
        y0 = ye*2.
        if abs(y) > 30.0 : y1 = 30.1;y0 = 0.5
        if y1-0.4 < ylimit and y1>20: ylimit = y1-0.5
        if abs(y) > 50.0 : y = 35;ye = 0.1
        if cati == 0:
           aa=ax.errorbar(array(x), array(y),xerr=[array(xe)], yerr=[array(ye)], fmt='s',color='black',markeredgecolor='black',ecolor='0.6',alpha=0.85)  
           mag1.append(y)
        elif cati == 1:
           bb=ax.errorbar(array(x), array(y),xerr=[array(0)], yerr=[array(ye)], fmt='s',color='red',markeredgecolor='red',ecolor='red',alpha=0.5,markersize=4)   
           mag2.append(y)
        #elif cati == 2: 
        #   cc=ax.errorbar(array(x), array(y),xerr=[array(0)], yerr=[array(ye)], fmt='o',color='green',markeredgecolor='green',ecolor='green',alpha=0.5,markersize=4)  
        #   mag3.append(y)
        #
      #
    # plot line
    '''
    for cati in range(len(plot_cat)):
      if cati == 0:
           ax.plot(wave,mag1,'-',color='black',alpha=0.85)
      elif cati == 1:
           ax.plot(wave,mag2,'-',color='red',alpha=0.3)  
      #elif cati == 2: 
      #     ax.plot(wave,mag3,'-',color='green',alpha=0.3)     
    #
    '''
    ax.set_xscale('log')
    ax.set_xticks([235.9,270.4,335.5,392.1,432.5,477.3,588.7,624.2,764.7,802.4,916.6,1055.2,1153.4,1248.6,1392.3,1536.9,268.3])
    ax.set_xticklabels(['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w'],fontsize=8)
    ax.set_xlabel('wavelength')
    ax.set_ylabel('magnitude')
    ax.set_xlim(200,1700)
    ax.set_ylim(31.5,ylimit)
    leg = ax.legend([aa[0],bb[0]],['Zheng','Coe'],loc='lower right',bbox_to_anchor=(0.9,0.1), bbox_transform=gcf().transFigure)  
    leg.get_frame().set_alpha(0)
    #leg.draw_frame(False)
    for label in ax.get_xticklabels():
       label.set_rotation(45)
    #pdb.set_trace()
    # cluster name
    txt = 'obj: %4i' %(int(plot_name[0][index][0]))
    text(0.3,0.9,txt,ha='left',va='center',transform=ax.transAxes)
    # ra dec
    txt1 = 'RA : %10.6f' %(plot_name[1][index][5])
    txt2 = 'DEC: %10.6f' %(plot_name[1][index][6])
    text(0.3,0.85,txt1,ha='left',va='center',transform=ax.transAxes)
    text(0.3,0.8,txt2,ha='left',va='center',transform=ax.transAxes)
    savename = saveprefix+'_'+str(index+1)+'_'+str(int(cat_name[index][0]))+'.png'
    savefig('./spec_compare_bright/'+savename)       
    

      
    '''    
    redshift = [ii for ii in range(4)]
    lines = [121.6,372.7,500.7,656.4]
    linewidth = 10.
    #for line in lines:
    #  plot([line*(1+z) for z in redshift],[28.+z/3. for z in redshift],'o-',color='0.4')
    #plot([0,9999],[28,28],'-')  
    ax.set_xlim(200,1700)
    #ax.set_yticks([29,28.67,28.3,28.,27.,26.,25.,24.,23.,22.,21.,20.])
    #ax.set_yticklabels(['z=3','z=2','z=1','z=0, 28',27.,26.,25.,24.,23.,22.,21.])
    #text(270,28.8,'Ly a')
    #text(850,28.8,'[O II]')
    #text(1350,28.8,'[O III]')
    #text(1600,28.4,'Ha')
    #text(1200,27.7,'Dmag1: %5.2f+%5.2f' %(abs(mag1-mag0),abs(mag1e+mag0e) )  )
    #text(1200,27.9,'Dmag2: %5.2f+%5.2f' %(abs(mag1-mag2),abs(mag1e+mag2e) )  )
    ax.set_ylim(30.5,ylimit)
    ax.set_xticks([235.9,270.4,335.5,392.1,432.5,477.3,588.7,624.2,764.7,802.4,916.6,1055.2,1153.4,1248.6,1392.3,1536.9,268.3])
    ax.set_xticklabels(['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w'],fontsize=8)
    text(1200,29.2,'Dmag1: %5.2f+%5.2f  %5.2f' %(abs(mag1-mag0),abs(mag1e-mag0e), abs(mag1-mag0)-abs(mag1e-mag0e))  )
    text(1200,29.5,'Dmag2: %5.2f+%5.2f  %5.2f' %(abs(mag1-mag2),abs(mag1e-mag2e), abs(mag1-mag2)-abs(mag1e-mag2e))  )
    for label in ax.get_xticklabels():
      label.set_rotation(45)
    ax.set_xlabel('wavelength')
    ax.set_ylabel('magnitude')
    ax.grid(True)
    name = self.source+'_'+CatalogType+'_'+band+'_%3.3d_%5.5d_%4.4d_%4.4d' %(count,num,int(x),int(y))+'_spec.png'
    savefig(os.path.join(self.outdir,name))
    #pdb.set_trace()
    '''
