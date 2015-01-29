# some program about reading files
from __init__ import *


################################################
#The five reddening laws presently implemented in hyperz are:
# Allen (1976) for the Milky Way (MW);
# Seaton (1979) fit by Fitzpatrick (1986) for the MW;
# Fitzpatrick (1986) for the Large Magellanic Cloud (LMC);
# Prevot et al. (1984) and Bouchet et al. (1985) for the Small Magellanic Cloud (SMC);
# Calzetti et al. (2000) for starburst galaxies.

def ccm_unred(wave, flux, ebv, r_v=""):
    # https://github.com/mubdi/pyastrolib/blob/master/astro.py
    """ccm_unred(wave, flux, ebv, r_v="")
    Deredden a flux vector using the CCM 1989 parameterization 
    Returns an array of the unreddened flux
  
    INPUTS:
    wave - array of wavelengths (in Angstroms)
    dec - calibrated flux array, same number of elements as wave
    ebv - colour excess E(B-V) float. If a negative ebv is supplied
          fluxes will be reddened rather than dereddened     
  
    OPTIONAL INPUT:
    r_v - float specifying the ratio of total selective
          extinction R(V) = A(V)/E(B-V). If not specified,
          then r_v = 3.1
            
    OUTPUTS:
    funred - unreddened calibrated flux array, same number of 
             elements as wave
             
    NOTES:
    1. This function was converted from the IDL Astrolib procedure
       last updated in April 1998. All notes from that function
       (provided below) are relevant to this function 
       
    2. (From IDL:) The CCM curve shows good agreement with the Savage & Mathis (1979)
       ultraviolet curve shortward of 1400 A, but is probably
       preferable between 1200 and 1400 A.
    3. (From IDL:) Many sightlines with peculiar ultraviolet interstellar extinction 
       can be represented with a CCM curve, if the proper value of 
       R(V) is supplied.
    4. (From IDL:) Curve is extrapolated between 912 and 1000 A as suggested by
       Longo et al. (1989, ApJ, 339,474)
    5. (From IDL:) Use the 4 parameter calling sequence if you wish to save the 
       original flux vector.
    6. (From IDL:) Valencic et al. (2004, ApJ, 616, 912) revise the ultraviolet CCM
       curve (3.3 -- 8.0 um-1).    But since their revised curve does
       not connect smoothly with longer and shorter wavelengths, it is
       not included here.
 
    7. For the optical/NIR transformation, the coefficients from 
       O'Donnell (1994) are used
  
    >>> ccm_unred([1000, 2000, 3000], [1, 1, 1], 2 ) 
    array([9.7976e+012, 1.12064e+07, 32287.1])
    """
    wave = np.array(wave, float)
    flux = np.array(flux, float)
    
    if wave.size != flux.size: raise TypeError, 'ERROR - wave and flux vectors must be the same size'
    
    if not bool(r_v): r_v = 3.1 

    x = 10000.0/wave
    npts = wave.size
    a = np.zeros(npts, float)
    b = np.zeros(npts, float)
    
    ###############################
    #Infrared
    
    good = np.where( (x > 0.3) & (x < 1.1) )
    a[good] = 0.574 * x[good]**(1.61)
    b[good] = -0.527 * x[good]**(1.61)
    
    ###############################
    # Optical & Near IR

    good = np.where( (x  >= 1.1) & (x < 3.3) )
    y = x[good] - 1.82
    
    c1 = np.array([ 1.0 , 0.104,   -0.609,    0.701,  1.137, \
                  -1.718,   -0.827,    1.647, -0.505 ])
    c2 = np.array([ 0.0,  1.952,    2.908,   -3.989, -7.985, \
                  11.102,    5.491,  -10.805,  3.347 ] )

    a[good] = np.polyval(c1[::-1], y)
    b[good] = np.polyval(c2[::-1], y)

    ###############################
    # Mid-UV
    
    good = np.where( (x >= 3.3) & (x < 8) )   
    y = x[good]
    F_a = np.zeros(np.size(good),float)
    F_b = np.zeros(np.size(good),float)
    good1 = np.where( y > 5.9 )    
    
    if np.size(good1) > 0:
        y1 = y[good1] - 5.9
        F_a[ good1] = -0.04473 * y1**2 - 0.009779 * y1**3
        F_b[ good1] =   0.2130 * y1**2  +  0.1207 * y1**3

    a[good] =  1.752 - 0.316*y - (0.104 / ( (y-4.67)**2 + 0.341 )) + F_a
    b[good] = -3.090 + 1.825*y + (1.206 / ( (y-4.62)**2 + 0.263 )) + F_b
    
    ###############################
    # Far-UV
    
    good = np.where( (x >= 8) & (x <= 11) )   
    y = x[good] - 8.0
    c1 = [ -1.073, -0.628,  0.137, -0.070 ]
    c2 = [ 13.670,  4.257, -0.420,  0.374 ]
    a[good] = np.polyval(c1[::-1], y)
    b[good] = np.polyval(c2[::-1], y)

    # Applying Extinction Correction
    
    a_v = r_v * ebv
    a_lambda = a_v * (a + b/r_v)
    
    funred = flux * 10.0**(0.4*a_lambda)   

    return funred
    
