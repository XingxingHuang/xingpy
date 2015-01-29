# ~/CLASH/pipeline/catamk/bpzlabel.py
# ~/CLASH/data/a383/wei/v2/bpz2/checkbpz.py

#from coeplottk import *
#from coeio import *

from PIL import Image, ImageDraw, ImageFont
from coeio import *

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
    if mycat.chisq2[i] > 1:
        color = red
    elif mycat.odds[i] < 0.95:
        color = yellow
    else:
        color = green
    x = mycat.x[i]
    y = ny-mycat.y[i]
    draw.text((x, y), '%.2f' % mycat.zb[i], fill=color)

#x, y = 10, 10
#dy = 12
x, y, dy = 20, 80, 15
draw.text((x, y), 'BPZ results', fill=white)
y += dy
draw.text((x, y), 'green = most confident (95% of P(z) within +/- 0.04(1+z))', fill=green)
y += dy
draw.text((x, y), 'yellow = broader P(z)', fill=yellow)
y += dy
draw.text((x, y), 'red = no good SED fit (all chisq2 > 1)', fill=red)

#im.show()
im.save(outfile)
os.system('open ' + outfile)
