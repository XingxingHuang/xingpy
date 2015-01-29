#!/usr/bin/env python
####################################################################################
# Jan 28 :  Change the output in run.log 
#	 :  Change the individual output image name to : nir_f125w_001_00544_f110w.fits 
#        :  Put the opt and nir into only one directory	
#        :  print error message while plotting images
#        :  impovement of the plotmag
#        :  Do not create individual band image to save time and space.
# Jan 29 :  Change the reg file name
# Jan 30 :  add "weight" in the options. "context"
# Feb 1  :  add "context" in the options and revise the "weight" options
#        :  impove the speed in  __init__, please take care of it
# Feb 4  :  fixed the weight
#        :  add tips for checking the speed
# Feb 20 :  for new data come, I add '_drz_' in the name of catalogs. a1423_f814w_drz_nir.cat
# Feb 21 :  improved. it will consider data with 99. this means the no-detection data.
#	 :  fiexed file name for some bpz files are bpz_nir.cat.   
# Jul 02 :  define the mag limit.
# Jul 24 :  add parameter special 
#        :  now the png image will plot imediately after the creation of fits file
# --------------------------------------------------------------------- 
# Dec 03 :  motified from catalog.py for CLASH 
# --------------------------------------------------------------------- 
# Dec 16 :  motified from plot_img_compare.py for A2744
#	read a catalog and save the images for several bands into a directory.
#       add the parameters in the begining of the pipline
####################################################################################




# --------------------------------------------------------------------- 
#             		parameters (set them here)
# --------------------------------------------------------------------- 
# catalog
catfile 	= './photo8.cat'			# the catalog where ra dec can be found
NAMEnum		= 1					# the column of source names. This will be used for the output file names
RAnum 		= 2					# the column of ra dec
DECnum 		= 3

# redshift of nearby objects 
include_bpz 	= 0					# include the bpz of nearby objects or not
BPZsize     	= 50 					# the search area is box with [searchsize*2+1]
BPZnum 		= 2					# the column of redshift 
BPZnumx 	= 2			
BPZnumy 	= 3
BPZnumobj	= 1				
bpzfile         = './a2744_new/multicolor_red.cat'  	# the file that includes redshift
######################################################### I do not include the bpzfile2 in the code, please revise by hands!!!
bpzfile2         = './a2744_new/bpz_red.cat'  		# in current pipline the accordinates are not included in the bpz results. so there are two files.

# input images
# if "otherprefix" is not defined. Then the program will only grab images that match the name "imageprefix"
# if "otherprefix" is defined, for example, as 'drz', then the program will only use the images with 'drz' in the names.
indir 	 	= '../images'				# the directory for images
imageprefix	= ['*_sci.fits','*_drz.fits']				# The program will grab the images that match the name here. PLEASE also make sure the 'bands' defined bellow also included in the names of images.
otherprefix 	= None					# define another prefix
delprefix       = None 					# if the image name contain this string, it will be excluded from the list
plot_separate	= 0					# plot the images of different bands separately.
plot_allinone	= 1					# plot all images into one figure. However the WCS information will be lost.
plot_web	= 1					# create a webpage to make work easer. 

# output images
# the images will be output into the directory with the names as:
# [namepre]_[index number]_[source name].fits
# tmp_0_0.fits
outdir		= './img/'
bands   	= ['f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']		# the bands of output images. PLEASE make sure these bands are included in the bands_all(check the default setting).
boxsize 	= 50					# the size of output images. the final size will be 2*boxsize+1
namepre		= 'obj'				# the prefix of output images
includeindex	= 1					# inlude the index of sources into the names of output files.  
    		 
# messages
silence = 0
# --------------------------------------------------------------------- 
#			default setting	(do no need to change for most cases)
# --------------------------------------------------------------------- 
default_width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
    	 [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]   
default_bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
# --------------------------------------------------------------------- 




import os,sys,string,glob
import pdb
from pyraf import iraf
import numpy as np
from pylab import *
from drizzlepac import skytopix

import pyfits
#from cosmocalc import cosmocalc
#from matplotlib import cm
from pylab import *

