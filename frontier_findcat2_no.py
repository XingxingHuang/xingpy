# July 1 : Now it can read the f125w.cat. For example:
# Oct 20 : revised 
# Dec 03 : revised for frontier a2744. Compare two catalog.

# #a1423 nir  833    x    y         ra        dec   f225w           f275w           f336w           f390w           f435w           f475w           f606w           f625w           f775w           f814w          f850lp           f105w           f110w           f125w           f140w           f160w           redshift
# a1423   1  833 2685 2703 179.332885  33.604235  27.1595 0.4606   0.0000 0.0000  25.5483 0.0785  26.2373 0.0895  26.5138 0.1474  26.3398 0.0942  26.1541 0.0735  26.4246 0.1322  26.1103 0.1133  25.8834 0.0551  27.0099 0.3270  26.0058 0.0778  25.5968 0.0397  25.3666 0.0491  25.4596 0.0443  25.9883 0.0700   1.7600
import os,sys,string,time,math
from glob import glob
import pdb
import numpy as np

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
class find:
  def __init__(self, fname='', ra1=None, dec1=None, comfile='', ra2=None, dec2=None, outcol=[], pdb_=0, silent =0):
#def __init__(self,fname=None, ra1=2, dec1=3, comfile=None, ra2=2, dec2=3, pdb_=1, prefix='tmp'):
    '''
    fname     :  include the ra dec for output catalogs
    ra1, dec1:  the ra dec index in fname.
    comfile   :  full catalogs with everything you need
    outcol     :  the columns of output data
    '''

    f = open(fname,'r')
    lines=f.readlines()
    data_all = [line.split() for line in lines if line.strip()!=''] 
    self.data = [i for i in data_all if not ('#' in i[0]) ]     # delete the elements begin with '#'
    f.close()

    cat = comfile  
    ############### define the index  of x y 
    if 1:
             m = outcol
             index_obj = 1
    # ra dec have been included in the input param
   ############### define the index  of x y 
    mag  = []
    mage = []
    allra = []
    alldec = []
    objnum =[]


    for source in self.data:  # different objects
      
        fcat = open(cat,'r')
        lines=fcat.readlines()
        data_all = [line.split() for line in lines if line.strip()!=''] 
        data = [i for i in data_all if not ('#' in i[0]) ]     
        fcat.close()
        detection = 0 

        ############### begin to select
        distance = 0.1    
        rmin = 90.*3600    
        findout=0   
        ################search in distance  
        for i in range (len(data)): # searching the catalog.
          # all objects
          ra = float(data[i][ra2-1])
          dec = float(data[i][dec2-1])
          # selected objects
          Zhengra = float(source[ra1-1])
          Zhengdec= float(source[dec1-1])  

          # detect closed object                
          if abs(ra-float(Zhengra) )< distance/3600. and abs(dec-float(Zhengdec) ) < distance/3600.:   
            findout =1+findout
            num = i
            r = math.sqrt((abs(ra-float(Zhengra))*3600. ) **2 + (abs(dec-float(Zhengdec) )*3600.)**2 )
            if silent ==0:
                 tmp = int(data[i][index_obj-1])
                 print '%4i     %f %f %f' %(tmp, ra, dec, r/0.065)
            if r < rmin:
             rmin=r
             index = i
            #pdb.set_trace() 
            

        if findout==0:
            print  'not found %6s in %10s' %(source[0],cat)
            print
            pdb.set_trace()
        elif findout>1:
            print  'too many found %6s in %10s' %(source[0],cat)
            #print
        else:
             num = index
             select_index=index
             r = rmin
             
             objnum.append(float(data[select_index][index_obj-1]))
             allra.append(float(data[select_index][ra2-1]))
             alldec.append(float(data[select_index][dec2-1]))
             try:
                tmp = float(data[select_index][m[0]-1])
             except:
                tmp = 99
             mag.append(tmp)
             try:
                tmp = float(data[select_index][m[1]-1])
             except:
                tmp = 99
             mage.append(tmp)   

        if pdb_==1:
            pdb.set_trace()
    #### End of the big loop 
    self.mag = mag
    self.mage = mage
    self.ra = allra
    self.dec = alldec
    self.obj = objnum

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


if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  text = 'Tips:  \n'
  usage=mod+" select_catfile cluter -outcol  <16,30  44,58>  [-col1  2,3]  [-col2 2,3]  [-outpre  obj]  \n"+text
  usage = 'Usage: \n    '+usage
  #usage += '    Set select_catfile to <cluster> to use the default catfile\n'
  usage += '    Default x y are  in 4th 5th columns\n'
  usage += '    Catalog name must be      <cluster>_<f160w>.cat\n'
  usage += '    Catalogs must be under  /Users/xing/data/clash_cat/<cluster>/cat_RED/**/sex\n'
  usage += '    -outpre :  define the output name. ./cat/<outpre>_frontier_aper.cat   else   ./cat/obj_frontier_aper.cat \n'
  usage += '    -outcol :  define the columns which will be selected for output catalogs. \n'
  usage += '             In my pipeline, FLUX_APER starts from 16, MAG_APER starts from 44.\n'   
  usage += '             The aperture sizes are 2,3,4,6,8,10,14,20,28,40,60,80,100,160\n'
  usage += 'Example: \n    python /Users/xing/programs/xing/frontier_findcat2.py ../clash_cat/a2744/highz/tmp.reg a2744 -outcol 44,58 -col1 4,5\n'   


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
  select_catfile = args[0]
  cluster = args[1]
  tmp = params.get('col1', [2,3])
  ra1 = tmp[0]
  dec1 =tmp[1]
  tmp = params.get('col2', [2,3])
  ra2 = tmp[0]
  dec2 =tmp[1]
  prefix = params.get('outpre', cluster)#define a prefix name for the output 
  outcol = params.get('outcol', None)
  xycol =[3,4]


  bands =[]
  inputs = []
  allbands =  ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
  catfiles = ['%s_%s.cat' %(cluster, band) for band in bands]
  catdir = '/Users/xing/data/clash_cat/%s/cat_RED/**/sex'  %(cluster)
 
  # check band
  for band in allbands:
      tmpfile = os.path.join(catdir,  '%s_%s.cat' %(cluster, band) )
      catfile = glob(tmpfile)
      #if not os.path.isfile(catfile):
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
  
  # find data from each catalog
  datas = {}
  for index in range(len(bands)):
      print 'reading %s ....' %bands[index]
      comfile = inputs[index]
      a = find(fname=select_catfile, ra1=ra1, dec1=dec1, comfile=comfile, ra2=ra2, dec2=dec2, outcol=outcol, pdb_=0)
      d  =a.mag
      de = a.mage
      ra  = a.ra
      dec = a.dec 
      obj = a.obj
      findxy  = find(fname=select_catfile, ra1=ra1, dec1=dec1, comfile=comfile, ra2=ra2, dec2=dec2, outcol=xycol, pdb_=0,silent =1)
      x =findxy.mag
      y = findxy.mage
      datas[bands[index]]=d 
      datas[bands[index]+'e'] = de

  # set output data format 
  # example : src cat  num    x    y         ra        dec       f225w               f275w     ...
  outdata = {}
  outdata['obj'] = obj 
  outdata['note'] = np.zeros(len(obj),dtype=int)
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


  # save to outfile
  outdir = './cat/'
  outfile  = '%s_frontier_aper.cat ' %prefix
  if not os.path.isdir(outdir): os.mkdir(outdir) 
  output = os.path.join(outdir, outfile)
  savefile(outdata, output)     
  print 
  print 'Saveing to ',output        
  print 








      
