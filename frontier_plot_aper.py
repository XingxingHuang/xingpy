# July 1 : Now it can read the f125w.cat. For example:
# Oct 20 : revised 
# Dec 03 : revised for frontier a2744. Compare two catalog.
# Mar 09 : motified



# #a1423 nir  833    x    y         ra        dec   f225w           f275w           f336w           f390w           f435w           f475w           f606w           f625w           f775w           f814w          f850lp           f105w           f110w           f125w           f140w           f160w           redshift
# a1423   1  833 2685 2703 179.332885  33.604235  27.1595 0.4606   0.0000 0.0000  25.5483 0.0785  26.2373 0.0895  26.5138 0.1474  26.3398 0.0942  26.1541 0.0735  26.4246 0.1322  26.1103 0.1133  25.8834 0.0551  27.0099 0.3270  26.0058 0.0778  25.5968 0.0397  25.3666 0.0491  25.4596 0.0443  25.9883 0.0700   1.7600
import os,sys,string,time,math
from glob import glob
import pdb
import numpy as np
from pylab import *
# need readcol
from  readcol import fgetcols


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
def flux2mag(flux, zero_pt="", abwave=""):
    """ flux2mag(flux, zero_pt="", abwave="")
    http://www.astrobetter.com/wiki/tiki-index.php?page=Python+Switchers+Guide
    Convert from flux (ergs/s/cm^2/A) to magnitudes
    returns a float or array of magnitudes
    
    INPUTS: 
      flux -  float or array flux vector, in erg cm-2 s-1 A-1

    OPTIONAL INPUTS:
      zero_pt - float giving the zero point level of the magnitude.
                If not supplied then zero_pt = 21.1 (Code et al 1976)
                Ignored if the abwave is supplied
      abwave - wavelength float or array in Angstroms.   If supplied, then 
               FLUX2MAG() returns Oke AB magnitudes (Oke & Gunn 1983, ApJ, 266,
               713). 
      
    OUTPUTS: 
      mag - magnitude vector.
        
    NOTES:
      1. If the abwave input is set then mag is given by the expression 
         abmag = -2.5*alog10(f) - 5*alog10(abwave) - 2.406
         Otherwise, mag is given by the expression
         mag = -2.5*alog10(flux) - zero_pt
    
    >>>flux2mag(10.0)
    -23.6
    """

    if not bool(zero_pt): zero_pt = 21.10        #Default zero pt
    if flux <=0:
        #print 'flux warning: ',flux
        return(99)
        
    if zero_pt !=  "":
        mag = -2.5*math.log10(flux) + zero_pt    
        return mag

    if abwave != "":
        mag = -2.5*math.log10(flux) - 5*math.log10(abwave) - 2.406
    else:
        mag = -2.5*math.log10(flux) + zero_pt    
        
    return mag

