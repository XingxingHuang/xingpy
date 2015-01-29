# python bpzchisq2run.py ACS-Subaru
# PRODUCES ACS-Subaru_bpz.cat

# ADDS A FEW THINGS TO THE BPZ CATALOG
# INCLUDING chisq2 AND LABEL HEADERS

# ~/p/bpzchisq2run.py NOW INCLUDED!
# ~/Tonetti/colorpro/bpzfinalize7a.py
# ~/UDF/Elmegreen/phot8/bpzfinalize7.py
# ~/UDF/bpzfinalize7a.py, 7, 5, 4, 23_djh, 23, 3

# NOW TAKING BPZ OUTPUT w/ 3 REDSHIFT PEAKS
# ALSO USING NEW i-band CATALOG istel.cat -- w/ CORRECT IDs

# python bpzfinalize.py bvizjh_cut_sexseg2_allobjs_newres_offset3_djh_Burst_1M
#from coetools import *
from coeio import *
sum = add.reduce # Just to make sure

##################
# add nf, jhgood, stellarity, x, y

inbpz = capfile(sys.argv[1], 'bpz')
inroot = inbpz[:-4]

infile = loadfile(inbpz)
for line in infile:
    if line[:7] == '##INPUT':
        incat = line[8:]
        break

for line in infile:
    if line[:9] == '##N_PEAKS':
        npeaks = string.atoi(line[10])
        break

#inchisq2 = inroot + '.chisq2'

#outbpz = inroot + '_b.bpz'
outbpz = inroot + '_bpz.cat'

if npeaks == 1:
    labels = string.split('id   zb   zbmin  zbmax  tb    odds    zml   tml  chisq')
elif npeaks == 3:
    labels = string.split('id   zb   zbmin  zbmax  tb    odds    zb2   zb2min  zb2max  tb2    odds2    zb3   zb3min  zb3max  tb3    odds3    zml   tml  chisq')
else:
    print 'N_PEAKS = %d!?' % npeaks
    sys.exit(1)

labelnicks = {'Z_S': 'zspec', 'M_0': 'M0'}

read = 0
ilabel = 0
nlabels = len(labels)
for iline in range(len(infile)):
    line = infile[iline]
    if line[:2] == '##':
        if read:
            break
    else:
        read = 1
    if read == 1:
        ilabel += 1
        label = string.split(line)[-1]
        #if ilabel >= 10:
        if ilabel > nlabels:
            labels.append(labelnicks.get(label, label))

print inbpz, labels
mybpz = loadvarswithclass(inbpz, labels=labels)
print mybpz.len(), 'OBJECTS'

if not exists(incat):
    print 'Photometric catalog', incat, 'does not exist.'
    incat = inroot + '.cat'

if exists(incat):
    mycat = loadcat(incat)
    print mycat.labels
    if mycat.labels == []:
        print "Let's try loading again as a SExtractor catalog"
        mycat = loadsexcat0(incat)
        print
        if mycat.labels == []:
            mycat = None
else:
    mycat = None
    print 'Photometric catalog', incat, 'does not exist either.'

print mycat.len(), 'OBJECTS'

#icat = loadvarswithclass('/home/coe/UDF/istel.cat')
#icat = icat.takeids(mycat.id)
#bpzchisq2 = loadvarswithclass(inchisq2)


#################################
# CHISQ2, nfdet, nfobs

if exists(inroot+'.flux_comparison'):
    data = loaddata(inroot+'.flux_comparison+')

    #nf = 6
    nf = (len(data) - 5) / 3
    # id  M0  zb  tb*3
    id = data[0]
    print len(id), 'OBJECTS'
    ft=data[5:5+nf]  # FLUX (from spectrum for that TYPE)
    fo=data[5+nf:5+2*nf]  # FLUX (OBSERVED)
    efo=data[5+2*nf:5+3*nf]  # FLUX_ERROR (OBSERVED)

    # chisq 2
    eft = ft / 15.
    eft = max(eft)  # for each galaxy, take max eft among filters
    ef = sqrt(efo**2 + eft**2)  # (6, 18981) + (18981) done correctly

    dfosq = ((ft - fo) / ef) ** 2
    dfosqsum = sum(dfosq)

    detected = greater(fo, 0)
    nfdet = sum(detected)

    observed = less(efo, 1)
    nfobs = sum(observed)

    # DEGREES OF FREEDOM
    dof = clip2(nfobs - 3., 1, None)  # 3 params (z, t, a)

    chisq2clip = dfosqsum / dof

    sedfrac = divsafe(max(fo-efo), max(ft), -1)  # SEDzero

    chisq2 = chisq2clip[:]
    chisq2 = where(less(sedfrac, 1e-10), 900., chisq2)
    chisq2 = where(equal(nfobs, 1), 990., chisq2)
    chisq2 = where(equal(nfobs, 0), 999., chisq2)
    #################################


    #print 'BPZ tb N_PEAKS BUG FIX'
    #mybpz.tb = mybpz.tb + 0.667
    #mybpz.tb2 = where(greater(mybpz.tb2, 0), mybpz.tb2 + 0.667, -1.)
    #mybpz.tb3 = where(greater(mybpz.tb3, 0), mybpz.tb3 + 0.667, -1.)

    mybpz.add('chisq2', chisq2)
    mybpz.add('nfdet', nfdet)
    mybpz.add('nfobs', nfobs)
else:
    print inroot+'.flux_comparison', 'does not exist.'

#mybpz.add('jhgood', jhgood)
if mycat <> None:
    if 'stel' in mycat.labels:
        mybpz.add('stel', mycat.stel)
    elif 'stellarity' in mycat.labels:
        mybpz.add('stel', mycat.stellarity)
    if 'maxsigisoaper' in mycat.labels:
        mybpz.add('sig', mycat.maxsigisoaper)
    if 'sig' in mycat.labels:
        mybpz.assign('sig', mycat.maxsigisoaper)
    #mybpz.add('x', mycat.x)
    #mybpz.add('y', mycat.y)
    if 'zspec' not in mybpz.labels:
        if 'zspec' in mycat.labels:
            mybpz.add('zspec', mycat.zspec)
            print mycat.zspec
            if 'zqual' in mycat.labels:
                mybpz.add('zqual', mycat.zqual)

print mybpz.labels
mybpz.header.append('-')  # SPECIAL CODE TO KEEP ONLY BEGINNING ## LINES OF HEADER
mybpz.save(outbpz, maxy=None)

##################

#inphot = inroot + '.cat'
#if exists(inphot): # and not exists(outall):
if mycat <> None:
    outall = inroot + '_photbpz.cat'
    #allcat = loadcat(inphot)
    allcat = mycat
    if 'M0' in mycat.labels:
        mycat.labels.remove('M0')
    allcat.merge(mybpz, replace=1)  # Use mybpz results
    #allcat.labels.remove('M0')
    print allcat.labels
    allcat.header.append('-')  # SPECIAL CODE TO KEEP ONLY BEGINNING ## LINES OF HEADER
    allcat.save(outall)

##################

# det
# 0 < mag < 99
# dmag > 0
# fo > 0
# efo -> 1.6e-8, e.g.

# undet
# mag = 99
# dmag = -m_1sigma
# fo = 0
# efo = 0 -> 5e13, e.g.

# unobs
# mag = -99
# dmag = 0
# fo = 0
# efo = inf (1e108)


## # original chisq usually matches this:
## dfosq = ((ft - fo) / efo) ** 2
## dfosqsum = sum(dfosq)

## observed = less(efo, 1)
## nfobs = sum(observed)

## chisq = dfosqsum / (nfobs - 1.)

