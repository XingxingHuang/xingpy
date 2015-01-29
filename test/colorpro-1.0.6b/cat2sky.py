from coetools import *
import os

def cat2sky(infits, incat, options='', silent=0):
    infits = capfile(infits, 'fits')
    inroot = decapfile(incat, 'cat')
    
    cat = loadcat(incat)
    cat.labels = string.split('x y')
    cat.save('temp.xy')

    # cmd = 'xy2sky -d -n 8 %s @temp.xy > %s.wcs' % (infits, inroot)
    if not silent:
        cmd = 'xy2sky %s %s @temp.xy > %s.wcs' % (options, infits, inroot)
    print cmd
    os.system(cmd)


if __name__ == '__main__':
    infits = sys.argv[1]
    incat = sys.argv[2]
    options = string.join(sys.argv[3:], ' ')
    #print options

    cat2sky(infits, incat, options)

