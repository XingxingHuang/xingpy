Please see Postman et al. 2011 for more information on CLASH.


Source List Construction Summary:

SExtractor (Bertin & Arnouts 1996) is used to detect objects and measure their 
photometry. We run SExtractor (version 2.5.0) in dual image mode, using a 
detection image created from a weighted sum of the ACS/WFC and WFC3/IR images.  
The weights come from the inverse variance images produced by Mosaicdrizzle. 
We do not use the WFC3/UVIS images in the construction of the detection image 
but, of course, run SExtractor on the UVIS data to compute source photometry. 
We also create a detection image solely from the WFC3/IR images to optimize
the search for high redshift (z > 6) objects.

For object detection in the ACS+IR images, we require a minimum of 9
contiguous 
pixels at the level of the observed background RMS or higher. The detection 
phase background sky level is computed in 5 x 5 grids of cells, with each cell 
being 128 x 128 pixels.  For photometry, the local sky is estimated from a 
24-pixel wide rectangular annulus around each detected object.  The deblender 
minimum contrast ratio and number of threshold levels are 0.0015 and 32, 
respectively.  These parameters were chosen after a systematic investigation
of possible values and yields reasonable performance in minimizing spurious
detections and suppressing over-deblending of bright objects, while achieving 
reasonable completeness in detecting faint sources behind bright cluster galaxies.

NOTE: Our image processing effectively rejects cosmic rays from the central 
regions of our UVIS and ACS images where we have four or more overlapping 
exposures.  However such rejection is not possible in the corners and edges of 
our images, where we have fewer exposures due to our observing strategy (two 
roll angles and dithering).  As each cosmic ray only affects a single 
observation, it will often only be detected in a single filter. We prune these 
detections from our ACS+IR catalog by rejecting any object with only a single 
5-sigma detection in one UVIS/ACS filter, as measured by SExtractor.  We also 
reject any object in the ACS+IR catalog without any 5-sigma detections.

NOTE: We perform a separate IR-based detection with more aggressive deblending 
(64 levels of 0.0001 minimum contrast) and background subtraction (3 x 3 grids 
of 64 x 64 pixels).  This detection is slightly more sensitive to redder objects, 
including those at high-redshift.  It also performs slightly better at deblending 
these fainter objects, including those at high-z as well as arcs (strongly-lensed 
galaxies), from brighter nearby cluster galaxies.  The tradeoff is that bright
galaxies are more often segmented into multiple objects. As no further cosmic ray 
rejection is necessary for the WFC3/IR observations, and to preserve our sensitivity to 
faint high-redshift objects, we do not prune this catalog based on 5-sigma
detections.


Photometry:

SExtractor computes isophotal apertures in each detection image and then uses these 
to compute isophotal fluxes and uncertainties in all filters.  In the catalogs, 
we provide these fluxes in native units (electrons / second) after correcting for 
Galactic extinction derived from Schlegel et al. (1998) IR dust emission maps.  
Based on these, we derive AB magnitudes:

mag = zeropoint - 2.5 * log10(flux)

and magnitude uncertainties corresponding to the flux 1-sigma upper limits:

magerr = 2.5 * log10(1 + fluxerr / flux)

We provide the zeropoints and dust extinctions for each filter both in the
catalog files and also in separate files.


Photometric Redshifts:

In these catalogs we provide photometric redshift estimates from BPZ (Bayesian 
Photometric Redshifts; Benitez et al. 2000, 2004; Coe et al. 2006).  These
results are intended for galaxies only.  (Stars may be pruned as having higher 
values of SExtractor stellarity.)  For each object, the most likely redshift 
is given by zb, and the 95% confidence range is given by zbmin - zbmax.  
Objects with high ODDS values have sharply peaked unimodal redshift likelihood 
distributions.  Objects with chisq2 < 1 generally have photometry well 
fit by the model SEDs.

