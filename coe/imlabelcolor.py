# ~/CLASH/pipeline/catamk/bpzlabel.py
# ~/CLASH/data/a383/wei/v2/bpz2/checkbpz.py

#from coeplottk import *
#from coeio import *

from PIL import Image, ImageDraw, ImageFont
from coeio import *
#from coeplot import *  # colormaprgb
#import mycolormaps

imfile = sys.argv[1]
catfile = sys.argv[2]
outfile = sys.argv[3]
param = sys.argv[4]
precision = int(sys.argv[5])

params = params_cl()  # other options: FONT, MIN, MAX

im = Image.open(imfile)
cat = loadcat(catfile)

if param not in cat.labels:
    cat = loadsexcat0(catfile)
    if param not in cat.labels:
        print catfile, 'does not contain the parameter', param
        print "Please check your parameter and try again."
        quit()

#########

import matplotlib
from matplotlib import cm

LUTSIZE = matplotlib.rcParams['image.lut']

# cyan-yellow-red
#    R   G   B
# c: 0,  75, 75
# y: 75, 75, 22
# r: 100, 0, 0

lo, hi = 0.1, 0.7
x = 1  # DOESN'T MATTER??
y = 0.9
_cyr_data =  {
    'red':   ((0., x, 0),    (0.5, y, x), (0.5, x, y), (1, 1, x)),
    'green': ((0., x, y), (0.5, y, x), (0.5, x, y), (1, 0, x)),
    'blue':  ((0., x, y), (0.5, 0.2, x), (0.5, x, 0.2), (1, 0, x))}

cm.cyr = matplotlib.colors.LinearSegmentedColormap('cyr', _cyr_data, LUTSIZE)

cm.datad['cyr'] = _cyr_data

def cyr():
    rc('image', cmap='cyr')
    im = gci()
    
    if im is not None:
        im.set_cmap(cm.cyr)
    draw_if_interactive()

def colormaprgb(val, valrange=[0.,1.], cmap='jet', silent=0):
    if valrange <> [0.,1.]:
        lo = float(valrange[0])
        hi = float(valrange[1])
        val = (val - lo) / (hi - lo)
    
    try:
        n = len(val)
    except:  # SINGLE VALUE
        val = array([val])
    
    if cmap in colormap_map.keys():
        cmapa = colormap_map[cmap]
        
        xa = arange(len(cmapa)) / float(len(cmapa)-1)
        ra, ga, ba = transpose(cmapa)
    else:
        cmapd = cm.datad[cmap]
        xa = array(cmapd['blue'])[:,0]
        ra = array(cmapd['red'])[:,1]
        ga = array(cmapd['green'])[:,1]
        ba = array(cmapd['blue'])[:,1]
        
    r = interpn(val, xa, ra, silent)
    g = interpn(val, xa, ga, silent)
    b = interpn(val, xa, ba, silent)
    rgb = ravel(array([r, g, b]))
    return rgb

#########
# Shift coords

if 'DX' in params:
    cat.x = cat.x + float(params['DX'])

if 'DY' in params:
    cat.y = cat.y + float(params['DY'])

#########

colordict = {
    'white'  : (1,1,1),
    'red'    : (1,0,0),
    'green'  : (0,1,0),
    'blue'   : (0,0,1),
    'cyan'   : (0,1,1),
    'magenta': (1,0,1),
    'yellow' : (1,1,0),
    'black'  : (0,0,0),
    }

if 'COLOR' in params:
    color = colordict[params['COLOR']]
    color = tuple(255 * array(color))

#########
# Load font

fontsize = int(params.get('FONT', '10'))

fontfile = 'Vera.ttf'
#fontfile = 'VeraBd.ttf'
#fontdir = '/opt/local/share/gnubg/fonts'
fontdir = '/sw/lib/python2.7/site-packages/matplotlib/mpl-data/fonts/ttf'
fontfile = join(fontdir, fontfile)
#fontsize = 24
#font = ImageFont.truetype(fontfile, fontsize)
#fontsize = 36
font = ImageFont.truetype(fontfile, fontsize)

#########

nx, ny = im.size
draw = ImageDraw.Draw(im)

mycat = cat

if precision:
    fmt = '%%.%df' % precision
else:
    fmt = '%d'

data = mycat.get(param)
#lo, hi = minmax(data)
lo = params.get('MIN', min(data))
hi = params.get('MAX', max(data))

for i in range(mycat.len()):
    x = mycat.x[i]
    if not (0 < x < nx):
        continue

    y = ny-mycat.y[i]
    if not (0 < y < ny):
        continue
    
    val = mycat.get(param)[i]
    
    if 'COLOR' not in params:
        #color = colormaprgb(val, [lo, hi], 'jet')
        #z = interp(val, (lo, hi), (1, 0))
        z = interp(val, (lo, hi), (0, 1))
        if 'REDHI' not in params:
            z = 1 - z  # blue high
	#cmap = 'jet'
	#color = colormaprgb(z, [0, 1], cmap)
	cmap = mycolormaps.cm.cyr
	color = mycolormaps.cm.cyr(val)[:3]
	#print val, color
        color = color1to255(color)

    s = fmt % val
    if val == -99:
	s = '-99'
	color = 255,255,255
	
    draw.text((x, y), s, fill=color, font=font)

#im.show()
im.save(outfile)
os.system('open ' + outfile)
