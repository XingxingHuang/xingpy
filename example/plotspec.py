#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pyfits
import pylab
import scipy
import sys
from matplotlib import cm
from numdisplay import zscale

# default values
fileroot = ''
file1d = 'e'; file2d = 's'
contrast = 0.6; z1 = None; z2 = None
z = 0.; cz = 0.; dv = 0
thresh = 20
title = ''
tickspace = 500
linefill = 0.8
linefile = ''
lheight = 0.2

# given in the command line?
for argv in sys.argv:
  if argv[:9] == 'fileroot=':
    fileroot = argv[9:]
  if argv[:7] == 'file1d=':
    file1d = argv[7:]
  if argv[:7] == 'file2d=':
    file2d = argv[7:]
  if argv[:2] == 'z=':
    z = float(argv[2:])
  if argv[:3] == 'cz=':
    cz = float(argv[3:])
  if argv[:3] == 'dv=':
    dv = float(argv[3:])
  if argv[:9] == 'contrast=':
    contrast = float(argv[9:])
  if argv[:7] == 'thresh=':
    thresh = float(argv[7:])
  if argv[:3] == 'z1=':
    z1 = float(argv[3:])
  if argv[:3] == 'z2=':
    z2 = float(argv[3:])
  if argv[:10] == 'tickspace=':
    tickspace = float(argv[10:])
  if argv[:9] == 'linefill=':
    linefill = float(argv[9:])
  if argv[:9] == 'figtitle=':
    title = argv[9:]
  if argv[:9] == 'linefile=':
    linefile = argv[9:]
  if argv[:8] == 'lheight=':
    lheight = float(argv[8:])
if cz != 0. and z == 0.:
  z = cz / 299792.458

# plot at rest-frame?
rest = False
if '--rest' in sys.argv:
  rest = True

# speed of light, in km/s
c = 2999792.458

# wrap up of all the tasks
def main(root = '',file1d = 'e', file2d = 's', title = '', contrast = 0.25, linefile = '',
         z = 0., dv = 1000, thresh = 20, z1 = None, z2 = None, tickspace = tickspace, linefill = 0.8,
         lheight = 0.2, rest = False):
  if not file1d:
    file1d = raw_input('Enter Filename for the 1d spectrum:\n\t')
  if root:
    file1d = fileroot + file1d
    file2d = fileroot + file2d
  dz = dv / c
  plot(file1d, file2d, title, z = z, dz = dz, contrast = contrast, thresh = thresh,
       z1 = z1, z2 = z2, tickspace = tickspace, linefill = linefill, linefile = linefile,
       lheight = lheight, rest = rest)
  return

def plot(file1d, file2d, title = '', contrast = 0.25, bin = 1, z = 0., dz = 0.0005,
         thresh = 20, z1 = None, z2 = None, tickspace = 500, linefill = 0.8, linefile = '',
         lheight = 0.2, rest = False):
  fig = pylab.figure(facecolor = 'white')
  
  fits = pyfits.open(file1d)
  wavelength = pix2wave(file1d)
  #if rest:
    #wavelength = wavelength / (1 + z)
  #print wavelength
  pix = scipy.arange(1, len(wavelength) + 1)
  spectrum = BadPixels(fits[0].data, thresh = thresh)
  fits.close()
  box1d = [0.1, 0.1, 0.8, 0.7]
  ax1d = fig.add_axes(box1d, yticklabels = [], xlabel = r'wavelength $(\AA)$')

  ax1d.annotate('z = %.4f\ndz = %.4f (%d km/s)' %(z, dz, int(c * dz)), xy = (0.06, 0.83),
                xycoords = 'axes fraction', color = 'k', fontsize = '15', family = 'serif')
  #Line labels:
  if linefile:
    lines, linenames = read_lines(linefile)
  else:
    linenames = ['Lya', 'CIV', 'CIII', 'MgII', '[OII]', 'Ca-K', 'Ca-H', 'G', \
		 'HeI', 'HeII', 'HeII', 'Hb', '[OIII]', '[OIII]', 'MgII', \
		 'NaI', 'N1', 'Ha', 'N2', 'S1', 'S2']
    lines = [1215.67, 1549., 1909., 2798., 3727.4, 3933.68, 3968.49, 4300., \
	     4471.6, 4541.6, 4685.7, 4861.34, 4958.91, 5006.84, 5172.7, \
	     5892.9, 6548.06, 6562.82, 6583.57, 6716.44, 6730.815]
  for i in range(len(lines)):
    # positions of spectral lines in the plot
    linepix = wave2pix(file1d, (1 + z) * lines[i])
    # give each line a width
    if 0 < dz < 1000:
      fillwidth = [wave2pix(file1d, (1 + z - dz / 2.) * lines[i]), wave2pix(file1d, (1 + z + dz / 2.) * lines[i])]
      fillx = [fillwidth[0], fillwidth[0], fillwidth[1], fillwidth[1]]
      fillheight = 2 * max(spectrum)
      filly = [-fillheight, fillheight, fillheight, -fillheight]
      ax1d.fill(fillx, filly, str(linefill), edgecolor = str(linefill))
    if dz > 1000 or dz == 0:
      ax1d.axvline(linepix, color = 'k', ls = '--')
    # annotate names:
    height = lheight * max(spectrum) + scipy.median(spectrum) * (1. + (-1) ** i / 4.)
    ax1d.annotate(linenames[i], xy = (linepix + 10, height), color = 'r')

  ax1d.plot(pix, spectrum)
  xticks_loc, xticks_val = ConvertTicks(file1d, wavelength, tickspace, z, rest)
  ax1d.set_xticks(xticks_loc)
  ax1d.set_xticklabels(xticks_val)

  # the 2d spectrum, which could not be given
  try:
    fits = pyfits.open(file2d)
    img = fits[0].data
    fits.close()
    if not z1:
      z1, blah = zscale.zscale(img, contrast = contrast)
    if not z2:
      blah, z2 = zscale.zscale(img, contrast = contrast)
    height = 0.001 * img.shape[0]
    if height < 150:
      box2d = [0.1, 0.9 - height / 2, 0.8, height]
    else:
      box2d = [0.1, 0.825, 0.8, 0.15]
    ax2d = fig.add_axes(box2d, sharex = ax1d, yticks = [])
    ax2d.imshow(img, aspect = 'auto', vmin = z1, vmax = z2, cmap = cm.Greys_r)
    ax2d.set_ylim(0, img.shape[0])
    wavelength = pix2wave(file2d)
    xticks_loc, xticks_val = ConvertTicks(file2d, wavelength, tickspace, z, rest)
    ax2d.set_xticks(xticks_loc)
    ax2d.set_xticklabels(xticks_val)
  except IOError as err:
    print err
    print '-- Only showing 1d spectrum --'

  if title:
    pylab.title(title)
  pylab.show()
  return

