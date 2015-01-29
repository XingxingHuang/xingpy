## Automatically adapted for numpy Jun 08, 2006 by 

from sexsegtools import loadfile, capfile
import string, sys

def sexsegconfiganalthresh(sexfile, rms, sexsegfile=''):
    """FIX ANALYSIS_THRESH IN .sex FILE
       WAS SET TO sigma, CHANGE TO absolute
       RETURN ANALYSIS_MINAREA (FROM sexsegfile)"""

    sexfile = capfile(sexfile, '.sex')
    sextext = loadfile(sexfile, keepnewlines=1)
    sexout = open(sexfile, 'w')

    print 'sexsegconfiganalthresh.py -> ', sexfile
    if type(rms) == str:
        rms = string.atof(rms)
    for line in sextext:
        if line[:15] == 'ANALYSIS_THRESH':
            words = string.split(line)
            sigmas = string.atof(words[1])
            if sigmas == 5e-7:
                print 'ANALYSIS_THRESH = 5e-7 (DEFAULT)'
            else:
                if not sigmas:
                    thresh = 5e-7
                    print "ANALYSIS_THRESH = 5e-7 (CAN'T QUITE DO ZERO, LIKE YOU REQUESTED)"
                    words[1] = '5e-7'
                else:
                    thresh = sigmas * rms
                    print 'ANALYSIS_THRESH = %.5f = %.2f * %.5f' % (thresh, sigmas, rms)
                    print '                = %g = %g * %.5f' % (thresh, sigmas, rms)
                    #print thresh
                    if not thresh:
                        thresh = 5e-7
                        print "ANALYSIS_THRESH = 5e-7 (CAN'T BE ZERO!)"
                        words[1] = '5e-7'
                    else:
                        words[1] = '%.4g' % thresh
                words[2] = string.join(words[2:], ' ')
                words = words[:3]
                #line = string.join(words, '\t') + '\n'
                line = '%s\t%s\t\t%s\n' % tuple(words)
            
        #print line
        sexout.write(line)

    sexout.close()


if __name__ == '__main__':
    sexsegconfiganalthresh(sys.argv[1], string.atof(sys.argv[2]))
