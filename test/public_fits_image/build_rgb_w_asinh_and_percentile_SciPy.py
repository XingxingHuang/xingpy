#!/usr/bin/env python

import numpy
import pyfits
import scipy
import img_scale

# Parameters
red_fn = "frame-i-007907-6-0143.fits"
green_fn = "frame-r-007907-6-0143.fits"
blue_fn = "frame-g-007907-6-0143.fits"
sig_fract = 5.0
per_fract = 5.0-2
max_iter = 20
sub_size_fract = 0.3
min_val = 0.0
red_factor = 1.0
green_factor = 1.0
blue_factor = 1.0
red_non_linear_fact = 0.005
green_non_linear_fact = 0.005
blue_non_linear_fact = 0.005


# Read red image
hdulist = pyfits.open(red_fn)
img_header = hdulist[0].header
img_data = hdulist[0].data
hdulist.close()
width=img_data.shape[0]
height=img_data.shape[1]
print "Red file = ", red_fn, "(", width, ",", height, ")"
img_data_r = numpy.array(img_data, dtype=float)
#sky = numpy.median(numpy.ravel(img_data_r))
#sky = numpy.mean(numpy.ravel(img_data_r))
#sky, num_iter = img_scale.sky_median_sig_clip(img_data_r, sig_fract, per_fract, max_iter)
#print "sky = ", sky, "(", num_iter, ") for red image \
#(", numpy.max(img_data_r), ",", numpy.min(img_data_r), ")"
#img_data_r = img_data_r - sky
##### find sub-samples for zscale
flat_img_data_r = numpy.ravel(img_data_r)
size_r = width * height
sub_img_ind = numpy.random.randint(0, size_r, size=int(sub_size_fract*size_r))
sub_img_ind = numpy.unique(sub_img_ind)
sub_img_data_r = flat_img_data_r[sub_img_ind]
print "size of the sample image = ", len(sub_img_data_r)
min_r, max_r = img_scale.range_from_percentile(sub_img_data_r, low_cut=0.5, high_cut=0.25)
print "scale = ", min_r, max_r


# Read green image
hdulist = pyfits.open(green_fn)
img_header = hdulist[0].header
img_data = hdulist[0].data
hdulist.close()
width=img_data.shape[0]
height=img_data.shape[1]
print "Green file = ", green_fn, "(", width, ",", height, ")"
img_data_g = numpy.array(img_data, dtype=float)
#sky = numpy.median(numpy.ravel(img_data_g))
#sky = numpy.mean(numpy.ravel(img_data_g))
#sky, num_iter = img_scale.sky_median_sig_clip(img_data_g, sig_fract, per_fract, max_iter)
#print "sky = ", sky, "(", num_iter, ") for green image \
#(", numpy.max(img_data_g), ",", numpy.min(img_data_g), ")"
#img_data_g = img_data_g - sky
##### find sub-samples for zscale
flat_img_data_g = numpy.ravel(img_data_g)
size_g = width * height
sub_img_ind = numpy.random.randint(0, size_g, size=int(sub_size_fract*size_g))
sub_img_ind = numpy.unique(sub_img_ind)
sub_img_data_g = flat_img_data_g[sub_img_ind]
print "size of the sample image = ", len(sub_img_data_g)
min_g, max_g = img_scale.range_from_percentile(sub_img_data_g, low_cut=0.5, high_cut=0.25)
print "scale = ", min_g, max_g


# Read blue image
hdulist = pyfits.open(blue_fn)
img_header = hdulist[0].header
img_data = hdulist[0].data
hdulist.close()
width=img_data.shape[0]
height=img_data.shape[1]
print "Blue file = ", blue_fn, "(", width, ",", height, ")"
img_data_b = numpy.array(img_data, dtype=float)
#sky = numpy.median(numpy.ravel(img_data_b))
#sky = numpy.mean(numpy.ravel(img_data_b))
#sky, num_iter = img_scale.sky_median_sig_clip(img_data_b, sig_fract, per_fract, max_iter)
#print "sky = ", sky, "(", num_iter, ") for blue image \
#(", numpy.max(img_data_b), ",", numpy.min(img_data_b), ")"
#img_data_b = img_data_b - sky
##### find sub-samples for zscale
flat_img_data_b = numpy.ravel(img_data_b)
size_b = width * height
sub_img_ind = numpy.random.randint(0, size_b, size=int(sub_size_fract*size_b))
sub_img_ind = numpy.unique(sub_img_ind)
sub_img_data_b = flat_img_data_b[sub_img_ind]
print "size of the sample image = ", len(sub_img_data_b)
min_b, max_b = img_scale.range_from_percentile(sub_img_data_b, low_cut=0.5, high_cut=0.25)
print "scale = ", min_b, max_b


# Apply scaling relations
r = red_factor * img_scale.asinh(img_data_r, scale_min = min_r, scale_max = max_r, non_linear=red_non_linear_fact)
g = green_factor * img_scale.asinh(img_data_g, scale_min = min_g, scale_max = max_g, non_linear=green_non_linear_fact)
b = blue_factor * img_scale.asinh(img_data_b, scale_min = min_b, scale_max = max_b, non_linear=blue_non_linear_fact)


# RGB image with SciPy
print "image size ", width, height
rgba_array = numpy.empty((width,height,4), numpy.uint8) # assuming 8 bits per channnel
rgba_array[:,:,0] = scipy.misc.bytescale(r) # red
rgba_array[:,:,1] = scipy.misc.bytescale(g) # green
rgba_array[:,:,2] = scipy.misc.bytescale(b) # blue
rgba_array[:,:,3] = 255 # Alpha transparency
scipy.misc.imsave('rgb.png', rgba_array)
