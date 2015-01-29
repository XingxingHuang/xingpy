#!/usr/bin/env python
# smooth

import pyfits
import pdb,sys
import numpy as np
from os.path import *
import os
from astropy.stats import sigma_clip
from readcol import fgetcols

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
def savefits(data, header,output):
    '''
  save fits file based on the header of the other file.
    '''
    hdu = pyfits.PrimaryHDU(data)
    hdu.header = pyfits.getheader(header)
    hdulist = pyfits.HDUList([hdu]) 
    if isfile(output): os.remove(output)
    hdulist.writeto(output)   
    
def get_bkg(data, sigma):
    '''
    calculate the background for the array. return  mean  median  std mode
    '''
    maskedarr = sigma_clip(data, sigma, None, np.mean)
    outdata = np.where(maskedarr.mask,  1.e10, data)

    # output
    in_list0 = data.reshape(np.size(data))
    in_list  = outdata.reshape(np.size(outdata))
    in_list = in_list.compress(in_list<1.e10)
    # before clip
    mean0 = np.mean(in_list0)
    median0 = np.median(in_list0)
    std0 = np.std(in_list0)
    mode0 = abs(2.5*median0 - 1.5*mean0)  
    # after clip
    mean = np.mean(in_list)
    median = np.median(in_list)
    std = np.std(in_list)
    mode = 2.5*median - 1.5*mean
    print '      %8s  %8s  %8s  %8s'  %('mean','median','stdev','mode') 
    print 'In:  %8.2f  %8.2f  %8.2f  %8.2f' %(mean0,median0,std0,mode0)
    print 'Out: %8.2f  %8.2f  %8.2f  %8.2f' %(mean,median,std,mode)
    return(mean,median,std,mode,outdata)
    

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
  import getopt
  from os.path import *

  mod  = basename(sys.argv[0])
  #text = 'Tips: add | awk \'{printf "%f\\n",$1}\' '
  txt = 'Write by:\n    Xingxing Huang (hxx@mail.ustc.edu.cn) '
  txt += '\nUsage:\n'
  usage=txt+mod+" file <-region regionfile> [-save 0]  [-sigma 3] [-stop 0]\n"
  usage += 'Tips: \n'
  usage += '    Need the sigma_clip in astropy. So use Ureka instead of scisoft \n'
  usage += '    Using the method in Sextractor to estimate the background in one stamp image: Mode = 2.5 x Median - 1.5 x Mean\n'
  usage += '    -save will save fits file with the outlayer value masked\n'
  usage += '    -region file includes the x, y and radius\n'
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
  infile = args[0]
  save = params.get('save', 0)
  sigma = params.get('sigma',3)
  region = params.get('region', '')
  if region =='': sys.exit(usage)
  x,y,r = fgetcols(region,1,2,3)
  bkg_mean =[]
  bkg_median = []
  bkg_std = []
  bkg_mode = []
  
  # sigma clip
  data = pyfits.getdata(infile)
  for index in range(len(x)):
       ri = int(r[index])
       xi = int(x[index])
       yi = int(y[index])
       data_choosed = data[(yi-ri-1):(yi+ri), (xi-ri-1):(xi+ri)]
       #pdb.set_trace()
       mean,median,std,mode,outdata = get_bkg(data_choosed, sigma)
       if save ==1 :
           output = 'img_masked_%2i.fits' %(index)
           savefits(outdata, infile, output)         
       bkg_mean.append(mean)
       bkg_median.append(median)
       bkg_std.append(std)
       bkg_mode.append(mode)
  
  # print final results
  print
  print 'median:   %8.2f   %8.2f'  %(np.mean(bkg_median), np.std(bkg_median))
  print 'mean :  %8.2f   %8.2f'  %(np.mean(bkg_mean), np.std(bkg_mean))
  print 'std :   %8.2f     %8.2f'  %(np.mean(bkg_std), np.std(bkg_std))
  print
  print '      %8s  %8s  %8s  %8s'  %('mean','median','stdev','mode') 
  for index in range(len(x)):
       print   '%4i  %8.2f  %8.2f  %8.2f  %8.2f' %(index+1, bkg_mean[index], bkg_median[index], bkg_std[index], bkg_mode[index])
  print 
  if 'stop' in params: pdb.set_trace()
