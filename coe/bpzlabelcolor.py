# ~/CLASH/pipeline/catamk/bpzlabelcolor.py
# ~/CLASH/pipeline/catamk/bpzlabel.py
# ~/CLASH/data/a383/wei/v2/bpz2/checkbpz.py

#from coeplottk import *
#from coeio import *

from PIL import Image, ImageDraw, ImageFont
from coeio import *
from coeplott import *  # colormaprgb

imfile = sys.argv[1]
catfile = sys.argv[2]
outfile = sys.argv[3]

im = Image.open(imfile)
cat = loadcat(catfile)

crdx = crdy = 4
nodx = nody = 5

white  = tuple(255 * array([1,1,1]))
red    = tuple(255 * array([1,0,0]))
green  = tuple(255 * array([0,1,0]))
yellow = tuple(255 * array([1,1,0]))

nx, ny = im.size
draw = ImageDraw.Draw(im)

mycat = cat

for i in range(mycat.len()):
    z = mycat.zb[i]
    
    if mycat.chisq2[i] > 1:  # bad fit
        s = '%.1f?' % z
    elif mycat.odds[i] < 0.95:
        s = '%.1f' % z
    else:
        s = '%.2f' % z
    
    #color = colormaprgb(z, [0, 6], 'gist_rainbow_r')
    if isnan(z):
        color = (1,0,1)
    else:
        color = colormaprgb(z, [0, 6], 'jet')
    
    color = color1to255(color)
    #color = tuple(color)
    
    x = mycat.x[i]
    y = ny-mycat.y[i]
    #print s, color
    draw.text((x, y), s, fill=color)

#im.show()
im.save(outfile)
os.system('open ' + outfile)
