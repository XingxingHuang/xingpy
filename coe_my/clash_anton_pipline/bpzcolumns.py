from coeio import *
from filttools import *

def bpzcolumns(inroot):
    cat = loadcat(inroot+'.cat')

    magcols = {}
    magerrcols = {}
    filts = []
    idcol = None
    zcol = None

    for i, label in enumerate(cat.labels): 
        if strend(label, '_mag'):
            filt = label[:-4]
            filts.append(filt)
            magcols[filt] = i + 1
        if strend(label, '_magerr'):
            filt = label[:-7]
            magerrcols[filt] = i + 1
        if label == 'id':
            idcol = i + 1
        if label == 'zspec':
            zcol = i + 1

    fullfilts = map(getfullfilt, filts)

    filtlen = 8  # minimum width for this column
    for fullfilt in fullfilts:
        filtlen = max((filtlen, len(fullfilt)))

    if 'M0' in cat.labels:
        priorcol = cat.labels.index('M0') + 1
    else:
        lams = map(getlam, filts)
        i = findbestmatch(lams, 775)
        priorfilt = filts[i]
        priorcol = magcols[priorfilt]

    print "Saving %s.columns ..." % inroot
    fout = open(inroot+'.columns', 'w')

    fout.write('# ')
    fout.write('Filter'.ljust(filtlen-2))
    fout.write('  columns  AB/Vega  zp_error  zp_offset\n')

    for filt in filts:
        line = getfullfilt(filt).ljust(filtlen+3)
        line += '%2d,%2d' % (magcols[filt], magerrcols[filt])
        line += '     AB       0.03       0.0\n'
        fout.write(line)

    fout.write('M_0'.ljust(filtlen+3))
    fout.write('%2d\n' % priorcol)

    if idcol <> None:
        fout.write('ID'.ljust(filtlen+3))
        fout.write('%2d\n' % idcol)

    if zcol <> None:
        fout.write('Z_S'.ljust(filtlen+3))
        fout.write('%2d\n' % zcol)

    fout.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        inroot = sys.argv[1]
    else:
        inroot = 'photometry'
    bpzcolumns(inroot)
    # inroot = 'specz'