def fm_unred(wave, flux, ebv, *args, **kwargs):
    
    '''
    NAME:
     FM_UNRED
    PURPOSE:
     Deredden a flux vector using the Fitzpatrick (1999) parameterization
    EXPLANATION:
     The R-dependent Galactic extinction curve is that of Fitzpatrick & Massa 
     (Fitzpatrick, 1999, PASP, 111, 63; astro-ph/9809387 ).    
     Parameterization is valid from the IR to the far-UV (3.5 microns to 0.1 
     microns).  UV extinction curve is extrapolated down to 912 Angstroms.

    CALLING SEQUENCE:
     fm_unred( wave, flux, ebv [, 'LMC2', 'AVGLMC', 'ExtCurve', R_V = ,  
                                   gamma =, x0=, c1=, c2=, c3=, c4= ])
    INPUT:
      wave - wavelength vector (Angstroms)
      flux - calibrated flux vector, same number of elements as "wave"
      ebv  - color excess E(B-V), scalar.  If a negative "ebv" is supplied,
              then fluxes will be reddened rather than dereddened.

    OUTPUT:
      Unreddened flux vector, same units and number of elements as "flux"

    OPTIONAL INPUT KEYWORDS
      R_V - scalar specifying the ratio of total to selective extinction
               R(V) = A(V) / E(B - V).  If not specified, then R = 3.1
               Extreme values of R(V) range from 2.3 to 5.3

      'AVGLMC' - if set, then the default fit parameters c1,c2,c3,c4,gamma,x0 
             are set to the average values determined for reddening in the 
             general Large Magellanic Cloud (LMC) field by Misselt et al. 
            (1999, ApJ, 515, 128)
      'LMC2' - if set, then the fit parameters are set to the values determined
             for the LMC2 field (including 30 Dor) by Misselt et al.
             Note that neither /AVGLMC or /LMC2 will alter the default value 
             of R_V which is poorly known for the LMC. 
             
      The following five input keyword parameters allow the user to customize
      the adopted extinction curve.  For example, see Clayton et al. (2003,
      ApJ, 588, 871) for examples of these parameters in different interstellar
      environments.

      x0 - Centroid of 2200 A bump in microns (default = 4.596)
      gamma - Width of 2200 A bump in microns (default = 0.99)
      c3 - Strength of the 2200 A bump (default = 3.23)
      c4 - FUV curvature (default = 0.41)
      c2 - Slope of the linear UV extinction component 
           (default = -0.824 + 4.717 / R)
      c1 - Intercept of the linear UV extinction component 
           (default = 2.030 - 3.007 * c2)
            
    OPTIONAL OUTPUT KEYWORD:
      'ExtCurve' - If this keyword is set, fm_unred will return two arrays.
                  First array is the unreddend flux vector.  Second array is
                  the E(wave-V)/E(B-V) extinction curve, interpolated onto the
                  input wavelength vector.

    EXAMPLE:
       Determine how a flat spectrum (in wavelength) between 1200 A and 3200 A
       is altered by a reddening of E(B-V) = 0.1.  Assume an "average"
       reddening for the diffuse interstellar medium (R(V) = 3.1)

       >>> w = 1200 + arange(40)*50       #Create a wavelength vector
       >>> f = w*0 + 1                    #Create a "flat" flux vector
       >>> fnew = fm_unred(w, f, -0.1)    #Redden (negative E(B-V)) flux vector
       >>> plot(w, fnew)                   

    NOTES:
       (1) The following comparisons between the FM curve and that of Cardelli, 
           Clayton, & Mathis (1989), (see ccm_unred.pro):
           (a) - In the UV, the FM and CCM curves are similar for R < 4.0, but
                 diverge for larger R
           (b) - In the optical region, the FM more closely matches the
                 monochromatic extinction, especially near the R band.
       (2)  Many sightlines with peculiar ultraviolet interstellar extinction 
               can be represented with the FM curve, if the proper value of 
               R(V) is supplied.
    REQUIRED MODULES:
       scipy, numpy
    REVISION HISTORY:
       Written   W. Landsman        Raytheon  STX   October, 1998
       Based on FMRCurve by E. Fitzpatrick (Villanova)
       Added /LMC2 and /AVGLMC keywords,  W. Landsman   August 2000
       Added ExtCurve keyword, J. Wm. Parker   August 2000
       Assume since V5.4 use COMPLEMENT to WHERE  W. Landsman April 2006
       Ported to Python, C. Theissen August 2012
    '''
    
    # Import needed modules
    from scipy.interpolate import InterpolatedUnivariateSpline as spline
    import numpy as n

    # Set defaults
    lmc2_set, avglmc_set, extcurve_set = None, None, None
    R_V, gamma, x0, c1, c2, c3, c4 = None, None, None, None, None, None, None
    
    x = 10000. / n.array([wave])                # Convert to inverse microns
    curve = x * 0.

    # Read in keywords
    for arg in args:
        if arg.lower() == 'lmc2': lmc2_set = 1
        if arg.lower() == 'avglmc': avglmc_set = 1
        if arg.lower() == 'extcurve': extcurve_set = 1
        
    for key in kwargs:
        if key.lower() == 'r_v':
            R_V = kwargs[key]
        if key.lower() == 'x0':
            x0 = kwargs[key]
        if key.lower() == 'gamma':
            gamma = kwargs[key]
        if key.lower() == 'c4':
            c4 = kwargs[key]
        if key.lower() == 'c3':
            c3 = kwargs[key]
        if key.lower() == 'c2':
            c2 = kwargs[key]
        if key.lower() == 'c1':
            c1 = kwargs[key]

    if R_V == None: R_V = 3.1

    if lmc2_set == 1:
        if x0 == None: x0 = 4.626
        if gamma == None: gamma =  1.05 
        if c4 == None: c4 = 0.42   
        if c3 == None: c3 = 1.92  
        if c2 == None: c2 = 1.31
        if c1 == None: c1 = -2.16
    elif avglmc_set == 1:
        if x0 == None: x0 = 4.596  
        if gamma == None: gamma = 0.91
        if c4 == None: c4 = 0.64  
        if c3 == None: c3 =  2.73 
        if c2 == None: c2 = 1.11
        if c1 == None: c1 = -1.28
    else:
        if x0 == None: x0 = 4.596  
        if gamma == None: gamma = 0.99
        if c4 == None: c4 = 0.41
        if c3 == None: c3 =  3.23 
        if c2 == None: c2 = -0.824 + 4.717 / R_V
        if c1 == None: c1 = 2.030 - 3.007 * c2
    
    # Compute UV portion of A(lambda)/E(B-V) curve using FM fitting function and 
    # R-dependent coefficients
 
    xcutuv = 10000.0 / 2700.0
    xspluv = 10000.0 / n.array([2700.0, 2600.0])
   
    iuv = n.where(x >= xcutuv)
    iuv_comp = n.where(x < xcutuv)

    if len(x[iuv]) > 0: xuv = n.concatenate( (xspluv, x[iuv]) )
    else: xuv = xspluv.copy()

    yuv = c1  + c2 * xuv
    yuv = yuv + c3 * xuv**2 / ( ( xuv**2 - x0**2 )**2 + ( xuv * gamma )**2 )

    filter1 = xuv.copy()
    filter1[n.where(xuv <= 5.9)] = 5.9
    
    yuv = yuv + c4 * ( 0.5392 * ( filter1 - 5.9 )**2 + 0.05644 * ( filter1 - 5.9 )**3 )
    yuv = yuv + R_V
    yspluv = yuv[0:2].copy()                  # save spline points
    
    if len(x[iuv]) > 0: curve[iuv] = yuv[2:len(yuv)]      # remove spline points

    # Compute optical portion of A(lambda)/E(B-V) curve
    # using cubic spline anchored in UV, optical, and IR

    xsplopir = n.concatenate(([0], 10000.0 / n.array([26500.0, 12200.0, 6000.0, 5470.0, 4670.0, 4110.0])))
    ysplir   = n.array([0.0, 0.26469, 0.82925]) * R_V / 3.1
    ysplop   = [n.polyval(n.array([2.13572e-04, 1.00270, -4.22809e-01]), R_V ), 
                n.polyval(n.array([-7.35778e-05, 1.00216, -5.13540e-02]), R_V ),
                n.polyval(n.array([-3.32598e-05, 1.00184, 7.00127e-01]), R_V ),
                n.polyval(n.array([-4.45636e-05, 7.97809e-04, -5.46959e-03, 1.01707, 1.19456] ), R_V ) ]
    
    ysplopir = n.concatenate( (ysplir, ysplop) )
    
    if len(iuv_comp) > 0:
        cubic = spline(n.concatenate( (xsplopir,xspluv) ), n.concatenate( (ysplopir,yspluv) ), k=3)
        curve[iuv_comp] = cubic( x[iuv_comp] )

    # Now apply extinction correction to input flux vector
    curve = ebv * curve[0]
    flux = flux * 10.**(0.4 * curve)
    if extcurve_set == None: return flux
    else:
        ExtCurve = curve - R_V
        return flux, ExtCurve
        
        