# add
from readcol import fgetcols

class ImageForCatalog:
    def __init__(self,catfile=None, NAMEnum=None, RAnum=1, DECnum=2, \
    		 indir='./', imageprefix='*_sci.fits*', otherprefix=None, delprefix=None, plot_separate=1, plot_allinone=1, plot_web=1, \
    		 outdir='./tmp', bands=['f814w'], boxsize=100, namepre='tmp', includeindex=1, \
    		 include_bpz = 0, BPZnum = None, BPZnumx=None, BPZnumy=None, BPZnumobj=None, bpzfile=None, BPZsize=100,\
    		 default_width = [[802.4,153.6]], default_bands = ['f814w'],\
    		 silence = 0 ):
    	self.catfile 	= catfile
    	self.NAMEnum 	= NAMEnum 
    	self.RAnum 	= RAnum 
    	self.DECnum 	= DECnum 
    	
    	self.indir	= indir 
    	self.imageprefix = imageprefix 
    	self.otherprefix = otherprefix 
    	self.delprefix   = delprefix
    	self.plot_separate = plot_separate 
    	self.plot_allinone = plot_allinone 
    	self.plot_web = plot_web 
    	
    	self.outdir = outdir 
    	self.bands = bands 
    	self.boxsize = boxsize 
    	self.namepre = namepre 
    	self.includeindex = includeindex 
        
        # bpz
    	self.include_bpz= include_bpz 
    	self.BPZsize    = BPZsize
    	self.BPZnum 	= BPZnum
    	self.BPZnumx	= BPZnumx
    	self.BPZnumy	= BPZnumy
    	self.BPZnumobj	= BPZnumobj
    	self.bpzfile	= bpzfile
    	self.bpzfile2	='./a2744_new/bpz_red.cat'
    	
    	self.default_bands = default_bands 
    	self.default_width = default_width 
        self.silence = silence

        self.obj = []
        self.z   = []
        self.ra  = []
        self.dec = []
        self.imglist = []
        self.imglist_detected = []
        
    def run(self):		 
        # read catalog
        self.obj, self.ra, self.dec = fgetcols(self.catfile, self.NAMEnum, self.RAnum, self.DECnum)
            
        # get image file list
        self.imglist, self.imglist_detected = self.get_imglist()
        print '**************  %s **************' %(self.namepre)
        print 'Number of objects: %3i' %(len(self.obj)) 
        print 'Number of images : %3i' %(len(self.imglist))
        
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)
        if self.plot_separate == 1:
            if self.silence == 0:
                print 'Plot separate images...'
            self.plot_sep_img()    
    
        if self.plot_allinone == 1:
            if self.silence == 0:
                print 'Plot stamp images...'
            self.plot_all_img()
                
        if self.plot_web ==1:
            if self.silence != 0:
                print 'Prepare for webpage...'
            self.plot_web_img()
        print '**************  finish **************\n' 
        #pdb.set_trace()
        
    def get_imglist(self):
        '''
        glob image list based on these parameters:
        indir
        imageprefix
        delprefix
        bands
        '''
        # glob image list
        imgfile= []
        imgfile_detected = []  # 0 is non detected, 1 is detected.
        for prefix in self.imageprefix:
              tmpfiles = os.path.join(self.indir,prefix)
              tmp = glob.glob(tmpfiles)
              print '   Get files %i  %s' %(len(tmp), tmpfiles)
              imgfile += tmp
        # otherprefix
        if self.otherprefix != None:
             for index in range(len(imgfile)):
                 img = imgfile[index]
                 if not self.otherprefix in img:
                     imgfile.pop(index)
        # delprefix             
        if self.delprefix != None:
             for index in range(len(imgfile)):
                 img = imgfile[index]
                 if self.delprefix in img:
                     imgfile.pop(index)
        # select image list for the bands  
        imgfile_band = []
        for band in self.bands:
            band_find = 0
            for img in imgfile:             
                if band in img:
                    band_find += 1
                    imgfile_band.append(img)  
            if band_find == 0 :
                print
                print 'WARNING : '+band+' image is not found in the '+indir
                print 'WARNING : USE FILE INSTEAD ',imgfile[-1]
                imgfile_band.append(imgfile[-1])  
                imgfile_detected.append(0)
                #sys.exit('WARNING : '+band+' image is not found in the '+indir)
            else:
                imgfile_detected.append(1)
            if band_find >1 :
                sys.exit('ERROR: too many image are found for '+band)        
        print 
        pdb.set_trace()    
        #if len(imgfile_band) != len(self.bands):
        #    sys.exit('fail to get image list!')        
        return(imgfile_band,imgfile_detected)
        
    def plot_sep_img(self):
        '''
        save the images arround objects with defined size.
        '''
        count = 0 
        box = self.boxsize
        for index in range(len(self.obj)):
            count += 1
            obj = self.obj[index]
            ra  = self.ra[index]
            dec = self.dec[index]
            iraf.stsdas.toolbox.imgtools.rd2xy(self.imglist[0],ra,dec,hour='no')
            x = iraf.stsdas.toolbox.imgtools.rd2xy.x
            y = iraf.stsdas.toolbox.imgtools.rd2xy.y
            x1 = int(x)-box
            x2 = int(x)+box
            y1 = int(y)-box
            y2 = int(y)+box
            for bi in range(len(self.bands)):
                fitsfile = self.imglist[bi]
                infile = fitsfile+'['+str(x1)+':'+str(x2)+','+str(y1)+':'+str(y2)+']'
                if self.includeindex ==1 :
                    outname = '%s_%s_%s_%s.fits' %(namepre,count,obj,self.bands[bi])
                else:
                    outname = '%s_%s_%s.fits' %(namepre,obj,self.bands[bi])    
                outfile = os.path.join(outdir,outname)
                if os.path.isfile(outfile):
                    os.rename(outfile,outfile+'_bck')
                iraf.imcopy(infile,outfile,verbose=0)
                
    def plot_all_img(self):
        '''
        save the images arround objects with defined size.
        all images will be plot in one fits file and png file
        '''
        count = 0 
        box = self.boxsize
        gridnum = len(self.bands)   # all the images will be put in one line
        for index in range(len(self.obj)):
            count += 1
            obj = self.obj[index]
            ra  = self.ra[index]
            dec = self.dec[index]
            #iraf.stsdas.toolbox.imgtools.rd2xy(self.imglist[0],ra,dec,hour='no')
            #x = iraf.stsdas.toolbox.imgtools.rd2xy.x
            #y = iraf.stsdas.toolbox.imgtools.rd2xy.y
            x,y = skytopix.rd2xy(self.imglist[0],ra,dec)
            x1 = int(x)-box
            x2 = int(x)+box
            y1 = int(y)-box
            y2 = int(y)+box
            infile = '' 
            for bi in range(len(self.bands)):
                fitsfile = self.imglist[bi]
                if not os.path.isfile(fitsfile):
                    sys.exit('WARNING:  not found ',fitsfile)
                text = fitsfile+'['+str(x1)+':'+str(x2)+','+str(y1)+':'+str(y2)+']'
                if infile=='':
                    infile = text
                else:  
                    infile=infile+','+text
            if self.includeindex ==1 :
                outname = '%s_%s_%s_all.fits' %(namepre,count,obj)
            else:
                outname = '%s_%s_all.fits' %(namepre,obj)    
            imgprefix = 'jpg'
            if self.includeindex ==1 :
                outname = '%s_%s_%s.fits' %(namepre,count,obj)
                outname2 = '%s_%s_%s.%s' %(namepre,count,obj, imgprefix)
                outname3 = '%s_%s_%s_z.%s' %(namepre,count,obj, 'jpg')
            else:
                outname = '%s_%s.fits' %(namepre,obj)    
                outname2 = '%s_%s.%s' %(namepre,obj, imgprefix) 
                outname3 = '%s_%s_%s_z.%s' %(namepre,count,obj, 'jpg')
                
            # save fits file 
            outfile = os.path.join(outdir,outname)   
            if os.path.isfile(outfile):
                os.rename(outfile,outfile+'_bck')
            offsets = "grid "+str(gridnum)+" "+str(box*2+10)+" 2 "+str(box*2+10)
            iraf.imcombine(infile,outfile,offsets=offsets)  
            print 
            print 'Infile   :  ',infile
            print 'outfile : ', outfile
            print 'offsets : ',offsets
            print
             
            # deal with some non detected bands with stored in self.imglist_detected
            data = pyfits.getdata(outfile)
            for i in range(len(bands)):
                if self.imglist_detected[i] ==0:
                     Txrange = [(box*2+10)*i , (box*2+10)*(i+1)+1]
                     Tyrange = [0, box*2+1]
                     data[Tyrange[0]:Tyrange[1] ,  Txrange[0]:Txrange[1]   ] = np.zeros((box*2+1,box*2+10+1))
            
            # save eps or png file
            vmin = 0.
            vmax = 80.
            blanksize = 15
            outfile2 = os.path.join(outdir,outname2)
            fig = plt.figure(figsize=(18,6))
            ax=fig.add_subplot(111)
            im   = imshow(data, vmin=vmin, vmax=vmax,origin='lower')
            plt.colorbar(shrink=0.3)
            # plot band name
            for index in range(len(self.bands)):
                #lx = 12+(box*2+10)*(j%8)
                #ly = (box*2+10)*(j//8)
                lx = (box*2+10)*index+box
                ly = box
                ax.text(lx,0,string.upper(self.bands[index]),color='red',ha='center') #,fontweight='bold',ha='center')    
                #ax.plot(lx,ly,'o',color='None', markeredgecolor='fuchsia', markersize=13, alpha=0.6,markeredgewidth=2)     
                ax.plot([lx,lx],[0,box-blanksize],color='white')
                ax.plot([lx,lx],[box*2,box+blanksize],color='white')
                ax.plot( [lx-box, lx-blanksize],[ly,ly],color='white')
                ax.plot( [lx+box, lx+blanksize],[ly,ly],color='white')      
                #print lx,ly      
            # save
            ax.set_xlim(0,len(self.bands)*(box*2+1+10))
            ax.set_ylim(0,box*2+1)
            if imgprefix == 'jpg':
                savefig(outfile2)
            else:   
                savefig(outfile2,format='eps')
           
            # plot redshift
            outfile3= os.path.join(outdir,outname3)   
            if self.include_bpz == 1:
                zx, zy, zz, zobj = fgetcols(self.bpzfile, self.BPZnumx, self.BPZnumy, self.BPZnum, self.BPZnumobj)
                tmp=fgetcols(self.bpzfile2, self.BPZnum)######################################################
                zz = tmp[0]
                near_x, near_y, near_z, near_obj = self.get_nearby(x,y, zx,zy,zz,zobj, box=self.BPZsize)    
                for zi in range(len(near_x)):
                  print '%5f %5.3f   %11f %11f'  %(near_obj[zi], near_z[zi], near_x[zi], near_y[zi])
                  locx = near_x[zi]-x+box
                  locy = near_y[zi]-y+box
                  ax.plot(locx,locy,'o',color='None', markeredgecolor='fuchsia', markersize=5, alpha=0.9)   
                  ax.text(locx,locy+4,str(near_obj[zi])+' %4.2f' %(near_z[zi]),color='fuchsia',ha='center',fontsize=6, alpha=1 ) 
                ax.set_xlim(0,len(self.bands)*(box*2+1+10))
                ax.set_ylim(0,box*2+1)
                savefig(outfile3)    
            fig.clf()
                
    def plot_web_img(self):
        outfile = '%s.html' %(namepre)
        fout = open(os.path.join(outdir,outfile), 'w')
        fout.write('\n')
        fout.write('<h1>selection results for %s </h1>\n\n' %(namepre) )
        count = 0 
        for index in range(len(self.obj)):
            count += 1
            obj = self.obj[index]
            imgprefix = 'jpg'
            if self.includeindex ==1 :
                outname = '%s_%s_%s.fits' %(namepre,count,obj)
                outname2 = '%s_%s_%s.%s' %(namepre,count,obj, imgprefix)
                outspec = '%s_%s_%s_spec.%s' %(namepre,count,obj, imgprefix)
            else:
                outname = '%s_%s.fits' %(namepre,obj)    
                outname2 = '%s_%s.%s' %(namepre,obj, imgprefix) 
                outspec = '%s_%s_spec.%s' %(namepre,obj, imgprefix)
            if not os.path.isfile(os.path.join(outdir,outspec)):
                 print 'WARNING: spectral figures not found!! '    
                 pdb.set_trace()
            
            image = outname2
            spectrum = outspec 

       
            # write to html 
            format = '%6s &nbsp; %5s &nbsp; '
            text1 = format %( 'Num', 'ID')
            text2 = format %(str(count),str(obj) )
            fout.write(text1+' <br>\n')
            fout.write(text2+' <br>\n')
            fout.write(' <img src="./%s"   border=0 height=400 width=1200>\n' %( image) )
            fout.write(' <img src="./%s"   border=0 height=400 width=600>' %(spectrum)  )
            fout.write('<br>\n\n')
 
        fout.close()

    def get_nearby(self, x,y, zx,zy,zz,zobj, box=10):
        near_x = [] 
        near_y = []
        near_z = []
        near_obj = []
        for i in range(len(zx)):
           if abs(zx[i]-x)<box and abs(zy[i]-y)<box:
              near_x.append(zx[i])
              near_y.append(zy[i])
              near_z.append(zz[i])
              near_obj.append(zobj[i])
        return(near_x, near_y, near_z, near_obj)     
              
        
    
