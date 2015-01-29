## Automatically adapted for numpy Jun 08, 2006 by 

# smooth.py

# SMOOTH OUT SCATTERED POINTS: AVERAGES AND UNCERTAINTIES, PLOTS

#from Numeric import *
from numpy import *
from MLab_coe import *

def smoothrogers(x, y, z, neighbors=20):
    """SMOOTHS z USING THE 'NEAREST NEIGHBORS' METHOD
    FINDS EACH POINT'S 20 NEAREST NEIGHBORS IN [x,y] SPACE
    REPLACES ITS z VALUE WITH THE MEDIAN OF ALL 21 z VALUES
    WILL PROBABLY BE VERY SLOW IF THERE ARE MANY POINTS"""

    dx = std(x)
    dy = std(y)

    n = len(x)
    #zsmooth = ones(n, dtype=Float32)
    zsmooth = []

    for i in range(n):
        # DISTANCE OF ALL CATALOGUE POINTS FROM POINT i:
        dist = ((x - x[i]) / dx) ** 2 + ((y - y[i]) / dy) ** 2
        SI = argsort(dist)
        # DON'T CHANGE z[i]'s VALUE UNTIL THE END
        #zsmooth[i] = median(z[SI[0:neighbors-1]])
        zsmooth.append( median( take(z, SI[0:neighbors+1]) ) )

    return array(zsmooth)


def smoothrogers2(x, y, cx, cy, cz, neighbors=21):
    """CALCULATES A SMOOTH z BASED ON THE CATALOGUED cz VALUES
    USES THE 'NEAREST NEIGHBORS' METHOD
    FINDS EACH POINT'S 21 NEAREST NEIGHBORS IN [x,y] SPACE
    REPLACES ITS z VALUE WITH THE MEDIAN OF ALL 21 cz VALUES
    WILL PROBABLY BE VERY SLOW IF THERE ARE MANY POINTS"""

    dx = std(cx)
    dy = std(cy)

    n = len(x)
    #zsmooth = ones(n, dtype=Float32)
    zsmooth = []

    for i in range(n):
        # DISTANCE OF ALL CATALOGUE POINTS FROM POINT i:
        dist = ( ((cx - x[i]) / dx) ** 2 + ((cy - y[i]) / dy) ** 2 )
        SI = argsort(dist)
        # DON'T CHANGE z[i]'s VALUE UNTIL THE END
        #zsmooth[i] = median(cz[SI[0:neighbors-1]])
        zsmooth.append( median( take(cz, SI[0:neighbors]) ) )

    return array(zsmooth)

def smoothrogers1(x, cx, cz, neighbors=21):
    """CALCULATES A SMOOTH z BASED ON THE CATALOGUED cz VALUES
    USES THE 'NEAREST NEIGHBORS' METHOD
    FINDS EACH POINT'S 21 NEAREST NEIGHBORS IN [x] SPACE
    REPLACES ITS z VALUE WITH THE MEDIAN OF ALL 21 cz VALUES
    WILL PROBABLY BE VERY SLOW IF THERE ARE MANY POINTS"""
    
    n = len(x)
    zsmooth = []
    
    for i in range(n):
        # DISTANCE OF ALL CATALOGUE POINTS FROM POINT i:
        dist = abs(cx - x[i])
        SI = argsort(dist)
        # DON'T CHANGE z[i]'s VALUE UNTIL THE END
        #zsmooth[i] = median(cz[SI[0:neighbors-1]])
        zsmooth.append( median( take(cz, SI[0:neighbors]) ) )
        
    return array(zsmooth)

def smoothrogers1e(x, cx, cz, neighbors=21, minneighbors=11):
    """CALCULATES A SMOOTH z BASED ON THE CATALOGUED cz VALUES
    USES THE 'NEAREST NEIGHBORS' METHOD
    FINDS EACH POINT'S 21 NEAREST NEIGHBORS IN [x] SPACE
    REPLACES ITS z VALUE WITH THE MEDIAN OF ALL 21 cz VALUES
    WILL PROBABLY BE VERY SLOW IF THERE ARE MANY POINTS
    e -- HANDLES THE EDGES BETTER
    CAN ACCEPT FEWER NEIGHBORS (minneighbors) IF CLOSE TO EDGE"""
    
    n = len(x)
    cn = len(cx)
    zsmooth = []

    SI = argsort(cx)
    cx = take(cx, SI)
    cz = take(cz, SI)

    dn = (neighbors-1)/2
    
    for i in range(n):
        i0 = searchsorted(cx, x[i])
        ilo = i0 - dn
        ihi = i0 + dn
        if ilo < 0:
            ihi += ilo
            ilo = 0
            if ihi < minneighbors-1:
                ihi = minneighbors-1
        elif ihi > cn:
            ilo += ihi-cn
            ihi = cn
            if ihi-ilo < minneighbors-1:
                ilo = cn-(minneighbors-1)
        zsmooth.append(median(cz[ilo:ihi]))
        
    return array(zsmooth)

