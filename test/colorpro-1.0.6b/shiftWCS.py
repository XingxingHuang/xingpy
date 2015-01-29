## Automatically adapted for numpy Jun 08, 2006 by 

"""
    shiftWCS.py SHIFTS A WCS HEADER BY [dx, dy]
    USAGE: python shiftWCS.py <infits> <outfits> [-dx <val> -dy <val> -head OR -cuthead]
    INPUT: FITS IMAGE
    OUTPUT: FITS IMAGE w/ WCS INFO SHIFTED BY [dx, dy]  (DATA ARRAY IS NOT SHIFTED)
    * IF -head OPTION IS SET, OUTPUT WILL BE A SMALL TEXT FILE WITH JUST THE WCS HEADER INFO (ENOUGH TO FOOL wregister, sky2xy...)
    -cuthead OPTION OUTPUTS THE WCS HEADER INFO WITH NO SHIFT

    SHIFT IS APPLIED TO WCS REFERENCE PIXEL, i.e.:
       A GIVEN OBJECT LIES AT A GIVEN (RA, DEC)
       THIS TRANSLATES TO AN INCORRECT POSITION [xin, yin], BASED ON THE INPUT WCS HEADER
       THE CORRECT POSITION OF THE OBJECT IS [xout, yout]
       [dx, dy] = [xout - xin, yout - yin]
    BY DEFAULT, [dx, dy] = [-59.5317, -36.0372], CORRECTING THE OFFSET IN ACS WCS HEADERS
"""


import sys, string
from coetools import capfile, str2num, striskey, params_cl


def shiftWCS(infits, outfits, dx=0, dy=0, fullfits=1):
    infits = capfile(infits, 'fits')
    outfits = capfile(outfits, 'fits')

    fin = open(infits,'r')
    fout = open(outfits,'w')

    key = ''
    while key <> 'END':
        line = fin.read(80)

        key = string.strip(line[:8])

        # from http://tdc-www.harvard.edu/software/wcstools/wcstools.wcs.html#FITS
        WCSkeys = ['SIMPLE', 'NAXIS', 'NAXIS1', 'NAXIS2', 'CRPIX1', 'CRPIX2', 'CRVAL1', 'CRVAL2', 'CTYPE1', 'CTYPE2', 'CD1_1', 'CD1_2', 'CD2_1', 'CD2_2', 'LTV1', 'LTV2', 'LTM1_1', 'LTM2_2', 'LTM1_2', 'LTM2_1', 'CDELT1', 'CDELT2', 'CROTA1', 'CROTA2', 'END']

        if key in WCSkeys or fullfits:
            if key[:-1] == 'CRPIX':
                eqpos = string.find(line, '=')
                slpos = string.find(line, '/')
                if slpos == -1:
                    slpos = 80
                valstr = line[eqpos+1 : slpos]
                val = string.atof(valstr)
                if key == 'CRPIX1':
                    val += dx
                else:  # 'CRPIX2'
                    val += dy
                newvalstr = '%%%ds' % (len(valstr)-1) % ('%.4f' % val) + ' '
                line = line[:eqpos+1] + newvalstr + line[slpos:]
            fout.write(line)

    if fullfits:
        fout.write(fin.read())

    fout.close()
    

################################################################################
# BEGIN PROGRAM

if __name__ == '__main__':
    infits  = sys.argv[1]
    outfits = sys.argv[2]
    params = params_cl()
    dx = string.atof(params.get('dx', '-59.5317'))
    dy = string.atof(params.get('dy', '-36.0372'))
    fullfits = 'head' not in params.keys()
    if 'cuthead' in params.keys():
        fullfits = 0
        dx = dy = 0
    shiftWCS(infits, outfits, dx, dy, fullfits)
