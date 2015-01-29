# Usage:
# python imlabel.py imfile catfile outfile param precision <-COLOR color -DX dx -DY dy>
#
# Example:
# python imlabel.py image.png catalog.cat labeled.png mag 1 -COLOR white

from PIL import Image, ImageDraw, ImageFont
from coeio import *
from coeim import *

def id2label(id):
    """2.51 -> 2.1e"""
    galid = int(id)
    label = '%d' % galid
    #
    iknot = roundint((id - galid) * 100) % 10
    if iknot:
        label += '.%d' % iknot
    #
    ltrs = string.lowercase
    iimage = int((id - galid) * 10 + 0.01) - 1
    ltr = ltrs[iimage]
    label += ltr
    #
    return label

#########
# Load font
fontdir = '/sw/lib/python2.7/site-packages/matplotlib/mpl-data/fonts/ttf'
fontfile = 'Vera.ttf'
#fontfile = 'VeraBd.ttf'
fontfile = join(fontdir, fontfile)
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

#0.5, 0.9, 0.9
#0.9, 0.9, 0.0
#0.87,0.1, 0.0

#    R    G    B
c = 0.0, 0.9, 0.9
y = 0.9, 0.9, 0.2
r = 1.0, 0.0, 0.0
cyr = array([c, y, r])
r, g, b = cyr.T
ii = arange(3) / 2.

def cyr(val):  # val between 0 & 1
    R = interp(val, ii, r)
    G = interp(val, ii, g)
    B = interp(val, ii, b)
    return R, G, B

cmaplist = 'cyr ryc'.split()
invcmaplist = 'ryc '.split()


def convertcolor(color1):
    if color1 not in cmaplist:
        if type(color1) == type('magenta'):
            color1 = colordict[color1]
            color1 = tuple(255 * array(color1))
    return color1

def imlabel(imfile, catfile, outfile, param=None, precision=None, colorparam=None, color=None, color2=None, dx=0, dy=0, showimage=True, lo=None, hi=None, fontsize=None, idletter=False, boxwidth=0, boxlinewidth=1):
    im = Image.open(imfile)
    cat = loadcat(catfile)

    if param not in cat.labels:
        cat = loadsexcat0(catfile)
        if param not in cat.labels:
            print catfile, 'does not contain the parameter', param
            print "Please check your parameter and try again."
            return

    if colorparam == None:
        colorparam = param
        if colorparam not in cat.labels:
            print catfile, 'does not contain the parameter', param
            print "Please check your parameter and try again."
            return

    #########
    # Shift coords

    if dx:
        cat.x = cat.x + dx

    if dy:
        cat.y = cat.y + dy

    #########
    # COLOR

    color1 = color
    if im.mode == 'L':
        im = im.convert('RGB')

    if im.mode == 'L':
        color1 = 255 * colordict[color][0]
        print color1
    else:
        color1 = convertcolor(color1)

    if fontsize:
        font = ImageFont.truetype(fontfile, fontsize)
    else:
        font = None
        
    #########

    nx, ny = im.size
    draw = ImageDraw.Draw(im)

    mycat = cat

    precision = int(precision)
    if precision == -1:
        pass # fmt = '%g'
    elif precision:
        fmt = '%%.%df' % precision
    else:
        fmt = '%d'

    data = mycat.get(param)
    colordata = mycat.get(colorparam)
    
    #lo, hi = minmax(data)
    if color in cmaplist:
        if lo == None:
            lo = min(colordata)
        if hi == None:
            hi = max(colordata)
        print 'Coloring according to data range:', lo, hi

    for i in range(mycat.len()):
        x = mycat.x[i]
        if not (0 < x < nx):
            continue

        y = ny-mycat.y[i]
        if not (0 < y < ny):
            continue

        val = data[i]
        colorval = colordata[i]

        ##
        if color in cmaplist:
            z = interp(colorval, (lo, hi), (0, 1))
            if color in invcmaplist:
                z = 1 - z

            color1 = cyr(z)
            color1 = color1to255(color1)
        else:
            color1 = convertcolor(color)
        
        ##

        if idletter:
            s = id2label(val)
        else:
            if precision == -1:
                fmt = '%%.%df' % ndec(val)

            s = fmt % val

        if val == -99:
            s = '-99'
            if color2 == None:
                if im.mode == 'L':
                    color1 = 0
                else:
                    color1 = 255,255,255
            else:
                color1 = convertcolor(color2)

        draw.text((x, y), s, fill=color1, font=font) #, font=font)

        if boxwidth:
            for jj in range(boxlinewidth):
                d = boxwidth / 2
                d += jj
                box = (x-d, y-d, x+d, y+d)
                draw.rectangle(box, outline=color1)

    #im.show()
    im.save(outfile)

    if showimage:
        os.system('open ' + outfile)


#################################


