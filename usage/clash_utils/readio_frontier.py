###
# some program related to clash data
from os.path import *
import numpy as np
from os.path import *
from matplotlib import pyplot as plt
from pylab import ion
from glob import glob
import pdb
import string,sys

######################################################################
###   make sure the following are right
######################################################################
rootdir = '/Volumes/Seagate/clash'
clusters =   ['a2744','m0416'] 
         

bands = ['f435w','f606w','f814w','f105w','f125w','f140w','f160w']

#cat_image = join(rootdir,'0readme','image.cat')
#cat_model = join(rootdir,'0readme','model.cat')
#cat_catlog = join(rootdir,'0readme','catalog.cat')
#cat_cluster = join(rootdir,'0readme','cluster.cat')

infodir = '/Users/xing/data/clash_web'
cat_image = join(infodir,'image_frontier.cat')
cat_model = join(infodir,'model_frontier.cat')
cat_catlog = join(infodir,'catalog_frontier.cat')
cat_catlog_xing = join(infodir,'catalog_xing_frontier.cat')
cat_cluster = join(infodir,'cluster_frontier.cat')


######################################################################
def clusterinfo(cluster):
    '''
    read the informations and return.
    '''
    infos = loaddict(cat_cluster)  
    info = infos[cluster]
    return(info)

#def getcat(cluster,special = 'IR'):
#        infos = loaddict(cat_cluster)  
#    info = infos[cluster]
    
def getcat(cluster,special=None):
    '''
    return the path and catalog
    '''
    infos = loaddict(cat_catlog)  
    info = infos[cluster]
    cat_name = join(rootdir,info[0],info[1])
    if special!=None:
        cat_name = join(rootdir,info[0],special)
        cat_files = globfiles(cat_name,keys = None)
        return(cat_files[0])
    cat_files = globfiles(cat_name,keys = None)
    return(cat_files[0])     
    
def getimage(cluster,special=None):
    '''
    return the path to CLASH images for the cluster
    '''
    if cluster not in clusters:
        print 'Not FOUND: ',cluster
        sys.exit()
    imgdict = loaddict(cat_image)    
    info = imgdict[cluster]
    image_name = join(rootdir,info[0],info[1])
    if special!=None:
        image_name = join(rootdir,info[0],special)
        image_files = globfiles(image_name,keys = ['total'])
        return(image_files)
    image_files = globfiles(image_name,keys = bands)
    return(image_files) 
    

def getmodel(cluster):
    '''
    return the path to CLASH models for the cluster
    '''
    if cluster not in clusters:
        print 'Not FOUND: ',cluster
        sys.exit()
    imgdict = loaddict(cat_model)    
    info = imgdict[cluster]
    image_alphax = join(rootdir,info[0],info[3])
    image_alphay = join(rootdir,info[0],info[4])   # in pixel scale
    if len(glob(image_alphax))==0:
        print '**WARNING**: No magnification map for ',cluster
        return(None,None)
    image_file1 = glob(image_alphax)[0]
    image_file2 = glob(image_alphay)[0]
    return(image_file1,image_file2) 
    
            
def getmagnif(cluster,txt='.'):    
    '''
    return the path to CLASH magnification images for the cluster
    only the file which includes the txt in the name will be return
    '''
    if cluster not in clusters:
        print 'Not FOUND: ',cluster
        sys.exit()

    imgdict = loaddict(cat_model)    
    info = imgdict[cluster]
    image_name = join(rootdir,info[0],info[7])
    image_files = glob(image_name)
    if len(image_files)<1:
        print 'ERROR: not found '
        print '   ',image_name
        sys.exit()
    outimages = [img for img in image_files if txt in basename(img)]   
    if len(outimages)<1:
        print 'ERROR: not found ',txt
        print '   ',outimages
        sys.exit()
    elif len(outimages)>1:
        print 'ERROR: too many files found'
        for f in outimages:
            print '   ', f
        sys.exit()
    else:   
        return(outimages[0])         


######################################################################
#  sub routing

def globfiles(ftext,keys=None):
    '''
    glob the files based on the fname. 
    if keys is set, then it will a dictionary.
    
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