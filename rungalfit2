#!/usr/bin/env python
#
#  need readcol
#
# Mar17: add more parameters

from readcol import fgetcols
import pdb,sys,os
import numpy as np

def getpar(param,  par, val):
   '''
   if par in param, returen the value, else return the val
   '''
   if par in param.keys():
   	value = param[par]
   else: 
       	value = val
   return(value)    	 	


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def create_title(param={}):
    '''
# IMAGE and GALFIT CONTROL PARAMETERS
A) r1347_36_621_all_2.fits      # Input data image (FITS file)
B) imgblock.fits       # Output data image block
C) r1347_ch2_mosaic_unc_2.fits      # Sigma image name (made from data if blank or "none") 
D) psf2.fits           # Input PSF image and (optional) diffusion kernel
E) 5                   # PSF fine sampling factor relative to data 
F) none                # Bad pixel mask (FITS image or ASCII coord list)
G) none                # File with parameter constraints (ASCII file) 
H) 5    17   5    17   # Image region to fit (xmin xmax ymin ymax)
I) 100    100          # Size of the convolution box (x y)
J) 21.580              # Magnitude photometric zeropoint 
K) 0.600  0.600        # Plate scale (dx dy)   [arcsec per pixel]
O) regular             # Display type (regular, curses, both)
P) 0                   # Choose: 0=optimize, 1=model, 2=imgblock, 3=subcomps   
    '''
    obj = {}
    obj['par'] = ['#','A', 'B', 'C', 'D', 'E', 'F' ,'G','H', 'I', 'J', 'K', 'O','P']
    obj['#'] =getpar(param, '#', ' ')+' '
    obj['A'] = getpar(param,'A','  img.fits')+'            # Input data image (FITS file)' 
    obj['B'] = getpar(param,'B',' output.fits ')+'          # Output data image block' 
    obj['C'] = getpar(param,'C',' none ')+'               # Sigma image name (made from data if blank or "none") ' 
    obj['D'] = getpar(param,'D',' /Users/xing/programs/IRAC/psf/psf1.fits ')+'               # Input PSF image and (optional) diffusion kernel' 
    obj['E'] = getpar(param,'E',' 5 ')+'                # PSF fine sampling factor relative to data ' 
    obj['F'] = getpar(param,'F',' none ')+'               # Bad pixel mask (FITS image or ASCII coord list)' 
    obj['G'] = getpar(param,'G',' none ')+'             # File with parameter constraints (ASCII file) ' 
    obj['H'] = getpar(param,'H',' 1  100  1 100 ')+'            # Image region to fit (xmin xmax ymin ymax)' 
    obj['I'] = getpar(param,'I',' 10 10 ')+'             # Size of the convolution box (x y)' 
    obj['J'] = getpar(param,'J',' 21.58 ')+'            # Magnitude photometric zeropoint  ' 
    obj['K'] = getpar(param,'K',' 0.600   0.600 ')+'              # Plate scale (dx dy)   [arcsec per pixel]' 
    obj['O'] = getpar(param,'O',' regular ')+'            # Display type (regular, curses, both)' 
    obj['P'] = getpar(param,'P',' 0 ')+'                # Choose: 0=optimize, 1=model, 2=imgblock, 3=subcomps   '   
    return(obj)
    
    
def create_sky(param={}):
    '''
# Component number: 1
 0) sky                    #  Component type
 1) 0.1655      1          #  Sky background at center of fitting region [ADUs]
 2) 0.000e+00      0       #  dsky/dx (sky gradient in x)     [ADUs/pix]
 3) 0.000e+00      0       #  dsky/dy (sky gradient in y)     [ADUs/pix]
 Z) 0                      #  Skip this model in output image?  (yes=1, no=0)  
    '''
    obj = {}
    obj['par'] = ['#' ,'0', '1', '3', 'z']
    obj['#'] =getpar(param, '#', ' ')+' '
    obj['0'] = getpar(param, '0',  'sky             ')+'  #  Sky background at center of fitting region [ADUs]'
    obj['1'] = getpar(param, '1',  '0.11    1    ')+' #  dsky/dx (sky gradient in x)     [ADUs/pix]'
    obj['3'] = getpar(param, '3',  '0  0         ')+'  #  dsky/dy (sky gradient in y)     [ADUs/pix]' 
    obj['z'] = getpar(param, 'z',  '0  0          ')+'  #  Skip this model in output image?  (yes=1, no=0)  '
    return(obj)
    
