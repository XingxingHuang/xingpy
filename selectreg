#!/usr/bin/env python
#
# selected the objects contained in the region file. So it will be more convenient to select sources.
# if the region file does not exit, it will create a region file for all of the objects.
#   
#  type selectreg and see the help information
#
from readcol import readcol
import pdb,sys,os
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

def testspeed(length, i, speed):
  percent = int(i*10//length)
  if percent > speed:
     print '%i %%' %(percent*10)
     return(percent)
  else:
     return(speed)  

def RegionTest(ra, dec, delx, dely, dr):
    yes = 0
    for index in range(len(delx)):
        if abs(delx[index]-ra)<dr and abs(dely[index]-dec)<dr:
            yes+=1
    return(yes)        
            
if __name__ == '__main__':
  import getopt
  from os.path import *

  mod  = basename(sys.argv[0])
  txt = 'Write by:\n    Xingxing Huang (hxx@mail.ustc.edu.cn) '
  txt += '\nUsage:\n'
  usage=txt+mod+" incat outcat region [-region_del region2] [-col1 4] [-col2 5]  [-dr 1.]  [-printdel 0] [-keep keepfile]\n"
  usage += 'Tips: \n'
  usage += '    Please make sure the x y value is in column 4,5  for the [incat]. \n'
  usage += '    Please the columns used in [region] and [region_del] will be 1 and 2.\n'
  usage += '    [region] will be created while it is not found!\n'
  usage += '    exclude the objects in [-region_del]\n'
  usage += 'To Do: \n'
  usage += '    add the option -keep to only save defined columns of the catalogs.\n'
  opts1="i"
  opts2=[]
  
  # read param
  try:
     opts, args = getopt.getopt(sys.argv[1:],opts1,opts2)
  except getopt.GetoptError:
     sys.exit(usage)
  params = params_cl()
  if len(args)<3:
      sys.exit(usage)
  
  # params
  # the x y must be in the column m and n
  ifile = args[0]
  ofile = args[1]
  region = args[2]
  oregion = region  #while region does not exit, create oregion
  region_del = params.get('region_del', None)
  printdel = params.get('printdel', 0.)
  m = params.get('col1', 4)
  n = params.get('col2', 5)
  dr = params.get('dr', 1.)
  x = 1
  y = 2

  f=open(ifile)
  icat=f.readlines()
  f.close()
  ocat=[]
  
  # check the region file
  if isfile(region):
    regx=readcol(region).getcol(x)
    regy=readcol(region).getcol(y)
  else:
    print 'WARNING: region file does not exit! create the region.reg without selection'
    f=open(oregion,'w')
    for i_cat in range(len(icat)):
        if '#' in icat[i_cat]:
             continue
        tmp=icat[i_cat].split()
        ra=float(tmp[m-1])
        dec=float(tmp[n-1])
        text='%f  %f' %(ra,dec)
        print >> f,text
    f.close()
    sys.exit(oregion+' created! Please select the region first and select region again\n')

  # check the region_del file
  if region_del != None:
    if not  isfile(region_del): sys.exit('Not found: %s' %region_del)
    delx=readcol(region_del).getcol(x)
    dely=readcol(region_del).getcol(y)
    
  # start  
  count=0
  length = len(icat)
  percent = 0     # speed purpose
  comment = 0  # number of comment lines
  delnum = 0     # number of obj deleted based on the region_del
  for i_cat in range(length):
    percent = testspeed(length, i_cat, percent)
    yes=0
    if '#' in icat[i_cat]:
        comment += 1
        continue
  
    tmp=icat[i_cat].split()
    ra=float(tmp[m-1])
    dec=float(tmp[n-1])
    obj=tmp[0]
    for i_reg in range(len(regx)):
        if abs(regx[i_reg]-ra)<dr and abs(regy[i_reg]-dec)<dr:
            yes=1
    if yes==1:
        # if object is in the region_del file
        if region_del != None:
           inRegDel = RegionTest(ra, dec, delx, dely, dr)
           if inRegDel >0: 
               delnum += 1
               continue
        ocat.append(icat[i_cat][0:-1])
        print '%2i   %5i Keep %3i: %6.1f %6.1f' %(i_cat+1- comment-count,i_cat, float(obj),float(ra),float(dec))
    else:
        count+=1
        if printdel ==1:
            print '%2i del %3i: %6.1f %6.1f' %(count,float(obj),float(ra),float(dec))

  print
  # left number, left number. total number in region file.
  print '1. final num; 2. selected num based on region; 3. total num in region'
  print 'Number left:  %i  %i /%i'   %(len(ocat), length- comment-count , len(regx))
  print 'Number del :  %i'  %(count)
  print 'Number del :  %i based on the file %s'  %(delnum, region_del)
  print 
  f=open(ofile,'w')
  for text in ocat:
    print >> f,text
  f.close()
  #pdb.set_trace()