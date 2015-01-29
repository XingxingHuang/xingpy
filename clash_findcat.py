# July 1 : Now it can read the f125w.cat. For example:
# Oct 20 : revised 
# Dec 03 : revised for frontier a2744. Compare two catalog.

# #a1423 nir  833    x    y         ra        dec   f225w           f275w           f336w           f390w           f435w           f475w           f606w           f625w           f775w           f814w          f850lp           f105w           f110w           f125w           f140w           f160w           redshift
# a1423   1  833 2685 2703 179.332885  33.604235  27.1595 0.4606   0.0000 0.0000  25.5483 0.0785  26.2373 0.0895  26.5138 0.1474  26.3398 0.0942  26.1541 0.0735  26.4246 0.1322  26.1103 0.1133  25.8834 0.0551  27.0099 0.3270  26.0058 0.0778  25.5968 0.0397  25.3666 0.0491  25.4596 0.0443  25.9883 0.0700   1.7600
import os,sys,string,glob,time,math
import pdb
import numpy as np
from pylab import *
import pyfits

class find:
  def __init__(self,fname=None, ra1=2, dec1=3, comfile=None, ra2=2, dec2=3, pdb_=1, prefix='tmp'):
    bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
    f = open(fname,'r')
    lines=f.readlines()
    data_all = [line.split() for line in lines] 
    self.data = [i for i in data_all if not ('#' in i[0]) ]     # delete the elements begin with '#'
    f.close()
    logfile = prefix+'_run.log'
    resultsfile =  prefix+'_runresults.log'
    if os.path.isfile(logfile):
        os.remove(logfile)      
      
    cat = comfile  
    for source in self.data:  # different objects
        print 'select the source %3i' %(float(source[0]))   ##
        fcat = open(cat,'r')
        lines=fcat.readlines()
        data_all = [line.split() for line in lines] 
        data = [i for i in data_all if not ('#' in i[0]) ]     
        fcat.close()
        detection = 0 
        ############### define the index 
        x2_index=2
        y2_index=3
        z2_index=1
        x1_index=2
        y1_index=3
        z1_index=1
        sigma2_index=10
        # the index of 16 bands
        # = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
        m = [1,       1,      1,      1,      41,     1,      31,     1,      1,      11,     1,       21,     1,      36,     26,     16   ]
        ############### begin to select
        distance = 3600.*20		
        rmin = 90.*3600		
        #index = 0	
        findout=0	 
        ################search in 1"	
        for i in range (len(data)): # searching the catalog.
          ra = float(data[i][ra2-1])
          dec = float(data[i][dec2-1])
          Zhengra = float(source[ra1-1])
          Zhengdec= float(source[dec1-1])	
          # detect closed object								
          if abs(ra-float(Zhengra) )< distance/3600. and abs(dec-float(Zhengdec) ) < distance/3600.:   
            findout =1+findout
            num = i
            #x   = float(data[i][3])
            #y   = float(data[i][4])
            #z   = float(data[i][115])
            #sigma = float(data[i][9])
            r = math.sqrt((abs(ra-float(Zhengra))*3600. ) **2 + (abs(dec-float(Zhengdec) )*3600.)**2 )
            print ra,' ', dec,' ', r
            if r < rmin:
             rmin=r
             index = i
            #pdb.set_trace() 
            
            #  print when there is one object in the distance. 
            if True:    
             select_index=i
             ra = float(data[select_index][ra2-1])
             dec = float(data[select_index][dec2-1])
             x   = float(data[select_index][x2_index-1])
             y   = float(data[select_index][y2_index-1])
             z   = float(data[select_index][z2_index-1])
             sigma = float(data[select_index][sigma2_index-1])
             
             # print the information
             self.printlog(source[0],fname=logfile)
             if os.path.exists(logfile):
              f = open(fname,'a')
             else:
              f = open(fname,'w') 
	     ## print in *IR.cat
             #print >> f, '%55s %4s %11s %11s %4s %4s %7s %7s %7s' %('source','num','ra','dec','x','y','z','r','det_sigma')
             #txt = '%55s %4.0f %11.7f %11.7f %4.0f %4.0f %7.5f %7.6f   %7f' %(source[0],num,ra,dec,x,y,z,r,sigma)
             #print >> f, txt
             #txt= '%5s ' %('num')+'%11s  '*16 %('f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w')
             #print >> f, txt
             # print in run.log
             self.printlog('%55s %4s %11s %11s %4s %4s %7s %7s %7s' %('source','num','ra','dec','x','y','z','r','det_sigma'),fname=logfile)
             self.printlog('%55s %4.0f %11.7f %11.7f %4.0f %4.0f %7.5f %7.6f   %7f' %(source[0],00,ra,dec,x,y,z,r,sigma),fname=logfile)
             txt= '%5s ' %('num')+'%11s  '*16 %('f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w')
             self.printlog(txt,fname=logfile)
             mag  = []
             mage = []
             for ii in [-4,-3,-2,-1,0]:
                print select_index
                #pdb.set_trace()
                f225w = data[select_index][m[0]+ii]  if m[0]!=1 else 99
                f275w = data[select_index][m[1]+ii]  if m[1]!=1 else 99
                f336w = data[select_index][m[2]+ii]  if m[2]!=1 else 99
                f390w = data[select_index][m[3]+ii]  if m[3]!=1 else 99
                f435w = data[select_index][m[4]+ii]  if m[4]!=1 else 99
                f475w = data[select_index][m[5]+ii]  if m[5]!=1 else 99
                f606w = data[select_index][m[6]+ii]  if m[6]!=1 else 99
                f625w = data[select_index][m[7]+ii]  if m[7]!=1 else 99
                f775w = data[select_index][m[8]+ii]  if m[8]!=1 else 99
                f814w = data[select_index][m[9]+ii]  if m[9]!=1 else 99
                f850lp = data[select_index][m[10]+ii]  if m[10]!=1 else 99
                f105w = data[select_index][m[11]+ii]  if m[11]!=1 else 99
                f110w = data[select_index][m[12]+ii]  if m[12]!=1 else 99
                f125w = data[select_index][m[13]+ii]  if m[13]!=1 else 99
                f140w = data[select_index][m[14]+ii]  if m[14]!=1 else 99
                f160w = data[select_index][m[15]+ii]  if m[15]!=1 else 99
                txt = '%5.0f ' %(num)+'%11s  '*16 %(f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w)
                self.printlog(txt,fname=logfile)
                # load the mag and mage
                if ii == -1: mag = [f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w]
                if ii == 0: mage = [f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w]
             txt='%5s %3f %4f %4f %4f  %10.6f %10.6f  ' %(source[0],0,0,x,y,ra,dec)
             for band in range(0,16):
              mag_  = mag[band]
              mage_ = mage[band]
              if mag_ =='inf': mag_='99'
              if mage_ =='inf': mage_='99'
              txt=txt+'%9.4f %8.4f  ' %(float(mag_),float(mage_) )
             print '*** mag ***: '+txt  
             
          # only print the closed objects to the final catalog          
          if i == len(data)-1: 
             num = index
             select_index=index
             r = rmin
             ra = float(data[select_index][ra2-1])
             dec = float(data[select_index][dec2-1])
             x   = float(data[select_index][x2_index-1])
             y   = float(data[select_index][y2_index-1])
             z   = float(data[select_index][z2_index-1])
             sigma = float(data[select_index][sigma2_index-1])
             mag  = []
             mage = []
             if findout == 0:
               self.printresults('#%5s not found' %(source[0]),fname=resultsfile)
               txt='%5s %3i %4i %4i %4i  %10.6f %10.6f  ' %(source[0],0,0,x,y,ra,dec)
               for band in range(0,16):
                mag_  = 99
                mage_ = 99
                txt=txt+'%9.4f %8.4f  ' %(float(mag_),float(mage_) )
               self.printresults(txt,fname=resultsfile)
               #self.printlog(txt,fname=logfile)
             else:
               for ii in [-4,-3,-2,-1,0]:
                 f225w = data[select_index][m[0]+ii]  if m[0]!=1 else 99
                 f275w = data[select_index][m[1]+ii]  if m[1]!=1 else 99
                 f336w = data[select_index][m[2]+ii]  if m[2]!=1 else 99
                 f390w = data[select_index][m[3]+ii]  if m[3]!=1 else 99
                 f435w = data[select_index][m[4]+ii]  if m[4]!=1 else 99
                 f475w = data[select_index][m[5]+ii]  if m[5]!=1 else 99
                 f606w = data[select_index][m[6]+ii]  if m[6]!=1 else 99
                 f625w = data[select_index][m[7]+ii]  if m[7]!=1 else 99
                 f775w = data[select_index][m[8]+ii]  if m[8]!=1 else 99
                 f814w = data[select_index][m[9]+ii]  if m[9]!=1 else 99
                 f850lp = data[select_index][m[10]+ii]  if m[10]!=1 else 99
                 f105w = data[select_index][m[11]+ii]  if m[11]!=1 else 99
                 f110w = data[select_index][m[12]+ii]  if m[12]!=1 else 99
                 f125w = data[select_index][m[13]+ii]  if m[13]!=1 else 99
                 f140w = data[select_index][m[14]+ii]  if m[14]!=1 else 99
                 f160w = data[select_index][m[15]+ii]  if m[15]!=1 else 99
                 if ii ==-1: mag = [f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w]
                 if ii == 0: mage = [f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w]
               txt='%5s %3i %4i %4i %4i  %10.6f %10.6f  ' %(source[0],0,0,x,y,ra,dec)
               for band in range(0,16):
                 mag_  = mag[band]
                 mage_ = mage[band]
                 if mag_ =='inf': mag_='99'
                 if mage_ =='inf': mage_='99'
                 txt=txt+'%9.4f %8.4f  ' %(float(mag_),float(mage_) )
               self.printresults(txt,fname=resultsfile)
               #self.printlog(txt,fname=logfile)
        if findout==0:
            self.printlog('not found %55s in %10s' %(source[0],cat),fname=logfile)  
        else:
            self.printlog('*** num ***: found out %4d %55s in %10s' %(findout,source[0],cat),fname=logfile)
        self.printlog('\n\n',fname=logfile)      
        if pdb_==1:
            pdb.set_trace()
        
  def printlog(self,text,fname='run.log'):
    '''
    write the text you define to the run.log file
    '''
    if os.path.exists(fname):
      f = open(fname,'a')
    else:
      f = open(fname,'w')   
      txt='####This file is used for recording the running messages ####'
      print >> f, txt
      print 'run.log created!'
    ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
    format = '%s %s'  
    print >> f, format % (ptime,text)
    #print >> f,text
    #print text
    f.close()  


  def printresults(self,text,fname='runresults.log'):
    '''
    write data as the same format as what find.py create.
    ''' 
    ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
    ptime2=time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.time()))   
    if os.path.exists(fname):
      f = open(fname,'a')
    else:
      f = open(fname,'w')   
      txt='####This file is used for recording the running messages ####'
      print >> f, txt
      format = '#%4s %3s %4s %4s %4s %10s %10s  '+'%10s          '*16
      txt = format %('src', 'cat', 'num', 'x','y','ra','dec','f225w', 'f275w', 'f336w', 'f390w', 'f435w', 'f475w','f606w', 'f625w', 'f775w', 'f814w', 'f850lp','f105w', 'f110w', 'f125w','f140w', 'f160w') 
      print >> f, txt
      del txt
      print 'runresults.log created!'
    #format = '%s %s'  
    #print >> f, format % (ptime,text)
    print >> f,text
    print text
    f.close()        
      
if __name__ == '__main__':
  runfile = ['a2744_bcg.cat']
  ra1 = 2
  dec1 = 3
  comfile = ['./a2744_new/multicolor_red.cat']
  ra2 =2
  dec2 =3
  prefix='a2744_bright'    #define a prefix name for the output 
      
  find(fname=runfile[0], ra1=ra1, dec1=dec1, comfile=comfile[0], ra2=ra2, dec2=dec2, pdb_=0, prefix=prefix)
  #find(fname=fname,ircatalog=0)









      
