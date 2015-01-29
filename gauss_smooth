#!/usr/bin/env python
# smooth

import scipy.signal 
import pyfits
import pdb,sys
import numpy as np
import glob
import shutil
from os.path import *
import os

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
import string
def params_cl(args=None, converttonumbers=True):
    """returns parameters from command line ('cl') as dictionary:
    keys are options beginning with '-'
    values are whatever follows keys: either nothing (''), a value, or a list of values
    all values are converted to int / float when appropriate
    need:  
       striskey
       str2num
    """
    if args == None:
        list = sys.argv[:]
    else:
        list = args
    i = 0
    dict = {}
    oldkey = ""
    key = ""
    list.append('')  # EXTRA ELEMENT SO WE COME BACK AND ASSIGN THE LAST VALUE
    while i < len(list):
        if striskey(list[i]) or not list[i]:  # (or LAST VALUE)
            if key:  # ASSIGN VALUES TO OLD KEY
                if value:
                    if len(value) == 1:  # LIST OF 1 ELEMENT
                        value = value[0]  # JUST ELEMENT
                dict[key] = value
            if list[i]:
                key = list[i][1:] # REMOVE LEADING '-'
                value = None
                dict[key] = value  # IN CASE THERE IS NO VALUE!
        else: # VALUE (OR HAVEN'T GOTTEN TO KEYS)
            if key:
                if value:
                    if converttonumbers:
                        value.append(str2num(list[i]))
                    else:
                        value = value + ' ' + list[i]
                else:
                    if converttonumbers:
                        if ',' in list[i]:
                            #value = stringsplitatof(list[i], ',')
                            value = list[i].split(',')
                            for j in range(len(value)):
                                value[j] = str2num(value[j])
                        else:
                            value = [str2num(list[i])]
                    else:
                        value = list[i]
        i += 1

    return dict


