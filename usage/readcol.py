# Utilities for reading column-oriented files
#
# H. Ferguson - revised 10/20/03 to allow use of Numeric or numarray
# H. Ferguson - revised 2/10/08 to use numpy
# H. Ferguson - revised to add some options and remove Numeric and numarray

"""Routines for reading general whitespace-delimited, column-oriented files.
   Returned values are either numpy one-dimensional arrays.
   The read routines parse the input looking for
   decimal points or non-numeric characters to decide on the format of
   the output.  Reading is therefore a bit slow, but the program interface
   is extremely simple. For example, if the file 'foo' has three columns,
   read them in as follows:
	a,b,c = fgetcols('foo')

   A few other options:
       a,b,c,d = fgetcols('foo',1,3,5,7)  # Read some selected columns
       a = fgetcols('foo')     # Read all the columns (a is then a tuple of arrays)
       a,b,c = fgetcols('foo',fs=',') # Change the field separator to a comma 
       a,b,c = fgetcols('foo',cmt='!') # Change the comment character to '!'

   The module also provides an object-oriented interface to save re-reading
   the file if multiple getcol calls are desired:
       f = readcol('foo')
       a,b = f.getcols(1,2)
       c,d = f.getcols(3,4)
       f.close()

   Ignores comment lines.
   Ignores blank lines. 
   Optionally changes INDEF to a desired value (e.g. -99.99).

   As of version 5.0, only numpy is offered (Numeric and numarray used to be 
   options).
"""

__version__ = '5.0' # Numpy is now the default
__author = 'Henry C. Ferguson, STScI'

import string
import numpy

def remove_comments(l,cmt='#'):
    comments = []
    for i in range(len(l)):
        l[i] = l[i].strip()
        if l[i] == '\n' or l[i][0] == cmt:
            comments = comments + [i]
    ngone = 0
    for i in comments:
        comment = l.pop(i-ngone)
        ngone = ngone+1
    return l

def replace_indef(l,indef):
    for i in range(len(l)):
        while string.find(l[i],"INDEF") > -1:
            idx = string.find(l[i],"INDEF")
            l[i] = l[i][:idx]+indef+l[i][idx+5:]
    return l

class readcol:
    """Column-oriented file methods."""
    def __init__(self,cfile,arraytype=numpy,indef=""):
        """Open file, read in all the lines, and return numpy arrays.
          
           Arguments:
           cfile -- file to read
           arraytype -- numpy (used to allow Numeric or numarray)
           indef -- string replacement for INDEF (e.g. NaN)
        """
        f = open(cfile,'r')
        self.l = f.readlines()
        self.l = remove_comments(self.l)
        if indef:
            self.l = replace_indef(self.l,indef)
        f.close()
        self.N = arraytype
    def getcol(self,col,fs=None):
        """Read in a single column (columns start at 1)."""
        return getcol(col,self.l,self.N,fs=fs)
    def getcols(self,*args,**kwargs):
        """Read in a multiple columns (columns start at 1)."""
        if 'fs' in keywords.keys():
            fs = keywords['fs']
        else:
            fs = None
        ret = []
        for i in range(len(args)):
           ret = ret + [getcol(args[i],self.l,self.N,fs=fs)]
        return ret
    def close(self):
        """Release the memory associated with the lines read by __init__"""
        del(self.l)
        

def getcol(col,lines,N,fs=None):
  """Read in a single column from a list of strings. Parse each column to
     determine the type of variable (integer, float, string) and return 
     either an array of that type (int64, float64) or a character array.

     Arguments:
     col -- desired column (starting at 1)	
     lines -- list of strings (one per line) read from input file
     N -- numpy
  """
  i = col-1
  nlines = len(lines)
  if fs != None: # If delimiter is not whitespace, remove the whitespace
      oldlines = lines
      lines = []
      for ol in oldlines:
          lines += [string.join(ol.split())] 
  a = lines[0].split(fs) # Determine the type from the first line
  if string.find(a[i],'.') < 0:
    try:
      x = int(a[i]) 
    except:
      values = range(nlines)
      getstrings(col,lines,values,fs=fs)
      values = N.array(values)
    else:
      values = N.zeros((nlines),N.int64)
      if type(getints(col,lines,values,fs=fs)) == type(1):
        values = N.zeros((nlines),N.float64)
        getfloats(col,lines,values,fs=fs)
  else:
    try:
      x = float(a[i]) 
    except:
      values = range(nlines)
      getstrings(col,lines,values,fs=fs)
      values = N.array(values)
    else:
      values = N.zeros((nlines),N.float64)
      getfloats(col,lines,values,fs=fs)
  return values

