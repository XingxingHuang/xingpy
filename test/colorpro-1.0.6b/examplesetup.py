# NEED TO RE-RUN THE COLORPRO EXAMPLE?
# FIRST MAKE A FRESH DIRECTORY WITH LINKS TO THE EXAMPLE INPUT FILES:
#
# (~/colorpro-1.0.5/)% python examplesetup.py test2
# (~/colorpro-1.0.5/)% cd test2
# (~/colorpro-1.0.5/)% colorpro

from coetools import *
from os.path import join

colorpropath = os.environ['COLORPRO']
exampledir = join(colorpropath, 'example')

newdir = sys.argv[1]
#newdir = 'test2'
if os.path.exists(newdir):
    print newdir, 'EXISTS'
    sys.exit(1)
else:
    os.mkdir(newdir)

txt = loadfile('example.txt')
for file in txt:
    os.symlink(join(exampledir, file), join(newdir, file))