#def addcrosshair(RGB, x, y, color=(255,255,255), d=15, d2=2):
def addcrosshair(RGB, x, y, color=(255,255,255), hairlength=31, hairwidth=5, hairbuf=0):
    d  = (hairlength + 1) / 2  # 31 -> 15
    d2 = (hairwidth - 1) / 2  #  5 ->  2;  1 -> 1
    d3 = (hairbuf + 1) / 2
    R, G, B = RGB
    #print x, y, c
    #R[y-d : y+d+1, x-d2 : x+d2+1] = color[0]
    #G[y-d : y+d+1, x-d2 : x+d2+1] = color[1]
    #B[y-d : y+d+1, x-d2 : x+d2+1] = color[2]

    # vertical
    R[y-d : y-d3+1, x-d2 : x+d2+1] = color[0]
    G[y-d : y-d3+1, x-d2 : x+d2+1] = color[1]
    B[y-d : y-d3+1, x-d2 : x+d2+1] = color[2]
    #
    R[y+d3 : y+d+1, x-d2 : x+d2+1] = color[0]
    G[y+d3 : y+d+1, x-d2 : x+d2+1] = color[1]
    B[y+d3 : y+d+1, x-d2 : x+d2+1] = color[2]
    
    if d <> d2:
        #R[y-d2 : y+d2+1, x-d : x+d+1] = color[0]
        #G[y-d2 : y+d2+1, x-d : x+d+1] = color[1]
        #B[y-d2 : y+d2+1, x-d : x+d+1] = color[2]

        # horizontal
        R[y-d2 : y+d2+1, x-d : x-d3+1] = color[0]
        G[y-d2 : y+d2+1, x-d : x-d3+1] = color[1]
        B[y-d2 : y+d2+1, x-d : x-d3+1] = color[2]
        #
        R[y-d2 : y+d2+1, x+d3 : x+d+1] = color[0]
        G[y-d2 : y+d2+1, x+d3 : x+d+1] = color[1]
        B[y-d2 : y+d2+1, x+d3 : x+d+1] = color[2]
    
    return R, G, B

#        im = Image.open(inimage)
#        RGBin = loadrgb(inimage)

def immark(imfile, catfile, outfile, color='white', dx=0, dy=0, showimage=True, hairlength=31, hairwidth=5, hairbuf=0):
    color1 = convertcolor(color)

    #im1, RGB = loadimage(imfile)
    print 'Loading %s...' % imfile
    RGB = loadrgb(imfile)
    #print type(RGB)
    #RGB = clip(RGB, 0, 100)
    #RGB[0] = 0.7 * RGB[0]
    #RGB = 0.7 * RGB
    three, ny, nx = RGB.shape

    cat = loadcat(catfile)
    if cat.len() == 0:
        print 'Trying again assuming x & y are the only columns...'
        cat = loadcat(catfile, labels=['x', 'y'])

    #########
    # Shift coords

    if dx:
        cat.x = cat.x + dx

    if dy:
        cat.y = cat.y + dy

    for i in range(cat.len()):
        x = cat.x[i]
        if not (0 < x < nx):
            continue

        y = ny-cat.y[i]
        if not (0 < y < ny):
            continue

        RGB = addcrosshair(RGB, x, ny-y, color=color1, hairlength=hairlength, hairwidth=hairwidth, hairbuf=hairbuf)
    
    im = rgb2im(RGB)
    
    if 0: #sh:
        im.show()
    
    #return im
    if 0:
        im.show()
    else:
        im.save(outfile)

    if showimage:
        os.system('open ' + outfile)


#################################


if __name__ == '__main__':
    imfile = sys.argv[1]
    catfile = sys.argv[2]
    outfile = sys.argv[3]

    verbose = 0
    if verbose:
        print 'imfile = ', imfile
        print 'catfile = ', catfile
        print 'outfile = ', outfile

    params = params_cl()  # other options: FONT, MIN, MAX
    dx = float(params.get('DX', 0))
    dy = float(params.get('DY', 0))

    textlab = False
    if len(sys.argv) > 4:
        if sys.argv[4][0] <> '-':
            textlab = True
    
    if textlab:
        param = sys.argv[4]
        precision = sys.argv[5]
        if verbose:
            print 'param = ', param
            print 'precision = ', precision
        
        color = params.get('COLOR', None)
        colorparam = params.get('COLORPARAM', None)

        if type(color) in (list, tuple):
            color, color2 = color
        else:
            color2 = None
        lo = params.get('MIN', None)
        hi = params.get('MAX', None)
        fontsize = params.get('FONT', None)
        if fontsize:
            fontsize = int(fontsize)

        idletter = 'IDLETTER' in params.keys()
        box = params.get('BOX', None)
        if type(box) in (list, tuple):
            boxwidth, boxlinewidth = box
        else:
            boxwidth = box
            boxlinewidth = 1

        imlabel(imfile, catfile, outfile, param, precision, colorparam=colorparam, color=color, color2=color2, dx=dx, dy=dy, lo=lo, hi=hi, fontsize=fontsize, idletter=idletter, boxwidth=boxwidth, boxlinewidth=boxlinewidth)

    else:
        color = params.get('COLOR', 'white')
        hairlength = 31  # default
        hairwidth = 1  # default
        hairbuf = 11  # default
        if type(color) == list:
            if len(color) == 3:
                color, hairlength, hairwidth = color
            elif len(color) == 2:
                color, hairlength = color
                hairwidth = hairlength
        immark(imfile, catfile, outfile, color=color, dx=dx, dy=dy, hairlength=hairlength, hairwidth=hairwidth, hairbuf=hairbuf)