def fluxe2mage(flux,fluxe, zero_pt="", abwave="",     sigma = 1.):
    '''
    version 2.0  by Xingxing Huang  :      
         if flux<0 or S/N < sigma: return 99,mag      
    '''
    if not bool(zero_pt): zero_pt = 21.10        #Default zero pt

    #mage1 = 2.5*np.log10(1+fluxe/flux)    
    if flux ==0. or fluxe==0.:
        return(-99,0)    
    elif flux<0 or abs(flux/fluxe) <sigma:
        mag = flux2mag(fluxe,zero_pt=zero_pt, abwave=abwave)      
        mage = fluxe/flux*2.5/np.log(10.)        # using the method as in Sextractor
        return(99, mag)
    else:
        mag = flux2mag(flux,zero_pt=zero_pt, abwave=abwave)      
        mage = fluxe/flux*2.5/np.log(10.)        # using the method as in Sextractor        
        return (mag, mage)
        
        
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
class find:
  def __init__(self, fname='', ra=0., dec=0.,  catfile ='', index_ra=None, index_dec=None, silent =0, outcol =[], addcol =None, addcole=None):
    '''
    None
    '''
    f = open(catfile,'r')
    lines=f.readlines()
    data_all = [line.split() for line in lines if line.strip()!=''] 
    data = [i for i in data_all if not ('#' in i[0]) ]     # delete the elements begin with '#'
    f.close()
    
    cat = comfile  
    ############### define the index  of x y 
    if 1:
             m = outcol
             index_obj = 1
             index_x = 4
             index_y = 5
             ra2 = index_ra
             dec2 = index_dec
    # ra dec have been included in the input param
   ############### define the index  of x y 
    mag  = []
    mage = []
    x = []
    y = []
    #ra = []
    #dec = []
    objnum =[]


    if True:
        detection = 0 

        ############### begin to select
        distance = 0.2
        rmin = 90.*3600    
        findout=0   
        ################search in distance  
        for i in range (len(data)): # searching the catalog.
          # all objects
          _ra = float(data[i][ra2-1])
          _dec = float(data[i][dec2-1])
          # selected objects
          Zhengra = float(ra)
          Zhengdec= float(dec)  

          # detect closed object                
          if abs(_ra-float(Zhengra) )< distance/3600. and abs(_dec-float(Zhengdec) ) < distance/3600.:   
            findout =1+findout
            num = i
            r = math.sqrt((abs(_ra-float(Zhengra))*3600. ) **2 + (abs(_dec-float(Zhengdec) )*3600.)**2 )
            if silent ==0:
                 tmp = int(data[i][index_obj-1])
                 print '%4i     %f %f %f' %(tmp, _ra, _dec, r/0.065)
            if r < rmin:
             rmin=r
             index = i
            #pdb.set_trace() 
            

        if findout==0:
            print  'not found in %10s' %(cat)
            print
            pdb.set_trace()
            sys.exit()
        if findout>1:
            print  'too many found in %10s' %(cat)
            print
        if True:
             num = index
             select_index=index
             r = rmin
             '''
             objnum.append(float(data[select_index][index_obj-1]))
             #ra.append(float(data[select_index][ra2-1]))
             #dec.append(float(data[select_index][dec2-1]))
             try:
                tmp = float(data[select_index][m[0]])
             except:
                tmp = 99
             mag.append(tmp)
             try:
                tmp = float(data[select_index][m[1]])
             except:
                tmp = 99
             mage.append(tmp)   
             '''
             # read all the 14 aperture magnitudes
             for aper in range(0,14):
               try:
                  tmp = float(data[select_index][m[0]-1+aper])
               except:
                  tmp = -99
               mag.append(tmp)
               try:
                  tmp = float(data[select_index][m[1]-1+aper])
               except:
                  tmp = -99
               mage.append(tmp)  
               # others
               objnum.append(float(data[select_index][index_obj-1]))
               x.append(float(data[select_index][index_x-1]))
               y.append(float(data[select_index][index_y-1]))
               ra_cat =   float(data[select_index][ra2-1])
               dec_cat =  float(data[select_index][dec2-1])
             
             #  read data from additional columns
             if addcol != None:
                 for aper in range(len(addcol)):
                     index = addcol[aper]-1
                     indexe = addcole[aper]-1
                     try:
                         tmp = float(data[select_index][index])
                     except:
                         tmp = -99
                     mag.append(tmp)
                     try:
                        tmp = float(data[select_index][indexe])
                     except:
                        tmp = -99
                     mage.append(tmp)  
                     # others
                     objnum.append(float(data[select_index][index_obj-1]))
                     x.append(float(data[select_index][index_x-1]))
                     y.append(float(data[select_index][index_y-1]))
                     ra_cat =   float(data[select_index][ra2-1])
                     dec_cat =  float(data[select_index][dec2-1])
               
    #### End of the big loop 
    self.mag = mag
    self.mage = mage
    #pdb.set_trace()
    self.ra = np.zeros(len(mag))+ra_cat
    self.dec = np.zeros(len(mag))+dec_cat
    self.obj = objnum
    self.x = x
    self.y = y
    
  def run(self):  
    return(self.mag,self.mage)

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
    #ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
    #format = '%s %s'  
    #print >> f, format % (ptime,text)
    print >> f,text
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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++      
def savefile(outdata, output):
  '''
    save catalog as Xingxing's format
    example : src cat  num    x    y         ra        dec       f225w               f275w     ...
  '''
  bands =  ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
  bandse = []
  for band in bands:
      bandse += [band, band+'e']
  keys = ['obj','note','num','x','y','ra','dec']+bandse
  # format       
  outform = {}
  outform['obj']   = ['%5s',  '%5i']
  outform['note'] = ['%5s',  '%5i']
  outform['num'] = ['%5s',  '%5i']
  outform['x']       = ['%6s',  '%4.1f']
  outform['y']       = ['%6s',  '%4.1f']
  outform['ra']     = ['%8s',  '%8.5f']
  outform['dec']   = ['%8s',  '%8.5f']
  for band in bands:
      outform[band] =  ['%8s',  '%8.4f']
      outform[band+'e'] =  ['%8s',  '%8.4f']

  # print 
  f = open(output,'w')
  # title
  title = '#'
  for key  in keys:
      title +='  '+outform[key][0]  %key
  print >> f, title
  # data
  for index in range(len(outdata['obj'])):
      txt = ' '    
      for key  in keys:
          txt +='  '+outform[key][1]  %outdata[key][index]
      print >> f, txt
  f.close()	                              



