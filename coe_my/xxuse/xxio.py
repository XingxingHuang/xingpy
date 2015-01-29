import string
import datetime
import sys
import os

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
def timestr():
     '''
     return the time string. example:  140128
     '''
     txt = datetime.date.today().strftime('%y%m%d') 
     return(txt)

def extractfilt(name):
    '''
    get the filter name from the string like "*_f105w_"
    '''
    words = name.split('_')
    for word in words:
        if string.lower(word[0]) == 'f':
            good = True
            for i in 1,2,3:
                good = good and (word[i] in string.digits)
            if good:
                return word

def makedirsmode(newpath, mode=0775):
    """Make a directory path and set permissions along the way"""
    path = ''
    for dir in splitdirs(newpath):
        path = os.path.join(path, dir)
        if not os.path.isdir(path):
            os.mkdir(path)
            os.chmod(path, mode)

def splitdirs(dir):
    """Splits a path into a list of directories"""
    print dir
    rootdir, basedir = os.path.split(dir)
    dirs = [basedir]
    while rootdir:
        rootdir, basedir = os.path.split(rootdir)
        dirs.append(basedir)
        if rootdir == '/':
            dirs.append('/')
            break
    return dirs[::-1]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
def load_indexdict(filename, dir="", silent=0):
    '''
    load parameters from a file 
    file looks like:
             1 id              Object ID Number
             2 RA              Right Ascension in decimal degrees
             3 Dec             Declination in decimal degrees
    output :
            {'id':0, 'RA':2, ....}         
    
    need: loadfile
    '''
    lines = loadfile(filename, dir, silent)
    dict = {}
    for line in lines:
        if line[0] <> '#':
            words = string.split(line)
            key = words[1]
            if len(words)<2:
                sys.exit('ERROR: check '+filename)
            val = int(words[0])-1
            dict[key] = val
    return dict

def loaddict0(filename, dir="", silent=0):
    '''
    load parameters from a file 
    need: loadfile
    '''
    lines = loadfile(filename, dir, silent)
    dict = {}
    for line in lines:
        if line[0] <> '#':
            words = string.split(line)
            key = words[0]
            val = ''  # if nothing there
            if len(words) == 2:
                val = words[1]
            elif len(words) > 2:
                val = []
                for word in words[1:]:
                    val.append(word)
                
            dict[key] = val
    return dict
       
def loadfile(filename, dir="", silent=0, keepnewlines=0):
    infile = os.path.join(dir,filename)
    if not silent:
        print "Loading ", infile, "...\n"
    fin = open(infile, 'r')
    sin = fin.readlines()
    fin.close()
    if not keepnewlines:
        for i in range(len(sin)):
            if sin[i][-1] == '\n':
                sin[i] = sin[i][:-1]
    return sin
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++