###
# some program related to clash data
from os.path import *
import numpy as np
from glob import glob
import pdb
import string,sys,os
import pyfits
from pyraf import iraf

from readcol import fgetcols
from readcol import fgetcols2
from program import printlog

######################################################################
###   make sure the following are right
######################################################################
#rootdir = '/Volumes/Seagate/clash'

'''
clusters =   ['a209', 'a383', 'a611', 'a1423', 'a2261', \
         'm0329', 'm0416', 'm0429', 'm0647', 'm0717', \
         'm0744', 'm1115', 'm1149', 'm1206', 'm1423', \
         'm1720', 'm1931', 'm2129', 'm2137', 'r1347', \
         'r1532', 'r2129', 'r2248', 'c1226', 'm1311'] 
         

bands = ['f225w','f275w','f336w','f390w',\
         'f435w','f475w','f555w','f606w','f625w','f775w','f814w','f850lp',\
         'f105w','f110w','f125w','f140w','f160w']

cat_image = join(rootdir,'0readme','image.cat')
cat_model = join(rootdir,'0readme','model.cat')
cat_catlog = join(rootdir,'0readme','catalog.cat')
cat_cluster = join(rootdir,'0readme','cluster.cat')

'''
HST_bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
HST_center= [2359.0, 2704.0, 3355.0, 3921.0, 4325.0, 4773.0, 5887.0, 6242.0, 7647.0, 8024.0, 9166.0, 10552.0, 11534.0, 12486.0, 13923.0, 15369.0]
HST_width = [467.0, 398.0, 511.0, 896.0, 618.0, 1344.0, 2182.0, 1463.0, 1171.0, 1536.0, 1182.0, 2650.0, 4430.0, 2845.0, 3840.0, 2683.0]

'''
HST_width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
         [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]] 
center = []
width = []
for i in HST_width:
    center.append(i[0]*10)
    width.append(i[1]*10)
print center
print width         
'''
         
VAN_datafile = '/Users/xing/programs/xing/usage/candels_utils/eelg.dat'
GSD_datafile = '/Users/xing/data/candels/CANDELS_GDS/CANDELS.GOODSS.F160W.v1.cat'
GSD_datafile2 = '/Users/xing/data/candels/CANDELS_GDS/hlsp_candels_hst_wfc3_goodss-tot-multiband_f160w_v1_cat.fits'

rootdir = '/Users/xing/data/candels'
candels_field = 'aegis cosmos goodsn goodss uds'.split()
threeHST_cat = {\
      'aegis' :'3dHST/aegis_3dhst.v4.1.cats/Catalog/aegis_3dhst.v4.1.cat',\
      'cosmos':'3dHST/cosmos_3dhst.v4.1.cats/Catalog/cosmos_3dhst.v4.1.cat',\
      'goodsn':'3dHST/goodsn_3dhst.v4.1.cats/Catalog/goodsn_3dhst.v4.1.cat',\
      'goodss':'3dHST/goodss_3dhst.v4.1.cats/Catalog/goodss_3dhst.v4.1.cat',\
      'uds'   :'3dHST/uds_3dhst.v4.2.cats/Catalog/uds_3dhst.v4.2.cat'\
      }

threeHST_dir = '/Volumes/Seagate/3dHST'      
threeHST_img = {\
      'aegis' :'img/AEGIS/aegis_3dhst.v4.0.*_orig_sci.fits',\
      'cosmos':'img/COSMOS/cosmos_3dhst.v4.0.*_orig_sci.fits',\
      'goodsn':'img/GOODSN/goodsn_3dhst.v4.0.*_orig_sci.fits',\
      'goodss':'img/GOODSS/goodss_3dhst.v4.0.*_orig_sci.fits',\
      'uds'   :'img/UDS/uds_3dhst.v4.0.*_orig_sci.fits'\
      }     
      

#________________________________________________________________________________________________
def readVAN():
    '''
    read the EELG informations from van der wel 2011
    '''
    VAN_dat = {}
    keys = 'ID  RA DEC    magH magHe   EWo3 EWo3e   beta betae   Mass Masse'.split()
    for i,key in enumerate(keys):
        VAN_dat[key]=fgetcols(VAN_datafile,i+1)[0]
        
    #pdb.set_trace()    
    VAN_dat['EW'] = VAN_dat['EWo3']/ (7./8.*3./4.)  # convert to EW of all lines    
    VAN_dat['EWe'] = VAN_dat['EWo3e']/ (7./8.*3./4.)  # convert to EW of all lines  
    print 'Read ',  VAN_datafile
    return(VAN_dat)    

