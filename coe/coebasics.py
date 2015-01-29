import string
import os, sys
from os.path import join, exists
from numpy import *

#################################
# coeio.py

def run(cmd, pr=1):
    if pr:
        print cmd
    os.system(cmd)

home = os.environ.get('HOME', '')

def dirfile(filename, dir=""):
    """RETURN CLEAN FILENAME COMPLETE WITH PATH
    JOINS filename & dir, CHANGES ~/ TO home"""
    if filename[0:2] == '~/':
        filename = join(home, filename[2:])
    else:
        if dir[0:2] == '~/':
            dir = join(home, dir[2:])
        filename = join(dir, filename)
    return filename

def loadfile(filename, dir="", silent=0, keepnewlines=0):
    infile = dirfile(filename, dir)
    if not silent:
        print "Loading ", infile, "...\n"
    fin = open(infile, 'r')
    sin = fin.readlines()
    fin.close()
    if not keepnewlines:
        for i in range(len(sin)):
            #sin[i] = sin[i][:-1]
            if sin[i][-1] == '\n':
                sin[i] = sin[i][:-1]
    return sin

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


def loaddict(filename, dir="", silent=0):
    lines = loadfile(filename, dir, silent)
    dict = {}
    for line in lines:
        if line[0] <> '#':
            words = string.split(line)
            key = str2num(words[0])
            val = ''  # if nothing there
            valstr = string.join(words[1:], ' ')
            valtuple = False
            if valstr[0] in '[(' and valstr[-1] in '])':  # LIST / TUPLE!
                valtuple = valstr[0] == '('
                valstr = valstr[1:-1].replace(',', '')
                words[1:] = string.split(valstr)
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

def recapfile(name, ext):
    """CHANGE FILENAME EXTENSION"""
    if ext[0] <> '.':
        ext = '.' + ext
    i = string.rfind(name, ".")
    if i == -1:
        outname = name + ext
    else:
        outname = name[:i] + ext
    return outname

def capfile(name, ext):
    """ADD EXTENSION TO FILENAME IF NECESSARY"""
    if ext[0] <> '.':
        ext = '.' + ext
    n = len(ext)
    if name[-n:] <> ext:
        name += ext
    return name

def decapfile(name, ext=''):
    """REMOVE EXTENSION FROM FILENAME IF PRESENT
    IF ext LEFT BLANK, THEN ANY EXTENSION WILL BE REMOVED"""
    if ext:
        if ext[0] <> '.':
            ext = '.' + ext
        n = len(ext)
        if name[-n:] == ext:
            name = name[:-n]
    else:
        i = string.rfind(name, '.')
        if i > -1:
            name = name[:i]
    return name

uncapfile = decapfile

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

def params_cl(args=None, converttonumbers=True):
    """RETURNS PARAMETERS FROM COMMAND LINE ('cl') AS DICTIONARY:
    KEYS ARE OPTIONS BEGINNING WITH '-'
    VALUES ARE WHATEVER FOLLOWS KEYS: EITHER NOTHING (''), A VALUE, OR A LIST OF VALUES
    ALL VALUES ARE CONVERTED TO INT / FLOAT WHEN APPROPRIATE"""
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
            if key: # (HAVE GOTTEN TO KEYS)
                if value:
                    if converttonumbers:
                        value.append(str2num(list[i]))
                    else:
                        value = value + ' ' + list[i]
                else:
                    if converttonumbers:
                        value = [str2num(list[i])]
                    else:
                        value = list[i]
        i += 1

    return dict


#################################
# coetools.py

def stringsplitatoi(str, separator=''):
    if separator:
        words = string.split(str, separator)
    else:
        words = string.split(str)
    vals = []
    for word in words:
        vals.append(string.atoi(word))
    return vals

def stringsplitatof(str, separator=''):
    if separator:
        words = string.split(str, separator)
    else:
        words = string.split(str)
    vals = []
    for word in words:
        vals.append(string.atof(word))
    return vals

def stringsplitstrip(str, separator=''):
    # SPLITS BUT ALSO STRIPS EACH ITEM OF WHITESPACE
    if separator:
        words = string.split(str, separator)
    else:
        words = string.split(str)
    vals = []
    for word in words:
        vals.append(string.strip(word))
    return vals

def stringsplit(str, separator=''):
    # SPLITS BUT ALSO STRIPS EACH ITEM OF WHITESPACE
    if separator:
        words = string.split(str, separator)
    else:
        words = string.split(str)
    vals = []
    for word in words:
        vals.append(str2num(word))
    return vals

def strbegin(str, phr):
    return str[:len(phr)] == phr

def strend(str, phr):
    return str[-len(phr):] == phr

def strbtw(s, left, right=None, r=False, retall=False):
    """RETURNS THE PART OF STRING s BETWEEN left & right
    EXAMPLE strbtw('det_lab.reg', '_', '.') RETURNS 'lab'
    EXAMPLE strbtw('det_{a}.reg', '{}') RETURNS 'a'
    EXAMPLE strbtw('det_{{a}, b}.reg', '{}', r=1) RETURNS '{a}, b'"""
    out = None
    if right == None:
        if len(left) == 1:
            right = left
        elif len(left) == 2:
            left, right = left
    i1 = string.find(s, left)
    if (i1 > -1):
        i1 += len(left) - 1
        if r:  # search from the right
            i2 = string.rfind(s, right, i1+1)
        else:
            i2 = string.find(s, right, i1+1)
        if (i2 > i1):
            out = s[i1+1:i2]
    if retall:
        return s[:i1+1], s[i1+1:i2], s[i2:]
    else:
        return out
    #out = string.split(s, left)[1]
    #out = string.split(out, right)[0]


#################################
# MLab_coe.py

def floorint(x):
    return(int(floor(x)))

def ceilint(x):
    return(int(ceil(x)))

def roundint(x):
    if singlevalue(x):
        return(int(round(x)))
    else:
        return asarray(x).round().astype(int)

intround = roundint

def singlevalue(x):
    """IS x A SINGLE VALUE?  (AS OPPOSED TO AN ARRAY OR LIST)"""
    return type(x) in [type(None), float, float32, float64, int, int0, int8, int16, int32, int64]  # THERE ARE MORE TYPECODES IN Numpy

def roundn(x, ndec=0):
    if singlevalue(x):
	fac = 10.**ndec
	return roundint(x * fac) / fac
    else:
	rr = []
	for xx in x:
	    rr.append(roundn(xx, ndec))
	return array(rr)

#################################

def loaddata(filename, dir="", silent=0, headlines=0):
    sin = loadfile(filename, dir, silent)
    i = 0
    while sin[i][0] == '#':
        i += 1
        if i == len(sin):
            break

    sin = sin[i:]
    ny = len(sin)
    ss = string.split(sin[0])
    nx = len(ss)
    data = zeros((ny,nx))

    for iy in range(ny):
        ss = string.split(sin[iy])
        for ix in range(nx):
            data[iy,ix] = str2num(ss[ix])

    if data.shape[0] == 1:  # ONE ROW
        return ravel(data)
    else:
        return data

