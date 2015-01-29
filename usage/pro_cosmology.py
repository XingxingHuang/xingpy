import os, sys
from math import sqrt
import pyfits
from scipy.integrate import quad

#################################
# Cosmology

h = 0.7  # Hubble constant / (100 km/s/Mpc)
Om = 0.3  # Omega matter
OL = 1 - Om  # Omega Lambda

H100 = 3.24077674937e-18  # 100 km/s/Mpc in units of 1 / S (inverse seconds)
c = 9.7155e-15  # MPC / S

def H(z):
    """Hubble constant [1/S] at redshift z for a flat universe"""
    return h * H100 * sqrt(Om * (1+z)**3 + OL)

def Hinv(z):
    return 1 / H(z)

def DA(z1, z2):
    """Angular-diameter distance (MPC)
    between two redshifts for a flat universe"""
    #return c / (1.+z2) * integral(lambda z: 1/H(z), z1, z2)
    return c / (1.+z2) * quad(Hinv, z1, z2)[0]

def Dds_Ds(zl, zs):
    """Ratio of angular diameter distances;
    Lensing deflections scale with this quantity"""
    if zs == float('Inf'):
        return 1
    else:
        Dds = DA(zl, zs)
        Ds  = DA(0,  zs)
        return Dds / Ds

#################################
#  my calculation
from cosmocalc import cosmocalc
import  numpy as np

H0    =  70.
WM    =  0.3
#H0    =  71.
#WM    =  0.27
def my_Dds_Ds(z1,z2):
    Dl = cosmocalc(z1,H0=H0,WM=WM)['DA_Mpc']  # distance of the cluster
    Ds = cosmocalc(z2,H0=H0,WM=WM)['DA_Mpc']  # distance of the object
    dls = angular_distance(z1,z2)
    dls2 = DA(z1,z2)
    print dls, dls2
    ds = Ds
    ratio = dls / ds
    return(ratio)
    
def  angular_distance(z1,z2):

   '''
Parameters: for cosmocalc
z - redshift
H0 - Hubble constant (default = 71)
WM - Omega matter (default = 0.27)
WV - Omega vacuum (default = 1.0 - WM - 0.4165/(H0*H0))
Return type:  
dictionary of cosmology values (name_unit = value)
   '''
   from scipy import constants
   c_kms = constants.c / 1000.
   dm1   = cosmocalc(z1,H0=H0,WM=WM)['DA_Mpc']*(1.+z1)
   dm2   = cosmocalc(z2,H0=H0,WM=WM)['DA_Mpc']*(1.+z2)
   #dm1 = cosmocalc(z1,H0=H0,WM=WM)['DCMR_Mpc']
   dh_2  = (c_kms / H0 )**2
   # wrong Ok    = 1.0 - WM - 0.4165/(H0*H0)
   Ok = 0.
   # check Hogg 9906116
   out = 1. / (1. + z2) * (dm2*np.sqrt(1. + Ok*dm1**2 / dh_2) -dm1*np.sqrt(1. + Ok*dm2**2 / dh_2))   
   #pdb.set_trace()
   return(out)