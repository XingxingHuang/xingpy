#!/usr/bin/python

import sys

sys.stdout = open("/Users/dcoe/cronlog.txt","w")
sys.stderr = open("/Users/dcoe/cronerrors.txt","w")

sys.path.append('/data01/cipphot/pipeline')
sys.path.append('/data01/cipphot/pipeline/bpz')
sys.path.append('/data01/cipphot/pipeline/bpz/plots')
#sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages/')
sys.path.append('/Library/Python/2.6/site-packages')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/PyObjC')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/wx-2.8-mac-unicode')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python26.zip')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-mac')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-mac/lib-scriptpackages')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-tk')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-old')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload')
sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages')
sys.path.append('/usr/local/scisoft/packages/python/lib/python2.6/site-packages/matplotlib')
#sys.path.append('')

print 'adding to path...'

for p in sys.path:
    print p

from coeplott import *
import datetime
from matplotlib.dates import MonthLocator

#figure(1, figsize=(90,28))
#closefig()
#thick(left=0.12, right=0.98)
#fac = 6
fac = 3
fontsize = 18*fac
titlefontsize = 2*fontsize
smallfontsize = fontsize/2.5
medfontsize = fontsize/1.5
#figure(1, figsize=(14, 6))
#figure(1, figsize=(14*fac, 8*fac))

pylab.rcParams.update({'lines.markersize':8})  # default = 6

months = string.split('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec')

def dateparse1(date):
    month, day, year = string.split(date)
    month = months.index(month) + 1
    day = int(day[:-1])
    year = int(year)
    return datetime.date(year, month, day).toordinal()

#dateparse1('Sep 29, 2011')

def dateparse2(date):
    m, d, y = stringsplitatoi(date, '/')
    date = datetime.date(y, m, d)
    return date.toordinal()

#dateparse2('4/20/2011')

def dateday(d):
    return datetime.date.fromordinal(d).day

months = string.split('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec')

def datemonth(d):
    month = datetime.date.fromordinal(d).month
    month = months[month-1]
    return month

def dateyear(d):
    return datetime.date.fromordinal(d).year

def dateweekday(d):
    return datetime.date.fromordinal(d).weekday()

def cropclus(clus):
    return clus.split('-')[0].replace('MACSJ', 'MACS').replace('MS ', 'MS')

#################################

#for pruneyear in (2011,2012):

infile = 'CLASH_Visits.tsv'
#infile = 'CLASH_Visits%20-%20Sheet1.tsv'
#txt = loadfile(infile)

# /Users/coe/clusters/all/NEDquery.py
# Simpler:
# http://www.daniweb.com/software-development/python/threads/113058
import urllib
url = 'https://docs.google.com/spreadsheet/pub?key=0AjaeL-o31prldHFGTnhFN00yNVhQSlljTzFqZjEyUWc&single=true&gid=0&output=txt'
infile, message = urllib.urlretrieve(url)
txt = loadfile(infile)


clusdates = {}

lines = []
for line in txt[1:]:
    if not line.strip():
        break
    lines.append(line)
    words = line.split('\t')
    #print len(words)
    #clus, program, id, date_time, filters, parfilters, status, reductionstatus = words[:8]  # comments
    clus, program, id, date_time = words[:4]
    date, t = date_time.split()
    date = dateparse2(date)
    #print date
    if clus not in clusdates.keys():
        clusdates[clus] = [date]
    else:
        clusdates[clus].append(date)

clusters = clusdates.keys()
starts = []
ends = []

for clus in clusters:
    #print clus, minmax(clusdates[clus])
    starts.append(min(clusdates[clus]))
    ends.append(max(clusdates[clus]))

starts = array(starts)
ends = array(ends)

SI = argsort(starts)
clusorder = []
for i in range(len(SI)):
    #print clusters[i], starts[i]
    clusorder.append(clusters[SI[i]])

