# FOR MORE PLOTTING IDEAS, SEE ksbtools.py (USED biggles)

import matplotlib
matplotlib.use('TkAgg')
#matplotlib.rc('text', usetex = True)
from pylab import *

plot([1])
title('KILL THIS WINDOW!')
show()
# IMAGE WILL DISPLAY, BUT YOU WON'T BE ABLE TO USE THE Python SHELL
# KILL THIS WINDOW, THEN...
ioff()

# WHEN YOU show() THE NEXT PLOT,
# YOU'LL STILL BE ABLE TO USE THE Python SHELL
# PLUS, THE PLOT WILL BE AUTOMATICALLY UPDATED WITH EACH COMMAND YOU GIVE

clear = cla  # cla() CLEAR PLOT

def rectangle(lolimits, hilimits, fillit=0, **other):
    [xmin,ymin] = lolimits
    [xmax,ymax] = hilimits
    if not fillit:
        return plot([xmin, xmin, xmax, xmax, xmin], [ymin, ymax, ymax, ymin, ymin], **other)
    else:
        return fill([xmin, xmin, xmax, xmax, xmin], [ymin, ymax, ymax, ymin, ymin], **other)

def fillbetween(x1, y1, x2, y2, **other):
    # MAKE SURE IT'S NOT A LIST, THEN IN CASE IT'S A numpy ARRAY, CONVERT TO LIST, THEN CONVERT TO numarray ARRAY
    if type(x1) <> list:
	x1 = x1.tolist()
    if type(y1) <> list:
	y1 = y1.tolist()
    if type(x2) <> list:
	x2 = x2.tolist()
    if type(y2) <> list:
	y2 = y2.tolist()
    x = x1[:]
    x[len(x):] = x2[::-1]
    y = y1[:]
    y[len(y):] = y2[::-1]
    return fill(x, y, **other)


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

