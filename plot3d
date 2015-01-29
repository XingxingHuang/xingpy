#!/usr/bin/env python
# revised for anton's catalog
import os,sys,string,glob,time
import pdb
from pyraf import iraf
import numpy as np
from pylab import *
import shutil
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import numpy as np
from matplotlib import cm
from matplotlib import pyplot as plt
import pyfits



class run():
  """
    
  """
  def __init__(self,fname='', x=0, y=0, size=0):
    self.indir = os.path.join('./',fname)
    fits = pyfits.open(self.indir)
    self.x    = np.linspace(x-size,x+size,size*2.)
    self.y    = np.linspace(y-size,y+size,size*2.)
    self.z    = fits[0].data[(y-size-1):(y+size-1),(x-size-1):(x+size-1)]
    maxz = [max(self.z[i,:]) for i in range(len(self.z[:,0]))]
    fits.close()
    
    
    fig = plt.figure()
    ax = Axes3D(fig) 
    

    # plot surface
    X, Y = np.meshgrid(self.x, self.y)
    surf = ax.plot_surface(X, Y, self.z,rstride=1, cstride=1, alpha=0.3, cmap=cm.jet)
    #cset=plt.contour(X, Y, self.z,zdir='z',offset=0)
    #ax.clabel(cset, fontsize=9, inline=1)
    #ax.set_zlim3d(0, 30)
    ax.set_zlim3d(0, max(maxz))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    '''
    # plot contour
    cset = ax.contour(self.x, self.y, self.z,100)
    ax.clabel(cset, fontsize=11, inline=1)
    fig.colorbar(cset, shrink=0.5, aspect=5)
    ax.set_zlim3d(0, max(maxz))
    ax.set_xlabel('x')		#(r'$\phi_\mathrm{real}$')
    ax.set_ylabel('y')		#(r'$\phi_\mathrm{im}$')
    ax.set_zlabel('counts')	#(r'$V(\phi)$')
    '''
    ion()
    plt.show()
    pdb.set_trace()
    

    
    
   

    '''
step = 0.04
maxval = 1.0
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# create supporting points in polar coordinates
r = np.linspace(0,1.25,50)
p = np.linspace(0,2*np.pi,50)
R,P = np.meshgrid(r,p)
# transform them to cartesian system
X,Y = R*np.cos(P),R*np.sin(P)

Z = ((R**2 - 1)**2)
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.YlGnBu_r)
ax.set_zlim3d(0, 1)
ax.set_xlabel(r'$\phi_\mathrm{real}$')
ax.set_ylabel(r'$\phi_\mathrm{im}$')
ax.set_zlabel(r'$V(\phi)$')
plt.show()
    '''       
    
    
if __name__ == '__main__':
  import getopt
  from drizzlepac import skytopix

  mod  = os.path.basename(sys.argv[0])
  usage='Usage: '+mod+" .fits x y size"
  option=''
  try:
    opts, arg = getopt.getopt(sys.argv[1:],'',option)
  except getopt.GetoptError:
    # print help information and exit:
    sys.exit(usage)
  if len(arg)<4:
    sys.exit(usage)

  fname  = arg[0]
  x      = int(float(arg[1]))
  y 	 = int(float(arg[2]))
  size	 = int(arg[3])
  
  
  if float(arg[1])%1.!=0:
    x = float(arg[1])
    y = float(arg[2])
    x,y = skytopix.rd2xy(fname,x,y)
      
  run(fname=fname, x=x, y=y, size=size)
  
  
  
  
  
  
  
  
  