def striskey(str):
    """IS str AN OPTION LIKE -C or -ker
    (IT'S NOT IF IT'S -2 or -.9)"""
    iskey = 0
    if str:
        if str[0] == '-':
            iskey = 1
            if len(str) > 1:
                iskey = str[1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    return iskey

def str2num(str, rf=0):
    """CONVERTS A STRING TO A NUMBER (INT OR FLOAT) IF POSSIBLE
    ALSO RETURNS FORMAT IF rf=1"""
    try:
        num = string.atoi(str)
        format = 'd'
    except:
        try:
            num = string.atof(str)
            format = 'f'
        except:
            if not string.strip(str):
                num = None
                format = ''
            else:
                words = string.split(str)
                if len(words) > 1:  # List
                    num = map(str2num, tuple(words))
                    format = 'l'
                else:
                    num = str
                    format = 's'
    if rf:
        return (num, format)
    else:
        return num

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++

def createker():
    ker = np.array([
        [0.5, 1,   0.5],
        [1,   0,   1  ],
        [0.5, 1,   0.5]])
    ker = ker / sum(ker.flat)
    return(ker)

def kernel_gauss(m,std):
    t =  scipy.signal.gaussian(m,std)
    ker = t.reshape(m, 1) * t.reshape(1, m)
    ker = ker / sum(ker.flat)
    return(ker)    
    
def kernel_gauss2(m,std):
    '''
    equal to minus smoothed data  
    ! do not use it
    '''      
    '''
    @This ker will not make the low surface objects clear
    ker = np.array([
        [-1, -1,   -1  , -1  , -1],
        [-1,  -0.5,   -0.5  ,  -0.5 , -1],
        [-1,  -0.5,   20     ,  -0.5 , -1] ,
        [-1,  -0.5,   -0.5  ,  -0.5 , -1] ,
        [-1, -1,   -1  ,  -1 , -1]])    
    ker = ker / 20.
    return(ker)
    '''      
    
    t1 = scipy.signal.gaussian(m,1)
    t2 = scipy.signal.gaussian(m,std)
    t = (t1+t2*0.5)/1.5
    ker = t.reshape(m, 1) * t.reshape(1, m)
    ker = ker / sum(ker.flat)
    return(ker)
        
        
    # do not use the following
    t =  scipy.signal.gaussian(m,std)
    ker = t.reshape(m, 1) * t.reshape(1, m)
    ker = ker/np.sum(ker.flat)
    t =  scipy.signal.gaussian(m,4)
    ker2 = t.reshape(m, 1) * t.reshape(1, m)
    ker2 = ker2/np.sum(ker2.flat)
        
    ker0 = ker*0.
    #ker0[m//2, m//2] = sum(ker.flat)*2
    ker0[m//2, m//2] = 1.
    ker_out = ker0 - ker+ker2*0.7
    #ker_out = ker_out / sum(ker_out.flat)  # norm to 1.
    ker_out = ker_out /0.7 # norm to 1.
    return(ker_out)    
    
    
def kernel_flat(m):
    t = scipy.signal.boxcar(m)
    ker = t.reshape(m, 1) * t.reshape(1, m)
    ker = ker / sum(ker.flat)
    return(ker)    

def savefits(data, header,output):
    '''
	save fits file based on the header of the other file.
    '''
    hdu = pyfits.PrimaryHDU(data)
    hdu.header = pyfits.getheader(header)
    hdulist = pyfits.HDUList([hdu]) 
    if isfile(output): os.remove(output)
    hdulist.writeto(output)   

def suggestscale(data1,data2,fraction = 0.05,silent = 0):
    '''
    get the scale between file1 and file2. (file1/file2)
    
    '''
    if len(data1)!=len(data2):
        print '\nCheck the length: %i %i\n' %(len(data1),len(data2) ) 
        pdb.set_trace()
    if silent == 0 :
        print '\n reshape and sort ...'
    list1 = data1.reshape(np.size(data1))
    list2 = data2.reshape(np.size(data2))
    list1 = np.where( list1>1e-10 ,list1,0)
    list1 = np.where( list2>1e-10 ,list1,0)

    list2 = np.where( list1>1e-10 ,list2,0)
    list2 = np.where( list2>1e-10 ,list2,0)

    list1=np.sort(list1 )
    list2=np.sort(list2) 

    index = np.size(list1)*(1.-fraction/100.)
    ratio = list1[index:]/list2[index:]
    ratio_median = np.median(ratio)
    ratio_mean = np.mean(ratio)
    number = len(np.where(list1>0)[0])
    num_total = len(list1)
    print 'Number_observed /Total    :  %i / %i ~ %6.4f'    %(number,num_total,float(number)/num_total*100.)
    print 'Mean of the ratio    :  %f' %(ratio_mean)
    print 'Median of the ratio :  %f' %(ratio_median)
    print
    return(ratio_mean,ratio_median)

def cutfraction(data, fraction):
    '''
    set the values to 0.
    '''
    datalist = data.reshape(np.size(data))
    datalist = datalist[np.where((datalist>0) & (datalist<1e8) )]
    datalist_sort = np.sort(datalist)
    index = np.size(datalist_sort)*(fraction)
    threshold = datalist_sort[index]
    outdata = np.where(data>threshold, threshold+np.sqrt(data), data)
    print 'threshold, ', threshold
    return(outdata)
    
  
def myglob(file0):
     file = glob.glob(file0)
     if len(file)>1 :
        print 'ERROR: Check %s' %(file)
        sys.exit()
     if len(file)==0:  
        print 'ERROR: no such file %s' %(file0)
     outfile = file[0]
     return(outfile)

if __name__ == '__main__':
  import getopt
  from os.path import *

  mod  = basename(sys.argv[0])
  #text = 'Tips: add | awk \'{printf "%f\\n",$1}\' '
  txt = 'Write by:\n    Xingxing Huang (hxx@mail.ustc.edu.cn) '
  txt += '\nUsage:\n'
  usage=txt+mod+" file1 [-file *.fits]  [-smooth 1] [-kernel  f/g/g2] [-kersize 7] [-mediansize 1] [-kerfraction 1] [-scale 0.95] [-replace 0]  [-getscale 0] [-scalefraction 0.05]   [-revmovesig  -1]  [-divide ]\n"
  usage += 'Tips: \n'
  usage += '    -file    if not defined, we use the image itself to substract.\n'
  usage += '    smooth = 1      default 1. The image will not smooth before the filtering\n'
  usage += '    kernel = f      Kernel flat is better when you want to subtract the smoothed image from the original image itself.\n'
  usage += '    kerfraction = 1 The pixels with value>this fraction will be set to 0 before smooth. 0.99 can be good for most cases.\n'
  usage += '    mediansize  = 1 using median filter before smooth the image.\n'
  usage += '    replace =1   when you want to overwrite the original file\n'
  usage += '    getscale =1  before you run this commands to get the scale\n'
  usage += '    removesig =100  remove pixels with S/N>0.5\n'
  usage += '    divide  will save smoothdata/data\n'
  opts1="i"
  opts2=[]
  
  # read param
  try:
     opts, args = getopt.getopt(sys.argv[1:],opts1,opts2)
  except getopt.GetoptError:
     sys.exit(usage)
  params = params_cl()
  if len(args) <1 : 
     sys.exit(usage)
  
  # define params
  file1 = args[0]
  file1 = myglob(file1)
  file2 = params.get('file', file1)
  file2 = myglob(file2)
  smooth = params.get('smooth', 1)
  kernel = params.get('kernel', 'f')
  kersize = params.get('kersize', 7)
  mediansize = params.get('mediansize', 1)
  kerfraction = params.get('kerfraction', 1)
  scale  = params.get('scale',0.95)
  replace = params.get('replace',0)
  getscale = params.get('getscale',0)
  scalefraction = params.get('scalefraction',0.05)
  removesig = params.get('removesig',-1)

  outprefix = 'g'
  dirname   =  dirname(file1)
  basename = basename(file1)
  outname = outprefix+basename
  output = join(dirname, outname)
  # run the smooth and  subtraction
  #ker = createker()
  #ker = kernel_gauss(5,2)
  print 'Using kernel: ', kernel
  if kernel == 'g':
      ker = kernel_gauss(11,kersize)
  elif kernel =='f':    
      ker = kernel_flat(kersize)
  elif kernel =='g2':    
      ker = kernel_gauss2(11, kersize)  
  else:
      sys.exit('ERROR: Please define your kernel!')


  # read data
  mode = "same"
  print
  print 'Reading ... '
  print '   %s' %(file1)
  print '   %s' %(file2)
  print
  data1 = pyfits.getdata(file1)
  data2 = pyfits.getdata(file2)
  
  print 'Median filter ...'
  print '   mediansize = ', mediansize
  if mediansize >1:
      data2 = scipy.signal.medfilt(data2, kernel_size=mediansize)
  print    
  
  print 'Delete high vlaues ...'
  print '   kerfraction = ', kerfraction
  if kerfraction <1 :
     data2 = cutfraction(data2,kerfraction)
  print
     
  
  print 'Smoothing ... '
  print '   %s' %(file2)
  print '   smooth size = ',smooth
  print
  if smooth >1 :
    ker = kernel_flat(smooth)
    data2 = scipy.signal.convolve2d(data2, ker,mode)
  
  print  
  print 'Filtering ... '
  print '   %s' %(file2)
  print
  if kersize ==0 :
     print 'No Smooth for '+file2
     smoothdata = data2
  else:   
     if 'divide' in params:
       print '\nWARNING: Diving the data....\n'
       g = lambda x: np.where((x>np.mean(x)+3.*np.std(x))|(x<3.*np.mean(x)-np.std(x)) , 0 , x) 
       tmp = data2
       for ii in range(2):
            print 'mean, std', np.mean(tmp),np.std(tmp)
            tmp = g(tmp)
       tmean = np.mean(tmp)
       smoothdata = scipy.signal.convolve2d(data2+tmean, ker,mode)/abs(data2+tmean)
       outname=outname.replace('.fits','_'+str(kersize)+'.fits')
     else:
       smoothdata = scipy.signal.convolve2d(data2, ker,mode)
     if os.path.isfile('t'+outname): os.remove('t'+outname)
     savefits(smoothdata,file1, 't'+outname)
     pdb.set_trace()


  # if getscale then return the scale and exit
  if getscale ==1:
      rmean, rmedian=suggestscale(data1,data2,fraction = scalefraction)
      scale = rmedian
      pdb.set_trace()
      #sys.exit()
   
  # output  
  print 'Scale = ', scale  
  outdata  = data1 - smoothdata*scale
  if removesig>0:
    value = -0.
    print 'Set pixels with value higher than %f6.1*std to %f'  %(removesig,value)
    std = np.std(outdata)
    print 'Std of outdata: %f ' %std
    outdata = np.where(outdata/std>removesig,  value, outdata)
    std = np.std(data1)
    print 'Std of indata: %f ' %std
    outdata = np.where(data1/std>removesig,  value, outdata)
  savefits(outdata,file1,output)
  print
  print 'Saving  '+output
  print
  if replace !=0:
      print 'Replacing  '+file1
      backfile = file1+'_bck'
      if isfile(backfile): os.remove(backfile)
      os.rename(file1,backfile)
      os.rename(output,file1)