#________________________________________________________________________________________________
def readGSD(test=0):
    '''
     if test is set, use test file to debug and save time
    '''
    datafile = GSD_datafile
    if test!=0:
         datafile= '/Users/xing/data/candels/CANDELS_GDS/CANDELS.GOODSS.F160W.v1_test.cat'
    print 'Reading ',  datafile
    keys = 'ID RA DEC   f435w f435we f606w f606we f775w f775we f814w f814we f850lp f850lpe f098m f098me f105w f105we f125w f125we f160w f160we K1 K1e K2 K2e ch1 ch1e ch2 ch2e ch3 ch3e ch4 ch4e MIPS24 MIPS24e '.split()
    index = '1  3  4    12 13        14 15        16 17         18 19       20 21           22 23       24 25         26 27         28 29      30 31  32 33  34 35      36 37   38 39   40 41    42 43'.split()
    index = np.array(index, dtype='int')
    data = fgetcols2(datafile,index)
    GSD_data={}
    for i,key in enumerate(keys):
        GSD_data[key]=data[:][i]
    print 'Read complete.'
    return(GSD_data)    
    

def readGSD2_delete():
    '''
    read fits 
    '''
    print 'Reading ',  GSD_datafile2
    keys = 'ID RA DEC   f435w f435we f606w f606we f775w f775we f814w f814we f850lp f850lpe f098m f098me f105w f105we f125w f125we f160w f160we K1 K1e K2 K2e ch1 ch1e ch2 ch2e ch3 ch3e ch4 ch4e MIPS24 MIPS24e '.split()
    index = '1  3  4    12 13        14 15        16 17         18 19       20 21           22 23       24 25         26 27         28 29      30 31  32 33  34 35      36 37   38 39   40 41'.split()
    index = np.array(index, dtype='int')
    data = pyfits.getdata(GSD_datafile2,1)
    GSD_data={}
    for i,key in enumerate(keys):
        GSD_data[key]=data[:][index[i]]
    print 'Read complete'
    return(GSD_data) 
    
def saveGSD(data,index,fname,nodata=0):   
    '''
    saving the GSD data.
    if nodata is set, 
    '''
    keys = 'ID RA DEC   f435w f435we f606w f606we f775w f775we f814w f814we f850lp f850lpe f098m f098me f105w f105we f125w f125we f160w f160we K1 K1e K2 K2e ch1 ch1e ch2 ch2e ch3 ch3e ch4 ch4e MIPS24 MIPS24e '.split()
    keys_format = '%5i  %10.7f %10.7f '+'   %11.5e %11.5e'*16
    keys_format = keys_format.split()
    formats={}
    for key,form in zip(keys,keys_format):
      formats[key]=form
    #print 'Saving %s' %(fname)
    #pdb.set_trace()
    if nodata!=0:
        txt ='# '
    else:
       txt = ''
    for key in keys:
        txt += formats[key] %(data[key][index]) +'    '
    printlog(txt,fname)
    
                    
def readUDS():
    return(None)    
    
#________________________________________________________________________________________________    3D-HST
def read3d(field):
   '''
   read the 3D-HST catlog
   using fits files
   '''
   if field not in candels_field:
       print 'Field Not found! ',field
       checkinfo('')  
   catfile = join(rootdir,threeHST_cat[field])
   catfitsfile = catfile+'.fits'
   print 'Loading ',catfitsfile    
   data = pyfits.getdata(catfitsfile,1)
   return(data)
   
#def save3dfits():
    

def save3d(data,logfile,names=None,printinfo=0):
    keys = 'id ra dec   f435w f435we f606w f606we f775w f775we f814w f814we f850lp f850lpe f098m f098me f105w f105we f125w f125we f160w f160we K1 K1e K2 K2e ch1 ch1e ch2 ch2e ch3 ch3e ch4 ch4e MIPS24 MIPS24e '.split()
    keys_format = '%5i  %10.7f %10.7f '+'   %11.5e %11.5e'*16
    keys_format = keys_format.split()
    formats={}
    for key,form in zip(keys,keys_format):
      formats[key]=form
    txt = ''  
    for key in keys:
        #pdb.set_trace()
        if key in 'id ra dec'.split():
            txt += formats[key] %(data[key]) +'    '
        elif key in 'f435w f435we f606w f606we f775w f775we f814w f814we f850lp f850lpe f098m f098me f105w f105we f125w f125we f160w f160we'.split():
            if 'e' in key: 
                key2 = 'e_%s' %(key[:-1]  )
            else:
                key2 = 'f_%s' %(key   )
            if names!=None and not key2 in names: 
                txt += formats[key] %(0) +'    ' 
                if printinfo!=0: print 'Not found',key2
            else:
                txt += formats[key] %(data[key2]) +'    '  
        elif key in 'ch1 ch1e ch2 ch2e ch3 ch3e ch4 ch4e':
            if 'e' in key: 
                key2 = 'e_irac%s' %(key[2])
            else:
                key2 = 'f_irac%s' %(key[2])   
            if names!=None and not key2 in names: 
                txt += formats[key] %(0) +'    ' 
                if printinfo!=0: print 'Not found',key2
            else:
                txt += formats[key] %(data[key2]) +'    '  
        else:
            txt += formats[key] %(0) +'    '     
            if printinfo!=0: print 'Not found',key2     
    printlog(txt,logfile)