def cal_unred(wave, flux, ebv, r_v=""):
    '''
    xingxing:  http://idlastro.gsfc.nasa.gov/ftp/pro/astro/calz_unred.pro

    klam[w1] = 2.659*(-1.857 + 1.040*x[w1]) + R_V
   
    klam[w2] = 2.659*(poly(x[w2], [-2.156, 1.509d0, -0.198d0, 0.011d0])) + R_V
    '''
    wave = np.array(wave, float)
    flux = np.array(flux, float)
    
    if wave.size != flux.size: raise TypeError, 'ERROR - wave and flux vectors must be the same size'
    
    if not bool(r_v): r_v = 3.1 

    x = 10000.0/wave
    
    npts = wave.size
    a = np.zeros(npts, float)
    #b = np.zeros(npts, float)
    R_V = 4.05
    
    ###############################
    #Infrared
    a_v = r_v * ebv
    good = np.where( (wave > 6300.) & (wave < 22000.) )
    a[good] = 2.659*(-1.857 + 1.040*x[good]) + R_V
    #2.659*np.polyval([1.040,-1.857], [1./0.63])+R_V
    
    ###############################
    # Optical & Near IR
    good = np.where( (wave  >= 912.) & (wave <= 6300.) )
    y = x[good] 
    c1 = np.array([-2.156,1.509,-0.198,0.011])
    a[good] = 2.659*np.polyval(c1[::-1], y)+R_V
    #2.659*np.polyval(c1[::-1], [1./0.63])+R_V
    
    # Applying Extinction Correction
    funred = flux * 10.0**(0.4*a*ebv )   
    
    # check
    '''
    from pylab import *
    ion()
    plot(flux)
    plot(funred)
    ylim(0,1)
    figure()
    plot(wave,a)
    ylim(0,100)
    xlim(500,18000)
    pdb.set_trace()
    '''
    #
    return funred
    