def smoothrogers1er(x, cx, cz, neighbors=21, minneighbors=11):
    """CALCULATES A SMOOTH z BASED ON THE CATALOGUED cz VALUES
    USES THE 'NEAREST NEIGHBORS' METHOD
    FINDS EACH POINT'S 21 NEAREST NEIGHBORS IN [x] SPACE
    REPLACES ITS z VALUE WITH THE MEDIAN OF ALL 21 cz VALUES
    WILL PROBABLY BE VERY SLOW IF THERE ARE MANY POINTS
    e -- HANDLES THE EDGES BETTER
    CAN ACCEPT FEWER NEIGHBORS (minneighbors) IF CLOSE TO EDGE
    r -- RETURNS THE RANGE THAT CONTAINS 1 SIGMA OF THE NEIGHBORS"""
    
    n = len(x)
    cn = len(cx)
    zsmooth = []
    zlo = []
    zhi = []

    SI = argsort(cx)
    cx = take(cx, SI)
    cz = take(cz, SI)

    dn = (neighbors-1)/2
    
    for i in range(n):
        i0 = searchsorted(cx, x[i])
        ilo = i0 - dn
        ihi = i0 + dn + 1
        if ilo < 0:
            ihi += ilo
            ilo = 0
            if ihi < minneighbors-1:
                ihi = minneighbors-1
        elif ihi > cn:
            ilo += ihi-cn
            ihi = cn
            if ihi-ilo < minneighbors-1:
                ilo = cn-(minneighbors-1)
	print i, ilo, ihi
	print neighbors, minneighbors
        zsmooth.append(median(cz[ilo:ihi]))
        czs = sort(cz[ilo:ihi])
        iczs = arange(ihi-ilo) / float(ihi-ilo)
        zlo.append(interp(.1587, iczs, czs))
        zhi.append(interp(.8413, iczs, czs))
        
    return array([zlo, zsmooth, zhi])

#################################
# REGULAR (1-D) SMOOTH PLOTS

def smoothint(x, y, avgtype='median', ext=1):
    """SMOOTHS VALUES IN 1-D
    ext TO EXTEND ARRAYS TO FULL LENGTH"""
    SI = argsort(x)
    x = take(x, SI)
    y = take(y, SI)
    
    xs = []
    ys = []
    n = len(x)
    
    i = 0
    while i < n:
        x0 = x[i]
        i2 = searchsorted(x, x0+1)
        xs.append(x0)
        ys.append(median(y[i:i2]))
        i = i2
    
    return [xs, ys]

def SmoothIntPlot(x, y, avgtype='median', plotraw=1, symbolsize=2):
    p = FramedPlot()
    [xs, ys] = smoothint(x, y, avgtype)
    if plotraw:
        p.add(Points(x, y, color='black', symbolsize=symbolsize))
    p.add(Curve(xs, ys, color='red'))  # 'blue'
    return p

def smoothintplot(x, y, avgtype='median', plotraw=1, symbolsize=2):
    """1-D SMOOTH PLOT"""
    p = SmoothIntPlot(x, y, avgtype, plotraw, symbolsize=symbolsize)
    p.show()

def extend(l, n1=0, n2=0):
    """EXTENDS A LIST BY REPLICATING THE END VALUES"""
    if n2 < 0:
        n2 = n1
    return [l[0]] * n1 + l + [l[-1]] * n2

## def smooth(x, y, ninbin=100, avgtype='median', ext=1):
##     """SMOOTHS VALUES IN 1-D
##     ext TO EXTEND ARRAYS TO FULL LENGTH"""
##     SI = argsort(x)
##     x = take(x, SI)
##     y = take(y, SI)
    
##     xs = []
##     ys = []
##     n = len(x)
    
##     print ninbin, n
##     if ninbin >= n:
##      new = n / 20
##      print "ninbin = %d > %d # OBJECTS!  USING ninbin = %d INSTEAD" % (ninbin, n, new)
##      ninbin = new
    
##     for i in range(n-ninbin):
##      if avgtype == 'mean':
##          xs.append(mean(x[i:i+ninbin]))
##          ys.append(mean(y[i:i+ninbin]))
##      else:
##          xs.append(median(x[i:i+ninbin]))
##          ys.append(median(y[i:i+ninbin]))
        
