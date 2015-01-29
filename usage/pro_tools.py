import os,pdb,sys
import string
import math
import datetime
from os.path import join, exists
from numpy import *  # zeros, sort, compress, concatenate, greater



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
#from pro_tools import *
#a = loaddict('ampfile.txt')


###################################################################################################
def checkinfo(txt):
      '''
      make a pause in the program 
      '''
      tmp  = raw_input('\n%s.. (press y for debug) \n' %txt)
      if tmp == 'y':   
          pdb.set_trace()  
          
def addwarning(warning, txt, silent=0 ):
      '''
      add warning message to the list and print out the message
      '''      
      if silent !=0:   
           print warning
      warning.append(txt)
      return(warning)
      
def printwarning(warning):
      '''
      print warning message. can be used in the end of one program
      '''   
      print '****************************************************************'   
      print '                           WARNING  '
      print '****************************************************************'   
      for txt in warning:
          print '   ', txt
          
###################################################################################################
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



def printlog(text,fname='tmp.log',ptime=0,overwrite=0,):
    '''
    write the text you define 
    '''
    if os.path.exists(fname):
      if overwrite==0:
        f = open(fname,'a')
      else:
        f = open(fname,'w')
    else:
      f = open(fname,'w')   
      txt='####This file is used for recording the results  ####'
      print >> f, txt
      del txt
      print fname+' created!'
    if ptime==1:
        ptime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()))   
        format = '#\n###  %s  ###'  
        print >> f, format % (ptime)    
    print >>  f, text
    print text
    f.close()     