def create_gauss(param={}):
    '''
 # Gaussian function
 0) gaussian           # object type
 1) 402.3  345.9  1 1  # position x, y        [pixel]
 3) 18.5       1       # total magnitude     
 4) 0.5        0       #   FWHM               [pixels]
 9) 0.3        1       # axis ratio (b/a)   
10) 25         1       # position angle (PA)  [Degrees: Up=0, Left=90]
 Z) 0                  # leave in [1] or subtract [0] this comp from data?
    '''
    obj = {}
    obj['par'] = ['#','0', '1', '3',  '4', '9', '10', 'z']
    obj['#'] =getpar(param, '#', ' ')+' '
    obj['0'] = getpar(param, '0',  'gaussian  	')
    obj['1'] = getpar(param, '1',  '0 0 1 1    	')+' # position x, y        [pixel]'
    obj['3'] = getpar(param, '3',  '20  1       	')+' # total magnitude ' 
    #pdb.set_trace()
    obj['4'] = getpar(param, '4',  '1.5 1       	')+' #   FWHM               [pixels]'
    obj['9'] = getpar(param, '9',  '1  1         	')+' # axis ratio (b/a)   '
    obj['10'] = getpar(param, '10',  '0 1      	')+' # position angle (PA)  [Degrees: Up=0, Left=90]'
    obj['z'] = getpar(param, 'z',  '0 	          	')+' # leave in [1] or subtract [0] this comp from data?'
    return(obj)


def create_sersic(param={}):
    '''
# Sersic function

 0) sersic             # Object type
 1) 300.  350.  1 1    # position x, y        [pixel]
 3) 20.00      1       # total magnitude    
 4) 4.30       1       #     R_e              [Pixels]
 5) 5.20       1       # Sersic exponent (deVauc=4, expdisk=1)  
 9) 0.30       1       # axis ratio (b/a)   
10) 10.0       1       # position angle (PA)  [Degrees: Up=0, Left=90]
 Z) 0                  #  Skip this model in output image?  (yes=1, no=0)
    '''
    obj = {}
    obj['par'] = ['#','0', '1', '3',  '4',  '5', '9', '10', 'z']
    obj['#'] =getpar(param, '#', ' ')+' '
    obj['0'] = getpar(param, '0',  'sersic    ')
    obj['1'] = getpar(param, '1',  '0 0 1 1      ')+' # position x, y        [pixel]'
    obj['3'] = getpar(param, '3',  '20  1         ')+' # total magnitude ' 
    obj['4'] = getpar(param, '4',  '2.0 1         ')+' #     R_e              [Pixels]'
    obj['5'] = getpar(param, '4',  '1. 1         ')+' # Sersic exponent (deVauc=4, expdisk=1)  '
    obj['9'] = getpar(param, '9',  '0.7  1           ')+' # axis ratio (b/a)   '
    obj['10'] = getpar(param, '10',  '10. 1        ')+' # position angle (PA)  [Degrees: Up=0, Left=90]'
    obj['z'] = getpar(param, 'z',  '0               ')+' # leave in [1] or subtract [0] this comp from data?'
    return(obj)


def printobj(obj,cat, silent =1):
    '''
    print a dictionary to a file
    '''
    if os.path.isfile(cat):
      output=open(cat, "a")
    else:
      output=open(cat, "w")

    keys = obj['par']
    output.write('\n\n')
    for key in keys:
      value = obj[key]
      txt = '%s)   %s\n' %(key, value)
      if silent!=1: 
            print txt
      output.write(txt)
    output.close()    
    