##     if ext:
##      xs = x
##      n1 = ninbin/2
##      n2 = n - len(ys) - n1
##      ys = extend(ys, ninbin/2, n2)
        
##     return [xs, ys]

def smooth(x, y, ninbin=100, avgtype='median', ext=1, mininbin=100):
    """SMOOTHS VALUES IN 1-D
    ext TO EXTEND ARRAYS TO FULL LENGTH
    HANDLES THE EDGES BETTER"""
    SI = argsort(x)
    x = take(x, SI)
    y = take(y, SI)
    
    xs = []
    ys = []
    n = len(x)
    
    print ninbin, n, mininbin
    if ninbin >= n:
        new = n / 20
        print "ninbin = %d > %d # OBJECTS!  USING ninbin = %d INSTEAD" % (ninbin, n, new)
        ninbin = new
    
    for i in range(n-mininbin):
        ilo = i
        #ihi = ilo + min([ilo + mininbin, ninbin])
##         ihi = 2*ilo + mininbin
##         if ihi > ninbin:
##             ihi = ninbin
        ihi = 2*i + mininbin
        #print ilo, ihi,
        #print n, ninbin, mininbin
        if ihi <= ninbin:
            ilo = 0
        else:
            ilo = i + mininbin/2 - ninbin/2
            ihi = ilo + ninbin
        #print ilo, ihi
        #pause()
        if avgtype == 'mean':
            #try:
            xs.append(mean(x[ilo:ihi]))
            #except:
                #print ilo, ihi
            ys.append(mean(y[ilo:ihi]))
        else:
            xs.append(median(x[ilo:ihi]))
            ys.append(median(y[ilo:ihi]))
        
    if ext:
        xs = x
        n1 = mininbin/2
        n2 = n - len(ys) - n1
        ys = extend(ys, mininbin/2, n2)
        
    return [xs, ys]

# FIRST 3 HERE ADDED IN ~/test-deblend/test8/loadmags.py
def smoothplothline(x, y, ninbin=5, avgtype='mean', ext=1, plotraw=1, symbolsize=2, linewidth=3, mininbin=5):
    p = SmoothPlot(x, y, ninbin=ninbin, avgtype=avgtype, ext=ext, plotraw=plotraw, symbolsize=symbolsize, linewidth=linewidth, mininbin=mininbin)
    p.add(HLine(x, 0, color='blue'))
    p.show()

def SmoothPlotHLine(x, y, ninbin=5, avgtype='mean', ext=1, plotraw=1, symbolsize=2, linewidth=3, mininbin=5):
    p = SmoothPlot(x, y, ninbin=ninbin, avgtype=avgtype, ext=ext, plotraw=plotraw, symbolsize=symbolsize, linewidth=linewidth, mininbin=mininbin)
    p.add(HLine(x, 0, color='blue'))
    return p

def addSmoothPlotHLine(p, x, y, ninbin=5, avgtype='mean', ext=1, plotraw=1, symbolsize=2, linewidth=3, mininbin=5):
    addSmoothPlot(p, x, y, ninbin=ninbin, avgtype=avgtype, ext=ext, plotraw=plotraw, symbolsize=symbolsize, linewidth=linewidth, mininbin=mininbin)
    p.add(HLine(x, 0, color='blue'))

def SmoothPlot(x, y, ninbin=100, avgtype='median', ext=1, plotraw=1, symbolsize=2, linewidth=3, mininbin=100):
    p = FramedPlot()
    [xs, ys] = smooth(x, y, ninbin, avgtype, ext, mininbin)
    if plotraw:
        p.add(Points(x, y, color='black', symbolsize=symbolsize))
    p.add(Curve(xs, ys, color='red', linewidth=linewidth))  # 'blue'
    return p

def smoothplot(x, y, ninbin=100, avgtype='median', ext=1, plotraw=1, symbolsize=2, linewidth=3, mininbin=100):
    """1-D SMOOTH PLOT"""
    p = SmoothPlot(x, y, ninbin, avgtype, ext, plotraw, symbolsize=symbolsize, linewidth=linewidth, mininbin=mininbin)
    p.show()

def addSmoothPlot(p, x, y, ninbin=100, avgtype='median', ext=1, plotraw=1, symbolsize=2, linewidth=3, mininbin=100):
    [xs, ys] = smooth(x, y, ninbin, avgtype, ext, mininbin)
    if plotraw:
        p.add(Points(x, y, color='black', symbolsize=symbolsize))
    p.add(Curve(xs, ys, color='red', linewidth=linewidth))  # 'blue'


