# prunecols <infile> <col1> <col2> ... <coln> <outfile>

## def prunecols(infile, cols, outfile, separator=" "):
##     """TAKES CERTAIN COLUMNS FROM infile AND OUTPUTS THEM TO OUTFILE
##     COLUMN NUMBERING STARTS AT 1!"""

import sys, string
#from ksbtools import stringsplitatoi
from coetools import stringsplitatoi

def prunecols(infile, cols, outfile, separator=""):
    """TAKES CERTAIN COLUMNS FROM infile AND OUTPUTS THEM TO OUTFILE
    COLUMN NUMBERING STARTS AT 1!
    ALSO AVAILABLE AS STANDALONE PROGRAM prunecols.py"""
    fin = open(infile, 'r')
    sin = fin.readlines()
    fin.close()

    outsep = separator
    if not outsep:
	outsep = ' '
    fout = open(outfile, 'w')
    for line in sin:
	line = string.strip(line)
	if line:
	    if line[0] <> '#':
		if separator:
		    words = string.split(line, separator)
		else:
		    words = string.split(line)
		for col in cols:
		    try:
			fout.write(words[col-1] + outsep)
		    except:
			break
		fout.write("\n")
    fout.close()

if __name__ == '__main__':
    infile = sys.argv[1]
    cols = sys.argv[2:-1]
    for i in range(len(cols)):
        cols[i] = string.atoi(cols[i])
    print cols
    outfile = sys.argv[-1]
    separator = ""
    prunecols(infile, cols, outfile, separator)