clusorder = clusorder[::-1]

starts = starts.take(SI[::-1])
ends   = ends.take(SI[::-1])

#########
# Prune to either 2011 or 2012

#pruneyear = int(sys.argv[1])
pruneyear = None

nclus = len(clusorder)
ii = []

if pruneyear == 2011:
    print "Pruning to pre-2012..."
    startmax = datetime.date(2012, 1, 1).toordinal()
    for i in range(nclus):
        #print clusorder[i], starts[i]-startmax
        if starts[i] < startmax:
            ii.append(i)
elif pruneyear == 2011:
    print "Pruning to 2012..."
    startmin = datetime.date(2012, 1, 1).toordinal()
    for i in range(nclus):
        #print starts[i]-startmin, clusorder[i]
        if starts[i] > startmin:
            ii.append(i)

if pruneyear:
    starts = starts.take(ii)
    ends = ends.take(ii)
    clusorder = array(clusorder).take(ii).tolist()
    # print clusorder

nclus = len(clusorder)

for i in range(nclus)[::-1]:
    print datetime.date.fromordinal(starts[i]).strftime('%m/%d/%y'),
    print '-',
    print datetime.date.fromordinal(ends[i]).strftime('%m/%d/%y'),
    print ':',
    print clusorder[i]

#continue

t0 = min(starts)
starts = starts - t0
ends = ends - t0

totaltime = max(ends)
#print totaltime

#########

#plotymargin = 1 - top + bottom
#yperclus = 8 / (nclus + 1.)
pym = 4.
yfigsize = 8 * (nclus + pym) / (10 + pym)
xfigsize = 2 + 12 * totaltime / 365.
#xfigsize = 14
#yfigsize = 8
#print yfigsize
#print xfigsize, yfigsize

left = 2 / float(xfigsize)
#print left
right = 0.98
bottom = 0.1
top = 0.925
#thick(left=0.12, right=0.98, bottom=0.1, top=0.925, fontsize=fontsize)
thick(left=left, right=right, bottom=bottom, top=top, fontsize=fontsize)

figure(1, figsize=(xfigsize*fac, yfigsize*fac))

#########

#symvisit = {'A':'s', 'B':'D'}
symvisit = {'A':'<', 'B':'>'}
colorinstr = {'UVIS':'m', 'ACS':'g', 'IR':'r'}

UVISfilters = 'F225W F275W F336W F390W'.split()
ACSfilters = 'F435W F475W F606W F625W F775W F814W F850LP'.split()
IRfilters = 'F105W F110W F125W F140W F160W'.split()
allfilters = UVISfilters + ACSfilters + IRfilters
nfilters = len(allfilters)

#allfilters = 'F225W F275W F336W F390W F435W F475W F606W F625W F775W F814W F850LP F105W F110W F125W F140W F160W'.split()

margin = 0.5

def ifilt(filt):
    return allfilters.index(filt)

def filty(filt):
    return allfilters[::-1].index(filt) / (nfilters - 1.)

def filtinstr(filt):
    if filt in UVISfilters:
        return 'UVIS'
    if filt in ACSfilters:
        return 'ACS'
    if filt in IRfilters:
        return 'IR'
clusymid = arange(nclus) * (1 + margin) + 0.5

#clf()

