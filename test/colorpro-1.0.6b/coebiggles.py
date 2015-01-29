from biggles import *

########################################################################################
# PLOTTING

def addLabels(p, x, y, labels, format='%s', **other):
    n = len(x)
    p.add(Points(x, y, size=0))
    for i in range(n):
        p.add(Label(x[i], y[i], format % labels[i], **other))
    return p

def LabeledPlot(x, y, labels, format='%s'):
    n = len(x)
    p = FramedPlot()
    p.add(Points(x, y, size=0))
    for i in range(n):
        p.add(Label(x[i], y[i], format % labels[i]))
    return p

# plotlabels
def plabels(x, y, labels, format='%s'):
    p = LabeledPlot(x, y, labels, format)
    p.show()

def xyLine(x, y, **other):
    """CREATES A DIAGONAL LINE (y=x) SPANNING THE RANGE OF x & y"""
    #return Curve([min(xlist), max(xlist)], [y, y], **other)
    xlo, xhi = min(x), max(x)
    ylo, yhi = min(y), max(y)
    try:
        xlo = xlo[0]
        xhi = xhi[0]
        ylo = ylo[0]
        yhi = yhi[0]
    except:
        pass
    lo = min([xlo, ylo])[0]
    hi = max([xhi, yhi])[0]
    return Curve([lo, hi], [lo, hi], **other)

def HLine(xlist, y, **other):
    """CREATES A HORIZONTAL LINE SPANNING THE RANGE OF xlist"""
    #return Curve([min(xlist), max(xlist)], [y, y], **other)
    xlo, xhi = min(xlist), max(xlist)
    try:
        xlo = xlo[0]
        xhi = xhi[0]
    except:
        pass
    return Curve([xlo, xhi], [y, y], **other)

def VLine(x, ylist, **other):
    """CREATES A VERTICAL LINE SPANNING THE RANGE OF Ylist"""
    #return Curve([min(xlist), max(xlist)], [y, y], **other)
    ylo, yhi = min(ylist), max(ylist)
    try:
        ylo = ylo[0]
        yhi = yhi[0]
    except:
        pass
    return Curve([x, x], [ylo, yhi], **other)

def Square(lolimits, hilimits, fill=0, **other):
    [xmin,ymin] = lolimits
    [xmax,ymax] = hilimits
    if not fill:
        return Curve([xmin, xmin, xmax, xmax, xmin], [ymin, ymax, ymax, ymin, ymin], **other)
    else:
        return FillBetween([xmin, xmin, xmax], [ymin, ymax, ymax], [xmax, xmax, xmin], [ymax, ymin, ymin], **other)

def spreadem(x, title="Spread 'em!"):
    """PLOTS POINTS VERSUS RANDOM NUMBERS, TO SPREAD THEM OUT"""
    points(x, rand(len(x))+0.1, title=title)

def prange(x, xinclude=None, margin=0.05):
    """RETURNS GOOD RANGE FOR DATA x TO BE PLOTTED IN.
    xinclude = VALUE YOU WANT TO BE INCLUDED IN RANGE.
    margin = FRACTIONAL MARGIN ON EITHER SIDE OF DATA."""
    xmin = min(x)
    xmax = max(x)
    if xinclude <> None:
        xmin = min([xmin, xinclude])
        xmax = max([xmax, xinclude])
    
    dx = xmax - xmin
    if dx:
        xmin = xmin - dx * margin
        xmax = xmax + dx * margin
    else:
        xmin = xmin - margin
        xmax = xmax + margin
    return [xmin, xmax]

def prangelog(x, xinclude=None, margin=0.05):
    """RETURNS GOOD RANGE FOR DATA x TO BE PLOTTED IN.
    xinclude = VALUE YOU WANT TO BE INCLUDED IN RANGE.
    margin = FRACTIONAL MARGIN ON EITHER SIDE OF DATA."""
    xmin = min(x)
    xmax = max(x)
    if xinclude <> None:
        xmin = min([xmin, xinclude])
        xmax = max([xmax, xinclude])
    
    fac = xmax / xmin
    xmin = xmin / (fac ** .05)
    xmax = xmax * (fac ** .05)

    return [xmin, xmax]

def plotconfig(size=600, persistent='no'):
    configure('screen', 'persistent', persistent)
    if type(size) == int:
        width = height = size
    else:
        width, height = size
    configure('screen', 'width', width)
    configure('screen', 'height', height)

plotconfigure = plotconfig

def xpoints(x):
    i = arange(len(x))
    points(i, x)