def get3dew(flux,fluxe,bands=[],z=1.68):
    '''
    data are dict and in units of jr
    return the ew and ewe
    '''    
    ft = flux[1]
    f1 = flux[0]
    f2 = flux[2]
    fte = fluxe[1]
    f1e = fluxe[0]
    f2e = fluxe[2]
    # band informations
    band_index = HST_bands.index(bands[1])
    band_index1 = HST_bands.index(bands[0])
    band_index2 = HST_bands.index(bands[2])
    center = HST_center[band_index]
    width = HST_width[band_index]
    center1 = HST_center[band_index1]
    width1 = HST_width[band_index1]    
    center2 = HST_center[band_index2]
    width2 = HST_width[band_index2]  
    # magnitude
    mag1,mag1e = flux2mag_array(f1,f1e)
    mag2,mag2e = flux2mag_array(f2,f2e)
    # convert to Jy
    f1 = 10.**( np.log10(f1)+(25.-8.9)/(-2.5))  
    f2 = 10.**( np.log10(f2)+(25.-8.9)/(-2.5))  
    ft = 10.**( np.log10(ft)+(25.-8.9)/(-2.5))  
    fte = 10.**( np.log10(fte)+(25.-8.9)/(-2.5))  
    f1e = 10.**( np.log10(f1e)+(25.-8.9)/(-2.5))  
    f2e = 10.**( np.log10(f2e)+(25.-8.9)/(-2.5))  

        
    # calculate 
    fc = (f1+f2)/2.
    fce = np.sqrt(f1e**2+f2e**2)/2.
    
    EW = (ft-fc)/fc*width/(1+z)
    EWe = (  abs(fte/fc)  + abs(ft*fce)/fc**2.  )*width/(1.+z)
    mag = -2.5*np.log10(fc)+8.9
    mage = fce/fc*2.5/np.log(10)
    #pdb.set_trace()
    #for i in range(len(mag1)): 
    #  print i,mag1[i],mag2[i]
    return(EW, EWe,mag,mage)

    '''
    #
    con1 = f1*center1**2/center**2
    con1e = f1e*center1**2/center**2
    con2 = f2*center2**2/center**2
    con2e = f2e*center2**2/center**2
    # calculate 
    #fc = (f1+f2)/2.
    #fce = np.sqrt(f1e**2+f2e**2)/2.
    fc = (con1+con2)/2.
    fce = np.sqrt(con1e**2+con2e**2)/2.
    
    EW = (ft-fc)/fc*width/(1+z)
    EWe = (  abs(fte/fc)  + abs(ft*fce)/fc**2.  )*width/(1.+z)
    mag = -2.5*np.log10(fc)+25.
    mage = fce/fc*2.5/np.log(10)
    return(EW, EWe,mag,mage)
    '''
    

from drizzlepac import skytopix
def get3dstamp(field,images,ID,ra,dec,box=30,outdir='./img/',outname=None,save_all=1,save_sep=1): 
    '''
    make stamp images
    '''
    if not isdir(outdir): 
        os.mkdir(outdir)
    #
    keys = images.keys()
    keys = sortkey(keys)
    x,y = skytopix.rd2xy(images[keys[-1]],ra,dec)
    #
    region = '[%i:%i,%i:%i]'  %(x-box, x+box, y-box, y+box)
    gridnum = len(keys)+1 
    offsets = "grid %s %s 1 %s "  %(str(gridnum),  str(box*2+9),   str(box*2+9))
    text = '' 
    for band in keys:
        text  = text+images[band]+region+','
    text = text[:-1]   
    # create combine images
    infile = text
    if outname==None:
        outname = '%s_%05i.fits' %(field,ID)   
    outfile = join(outdir,outname)
    if save_all ==1:
        if isfile(outfile): os.remove(outfile)
        iraf.imcombine(infile,outfile,offsets=offsets, mode='h')     
      
    # create separate images?
    if save_sep==1:
        dir_sep = join(outdir,field)
        if not isdir(dir_sep):
            os.mkdir(dir_sep)
        for band in keys:
            text = images[band]+region
            output = '%s_%05i_%s.fits' %(field,ID,band)   
            outfile = join(dir_sep, outname)
            if isfile(outfile): os.remove(outfile)
            iraf.imcopy(text,outfile)
                 
