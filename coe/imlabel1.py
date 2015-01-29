# ~/CLASH/pipeline/catamk/bpzlabel.py
# ~/CLASH/data/a383/wei/v2/bpz2/checkbpz.py

#from coeplottk import *
#from coeio import *

from PIL import Image, ImageDraw #, ImageFont
from coeio import *

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

    s = fmt % val
    if val == -99:
	s = '-99'
	color = 255,255,255
	
    draw.text((x, y), s, fill=color) #, font=font)

#im.show()
im.save(outfile)
os.system('open ' + outfile)
