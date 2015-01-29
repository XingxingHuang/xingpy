## Automatically adapted for numpy Jun 08, 2006 by 

# NOW ALLOWING BACK_SIZE & BACK_FILTERSIZE INTO .sex FILE
# -- STILL NEEDED WHEN I'M USING A WEIGHT MAP, WHICH ONLY PROVIDES RELATIVE RMS

from sexsegtools import loadfile, capfile
import string, sys, os
import popen2  # Read command line output

sexsegpath = os.environ['SEXSEG']
if sexsegpath[-1] <> '/':
    sexsegpath += '/'

defaultsexfile = sexsegpath + 'sexseg.sex'
defaultbacksexfile = sexsegpath + 'back.sex'

def sexsegconfig(sexsegfile, root, segmsexoutfits, backsexfile='', rmsfits='', backsubfits=''):
    """INPUT .sexseg
       OUTPUT .sex, .param
       RETURNS NAME OF .sex"""
    if not sexsegfile:
        sexfile = defaultsexfile
        print "NOT CREATING BACKGROUND IMAGES.  THIS COULD BE A PROBLEM!!"
    elif sexsegfile[-4:] == '.sex':
        sexfile = sexsegfile
        print "NOT CREATING BACKGROUND IMAGES. - THIS COULD BE A PROBLEM!!"
    else:
        sexfile = root + '.sex'
        paramfile = root + '.param'
        defaulttext = loadfile(defaultsexfile, keepnewlines=1)
        for iline in range(len(defaulttext)):
            defaulttext[iline] = string.replace(defaulttext[iline], '$SEXSEG', sexsegpath[:-1])
        
        sexsegtext = loadfile(capfile(sexsegfile, '.sexseg'), keepnewlines=1)

        iline = 0
        line = sexsegtext[iline]
        configdict = {}
        backconfigdict = {}

        # ----- CONFIGURATION -----
        if segmsexoutfits:
            checkimagetype = 'SEGMENTATION'
            checkimagename = segmsexoutfits
        else:
            checkimagetype = 'NONE'
        checkimagetypecomment = '"NONE", "BACKGROUND"'
        checkimagenamecomment = 'CHECK IMAGE'

        while len(line) > 1:
            if line[0] <> '#':
                key = string.split(line)[0]
                if key[:10] == 'CHECKIMAGE':
                    # EXTRACT VALUE
                    word = string.split(line)[1:]
                    word = string.split(word, '#')[0]
                    word = string.strip(word)
                    if key[-4:] == 'TYPE':
                        checkimagetype += ', ' + word
                    else:  # 'NAME'
                        checkimagename += ', ' + word
                else:
                    configdict[key] = line
                    if key == 'PHOT_APERTURES':
                        apers = string.split(line)[1]
                        apers = string.split(apers, ',')
                        apers = len(apers)  # RETURNS NUMBER OF APERS
                    if key == 'PARAMETERS_NAME':
                        paramfile = string.split(line)[1]
                if key[:5] == 'BACK_':
                    backconfigdict[key] = line
                if key in ['SATUR_LEVEL', 'GAIN']:
                    backconfigdict[key] = line
            iline += 1
            try:
                line = sexsegtext[iline]
            except:
                break

        if segmsexoutfits:
            configdict['CHECKIMAGE_TYPE'] = '%s\t%s\t# %s\n' % ('CHECKIMAGE_TYPE', checkimagetype, checkimagetypecomment)
            configdict['CHECKIMAGE_NAME'] = '%s\t%s\t# %s\n' % ('CHECKIMAGE_NAME', checkimagename, checkimagenamecomment)

        # ----- PARAMETERS -----
        paramsexist = 0
        while not paramsexist:
            iline += 1
            try:
                line = sexsegtext[iline]
                if len(line) > 1:
                    if line[0] <> '#':
                        paramsexist = 1
            except:
                break

        flagon = 0
        if paramsexist:
            paramout = open(paramfile, 'w')
            while 1:
                if line[0] <> '#':
                    param = line
                    if param[0] == '*':
                        param = param[1:]
                    i = string.find(param, '(')
                    if i > -1:  # GET RID OF ANYTHING IN PARENTHESES -- ABOUT TO DO THIS AUTOMATICALLY!
                        param = param[i-1:]
                    if param[-5:-1] == 'APER':  # ADD NUMBER OF APERS AUTOMATICALLY!
                        param = param[:-1] + '(%d)'%apers + '\n'
                    if param[:12] == 'IMAFLAGS_ISO':  # ADD NUMBER OF APERS AUTOMATICALLY!
                        flagon = 1
                    paramout.write(param)
                iline += 1
                try:
                    line = sexsegtext[iline]
                except:
                    break
            paramout.close()
        
        # .sex
        sexout = open(sexfile, 'w')
        for line in defaulttext:
            key = ''
            if len(line) > 1:
                key = string.split(line)[0]
            if flagon:
                if len(key) > 4:
                    if key[:5] == '#FLAG':
                        key = key[1:]  # REMOVE LEADING '#'
                        line = line[1:]
            if key:
                if key[0] == '#':
                    key = ''
            if key in configdict.keys():
                sexout.write(configdict[key])
            elif key == 'PARAMETERS_NAME':
                sexout.write('PARAMETERS_NAME\t%s\t# name of the file containing catalog contents\n' % paramfile)
            else:
                sexout.write(line)
        sexout.close()
    
        # back.sex
        if backsexfile:
            checkimagename = ''
            checkimagetype = ''
            if rmsfits:
                checkimagename = rmsfits
                checkimagetype = 'BACKGROUND_RMS'
                if backsubfits:
                    checkimagename += ', '
                    checkimagetype += ', '
            if backsubfits:
                checkimagename += backsubfits
                checkimagetype += '-BACKGROUND'
            backconfigdict['CHECKIMAGE_NAME'] = '%s\t%s\t# %s' % ('CHECKIMAGE_NAME', checkimagename, checkimagenamecomment)
            backconfigdict['CHECKIMAGE_TYPE'] = '%s\t%s\t# %s' % ('CHECKIMAGE_TYPE', checkimagetype, checkimagetypecomment)
            
            defaulttext = loadfile(defaultbacksexfile, keepnewlines=1)
            for iline in range(len(defaulttext)):
                defaulttext[iline] = string.replace(defaulttext[iline], '$SEXSEG', sexsegpath[:-1])
            
            sexout = open(backsexfile, 'w')
            for line in defaulttext:
                key = ''
                if len(line) > 1:
                    key = string.split(line)[0]
                if key in backconfigdict.keys():
                    sexout.write(backconfigdict[key])
                else:
                    sexout.write(line)
            sexout.close()
    
    return sexfile

if __name__ == '__main__':
    sexsegconfig(sys.argv[1], sys.argv[2], sys.argv[3])