def get3dimages(field):
    '''
    return the dictionary including images for 3D-HST
    '''
    bands = 'F435W F606W F775W F814W F850LP F125W F140W F160W'.split()
    fitsname = join(threeHST_dir,threeHST_img[field])
    fitfiles = globfiles(fitsname,keys=bands)
    return(fitfiles)   

def sortkey(keys):
    output = []
    for band in HST_bands:
       if band in keys:
           output.append(band)
       elif string.upper(band) in keys:
           output.append(string.upper(band))           
    return(output)          

def get_key_band(keys,bands,special=None):
    '''
    get the band name 
    '''         
    output ={}
    for band in bands:
        output[band] = None
        for key in keys:
            # special found?
            if special !=None:
                if not special in key:
                    continue
            # band found?        
            if string.lower(band) in key or string.upper(band) in key:
                if output[band]!=None:
                    print '\n\t  ERROR: multi-keys found! %s %s\n' %(output[band],key)
                    pdb.set_trace()
                if 'f_' in key:
                    output[band]=key
    return(output)  

def get_key_band2(keys,bands,special='f_'):
    '''
    similar but only consider keys like 'f_bands'
    '''
    output ={}
    for band in bands:
        key = special+band
        if string.lower(key) in keys or string.upper(key) in keys or key in keys:
            output[string.lower(band)]=key    
        else:
            print '\n\t ERROR: key not found!  \n     %s \n' %key
            pdb.set_trace()        
         
    return(output)       
#________________________________________________________________________________________________    
# flux to mag
flux2mag = lambda x: -2.5*np.log10(x)+25.
flux2mage = lambda f,fe: fe/f*2.5/np.log(10)

def flux2mag_array(f,fe):
    '''
    convert flux to magnitude for two array
    '''
    sigma = 0.3
    mag = []
    mage = []
    for flux,fluxe in zip(f,fe):
      if flux<=0:
        mag.append(-99)
        mage.append(-99)
      elif flux/fluxe<sigma:
        mag.append(99)
        mage.append(flux2mag(fluxe+flux))
      else:
        mag.append(flux2mag(flux))  
        mage.append(flux2mage(flux,fluxe))
    if len(mag)!=len(f) or len(mage)!=len(f):
      print '\nERROR: check mag and mage!\n'    
      pdb.set_trace()
    return(np.array(mag),np.array(mage))  
        
    
    
              
#________________________________________________________________________________________________
def readcat(fname):
    '''
    read flux
    '''
    keys = 'ID RA DEC   f435w f435we f606w f606we f775w f775we f814w f814we f850lp f850lpe f098m f098me f105w f105we f125w f125we f160w f160we K1 K1e K2 K2e ch1 ch1e ch2 ch2e ch3 ch3e ch4 ch4e MIPS24 MIPS24e '.split()
    index = np.arange(len(keys))+1
    data = fgetcols2(fname,index)
    output ={}
    for i,key in enumerate(keys):
        output[key]=data[i]
    print 'Read ',fname
    return(output) 
    
def getew(data,bands=[],z=1.68):
    '''
    data are dict and in units of jr
    return the ew and ewe
    '''    
    ft = data[bands[1]]
    f1 = data[bands[0]]
    f2 = data[bands[2]]
    fte = data[bands[1]+'e']
    f1e = data[bands[0]+'e']
    f2e = data[bands[2]+'e']    
    # band informations
    band_index = HST_bands.index(bands[1])
    band_index1 = HST_bands.index(bands[0])
    band_index2 = HST_bands.index(bands[2])
    center = HST_center[band_index]
    width = HST_width[band_index]
    center1 = HST_center[band_index1]
    width1 = HST_width[band_index1]    
    center2 = HST_center[band_index2]
    width2 = HST_width[band_index2]    
    # calculate 
    fc = (f1+f2)/2.
    fce = np.sqrt(f1e**2+f2e**2)/2.
    
    EW = (ft-fc)/fc*width/(1+z)
    EWe = (  abs(fte/fc)  + abs(ft*fce)/fc**2.  )*width/(1.+z)
    mag = -2.5*np.log10(fc*1.e-6)+8.9
    mage = fce/fc*2.5/np.log(10)
    return(EW, EWe,mag,mage)
    
    
    
    
