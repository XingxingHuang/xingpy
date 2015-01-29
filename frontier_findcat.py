# July 1 : Now it can read the f125w.cat. For example:
# Oct 20 : revised 
# Dec 03 : revised for frontier a2744. Compare two catalog.

# #a1423 nir  833    x    y         ra        dec   f225w           f275w           f336w           f390w           f435w           f475w           f606w           f625w           f775w           f814w          f850lp           f105w           f110w           f125w           f140w           f160w           redshift
# a1423   1  833 2685 2703 179.332885  33.604235  27.1595 0.4606   0.0000 0.0000  25.5483 0.0785  26.2373 0.0895  26.5138 0.1474  26.3398 0.0942  26.1541 0.0735  26.4246 0.1322  26.1103 0.1133  25.8834 0.0551  27.0099 0.3270  26.0058 0.0778  25.5968 0.0397  25.3666 0.0491  25.4596 0.0443  25.9883 0.0700   1.7600
import os,sys,string,glob,time,math
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
  def __init__(self,fname=None, ra1=2, dec1=3, comfile=None, ra2=2, dec2=3, pdb_=1, prefix='tmp'):
    bands = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
    f = open(fname,'r')
    lines=f.readlines()
    data_all = [line.split() for line in lines] 
    self.data = [i for i in data_all if not ('#' in i[0]) ]     # delete the elements begin with '#'
    f.close()
    outdir = './cat'
    if not os.path.isdir(outdir): os.mkdir(outdir) 
    logfile = os.path.join( outdir,prefix+'_run.log')
    resultsfile =  os.path.join( outdir,prefix+'_frontier.cat')
    if os.path.isfile(logfile):
        os.remove(logfile)      
    if os.path.isfile(resultsfile):
        os.remove(resultsfile)      

    cat = comfile  
    for source in self.data:  # different objects
        print 
        print '>>>>> select the source %3i' %(float(source[0]))   ##
        fcat = open(cat,'r')
        lines=fcat.readlines()
        data_all = [line.split() for line in lines] 
        data = [i for i in data_all if not ('#' in i[0]) ]     
        fcat.close()
        detection = 0 
        ############### define the index  of x y 
        x2_index=4
        y2_index=5
        z2_index=1
        x1_index=4
        y1_index=5
        z1_index=1
        sigma2_index=10
        # the index of 16 bands
        # = ['f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w']
        m = [14,       20,      26,      32,      38,     44,     56,      62,      68,     74,       80,     86,      92,     98,     104,     110   ]
        ############### begin to select
        distance = 0.5		
        rmin = 90.*3600		
        findout=0	 
        ################search in distance	
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
            print '    ',ra,' ', dec,' ', r
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
             self.printlog('%55s %4.0f %11.7f %11.7f %4.0f %4.0f %7.5f %7.6f   %7f' %(source[0],0,ra,dec,x,y,z,r,sigma),fname=logfile)
             txt= '%5s ' %('num')+'%11s  '*16 %('f225w','f275w','f336w','f390w','f435w','f475w','f606w','f625w','f775w','f814w','f850lp','f105w','f110w','f125w','f140w','f160w')
             self.printlog(txt,fname=logfile)
             mag  = []
             mage = []
             print select_index
             for ii in [0,1,2,3,4,5]:
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
                if ii == 0: mag = [f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w]
                if ii == 1: mage = [f225w,f275w,f336w,f390w,f435w,f475w,f606w,f625w,f775w,f814w,f850lp,f105w,f110w,f125w,f140w,f160w]
             txt='%5s %3f %4f %4f %4f  %10.6f %10.6f  ' %(source[0],0,0,x,y,ra,dec)
             for band in range(0,16):
              mag_  = mag[band]
              mage_ = mage[band]
              if mag_ =='inf': mag_='99'
              if mage_ =='inf': mage_='99'
              txt=txt+'%9.4f %8.4f  ' %(float(mag_),float(mage_) )
             print '*** mag ***: \n'+txt  
             
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
      
if __name__ == '__main__':
  import getopt
 
  mod  = os.path.basename(sys.argv[0])
  text = 'Tips:  \n'
  usage=mod+" objfile full_catalog [-col1_ra 2] [-col1_dec 3]  [-col2_ra 2 ] [-col2_dec 3]  [-outpre  obj]  \n"+text
  usage = 'Usage: \n    '+usage
  usage += '    use -outpre to define the output name. [outpre]_frontier.cat. Default: obj_frontier.cat \n'
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
  objfile = args[0]
  comfile = args[1]
  ra1 = params.get('col1_ra', 2)
  ra2 = params.get('col2_ra', 2)
  dec1 = params.get('col1_dec', 3)
  dec2 = params.get('col2_dec', 3)
  prefix = params.get('outpre', 'obj')#define a prefix name for the output 
      
  find(fname=objfile, ra1=ra1, dec1=dec1, comfile=comfile, ra2=ra2, dec2=dec2, pdb_=0, prefix=prefix)
  #find(fname=fname,ircatalog=0)









      