###############################################    
def readfilter(telescope,band):
  '''
  read through output for filter in one telescope.
  return(wave,throughouput)
  '''
  #filters ={}
  #filters['HST'] = 'F218W F225W F300X F336W F350LP F390W\
  #           F435W F475W F555W F606W F625W F775W F814W F850LP\
  #           F105W F110W F125W F126N F140W F160W'.split()
  #files ={}
  #files['HST'] = 'HST_ACS_WFC_F435W.res \
  #              '.split()           
  infoname = '0info.txt'
  local_dir = dirname(realpath(__file__))            
  filter_dir = join(local_dir, './FILTER')      
  # get the name from the information file
  infofile = join(filter_dir,infoname)
  info0,info1,info2 = fgetcols(infofile,1,2,3)
  bands = info1[np.where(info0==telescope)] 
  files = info2[np.where(info0==telescope)] 
  if band in bands: 
    filtername = files[np.where(bands==band)[0][0]] 
  else:  
    print '\n\tERROR: Filter not found\t',telescope,band   
    pdb.set_trace()   
    
  #
  filterfile = join(filter_dir,filtername)
  if not isfile(filterfile):
       print 'Loading ',filterfile
       print '\n\tERROR: Filter not found\t',telescope,band   
       pdb.set_trace()    
  w,f = fgetcols(filterfile,1,2)
  return(w,f)    