if __name__ == '__main__':
   #pdb.set_trace()
   #from img_prepare_bright import ImageForCatalog
  try:
      field   = sys.argv[1]
      namepre = field
  except :
      namepre ='obj'
  image=ImageForCatalog(catfile=catfile, NAMEnum=NAMEnum, RAnum=RAnum, DECnum=DECnum, \
    		 indir=indir, imageprefix=imageprefix, otherprefix=otherprefix, plot_separate=plot_separate, plot_allinone=plot_allinone, plot_web=plot_web, \
    		 outdir=outdir, bands=bands, boxsize=boxsize, namepre=namepre, includeindex=includeindex, \
    		 include_bpz = include_bpz, BPZnum = BPZnum, BPZnumx=BPZnumx, BPZnumy=BPZnumy, BPZnumobj=BPZnumobj, bpzfile=bpzfile, BPZsize=BPZsize,\
    		 default_width = default_width, default_bands = default_bands,\
    		 silence = silence)
  image.run()
'''    
#################### read magnitude
cat1 = 'a2744_zheng.cat'

cat1_name,cat1_mag = readmag_zheng(cat1)
print 'read Zheng catalog DONE!'




##################################################################  zheng
zheng=1

if zheng==1:
   cat=cat1_name
   indir = './a2744'
   outdir= 'img_zheng'
   index_ra =3
   index_dec=4
   zhenglist=glob.glob(os.path.join(indir,'*sci*.fits'))
   filelist=['' for i in range(len(bands))]
   for index_band in range(len(bands)):
       for fitsfile in zhenglist:
           if bands[index_band] in fitsfile: 
               filelist[index_band] = fitsfile
   for index_band in range(len(bands)):  
       if filelist[index_band] == '':
          filelist[index_band] = os.path.join(indir,'blank.fits') 
if zheng==1:        
 for index in range(len(cat)):    
   ra = float(cat[index][index_ra-1])
   dec= float(cat[index][index_dec-1])
   x,y = getxy(filelist[15],ra=ra,dec=dec)
   print  'x y  ra dec: %4i %4i   %8.4f %8.4f' %(x,y,ra,dec)
   obj  = 'a2744_%i' %(index+1)
   savename = 'a2744_'+str(index+1)+'_'+str(int(cat[index][0]))
   CreateFullImage(filelist,obj=obj,x=x,y=y,box=25,savename=savename,indir=indir,outdir=outdir,vmax=300)
'''