def plotimg_aper(outdata, plot_aper, outimg = ''):
    
    fig = plt.figure(figsize=(8,6)) #,dpi=160)
    ax = fig.add_subplot(111)
    for aperture in plot_aper:
       index = np.where(np.array(allapers)==aperture)[0][0]  # the index
       #color = hex( int(255.*index/len(plot_aper))* 0x00ffffff)  # the color
       tmp = float(np.where(np.array(plot_aper)==aperture)[0][0])/len(plot_aper)
       if tmp>0.67:
            r =  (tmp-0.67)/0.333
            g = 1.-r
            b = 0 
       elif tmp>0.333:
            r =  0
            g =  (tmp-0.333)/0.334
            b = 1.-g   
       elif tmp>=0:
            r =  1.-tmp/0.333
            g = 0
            b = tmp/0.333
       else:
            sys.exit('Error: color: %f'  %tmp)     
       color = (r,g,b)
       print color

       ylimit = 25.3   # this is the upper limit for y axis
       ylow  = 31.5    
       wave = []
       x = []
       xe = []
       y = []
       ye = []    
       ny = []  # non detected 
         
       for key in bands:
         i = bands.index(key)
         # x
         x.append( width[i][0] )
         wave.append(width[i][0])
         xe.append(width[i][1]/2)
         # y 
         yt = outdata[key][index]
         yet = outdata[key+'e'][index]
         if yt-0.4 < ylimit and yt>20: 
               ylimit = yt-0.5
         if abs(yt) > 50.0 :   # non detection
                ny.append(yet)
                yt = 0;  yet = 0.0001
         elif  abs(yet) > 0.92:   # catalog problem  
                ny.append(99.)
                yt = 31;  yet = 0.0001
         else:
                ny.append(0)       
         y.append(yt)
         ye.append(yet)
       #label 
       label = 'aper\_'+str(aperture)
       if aperture == plot_aper[0]:
           aa=ax.errorbar(array(x), array(y),xerr=array(xe), yerr=array(ye), fmt='s',color=color,markeredgecolor='black',ecolor='0.4',alpha=0.6,label=label ,capsize=2,markersize=5) #, vmin =vmin, vmax=vmax)  
       else:
           aa=ax.errorbar(array(x)-plot_aper.index(aperture)*2., array(y), yerr=array(ye), fmt='s',label=label,markeredgecolor='black',markersize=5,color = color, alpha=0.6,capsize=2, ecolor='0.4')  
       #plot non detection
       bb = ax.plot(x,ny,'v', color='None',markeredgecolor=color,alpha=0.6,markersize=6)
       ax.set_xticks([])
    # cluster name
    txt = 'obj: %5s' %(str(outdata['obj'][0]))
    #text(0.5,0.9,txt,ha='left',va='center',transform=ax.transAxes)
    title(txt)
    # ra dec
    txt1 = 'RA  : %10.6f' %(outdata['ra'][0])
    txt2 = 'DEC: %10.6f' %(outdata['dec'][0])
    txt3 = 'X    : %6.1f' %(outdata['x'][0])
    txt4 = 'Y    : %6.1f' %(outdata['y'][0])
    text(0.2,0.95,txt1,ha='left',va='center',transform=ax.transAxes,fontsize=8)
    text(0.2,0.90,txt2,ha='left',va='center',transform=ax.transAxes,fontsize=8)
    text(0.2,0.85,txt3,ha='left',va='center',transform=ax.transAxes,fontsize=8)
    text(0.2,0.80,txt4,ha='left',va='center',transform=ax.transAxes,fontsize=8)
    # legend
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles[::-1], labels[::-1],loc='upper left',numpoints = 1, bbox_to_anchor=(-0.1, -0.2, 0.5,0.5))
    for label in leg.get_texts():
        label.set_fontsize(8)  
    #ax.set_xscale('log')
    # plot line
    ax.set_xlim(200,1700)
    ax.set_ylim(ylow,ylimit)
    pdb.set_trace()
    ax.set_xticks(wave)
    ax.set_xticklabels(allbands,fontsize=6)
    ax.set_xlabel('Wavelength')
    ax.set_ylabel('Magnitude')
    #leg = ax.legend(loc='lower right',bbox_to_anchor=(0.1,0.9), bbox_transform=gcf().transFigure)
    #leg = ax.legend([aa[0],bb[0]],[name1,name2,name3],loc='lower right',bbox_to_anchor=(0.9,0.1), bbox_transform=gcf().transFigure)  
    #leg.get_frame().set_alpha(0)
    #leg.draw_frame(False)
    for label in ax.get_xticklabels():
       label.set_rotation(45)
    print '  Saveing  %s'  %(outimg)
    savefig(outimg)      
 
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  txt = 'Tips:  \n'
  usage=mod+"cluster ra dec  [-plot_aper  <aper_size>]  -outcol  <16,30  44,58>  [-col 2,3]   \n"+txt
  usage = '\nUsage: \n    '+usage
  usage += '    save the aperture photometry and plot the reuslts for one object found in the multi-band catalogs\n\n'
  usage += '    Default X Y are in 4th 5th columns\n'
  usage += '    Catalog name must be      <cluster>_<f160w>.cat\n'
  usage += '    Catalogs must be under  /Users/xing/data/clash_cat/<cluster>/cat_RED/**/sex\n'
  usage += '    -outcol :  define the columns which will be selected for output catalogs. \n'
  usage += '    -aper   :  which aper will be plot in the figure \n'
  usage += '        In my pipeline, FLUX_APER starts from 16, MAG_APER starts from 44.\n'   
  usage += '        The aperture sizes are 2,3,4,6,8,10,14,20,28,40,60,80,100,160\n'
  usage += '        The aperture index are 1,2,3,4,5, 6, 7, 8, 9,10,11,12,13, 14\n'
  usage += 'Example: \n    python /Users/xing/programs/xing/frontier_plot_aper.py  a209 22.978808 -13.604754 -plot_aper  4,6,8,10  -outcol 44,58  -col 2,3\n'   
  usage += 'WARNING: \n    You do not need to define the outcol in current version. It will use the both the flux and mag columns\n'   
  usage += 'WARNING: \n    We also read the mag_auto and mag_iso into the last two lines  and defined as 0 and 1\n'   
  opts1="i"
  opts2=[]
  
  try:
    opts, args = getopt.getopt(sys.argv[1:],opts1,opts2)
  except getopt.GetoptError:
    sys.exit(usage)
  if len(args)<2:
    sys.exit(usage)

  # define params
  params = params_cl()
  cluster = args[0]
  objra = float(args[1])
  objdec = float(args[2])
  tmp = params.get('col', [2,3])
  index_ra = tmp[0]
  index_dec =tmp[1]
  outcol = params.get('outcol', None)
  plot_aper = params.get('plot_aper', 0)  # apertures that will be plot 

  # check band
  bands =[]
  inputs = []
  allapers =  [2,3,4,6,8,10,14,20,28,40,60,80,100,160, 0, 1]  # notice that we add the mag auto and mag iso in the last two lines.
  allbands =  ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
  width = [ [235.9,46.7],[270.4,39.8],[335.5,51.1],[392.1,89.6],\
         [432.5,61.8],[477.3,134.4],[588.7,218.2],[624.2,146.3],[764.7,117.1],[802.4,153.6],[916.6,118.2],\
       [1055.2,265.0],[1153.4,443.0],[1248.6,284.5],[1392.3,384.0],[1536.9,268.3]]      
  wavelength = {'f225w': [235.9, 46.7], 'f275w': [270.4, 39.8], 'f336w': [335.5, 51.1], 'f390w': [392.1, 89.6],\
                            'f435w': [432.5, 61.8], 'f475w': [477.3, 134.4], 'f606w': [588.7, 218.2], 'f625w': [624.2, 146.3],  'f775w': [764.7, 117.1], 'f814w': [802.4, 153.6], 'f850lp': [916.6, 118.2],\
                            'f105w': [1055.2, 265.0], 'f110w': [1153.4, 443.0], 'f125w': [1248.6, 284.5], 'f140w': [1392.3, 384.0], 'f160w': [1536.9, 268.3]}
  catfiles = ['%s_%s.cat' %(cluster, band) for band in bands]
  catdir = '/Users/xing/data/clash_cat/%s/cat_RED/**/sex'  %(cluster)
 
  for band in allbands:
      tmpfile = os.path.join(catdir,  '%s_%s.cat' %(cluster, band) )
      catfile = glob(tmpfile)
      if len(catfile)!=1:
            print 'WARNING:  BAND NOT FOUND %s ' %band
            #print '      %s %s' %(catfile,tmpfile)
      else:
            bands.append(band)
            inputs.append(catfile[0])
            print '%s : %s'  %(band, catfile[0])
  if len(bands)==0:
       print 'ERROR: no catalog is found!'
       pdb.set_trace()
       sys.exit()
  print 
  print 'Band used: ', bands
  print
  
  ############################################################
  #                                plot the flux catalogs
  outcol = [16,30]
  addcol = [74,8]   # auto and iso
  addcole = [75,9]
  addnote = [0,1]
  ############################################################
  # find data from each catalog
  datas = {}
  for index in range(len(bands)):
      print 'reading %s ....' %bands[index]
      comfile = inputs[index]
      a = find( ra=objra, dec=objdec,  catfile =comfile, index_ra=index_ra, index_dec=index_dec, outcol=outcol, addcol = addcol , addcole = addcole)
      d  =a.mag
      de = a.mage
      x  = a.x
      y = a.y
      ra  = a.ra
      dec = a.dec 
      obj = a.obj
      datas[bands[index]]=d 
      datas[bands[index]+'e'] = de
      
  # set output data format 
  # example : src cat  num    x    y         ra        dec       f225w               f275w     ...
  outdata = {}
  outdata['obj'] = obj 
  outdata['note'] = allapers + addnote
  outdata['num'] = obj
  outdata['x'] = x
  outdata['y'] = y
  outdata['ra'] = ra
  outdata['dec'] = dec
  for band in allbands:
     if band in bands:
         outdata[band] = datas[band]
         outdata[band+'e'] = datas[band+'e']
     else:   # not observed set to -99,0
         outdata[band] = np.zeros(len(obj),dtype=float)-99
         outdata[band+'e'] = np.zeros(len(obj),dtype=float)
  # now the outdata stores the photometry for one objects, but it includes all the 14 aperture photometry.

  # save to outfile
  outdir = './'+cluster
  outfile  = '%s_%s_aper_flux.cat' %(cluster, str(int(obj[0]))  )
  if not os.path.isdir(outdir): 
       os.mkdir(outdir) 
  output = os.path.join(outdir, outfile)
  savefile(outdata, output)     
  print 
  print 'Saveing to ',output        
  print 
  
  ############################################################
  #                                Convert the flux catalog to mag catalog
  ############################################################
  zerofile = '/Users/xing/data/clash_cat/%s/cat_RED/**/zeropoints.txt'  %(cluster)
  zerofile = glob(zerofile)[0]
  if not os.path.isfile(zerofile):
      print 'ERROR: zeropoint file not found! ',zerofile
      pdb.set_trace()
      sys.exit()
  zbands, exptime, zeropoints  = fgetcols(zerofile, 1,5,4)
  zeros = {}
  for i in range(len(zbands)):
     zeros[zbands[i]] = zeropoints[i] 
  print 'Read zeropoints from ', zerofile

  for band in allbands:
     if band in bands:
         tmpmag = []
         tmpmage = []
         for tmp in range(len(datas[band])):  # for each obj
               t,te = fluxe2mage(datas[band][tmp], datas[band+'e'][tmp], abwave = wavelength[band][0]*10. , zero_pt=zeros[band])
               tmpmag.append(t)
               tmpmage.append(te)
         outdata[band] = tmpmag
         outdata[band+'e'] = tmpmage
     else:
         outdata[band] = np.zeros(len(obj),dtype=float)-99
         outdata[band+'e'] = np.zeros(len(obj),dtype=float)-99
  # now the outdata stores the photometry for one objects, but it includes all the 14 aperture photometry.

  # save to outfile
  outdir = './'+cluster
  outfile  = '%s_%s_aper_mymag.cat' %(cluster, str(int(obj[0]))  )
  if not os.path.isdir(outdir): os.mkdir(outdir) 
  output = os.path.join(outdir, outfile)
  savefile(outdata, output)     
  print 
  print 'Saveing to ',output        
  print     
  
  
  ############################################################
  #                                plot the SED
  ############################################################
  # plot the  SED
  if plot_aper!=0:
       print  'Plotting SED...'
       outimg = output.replace('.cat', '.jpg')
       plotimg_aper(outdata, plot_aper, outimg = outimg)
  
  pdb.set_trace()
  
  
  ############################################################
  #                                plot the magnitude catalogs
  outcol = [44,58]
  addcol = [6,10]   # auto and iso
  addcole = [7,11]  
  addnote = [0,1]
  ############################################################
  # find data from each catalog
  datas = {}
  for index in range(len(bands)):
      print 'reading %s ....' %bands[index]
      comfile = inputs[index]
      a = find( ra=objra, dec=objdec,  catfile =comfile, index_ra=index_ra, index_dec=index_dec, outcol=outcol, addcol = addcol , addcole = addcole)
      d  =a.mag
      de = a.mage
      x  = a.x
      y = a.y
      ra  = a.ra
      dec = a.dec 
      obj = a.obj
      datas[bands[index]]=d 
      datas[bands[index]+'e'] = de
      
  # set output data format 
  # example : src cat  num    x    y         ra        dec       f225w               f275w     ...
  outdata = {}
  outdata['obj'] = obj 
  outdata['note'] = allapers +   addnote 
  outdata['num'] = obj
  outdata['x'] = x
  outdata['y'] = y
  outdata['ra'] = ra
  outdata['dec'] = dec
  for band in allbands:
     if band in bands:
         outdata[band] = datas[band]
         outdata[band+'e'] = datas[band+'e']
     else:
         outdata[band] = np.zeros(len(obj),dtype=float)-99
         outdata[band+'e'] = np.zeros(len(obj),dtype=float)-99
  # now the outdata stores the photometry for one objects, but it includes all the 14 aperture photometry.

  # save to outfile
  outdir = './'+cluster
  outfile  = '%s_%s_aper_mag.cat' %(cluster, str(int(obj[0]))  )
  if not os.path.isdir(outdir): os.mkdir(outdir) 
  output = os.path.join(outdir, outfile)
  savefile(outdata, output)     
  print 
  print 'Saveing to ',output        
  print 
  
  ############################################################
  #                                plot the SED
  ############################################################
  # plot the  SED
  if plot_aper!=0:
       print  'Plotting SED...'
       outimg = output.replace('.cat', '.jpg')
       plotimg_aper(outdata, plot_aper, outimg = outimg)
  
  
  #pdb.set_trace()

  
  ############################################################
  #                                run bpz for *mymag.cat
  ############################################################
  bpzprefix = '%s_%s' %(cluster, str(int(obj[0]))  )
  imgdir = os.path.join(outdir, bpzprefix+'_html') 
  if not os.path.isdir(imgdir): os.mkdir(imgdir)

  mycat  = '%s_%s_aper_mymag.cat' %(cluster, str(int(obj[0]))  )
  mycat2 = '%s_%s.cat' %(cluster, str(int(obj[0]))  )
  bpzfile = '%s_%s.bpz' %(cluster, str(int(obj[0]))  )
  mycat = os.path.join(outdir, mycat)
  mycat2 = os.path.join(outdir, mycat2)
  bpzfile = os.path.join(outdir, bpzfile)
  parfile =  os.path.join(outdir, 'bpz.param')
  colfile =  os.path.join(outdir, 'bpz.columns')
  
  cmd ='mv %s %s' %(mycat, mycat2)  # rename my catalog
  cmd00 = 'cp %s %s' %('bpz.param', parfile)
  cmd01 = 'cp %s %s' %('bpz.columns', colfile)
  cmd1 = 'python $BPZPATH/bpz.py  %s  -P  %s  -COLUMNS  %s  -OUTPUT  %s'   %(mycat2, parfile, colfile, bpzfile)
  cmd2 = 'python $BPZPATH/bpzfinalize.py %s' %(os.path.join(outdir,bpzprefix) ) 
  cmd3 = 'python $BPZPATH/plots/webpage.py  %s  -DIR  %s' %(os.path.join(outdir,bpzprefix),  imgdir)   
  
  os.system(cmd)
  os.system(cmd00)
  os.system(cmd01)
  os.system(cmd1)
  os.system(cmd2)
  os.system(cmd3)
  print
  print '***************  bpz commands ********************'
  print cmd1
  print cmd2
  print cmd3
  print '***************  bpz commands ********************'
  print 
  #pdb.set_trace()



      