for i, clus in enumerate(clusorder):
    start, end = minmax(clusdates[clus]) - t0
    y = i * (1 + margin)
    dt = end - start
    #print clus, start, end, y, dt
    patch = Rectangle((start, y), dt, 1)
    #color = (1,1,1)
    color = (0.85,0.92,1)
    #color = (0.8,0.9,1)
    patch.set_fc(color)
    patch.set_ec(color)
    #patch.set_alpha(alpha)
    patch.set_zorder(-5)
    #patch.set_lw(lw)
    gca().add_patch(patch)
    #show()
    #pause()
    # ACS
    #dy1 = (filty('F390W') + filty('F435W')) / 2.
    #dy2 = (filty('F850LP') + filty('F105W')) / 2.
    #dy1 = filty('F435W')  #+ 0.3 / (nfilters - 1.)
    #dy2 = filty('F850LP') #- 0.3 / (nfilters - 1.)
    for filts in UVISfilters, ACSfilters, IRfilters:
        dy1 = filty(filts[0])
        dy2 = filty(filts[-1])
        patch = Rectangle((start, y+dy1), dt, dy2-dy1)
        color = (0.65,0.8,1)
        patch.set_fc(color)
        patch.set_ec(color)
        # patch.set_alpha(alpha)
        patch.set_zorder(-4.5)
        # patch.set_lw(lw)
        gca().add_patch(patch)


lightlinecolor = '0.85'

xlo = min(starts)
xhi = max(ends)

# Little legend
for i, clus in enumerate(clusorder):
    start, end = minmax(clusdates[clus]) - t0
    dt = end - start
    y = i * (1 + margin) + 0.5
    if i < len(clusorder)-2:
        #clus2fontsize = 18
        clus2fontsize = 18 * nclus / 10.
        text(start-7.5, y, cropclus(clus), fontsize=clus2fontsize, va='center', ha='right')
    for filt in allfilters:
        for x0 in (start-7.5, end):
            x = x0 + 1 + 2 * odd(ifilt(filt))
            y = filty(filt) + i * (1 + margin)
            instr = filtinstr(filt)
            color = colorinstr[instr]
            text(x, y, filt, fontsize=6, va='center', color=color)

#xtx = multiples(xlo, xhi)
#days = map(dateday, t0+xtx)
xtx = []
xlabs = []

for x in multiples(xlo,xhi):
    d = x+t0
    day = dateday(d)
    if day == 1:
        xline(x, zorder=0)
    else:
        xline(x, c=lightlinecolor, lw=1, zorder=-3)
    if day == 1:
        month = datemonth(d)
        year = dateyear(d)
        xtx.append(x)
        xlabs.append("%s'%d" % (month, year-2000))
        for i in range(1,nclus):
            y = i * (1 + margin) - margin / 2.
            text(x, y, month, fontsize=12, ha='center', va='center')

    weekday = dateweekday(d)
    if weekday == 6:  # Sunday
        xline(x, lw=1, c='0.50')
        #print day
        text(x, -margin, day, fontsize=smallfontsize, ha='center', va='center')
        y = nclus * (1+margin)
        text(x, y, day, fontsize=smallfontsize, ha='center', va='center')
        for i in range(1,nclus):
            y = i * (1 + margin) - margin / 2.
            text(x, y, day, fontsize=8, ha='center', va='center')

for i in range(nclus):
    for j in range(nfilters):
        #y = i * (1 + margin) + j / (nfilters - 1.)
        filt = allfilters[j]
        y = i * (1 + margin) + filty(filt)
        ## if filtinstr(filt) == 'ACS':
        ##     if even(j):
        ##         color = lightlinecolor
        ##     else:
        ##         color = '0.60'
        ##     zorder = -3
        ## else:
        ##     color = '0.40'
        ##     zorder = -0.5
        if odd(j):
            color = '0.70'
            zorder = -3
        else:
            color = '0.50'
            zorder = -0.5
        #color = colormaprgb(j, [0, nfilters-1], 'gist_rainbow_r')
        yline(y, c=color, lw=1, zorder=zorder)

# LEGEND
x0 = xhi * 0.669
dx = xhi * 0.005
dx2 = xhi * 0.045
previnstr = ''
for filt in allfilters:
    y = filty(filt) + (nclus - 1) * (1 + margin)
    #print filt, y
    instr = filtinstr(filt)
    color = colorinstr[instr]
    if instr <> previnstr:
        x = x0

        exec('instrfilters = %sfilters' % instr)
        n = len(instrfilters)
        ym = y - (n-1)/2. / (nfilters - 1.)
        #print instr, instrfilters, n, y, ym
        #print instr, n, y, ym
        text(x0 - dx2*0.7, ym, instr, fontsize=smallfontsize, va='center', color=color)

    plot1(x, y, '<', mfc=color, mec=color)
    text(x + dx, y, filt, fontsize=smallfontsize, va='center', color=color)
    x += dx2
    previnstr = instr