def getstrings(col,lines,values,fs=None):
  n = 0
  for l in lines:
    a = l.split(fs)
    values[n] = a[col-1]
    n = n+1

def getints(col,lines,values,fs=None):
  n = 0
  for l in lines:
    a = l.split(fs)
    if string.find(a[col-1],'.') > 0:
      return -1
    else:
      values[n] = int(a[col-1])
    n = n+1
  return values    


def getfloats(col,lines,values,fs=None):
  n = 0
  for l in lines:
    a = l.split(fs)
    values[n] = float(a[col-1])
    n = n+1


def fgetcol(cfile,col,arraytype="numpy",cmt='#',indef="-99.99"):
    """Read in a single column from a file. Parse the column to
       determine the type of variable (integer, float, string) and return 
       either an array of that type (int64, float64) or a character array.

       Arguments:
       cfile -- file to be read
       col -- desired column (starting at 1)	
       arraytype -- numpy
       indef="-99.99" (INDEF replacement string)
    """
    f = open(cfile,'r')
    l = f.readlines()
    f.close()
    l = remove_comments(l,cmt=cmt)
    if indef:
        l = replace_indef(l,indef)
    if arraytype == "numpy":
        N = numpy
    return getcol(col,l,N)

def fgetcols(cfile,*args,**keywords):
    """Read multiple columns from a file. Parse each column to
       determine the type of variable (integer, float, string) and return 
       either one-dimensional arrays of the appropriate type (int64, float64) 
       or a character array.

       Arguments:
       cfile -- file to be read
       *args -- desired columns (starting at 1) 
       **keywords -- indef="-99.99" (INDEF replacement string)
                  -- cmt="#" (comment character)
                  -- fs=None (field separator; defaults to whitespace)

       Examples:
         If the file 'foo' has three columns, read them in as follows:
       a,b,c = fgetcols('foo')

         A few other examples:
             a,b,c,d = fgetcols('foo',1,3,5,7) # read selected columns 
             a = fgetcols('foo')               # read all columns 
             a,b,c = fgetcols('foo',fs=',')    # Change the field separator
             a,b,c = fgetcols('foo',cmt='!')   # Change the comment character to '!'

    """
    f = open(cfile,'r')
    l = f.readlines()
    f.close()
    if 'cmt' in keywords.keys():
        cmt = keywords['cmt']
    else:
        cmt = '#'
    l = remove_comments(l,cmt=cmt)
    if 'indef' in keywords.keys():
        indef = keywords['indef']
        l = replace_indef(l,indef)
    N = numpy
    if 'arraytype' in keywords.keys():
        arraytype = keywords['arraytype']
        if arraytype != "numpy":
            print "readcol: As of v5.0, only numpy arrays are returned"
    if 'fs' in keywords.keys():
        fs = keywords['fs']
    else:
        fs = None
    ret = []
    ncols = len(args)
    colnumbers = args
    if ncols == 0:       # If no columns are listed, read them all
        ncols = len(l[0].split(fs))
        colnumbers = N.array(range(ncols))+1
    for i in range(ncols):
        ret = ret + [getcol(colnumbers[i],l,N,fs=fs)]
    return ret


def fgetcols2(cfile,index,*args,**keywords):
    """
    revised by xingxing, Huang in Oct18 2014
    index is an array include the columns
    """
    f = open(cfile,'r')
    l = f.readlines()
    f.close()
    if 'cmt' in keywords.keys():
        cmt = keywords['cmt']
    else:
        cmt = '#'
    l = remove_comments(l,cmt=cmt)
    if 'indef' in keywords.keys():
        indef = keywords['indef']
        l = replace_indef(l,indef)
    N = numpy
    if 'arraytype' in keywords.keys():
        arraytype = keywords['arraytype']
        if arraytype != "numpy":
            print "readcol: As of v5.0, only numpy arrays are returned"
    if 'fs' in keywords.keys():
        fs = keywords['fs']
    else:
        fs = None
    ret = []
    ncols = len(index)
    colnumbers = index
    if ncols == 0:       # If no columns are listed, read them all
        ncols = len(l[0].split(fs))
        colnumbers = N.array(range(ncols))+1
    for i in range(ncols):
        ret = ret + [getcol(colnumbers[i],l,N,fs=fs)]
    return ret

