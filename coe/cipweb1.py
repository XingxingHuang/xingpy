from coebasics import *
import dossier

testing = '-test' in sys.argv
notadrill = not testing
if testing:
    print 'Just testing...'
    print

#################################
# FIELD AND REDSHIFT

def fieldshorten(field):
    field = field.replace('abell_', 'a')
    return field

def fieldlengthen(field):
    if field[0] == 'a':
        if field[:5] <> 'abell':
            field = 'abell_' + field[1:]
    return field

def strendnum(s):
    for i in range(len(s)):
        #if s[i] in '0123456789':
        if s[i] in '123456789':
            return s[i:]

cipdir = '/data01/cipphot/pipeline/'
if exists(join(cipdir, 'redshifts.txt')):
    redshifts = loaddict('redshifts.txt', dir=cipdir)
else:
    # on laptop
    cipdir = '~/cipphot'
    redshifts = loaddict('redshifts.txt', dir=cipdir)
fields = redshifts.keys()
fieldnums = map(strendnum, fields)

#################################

# field: string, with or without leading 0 or name
# id: integer
def cipweb(field, id, IRdet=False, justlinks=False):
    fieldnum = strendnum(field)
    if fieldnum == '2129':
        print '2129 IS AMBIGUOUS (macs2129 / rxj2129) ...',
        print 'SELECTING macs2129 BY DEFAULT'
        print
        field = 'macs2129'
    else:
        i = fieldnums.index(fieldnum)
        field = fields[i]

    zclus = redshifts[field]

    if IRdet:
        instr  = 'IR'
        instr2 = 'IR'
    else:
        instr  = 'ACS_IR'
        instr2 = 'ACS+IR'

    pagetitle = '%s %s detection object #%d' % (field.upper(), instr2, id)
    
    if not justlinks:
        #outdir = '/astro/clash1/ftp/outgoing/%s/HST/catalogs/mosaicdrizzle_image_pipeline/%s_detection/PhotoZ/' % (field, instr)
        #colordir   = '/astro/clash1/ftp/outgoing/%s/HST/color_images/mosaicdrizzle_image_pipeline' % field

        fielddir = '/astro/clash1/ftp/outgoing/%s/HST/' % field
        catdir = join(fielddir, 'catalogs/mosaicdrizzle_image_pipeline/%s_detection' % instr)
        outdir = join(catdir, 'PhotoZ')
        sexdir = join(catdir, 'SExtractor')
        labeleddir = join(catdir, 'labeled_images')
        colordir = join(fielddir, 'color_images/mosaicdrizzle_image_pipeline')

        cmd = 'python $BPZPATH/plots/webpage.py photometry'

        cmd += ' %d' % id

        cmd += ' -OUTPUT %d.html' % id

        cmd += ' -TITLE "%s"' % pagetitle
        #cmd += ' -TITLE "%s %s detection object #%d"' % (field.upper(), instr2, id)

        cmd += ' -ZCLUS %.3f' % zclus
        cmd += ' -ZMAX 7'

        cmd += ' -SEGM %s/detectionImage_SEGM.fits' % sexdir

        cmd += ' -COLORNAMES ACS+IR ACS IR IRBRIGHT UVIS SEGMID SEGM'

        cmd += ' -COLOR'
        cmd += ' %s/%s.png'             % (colordir, field)
        cmd += ' %s/%s_acs.png'         % (colordir, field)
        cmd += ' %s/%s_ir.png'          % (colordir, field)
        cmd += ' %s/%s_irbright.png'    % (colordir, field)
        cmd += ' %s/%s_uvis.png'        % (colordir, field)
        cmd += ' %s/%s_segm_id.png'     % (labeleddir, field)
        cmd += ' %s/%s_segm.png'        % (labeleddir, field)

        #print string.join(cmd.split(), '\n')
        #print

        print 'Changing to directory:'
        print outdir
        if notadrill:
            os.chdir(outdir)
        print
        print 'Running command:'
        print cmd
        if notadrill:
            #run(cmd)
            dossier.run(cmd.split()[1:])

    outpage = 'http://archive.stsci.edu/pub/clash/outgoing/%s/HST/' % field
    outpage += 'catalogs/mosaicdrizzle_image_pipeline/%s_detection/' % instr
    outpage += 'PhotoZ/html/%d.html' % id

    print
    print 'Created webpage:'
    print outpage
    print
    
    return outpage, pagetitle

#################################

def reformattitle(pagetitle):
    words = pagetitle.split()
    words[0] = words[0].ljust(10)
    #words[1] = words[1].rjust(6)
    words[-1] = words[-1].rjust(6)
    pagetitle = string.join(words)
    return pagetitle

#################################

def splitdirs(dir):
    """Splits a path into a list of directories"""
    print dir
    rootdir, basedir = os.path.split(dir)
    dirs = [basedir]
    while rootdir:
        rootdir, basedir = os.path.split(rootdir)
        dirs.append(basedir)
        if rootdir == '/':
            dirs.append('/')
            break
    
    return dirs[::-1]

def chmod1(path, mode):
    try:
        os.chmod(path, mode)
    except:  # Maybe it's not your file
        pass

def makedirsmode(newpath, mode=0775):
    """Make a directory path and set permissions along the way"""
    path = ''
    for dir in splitdirs(newpath):
        path = os.path.join(path, dir)
        if not exists(path):
            os.mkdir(path)
            chmod1(path, mode)