######################################################################
#  sub routing

def globfiles(ftext,keys=None):
    '''
    glob the files based on the fname. 
    if keys is set, then it will be a dictionary.
    
    '''        
    files = glob(ftext)
    if len(files) ==0:
        print 'ERROR: no file found. ',ftext
    if keys== None:
       return(files)
    # if keys is set   
    outdict = {}   
    for fname in files:
        fkey = 'other'
        for key in keys:
            if key in fname:
                fkey = key
        if fkey in outdict.keys() and fkey!='other':
            print 'ERROR: two files have the same key ',fkey
            print '   ',   outdict[fkey]
            print '   ',   fname
            sys.exit()
        outdict[fkey] = fname        
    return(outdict)         
  
  
def readinfo(info):
    '''
    read info files in the following foramt
    # tag1
    cluster1  data
    # tag2
    cluster2 data    
    ...
    '''
    #split_symbol = ''
    out = {}
    f = open(info)
    lines = np.array(f.readlines())
    index = [i for i,line in enumerate(lines) if '##' in line]
    for i in index:  
        tmp = lines[i].split()
        ID = tmp[1]
        index1 = int(tmp[2])  # the line index for the ## line.  start from 1
        index2 = index1+int(tmp[3])
        outlines = np.array([np.array(line.split()) for line in lines[index1:(index2)]] )
        out[ID] = outlines
        #pdb.set_trace()
    f.close()
    return(out)                
    
def checkinfo(txt):
      '''
      make a pause in the program 
      '''
      tmp  = raw_input('\n%s.. (press y for debug) \n' %txt)
      if tmp == 'y':   
          pdb.set_trace()    
        
###################################################################################################
# loaddict

def str2num(str, rf=0):
    """CONVERTS A STRING TO A NUMBER (INT OR FLOAT) IF POSSIBLE
    ALSO RETURNS FORMAT IF rf=1"""
    str = string.strip(str)
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
                if ',' in str:
                    words = string.split(str, ',')
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

def loadfile(filename, dir="", silent=0, keepnewlines=0):
    infile = join(dir, filename)
    if not silent:
        print "Loading ", infile, "..."
    fin = open(infile, 'r')
    sin = fin.readlines()
    fin.close()
    if not keepnewlines:
        for i in range(len(sin)):
            #sin[i] = sin[i][:-1]
            if sin[i][-1] == '\n':
                sin[i] = sin[i][:-1]
    return sin

def loaddict(filename, dir="", silent=0):
    lines = loadfile(filename, dir, silent)
    dict = {}
    for line in lines:
        if line[0] <> '#':
            words = string.split(line)
            key = str2num(words[0])
            valstr = string.join(words[1:], ' ')
            valtuple = False
            # if nothing there
            if valstr == '': 
                val = [] 
                dict[key] = []
                continue
            #  LIST / TUPLE!
            if valstr[0] in '[(' and valstr[-1] in '])':  
                valtuple = valstr[0] == '('
                valstr = valstr[1:-1].replace(',', '')
                words[1:] = string.split(valstr)
            # read  words to array    
            if len(words) == 2:
                val = str2num(words[1])
            elif len(words) > 2:
                val = []
                for word in words[1:]:
                    val.append(str2num(word))
                if valtuple:
                    val = tuple(val)
            dict[key] = val
    return dict
 
   
def loadlines(filename, dir="", silent=0, keepnewlines=0):
    '''
    Return the lines 
    by xingxing.  
    '''
    infile = join(dir, filename)
    if not silent:
        print "Loading ", infile, "..."
    fin = open(infile, 'r')
    sin = fin.readlines()
    lines = [tmp[:-1] for tmp in sin if tmp[0]<> '#'  and tmp.strip() <> '']  # delete the comment lines and '\n'
    fin.close()
    return(lines)
    
def loaddictlines(filename, dir="", silent=0, keepnewlines=0):
    '''
    Return dict cotaining the lines. the first column will be the keys
    by xingxing.  
    '''
    infile = join(dir, filename)
    if not silent:
        print "Loading ", infile, "...\n"
    fin = open(infile, 'r')
    sin = fin.readlines()
    lines = [tmp[:-1] for tmp in sin if tmp[0]<> '#'  and tmp.strip() <> '']  # delete the comment lines and '\n'
    fin.close()
    # 
    dictlines = {} 
    for line in lines:
        key = line.split()[0]
        dictline = line.split(' ',1)[1]
        dictline = dictline.strip()
        dictlines[key]=dictline
    return(dictlines)
###################################################################################################