def printreg(obj,cat, silent =1,last =0):
    '''
    print the choosed objects
    '''
    if os.path.isfile(cat):
      output=open(cat, "a")
    else:
      output=open(cat, "w")

    xyt = obj['1']
    magt = obj['3']
    x = float(xyt.split()[0])
    y = float(xyt.split()[1])
    mag =  float(magt.split()[0])
    txt = '%f  %f  %f\n' %(x,y,mag)
    if last!=0: txt = '%f  %f  %f' %(x,y,mag)
    output.write(txt)
    output.close()    
          		
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



if __name__ == '__main__':
  import getopt
  from os.path import *

  # usage
  mod  = basename(sys.argv[0])
  txt = 'Write by:\n    Xingxing Huang (hxx@mail.ustc.edu.cn) '
  txt += '\nUsage:\n     '
  #usage=txt+mod+" <ch1.cat> \n"
  usage=txt+mod+" <input.cat> <--fixxy>\n"
  usage += 'Tips: \n'
  usage += '     (0) getcat r1347\n'
  usage += "     (1) search  photometry.cat 2 3  206.90479  -11.75055  0.0035  | awk '{printf \"%f  %f   %f   %f    %f\n\", $2,$3,$110,$6,$9}'    > input.cat  \n" 
  usage += "     (2) convertxy input.cat  1 2  r1347_36_621_all_1.fits \n" 
  usage += "           selectreg input.reg input2.reg input_select.reg  -col1 1 -col2 2  -dr 0.5 -printdel 1  "
  usage += "     (3) rungalfit2 input2.reg \n"
  usage += "     (4) galfit galfit.out\n"
  usage += "     (5) ds9 output.fits[1] output.fits[2] output.fits[3] &"
  usage += 'Attention: \n'
  usage += "     (*) Fixed the position, fwhm, sersic index, ellipticity for the first run. Then check the results and decide how to release the parameters."
  usage += "     (*) The positions of objects near the edge should be fixed."
  usage += "     (*) The positions of objects near the edge should be fixed."
  usage += 'To Do: \n'
  usage += '    --fixxy not work  \n'
  opts1=''
  opts2=['fixxy']
  
  # read param
  try:
     opts, args = getopt.getopt(sys.argv[1:],opts1,opts2)
  except getopt.GetoptError:
     sys.exit(usage)
  #pdb.set_trace()
  #params = params_cl()
  if len(args)<1:
      sys.exit(usage)
  incat = args[0]
  outcat = 'galfit.run'
  outreg = 'galfit.reg'
  maglimit = 26.6


  # read and create galfit.run
  if os.path.isfile(outcat):
      os.system('mv %s  %sbak' %(outcat, outcat))
  if os.path.isfile(outreg):
      os.system('mv %s  %sbak' %(outreg, outreg))  
  if incat ==outreg:
       incat = '%sbak' %(outreg)
  
  x, y, mag, fwhm, ell =  fgetcols(incat,1,2,3,4,5)
  # pixel size
  size_pixel = 0.6
  length = len(x)
  #
  obj = create_title()
  printobj(obj, outcat, silent=1)
  #
  obj = create_sky()
  printobj(obj, outcat, silent=1)  
  #
  print
  for i in range(length):
      if mag[i]>maglimit:
           info = '#del obj %i: %6.1f  %6.1f    %5.2f ' %(i+1, x[i], y[i], mag[i])
           print info
           continue
      #obj  = create_gauss()
      obj = create_sersic()
      obj['1']  = '%f    %f    0    0'  %(x[i],y[i])
      obj['3']  = '%f  1 ' %(mag[i])
      fwhm2 = np.sqrt(fwhm[i]**2+0.6**2)/size_pixel
      obj['4']  = '%f  0 ' %(fwhm2) # notice the fwhm is in unit of arcsec
      obj['5']  = '1. 0 '     # sersic index
      obj['9']  = '%f  0 ' %(1-ell[i])   #notice the ell is defined as Ellipticity = 1 - B/A
      info = '# obj %i: %6.1f  %6.1f    %5.2f ' %(i+1, x[i], y[i], mag[i])
      obj['#']  = info
      print info
      printobj(obj, outcat, silent=1)
      if i == length-1: 
          printreg(obj,outreg,last =1)
      else:
          printreg(obj,outreg,last =0)    
  print
  print
  pdb.set_trace()




  