y = (nclus - 2) * (1 + margin)
dy1 = filty('F475W')
dy2 = filty('F850LP')
plot1(x0,   y+dy1, 'k<')
text(x0+dx, y+dy1, 'Orient A', fontsize=smallfontsize, va='center')
plot1(x0,   y+dy2, 'k>')
text(x0+dx, y+dy2, 'Orient B', fontsize=smallfontsize, va='center')

#medfontsize = fontsize/2.2
figtext(0.725, 0.97, 'Future dates are approximate (obs may be up to 3 days later).', fontsize=medfontsize)
figtext(0.725, 0.95, 'Exact dates are assigned 10 days before those shown here.', fontsize=medfontsize)
figtext(0.725, 0.93, 'Sundays are numbered.', fontsize=medfontsize)

todaystr = datetime.date.today().strftime('%b %d, %Y')
figtext(0.88, 0.93, 'Updated '+todaystr, fontsize=medfontsize, color='r')

#print
#print 'any mistakes in CLASH_Visits.tsv below:'
for line in lines:
    #clus, program, visit, date_time, filters, parfilters, status, reductionstatus = line.split('\t')[:8]  # comments
    words = line.split('\t')
    clus, program, visit, date_time = words[:4]
    if clus not in clusorder:
        continue  # pruned

    if len(words) >= 5:
        filters    = words[4]
        filtblank = False
    else:
        filters = 'ACS F625W'
        filtblank = True

    date, t = date_time.split()
    date = dateparse2(date)

    sym = symvisit[visit[0]]
    if filters[0] == '"':
        filters = filters[1:-1]

    for instrfilt in filters.split(', '):
        instr, filt = instrfilt.split()
        if filtblank:
            color = 'k'
        else:
            color = colorinstr[instr]
        if filt not in allfilters:
            print filt
            print line
            print
        else:
            #filty = allfilters[::-1].index(filt) / (nfilters - 1.)
            y = clusorder.index(clus) * (1 + margin) + filty(filt)
            #print clus, y
            # y += 1 - ((lam - 200) / 1000.)
            plot1(date-t0, y, sym, mfc=color, mec=color)

#xlim(xlo, xhi)
xlim(prange((xlo, xhi), margin=0.01))
xticks(xtx, xlabs, rotation=30)
#xticks(xtx, xlabs)

ylo = -margin*2
yhi = nclus * (1+margin) + margin
ylim(ylo, yhi)

#yticks(clusymid, clusters)
cluslabs = map(cropclus, clusorder)
yticks(clusymid, cluslabs)

#yticks(multiples(ylo, yhi))
#grid()

#title('CLASH Cycle 18 Schedule')
title('CLASH HST Schedule', fontsize=titlefontsize)
#title('CLASH HST Schedule %d' % pruneyear)

#outroot = 'CLASHschedule%d_' % pruneyear
outroot = 'CLASHschedule'
#outroot += datetime.date.today().strftime('%m%d')  # e.g., 0930
#savepngpdf(outroot, saveeps=0)
outdir = '/astro/clash1/ftp/outgoing/'
outroot = join(outdir, outroot)
savepng(outroot)
# http://archive.stsci.edu/pub/clash/outgoing/CLASHschedule.png
#os.system('open %s.png' % outroot)
#show()
#pause()

    #plot1(date-t0, clusy[clus], 'o')
    #text(date-t0, clusy[clus], filters)
    #text(date-t0, clusy[clus], clus)
