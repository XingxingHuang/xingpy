For my pipeline:
  python cipcat_xing.py
This will read the detection image, but will not create one. 

 
if the images in c/s. Use this:
  python cipcat_xing_rmsproblem.py


Based on these, we derive AB magnitudes:
   mag = zeropoint - 2.5 * log10(flux)

and magnitude uncertainties corresponding to the flux 1-sigma upper limits:
   magerr = 2.5 * log10(1 + fluxerr / flux)





############################################
# CLASH Image Pipeline
# Photometry catalog generator
# -Dan Coe
############################################

# python /data01/cipphot/pipeline/cipcat.py <field> <datestr> <subdir>
#
# Example:
# python /data01/cipphot/pipeline/cipcat.py a383 20110426 scale_065mas_science
# will read in images from:
#   /data01/amk_mosaicdrizzle/a383/20110426/scale_065_science/'
# and create output here:
#   /data01/cipphot/a383/mosdriz/20110426/scale_065_science/
#
# These directories can be overridden with the options:
# -indir my_indir -- imports images from my_dir
# -inweightdir my_weight_dir -- imports weight images from my_weight_dir
# -outdir my_outdir -- writes output to (subdirectories in) my_outdir
#
# Other options:
# -IR -- IR-based detection image
# -faint -- aggressive SExtractor background subtraction


############################################
# CLASH Image Pipeline
# Photometry + Photo-z catalog generator
# -Dan Coe
############################################

"""
python $CIPPHOT/cipcat.py macs1115
cd /data02/cipphot/macs1115/mosdriz/20111202/scale_65mas/cat/120118

python $CIPPHOT/cipcat.py macs1115 -IR
cd /data02/cipphot/macs1115/mosdriz/20111202/scale_65mas/cat_IR/120118

python $CIPPHOT/bpzcolumns.py photometry

bpz photometry.cat -P $BPZPATH/bpzCLASH.param

python $CIPPHOT/bpzfinalize.py photometry

python $CIPPHOT/catfinal.py macs1115
"""
