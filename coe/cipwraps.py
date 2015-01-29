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


field = sys.argv[1]
args = string.join(sys.argv[2:])

run('python $CIPPHOT/cipwrap.py %s %s'     % (field, args))
run('python $CIPPHOT/cipwrap.py %s -IR %s' % (field, args))