def cipwebs(infields, ids, IRdet, outpage, pagetitle=None, justlinks=False):
    if outpage:
        outdir = '/astro/clash1/ftp/outgoing/galaxies/dossiers'
        fulloutpage = join(outdir, outpage)
        fulloutdir = os.path.dirname(fulloutpage)
        makedirsmode(fulloutdir, 0755)
        fout = open(fulloutpage, 'w')
        if pagetitle:
            fout.write('<h1>%s</h1>\n' % pagetitle)
        fout.write('<h3><pre>')
        fout.close()
    for i in range(len(ids)):
        print '---------------------------------'
        print
        print '%d / %d' % (i+1, len(ids))
        print
        field = infields[i]
        #if type(field) in (type(1234), type(1234.0)):
        if type(field) <> type('sss'):
            field = str(roundint(field))
        id = roundint(ids[i])
        print 'cipweb', field, id, IRdet, type(field)
        outpage1, pagetitle1 = cipweb(field, id, IRdet, justlinks=justlinks)
        if outpage:
            pagetitle1 = reformattitle(pagetitle1)
            fout = open(fulloutpage, 'a')
            fout.write('<a href=%s>' % outpage1)
            fout.write(pagetitle1)
            #fout.write('</a><br>\n')
            fout.write('</a><br>')
            fout.close()
    if outpage:
        #fout.close()
        print
        print 'CREATED WEBPAGE LINKING TO ALL THE OTHERS:'
        print 'http://archive.stsci.edu/pub/clash/outgoing/galaxies/dossiers/' + outpage
    
#################################
# READ INPUT AND RUN

# python $CIPPHOT/cipweb.py 383 1309
# python $CIPPHOT/cipweb.py 383 IR 1309
# python $CIPPHOT/cipweb.py a383 IR 1309
# python $CIPPHOT/cipweb.py abell_383 IR 1309
# python $CIPPHOT/cipweb.py 383 IR1309

# python $CIPPHOT/cipweb.py 383 1309,572 webpage.html
# python $CIPPHOT/cipweb.py 383 IR 1309,572 webpage.html

# python $CIPPHOT/cipweb.py objects.cat webpage.html
# python $CIPPHOT/cipweb.py objects.cat IR webpage.html -TITLE "Far out galaxies" -JUSTLINKS
# object.cat first two columns are: field, id

IRdet = 0  # ACS+IR default
outpage = None

field = sys.argv[1]
justlinks = '-JUSTLINKS' in sys.argv
pagetitle = params_cl(converttonumbers=False).get('TITLE', None)

if '.' in field:  # filename!
    print 'filename!'
    infields, ids = loaddata(field).T[:2]
    if len(sys.argv) > 2:
        IRdet = sys.argv[2] == 'IR'
        if strend(sys.argv[2], '.html'):
            outpage = sys.argv[2]
    if len(sys.argv) > 3:
        outpage = sys.argv[3]
    infields = infields.astype(int)
    cipwebs(infields, ids, IRdet, outpage, pagetitle, justlinks)
else:
    args = sys.argv[2:]
    if args[0][:2].upper() == 'IR':
        IRdet = 1
        if len(args) == 1:  # IR1309
            id = id[2:]
        args = args[1:]
    
    if len(args):
        id = args[0]  # 1309
        args = args[1:]
        if len(args):
            outpage = args[0]

    if '.' in id:
        ids = loaddata(id).T
        if len(ids.shape) == 2:
            ids = ids[0]
        print ids
        infields = [field] * len(ids)
        cipwebs(infields, ids, IRdet, outpage, pagetitle, justlinks)
    elif ',' in id:
        ids = stringsplitatoi(id, ',')
        infields = [field] * len(ids)
        cipwebs(infields, ids, IRdet, outpage, pagetitle, justlinks)
    else:
        id = strendnum(id)
        id = int(id)
        outpage1, pagetitle1 = cipweb(field, id, IRdet)

#################################

"""
cd /astro/clash1/ftp/outgoing/macs0717/HST/catalogs/mosaicdrizzle_image_pipeline/IR_detection/PhotoZ/

python $BPZPATH/plots/webpage.py photometry

1728

-OUTPUT 1728.html

-TITLE "MACS0717 IR detection object #1728"

-COLOR
/astro/clash1/ftp/outgoing/macs0717/HST/color_images/mosaicdrizzle_image_pipeline/macs0717.png
/astro/clash1/ftp/outgoing/macs0717/HST/color_images/mosaicdrizzle_image_pipeline/macs0717_acs.png
/astro/clash1/ftp/outgoing/macs0717/HST/color_images/mosaicdrizzle_image_pipeline/macs0717_ir.png
/astro/clash1/ftp/outgoing/macs0717/HST/color_images/mosaicdrizzle_image_pipeline/macs0717_irbright.png
/astro/clash1/ftp/outgoing/macs0717/HST/color_images/mosaicdrizzle_image_pipeline/macs0717_uvis.png
../labeled_images/macs0717_segm_id.png
../labeled_images/macs0717_segm.png
-SEGM /astro/clash1/ftp/outgoing/macs0717/HST/catalogs/mosaicdrizzle_image_pipeline/IR_detection/SExtractor/detectionImage_SEGM.fits
-ZCLUS 0.548
-COLORNAMES ACS+IR ACS IR IRBRIGHT UVIS SEGMID SEGM
-ZMAX 7

http://archive.stsci.edu/pub/clash/outgoing/macs0717/HST/catalogs/mosaicdrizzle_image_pipeline/IR_detection/PhotoZ/html/1728.html
"""
