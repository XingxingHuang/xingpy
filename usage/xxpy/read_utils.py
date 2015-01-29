# some program about reading files
from __init__ import *
import scipy
from scipy import ndimage

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
  

def radec(ra, dec, hours=""):
  """radec(ra, dec, hours="")
  Converts RA and Dec from decimal to sexigesimal units
  Returns a tuple (ihr, imin, xsec, imn, wsc)
  
  INPUTS:
    ra - right ascension, float or array, in degrees unless 
         "hours" is set
    dec - declination in decimal degrees, float or array, same
          number of elements as ra     
  
  OPTIONAL INPUT:
    hours - if set to true, then the right ascension input should
            be set to hours instead of degrees
            
  OUTPUTS:
    ihr - right ascension hours (float or array)
    imin - right ascension minutes (float or array)
    xsec - right ascension seconds (float or array)
    ideg - declination degrees (float or array)
    imn - declination minutes (float or array)
    xsc - declination seconds (float or array)         
  
  >>> radec(0,0) 
  array(0,0,0,0,0)
  """


  # Compute RA
  if(hours):
    ra =  np.mod(ra, 24)
    ra = ra + 24*(np.less(ra, 0) )
    ihr = np.fix(ra)
    xmin = np.abs(ra*60.0 - ihr*60.0)
  else:
    ra = np.mod(ra, 360)
    ra = ra + 360*(np.less(ra, 0))
    ihr = np.fix(ra/15.0)
    xmin = np.abs(ra*4.0 - ihr*60.0)

  imin = np.fix(xmin)
  xsec = (xmin - imin)*60.0

  # Compute Dec
  ideg = np.fix(dec)
  xmn = np.abs(dec - ideg)*60.0
  imn = np.fix(xmn)
  xsc = (xmn - imn)*60.0
  
 
def data_rebin(inarray,err=None, factor=10):
    #rebin the array by the defined factor
    #length = len(inarray)
    #length2 = int(length/factor)+1
    #newarray = scipy.ndimage.interpolation.zoom(inarray, factor)
    #pdb.set_trace()
    newarray = array_rebin(np.array(inarray),factor )
    if err !=None:
      #newerr = scipy.ndimage.interpolation.zoom(err, factor)
      newerr = array_rebin(err,factor)
      return(newarray,newerr)
    return(newarray)

def array_rebin(a,factor=2):
  length = len(a)
  length2 = int(int(len(a)//factor)*factor+factor)
  data = []
  for i in range(length2):
    if i>length-1:
        data[-1].append(a[-1])
        continue
    if i%factor==0:
        data.append([])
        data[-1].append(a[i]) 
    else:
        data[-1].append(a[i])  
  data = np.array(data)
  newdata = np.mean(data,axis=1)
  return(newdata)       


##########################################
### linear fit
# http://docs.scipy.org/doc/scipy-0.14.0/reference/odr.html
# using odr in scipy

#Define the function you want to fit against.:
def f(B, x):
    '''Linear function y = m*x + b'''
    # B is a vector of the parameters.
    # x is an array of the current x values.
    # x is in the same format as the x passed to Data or RealData.
    #
    # Return an array in the same format as y passed to Data or RealData.
    return B[0]*x + B[1]
def f2(B, x):
    '''Linear function y = m*(x + b)'''
    return B[0]*(x + B[1] ) 
#Create a Model.:
#     linear = Model(f)
#Create a Data or RealData instance.:
#     mydata = Data(x, y, wd=1./power(sx,2), we=1./power(sy,2))
#or, when the actual covariances are known:
#     mydata = RealData(x, y, sx=sx, sy=sy)
#Instantiate ODR with your data, model and initial parameter estimate.:
#     myodr = ODR(mydata, linear, beta0=[1., 2.])
#Run the fit.:
#     myoutput = myodr.run()
#Examine output.:
#     myoutput.pprint()  
def linear_fit(x,sx,y,sy,init_value=[1.,2.],printinfo=1):
    index = np.where( (x>-9e99) & (x<9e99) & (y>-9e99) & (y<9e99) )
    x = x[index]
    y = y[index]
    sx = sx[index]
    sy = sy[index]
    from scipy.odr import *
    linear = Model(f)
    #mydata = Data(x, y, wd=1./np.power(sx,2), we=1./np.power(sy,2))
    mydata = RealData(x, y, sx=sx, sy=sy)
    myodr = ODR(mydata, linear, beta0=init_value)
    myoutput = myodr.run()
    if printinfo==1:
      myoutput.pprint()  
    return(myoutput )
    
    
##########################################
### plot commands
##########################################

# ax.text(0.05, 0.95, txt, size=12, ha='left', va='top', transform=ax.transAxes)    
# ax.fill_between(redshift,i[0:zlen*1], i[zlen*2:zlen*3],facecolor= color0,edgecolor= 'None', alpha=0.3)
