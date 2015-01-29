#!/usr/bin/env python

# $Id: extinction.py,v 1.2 2003/02/27 23:59:20 anderson Exp $ 
# ---------------------------------------------------------------------
# This module provides functionality to calculate the extinction correction
# for a given position on the sky.  This is done using the 
# Schlegel, Finkbeiner & Davis (SFD) dust maps (ApJ, 1998, 500, 525)
# and the interface to these maps provided by SFD.
#
# RA & DEC coordinates are passed by the caller and converted herein
# to the required galactic coords, l, b. via the iraf astutil task
# galactic.  The dust_getval code is then run twice, once to get the
# extinction correction and another to get the data quality flags for
# the sky position.  See the README.C in SFD for a description of the
# mask values returned.

# Modified from original APSIS code to import a dicitonary of filter extinction values
#__version__      = '$Revision: 1.2 $ '[11:-3]
#__version_date__ = '$Date: 2003/02/27 23:59:20 $ '[7:-3]
#__author__       = "Ken Anderson, anderson@pha.jhu.edu"

import popen2  #,fUtil
from pyraf import iraf
from iraf  import astutil

import string
import os
from os.path import join, exists
from coeio import loaddict

def _calc_ebv(cmd):
    sproc  = popen2.Popen3(cmd,1)
    output = sproc.fromchild.readlines()
    errs   = sproc.childerr.readlines()
    return output

def getEBV(ra,dec):
    """function recieves a coordinate pair, RA and DEC from the caller, 
    converts to galactic coords and runs the dust_getval code, installed under the pipeline 
    environment.  Returns an extinction correction in magnitudes and an error object 
    (a list of strings) of possible reported problems with the region of the sky.
    """
    # convert ra and dec to l,b using astutil.  ra should be in hours (freaking iraf).
    # we emulate pipes to Stdin and Stdout so we don't write no stinking files
    raanddec = [str(ra/15) +" "+str(dec)+" 2000"]
    conversion = astutil.galactic(Stdin=raanddec,print_c="no",Stdout=1)
    # conversion is a list of strings, this has only one element:
    # eg. ['     227.5430   46.1912']
    # which is l and b
    gall = conversion[0].split()[0]
    galb = conversion[0].split()[1]
    
    # ok, we have l and b. now onto the extinction stuff. build the dust_val command line
    import pdb;pdb.set_trace()
    cmd    = "dust_getval "+ gall+ " "+ galb+" interp=y verbose=n"
    #print os.getcwd()
    #print cmd
    output = _calc_ebv(cmd)
    #print output
    # output is a list of strings, only one element in this case. looks like
    # [' 227.543  46.191      0.03452\n']
    # dust_getval returns the original coords and the extinction correction in mags
    # which is the last piece of that string
    eBV = output[0].split()[2]
    # next run dust_getval with the mask option to look for anomolies in the maps
    cmd  = "dust_getval "+ gall+ " "+ galb+" map=mask verbose=n"
    mask = _calc_ebv(cmd)
    #print mask
    # quality is a string of data quality flags returned by dust_getval when map=mask.
    # looks like
    # ' 227.543  46.191  3hcons OK      OK      OK      OK      OK      OK     \n'
    quality = mask[1]
    # return this with the extinction.
    return eBV,quality

#################################

class filterError(Exception):
    """raise a filter error exception."""

def filterFactor(filter):
    """caller passes a WFC3 filter of the form "DET_FILTER" and function returns the
    extinction correction factor, a float, for that filter.  Now this function defines a dictionary
    of extinction correction factors directly, but this also exists as a file in 
    $PIPELINE/maps.  It is anticipated that these values will not change often, if at all,
    hence, the dictionary is defined here rather than created on the fly from the file, but
    that could be changed if it is anticipated that these numbers might change a lot.

    eg.
    >>>filterFactor("IR_F105W")
    '3.24695724147'
    """
    ffactors = loaddict('extfiltfact.dict', silent=1)
    for key in ffactors.keys():
        if string.find(key, filter) > -1:  # filter is in key
            return ffactors[key]
        
    # Otherwise...
    raise filterError,"No correction factor for filter "+filter

