############################################
# CLASH Image Pipeline
# Photometry + Photo-z catalog generator
# -Dan Coe
############################################

from coeio import *

def run(cmd, pr=1):
    if pr:
        print cmd
    os.system(cmd)


def fieldlengthen(field):
    if field[0] == 'a':
        if field[:5] <> 'abell':
            field = 'abell_' + field[1:]
    return field


field = fieldlengthen(sys.argv[1])
args = string.join(sys.argv[2:])


# COLOR IMAGES
#run('python $CIPPHOT/makecolorimages.py %s' % field)
run('python $CIPPHOT/makecolorimages.py %s %s' % (field, args))

# CATALOGS, LABELED COLOR IMAGES, OBJECT WEBPAGES
run('python $CIPPHOT/cipcatwrap.py %s %s'     % (field, args))
run('python $CIPPHOT/cipcatwrap.py %s -IR %s' % (field, args))
