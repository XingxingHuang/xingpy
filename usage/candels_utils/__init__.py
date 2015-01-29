from os.path import *
import numpy as np
from glob import glob
import pdb

rootdir = '/Volumes/Seagate/clash'
clusters =   ['a209', 'a383', 'a611', 'a1423', 'a2261', \
         'm0329', 'm0416', 'm0429', 'm0647', 'm0717', \
         'm0744', 'm1115', 'm1149', 'm1206', 'm1423', \
         'm1720', 'm1931', 'm2129', 'm2137', 'r1347', \
         'r1532', 'r2129', 'r2248', 'c1226', 'm1311'] 
         

bands = ['f225w','f275w','f336w','f390w',\
         'f435w','f475w','f555w','f606w','f625w','f775w','f814w','f850lp',\
         'f105w','f110w','f125w','f140w','f160w']

cat_image = join(rootdir,'0readme','image.cat')
cat_model = join(rootdir,'0readme','model.cat')
cat_catlog = join(rootdir,'0readme','catalog.cat')