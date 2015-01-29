from coeio import *

def catsave(cat, outfile='', dir=''):
    
    #################################
    # Lengthen formats as necessary to allow labels to fit
    maxcollen = 0
    collens = {}
    for label in cat.labels:
        #print label, cat.formats[label],
        fmt = cat.formats[label]
        if 'd' in fmt:
            nstr = strbtw(fmt, '%', 'd')
        else:        
            nstr = strbtw(fmt, '%', '.')
        #print nstr
        if int(nstr) < len(label):
            #fmt = fmt.replace(nstr, '%d'%len(label), 1)  # 1 at end means only replace 1st instance
            n = len(label)
            nextra = n - int(nstr)
            nl = nextra / 2
            nr = nextra - nl
            fmt = ' '*nl + fmt + ' '*nr
            cat.formats[label] = fmt
            #print 'being lengthened: |' + fmt + '|'
            collen = n
        else:
            collen = int(nstr)
        collens[label] = collen
        if collen > maxcollen:
            maxcollen = collen

    #################################
    # Format
    format = ' '
    for label in cat.labels:
        if label not in cat.formats.keys():
            print 'Missing %s key in format' % label
            format = ''
            break
        fmt = cat.formats[label]
        format += fmt + '  '
    if format:
        format = format[:-2] + '\n'

    #print 'format:', format

    #################################
    # Header
    addtohead = True
    outfile = outfile or cat.name
    outfile = join(dir, outfile)
    print 'Saving', outfile, "..."
    fout = open(outfile, 'w')
    for headline in cat.header:
        if headline == '.':
            addtohead = False
            break
        
        if headline[-1] <> '\n':
            headline += '\n'
        
        fout.write(headline)

    #################################
    # Data Header
    if addtohead:
        for i, label in enumerate(cat.labels):
            line = '# %2d ' % (i+1)
            #print label, maxcollen, type(maxcollen)
            line += string.ljust(label, maxcollen)
            line += '  '
            line += cat.descriptions[label]
            line += '\n'
            fout.write(line)

        fout.write('##\n')

        # Pentultimate headline
        line = '##'
        for label in cat.labels:
            s = label.center(collens[label])
            line += s
            #print 'x'+s+'x'
            line += '  '

        line = line[:-2]  # get rid of last double space
        line += '\n'
        fout.write(line)

    #################################
    # Data
    cat.updatedata()
    for i in range(cat.len()):
        #print data.shape, i
        dataline = cat.data[:,i]
        #print 'dataline', dataline, type(dataline)
        #line = format % tuple(dataline)
        line = ' '
        for i in range(len(cat.labels)):
            label = cat.labels[i]
            datum = dataline[i]
            fmt = cat.formats[label]
            if abs(datum) > 1e6:
                collen = collens[label]
                ndec = collen - 7
                fmt = '%% %d.%de' % (collen, ndec)
            line += fmt % datum
            line += '  '

        line = line[:-2]
        line += '\n'
        fout.write(line)

    fout.close()