def infofilter(telescope,band):
  # center and the width for the band
  filter_w,filter_f = readfilter(telescope,band)
  #new_f = spec_rebin(w, filter_w, f)
  delta_wave = np.diff(np.hstack( (filter_w[0],filter_w) ))
  # check http://www.stsci.edu/hst/wfc3/documents/handbooks/currentIHB/c09_exposuretime04.html#328554 
  filter_center = np.sqrt( np.sum(filter_f*filter_w*delta_wave) /np.sum(filter_f/filter_w*delta_wave)   )
  filter_width = np.sum(filter_f*delta_wave)/np.max(filter_f)
  return(filter_center,filter_width) 
    
def spec_filter(w,f, telescope,band,zeropoint=None):
  filter_w,filter_f = readfilter(telescope,band)
  new_f = spec_rebin(w, filter_w, f)
  delta_wave = np.diff(np.hstack( (filter_w[0],filter_w) ))
  # check http://www.stsci.edu/hst/wfc3/documents/handbooks/currentIHB/c09_exposuretime04.html#328554 
  filter_center = np.sqrt( np.sum(filter_f*filter_w*delta_wave) /np.sum(filter_f/filter_w*delta_wave)   )
  filter_width = np.sum(filter_f*delta_wave)/np.max(filter_f)
  # total flux observed
  total_flux = np.sum(delta_wave*new_f*filter_f)/filter_width
  # consider the throughput
  total_flux = total_flux/np.max(filter_f)
  #final_flux = delta_wave*new_f*filter_f
  if zeropoint==None:
      magnitude = spec_flux2mag(total_flux,filter_center)
  elif zeropoint>0:
      magnitude = flux2mag(total_flux,zeropoint)    
  return(total_flux,magnitude)

def spec_flux2mag(f,w):
  mag = -2.5*np.log10(f)-5.*np.log10(w)-2.406
  return(mag)
def flux2mag(f,zeropoint):
  mag = 2.5*np.log10(f)+zeropoint
  return(mag)  
         
###############################################  
from scipy import interpolate
#from pysynphot import observation
#from pysynphot import spectrum
 
def rebin_spec(wave, specin, wavnew):
    '''
    from: http://www.astrobetter.com/python-tip-re-sampling-spectra-with-pysynphot/
    '''
    spec = spectrum.ArraySourceSpectrum(wave=wave, flux=specin)
    f = np.ones(len(wave))
    filt = spectrum.ArraySpectralElement(wave, f, waveunits='angstrom')
    obs = observation.Observation(spec, filt, binset=wavnew, force='taper')
    return obs.binflux
    
def spec_rebin(wave_old, wave_new, spectrum):
        """Rebin the spectrum to a new grid.

        Parameters
        ----------
        wave_old:
           old bins
        wave_new:
           new_bins
        flux:
           flux in old binds      
        Returns
        -------
        S_new: 
            The new spectrum, rebinned to the desired wavelength binning
        """
        
        spectrum = np.array(spectrum)*np.hstack( (0,np.diff(wave_old)) )

        # Perform the interpolation.  We'll interpolate the cumulative sum
        #  so that the total flux of the spectrum is conserved.

        # interpolate spectrum
        spec_cuml_old = spectrum.cumsum()
        #tck = interpolate.splrep(wave_old, np.hstack(([0], spec_cuml_old)), k=1)
        tck = interpolate.splrep(wave_old, spec_cuml_old, k=1)
        spec_cuml_new = interpolate.splev(wave_new, tck)
        '''
        from pylab import *
        ion()
        plot(wave_old,spectrum*5000.)
        plot(wave_old,spec_cuml_old)
        plot(wave_new,spec_cuml_new)
        xlim(200,16000.)
        show()
        pdb.set_trace()
        '''
        spec_cuml_new[wave_new >= wave_old[-1]] = wave_old[-1]
        spec_cuml_new[wave_new <= wave_old[0]] = 0
        snew = np.diff(spec_cuml_new)/np.diff(wave_new)
        snew = np.hstack( (0,snew) )
        return snew

def spec_z(wave, spectrum, z):
    wave_z = wave*(1.+z)
    spectrum_z = spectrum/(1.+z)**2.
    #spec = spec_rebin(wave,wave_z,spectrum_z)
    return(wave_z,spectrum_z)

###############################################