def read_lines(file):
  lines = []; linenames = []
  f = open(file)
  for line in f:
    if line[0] != '#':
      line = line.split()
      lines.append(float(line[0]))
      linenames.append(line[1])
  return lines, linenames

def to_restframe(z, wave):
  return wave / (1 + z)

def ConvertTicks(file2dfile, wave, tickspace = 500, z = 0, rest = False):
  if rest:
    tickspace = 500 * (1 + z)
  N = len(wave)
  ticks_loc = []
  ticks_val = []
  wavemin = min(wave)
  wavemax = max(wave)
  tick_min = int(wavemin + (tickspace - wavemin%tickspace))
  Nticks = int((wavemax - wavemin) / tickspace)
  for i in range(Nticks + 1):
    ticks_val.append(int(tick_min + i * tickspace))
    ticks_loc.append(wave2pix(file2dfile, ticks_val[i]))
  ticks_val = scipy.array(ticks_val)
  if rest:
    for i in range(Nticks + 1):
      ticks_val[i] = int(ticks_val[i] / (1 + z)) + 1 # it is always (apparently) barely less than the round number (e.g., 4999.3)
  ticks_loc = scipy.array(ticks_loc)
  return ticks_loc, ticks_val

def pix2wave(specfilename, refpix_key = 'CRPIX1', refwave_key = 'CRVAL1', slope_key = 'CD1_1', Npix_key = 'NAXIS1'):
  specfile = pyfits.open(specfilename)
  head = specfile[0].header
  refpix = head[refpix_key]
  refwave = head[refwave_key]
  slope = head[slope_key]
  Npix = head[Npix_key]
  specfile.close()
  t = scipy.arange(1, Npix + 1)
  return slope * (t - refpix) + refwave

def wave2pix(specfilename, wave, refpix_key = 'CRPIX1', refwave_key = 'CRVAL1', slope_key = 'CD1_1'):
  """
  Returns the pixel value at which the wavelength equals wave (most likely not an integer)
  """
  specfile = pyfits.open(specfilename)
  head = specfile[0].header
  refpix = head[refpix_key]
  refwave = head[refwave_key]
  slope = head[slope_key]
  specfile.close()
  return (wave - refwave) / slope + refpix

def getWaveValue(specfilename, pix, refpix_key = 'CRPIX1', refwave_key = 'CRVAL1', slope_key = 'CD1_1'):
  specfile = pyfits.open(specfilename)
  head = specfile[0].header
  refpix = head[refpix_key]
  refwave = head[refwave_key]
  slope = head[slope_key]
  specfile.close()
  return slope * (pix - refpix) + refwave  
    
def BadPixels(spectrum, niter = 3, add_local = 10, thresh = 20):
  """
  If a number of pixels in the 1d spectrum have too many counts (given by thresh), their values are
  set to the local average. These counts can still be identified in the 2d spectrum, but not in the
  1d spectrum, for visual aid. Be careful not to remove strong emission lines (by setting a high
  value for thresh).
  """
  Npix = len(spectrum)
  for l in range(niter):
    sigma = scipy.std(spectrum)
    median = scipy.median(spectrum)
    for j in range(1, Npix - 1):
      if abs(spectrum[j]) > thresh * median:
	local = []
	if abs(spectrum[j]) > abs(median - sigma):
	  for k in range(add_local / 2):
	    try:
	      local.append(spectrum[j - k])
	    except IndexError:
	      pass
	  for k in range(add_local / 2):
	    try:
	      local.append(spectrum[j - k])
	    except IndexError:
	      pass
	  local = scipy.median(local)
	  spectrum[j] = local
  return spectrum

# introduction -- please don't delete
#print ''
#print '\t**********************************************'
#print '\t*                                            *'
#print '\t*                  plotspec                  *'
#print '\t*                                            *'
#print '\t*             by Cristobal Sifon             *'
#print '\t*      P. Universidad Catolica de Chile      *'
#print '\t*                 May, 2011                  *'
#print '\t*                                            *'
#print '\t* ------------------------------------------ *'
#print '\t*            cjsifon@astro.puc.cl            *'
#print '\t*        http://astro.puc.cl/~cjsifon/       *'
#print '\t**********************************************'
#print ''

# automatically add the ".fits" extension when not given
if file1d[-5:] != '.fits' and file1d[-4:] != '.fit':
  file1d += '.fits'
if file2d[-5:] != '.fits' and file2d[-4:] != '.fit':
  file2d += '.fits'

main(fileroot, file1d, file2d, title, contrast, linefile, z, dv, thresh, z1, z2, tickspace, linefill, lheight, rest)

