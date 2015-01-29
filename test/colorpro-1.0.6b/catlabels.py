from coeio import loadfile
import os
import string

colorpropath = os.environ['COLORPRO']
if colorpropath[:-1] <> '/':
    colorpropath += '/'

formats = {}
descriptions = {}

txt = loadfile(colorpropath+'catlabels.txt', silent=1)
for line in txt:
    label, format, description = string.split(line, "'")
    label = string.strip(label)
    description = string.strip(description)
    
    formats[label] = format
    descriptions[label] = description

