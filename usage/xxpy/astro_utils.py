# astronomy
from __init__ import *


#from cosmolopy import cmag
import cosmolopy.magnitudes as cmag
import cosmolopy.distance as cd

# cosmos
cosmo = {'omega_M_0' : 0.3, 'omega_lambda_0' : 0.0, 'h' : 0.7}
cosmo = cd.set_omega_k_0(cosmo)

######################  magnitude convert ######################
# flux to magnitude
# ab_app, ab_abs = magnitude_AB(z, f_lambda, wavelength, **cosmo)
# luminosity to magnitude  (erg s^-1 Hz^-1)
# magAB = magnitude_AB_from_L_nu(luminosity_nu)
#
# L_star = cmag.L_nu_from_magAB(M_star)
# print cmag.magnitude_AB_from_L_nu(L_star)
#

def absolute_2_apparent(mag,z,**cosmo):
    # absolute magnitude to apparent magnitude
    mag2flux = lambda x: 10**((x-25.)/(-2.5))  # assuming zeropoint to 25.
    flux2mag = lambda x: -2.5*np.log10(x)+25.
    flux = mag2flux(mag)

    zdistance = cd.luminosity_distance(z, **cosmo)  # Mpc
    zflux = flux*(10.)**2./(zdistance*1.e6 )**2
    zmag = flux2mag(zflux)
    return(zmag)
    
    
######################  luminosity ######################
    
def Schechter_Lum(L, L_star=None, Alpha=None, Density=None):
    '''
    Schechter luminosity function in LUMINOSITY  
    number per dex
    # per lum to per dex
    # LF = schechterL(L, Density, Alpha, L_star)*np.log(10)*L
    '''
    ratio = L/L_star
    f = Density* np.e**(-ratio) *(ratio)**Alpha *ratio*np.log(10.) 
    #pdb.set_trace()
    return(f)
    
def Schechter_Lum_perL(L, L_star=None, Alpha=None, Density=None):
    '''
    Schechter luminosity function in LUMINOSITY  
    number per dex
    '''
    ratio = L/L_star
    f = Density* np.e**(-ratio) *(ratio)**Alpha  / L_star
    #pdb.set_trace()
    return(f)    
    
    
def Schechter_mag(M, M_star=None, Alpha=None, Density=None):
    '''
    Schechter luminosity function in magnitude
    '''    
    ratio =10**(-0.4*(M-M_star) )
    f = 0.4*np.log(10.) * Density*ratio**(Alpha+1) * np.e**(-ratio)
    return(f)

#  Bouwens with magnification of 9 for redshift 9
M_star = -22.4 
Alpha = -2.0
Density = 5.5*1.e-5

# Coe for redshfit 8
M_star = -20.26 
Alpha = -1.98
Density = 4.3*1.e-4

# Coe for redshfit 9
M_star = -19.86 
Alpha = -1.98
Density = 4.3*1.e-4

# bounwens redshift 9  Table 3.
M_star = -20.04
Alpha = -2.06
Density = 0.11*1.e-3

# Alavi 14 for z=2 galaxies
M_star = -20.01 #0.24
Alpha = -1.74 #0.08
Density = 10**(-2.54) #0.15

# test the luminosity function
'''    
print np.log10(Schechter_mag(M_star))
print np.log10(Schechter_Lum(cmag.L_nu_from_magAB(M_star)))
x = np.arange(20)/4.-22.
y = Schechter_mag(x)
fig = figure()
ax=fig.add_subplot(111)
ax.plot(x,np.log10(y))
ax.set_xlim(-22,-17.5)
ax.set_ylim(-6,-2)
ion()
grid()
show()
'''