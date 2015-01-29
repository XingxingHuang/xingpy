## Automatically adapted for numpy Jun 08, 2006 by 

# ~/home/colorpro/test/3/sexsegcat.py
# ~/home/colorpro/test/2/sexsegcat.py -- CALLED BY colorpro.py
# ~/home/colorpro/test/2/photcat.py
# ~/Tonetti/colorpro/cat.py
# ~/UDF/VLT/cat.py -- TRYING TO MAKE THIS PROGRAM MORE GENERIC :)
#
# ~/UDF/cat3.py
# ~/UDF/laptop/jhdiff5.py -- UNCERTAINTIES: SMOOTH NEIGHBORS
# ~/UDF/cor7.py

from coetools import *
#from bpz_tools import sex2bpzmags
from census import census

def sexsegcat(filts, detfilt, mapped2Afilts, blurryfilts, zpdict, extdict, outfile):
    # -> FILE NAMES
    # NOTE THAT 'detfilt' HERE IS REALLY photframe FROM colorpro.py
    #   (NORMALLY THESE WILL BE THE SAME, HENCE THE CONFUSION)
    # THAT IS, THE REFERENCE FILTER IN THE "A" FRAME
    #  THAT GETS DEGRADED TO MATCH THE SEEING OF ALL OTHER IMAGES
##     if detfilt == 'det':
##         detfilt2 = 'd'
##     else:
##         detfilt2 = detfilt
    detfilt2 = detfilt

    # LOAD detauto, iso, aper
    detcat = loadcat(detfilt+'_sexseg.cat')
    detauto, deterrauto = sex2bpzmags(detcat.fluxauto, detcat.fluxerrauto, zpdict[detfilt])
    detiso,  deterriso  = sex2bpzmags(detcat.fluxiso,  detcat.fluxerriso,  zpdict[detfilt])
    detaper, deterraper = sex2bpzmags(detcat.fluxaper, detcat.fluxerraper, zpdict[detfilt])

    if not os.path.exists('census.dat'):
        census()  # DEFAULT IS segm.fits -> census.dat
    cens = loadcat('census.dat')
    cens = cens.takeids(detcat.id)  # USUALLY UNECESSARY

    RA = []
    if os.path.exists(detfilt+'.wcs'):
        RA, Dec = loaddata(detfilt+'.wcs+')

    format = {}

    outcat = VarsClass()
    outcat.add('id', detcat.id)
    if RA <> []:
        outcat.add('RA', RA)
        outcat.add('Dec', Dec)
    outcat.add('x', detcat.x)
    outcat.add('y', detcat.y)
    outcat.add('area', cens.area)
    outcat.add(detfilt+'auto', detauto)
    outcat.add(detfilt+'iso', detiso)
    outcat.updatedata()
    n = outcat.len()
    
    if RA <> []:
        labels2 = string.split('id RA Dec x y area')
    else:
        labels2 = string.split('id x y area')

    format['id'] = '%5d'
    format['RA'] = '%12.8f'
    format['Dec'] = '% 12.8f'
    format['x'] = '%9.3f'
    format['y'] = '%9.3f'
    format['area'] = '%6d'
    format[detfilt+'auto'] = '% 8.4f'
    format[detfilt+'iso']  = '% 8.4f'
    
    # FOR LESS FORTUNATE NEIGHBORS
    if os.path.exists('isocors.cat'):
        corcat = loadcat('isocors.cat')
        xarea = corcat.area
    else:
        detautocat = outcat.subset(between(-99, detauto, 99))
        xarea = sort(detautocat.area)
        iii = arange(len(xarea))
        ngap = detautocat.len() / 10.
        if ngap > 100:
            ngap = 100
        else:
            ngap = int(ngap)
        interval = logical_not((iii + ngap/2) % ngap)
        # interval = logical_not((iii + 50) % 100)  # = 1 at 50, 150, 250...
        # ngap = 100
        # ngap = 10
        # interval = logical_not((iii + 5) % 10)  # = 1 at 5, 15, 25...
        interval[0] = 1
        interval[-1] = 1
        # print interval
        xarea = compress(interval, xarea)
        xarea = norep(xarea)
        corcat = VarsClass()
        corcat.add('area', xarea)
        # print corcat.area
        
    #
    for filt in filts:
        # blurry = filt in ['J', 'K']
        blurry = filt in blurryfilts
        inAframe = filt not in mapped2Afilts
        #print filt, blurry, inAframe

        # -> VARIABLE NAMES
        if blurry:
            filtb = filt
        else:
            filtb = detfilt
        
        # -> FILE NAMES
        if inAframe:
            filt2 = filt
        else:
            filt2 = filt + '2A'
        
        # LOAD SExSeg CATALOG: FLUX -> MAG
        cat = loadcat(filt2+'_sexseg.cat')
        mag, magerr = sex2bpzmags(cat.fluxiso, cat.fluxerriso, zpdict[filt])

        # detmag FROM det OR dto...
        if not blurry:
            detmag, detmagerr = detiso, deterriso
        else:
            dtocat = loadcat(detfilt2+'to'+filt2+'_sexseg.cat')
            if detcat.len() <> dtocat.len():
                print 'CATALOGS HAVE DIFFERENT LENGTHS IN sexsegcat.py'
                print detcat.len(), detfilt+'_sexseg.cat'
                print dtocat.len(), detfilt2+'to'+filt2+'_sexseg.cat'
                sys.exit()
            detmag, detmagerr = sex2bpzmags(dtocat.fluxiso, dtocat.fluxerriso, zpdict[detfilt])

        if detauto.shape <> detmag.shape:
            print 'detauto & detmag DIFFERENT LENGTHS IN sexsegcat.py'
            print detauto.shape, detmag.shape
            sys.exit()
        #a = between(-99, detauto, 99)
        #b = between(-99, detmag, 99)
        #print type(a), type(b)
        #pause()
        detgood = logical_and(between(-99, detauto, 99), between(-99, detmag, 99))
        maggood = between(-99, mag, 99)
        undet = greater(mag, 98)
        
        # ADD TO CATALOG (BUT MAGS WILL BE MODIFIED BELOW)
        outcat.add(filt, mag)
        outcat.add('d'+filt, magerr)
        outcat.add('d'+filt+'b', magerr)
        outcat.add('dto'+filt, detmag)
        # outcat.add(filtb+'cor', isocor)
        # outcat.add('d'+filt+'cor', 0)
        labels2.append(filt)
        labels2.append('d'+filt)
        format[filt] = '% 8.4f'
        format['d'+filt] = '%7.4f'
        format['d'+filt+'b'] = '%7.4f'
        format['dto'+filt] = '% 8.4f'
        
        isocor = None
        
        # DERIVE ISOPHOTAL CORRECTIONS
        # DERIVE TABLE OF SMOOTH CORRECTIONS FOR NEIGHBORS
        # BUT ONLY CALCULATE detcor ONCE (FOR NON-BLURRY FILTERS)
        # if blurry or ('detcor' not in corcat.labels):
        if filtb+'cor' not in corcat.labels:
            print 'NEIGHBORS...'
            isocor = where(detgood, detauto - detmag, 0)
            area = compress(detgood, cens.area)
            cor = compress(detgood, isocor)
            n = len(area)
            neighbors = len(area) / 10.
            neighbors = min([neighbors, 251])
            neighbors = max([9, neighbors])
            neighbors = int(neighbors)
            if even(neighbors):
                neighbors += 1
            minneighbors = neighbors / 2 + 1
        
            # points(log10(area), cor)
            corlo, cormed, corhi = smoothrogers1er(xarea, area, cor, neighbors, minneighbors)
            # corlo, cormed, corhi = smoothrogers1er(xarea, area, cor, 251, 101)
            # corlo, cormed, corhi = smoothrogers1er(corcat.area, area, cor, 21, 11)
            # corlo, cormed, corhi = smoothrogers1er(corcat.area, area, cor, 3, 3)
            corrms = (corhi - corlo) / 2.
            corcat.add(filtb+'cor', cormed)
            corcat.add('d'+filtb+'cor', corrms)
            corcat.save('isocors.cat')

        if filtb+'cor' not in outcat.labels:
            # (isocor now measured regardless of whether there's a detection in this filter)
            if isocor == None:
                isocor = where(detgood, detauto - detmag, 0)
            outcat.add(filtb+'cor', isocor)
            format[filtb+'cor'] = '% 8.4f'

            # DERIVE ISO-CORRECTIONS FOR ALL OBJECTS LACKING IT
            # (THOSE WITHOUT BOTH detauto & detmag, WHERE detmag = detiso OR dtojiso, FOR EXAMPLE
            goodcat = outcat.subset(logical_not(detgood))
            cor = interpn(goodcat.area, corcat.area, corcat.get(filtb+'cor'))
            outcat.putids(filtb+'cor', goodcat.id, cor)
            
            # DERIVE ISO-CORRECTION UNCERTAINTIES FOR ALL OBJECTS
            # (ONLY NEEDED FOR DETECTIONS, BUT THESE VARY FROM FILTER TO FILTER)
            dcor = interpn(outcat.area, corcat.area, corcat.get('d'+filtb+'cor'))
            outcat.add('d'+filtb+'cor', dcor)
            format['d'+filtb+'cor'] = '%7.4f'
    
            # ISO-CORRECT MAGNITUDES (& EXTINCTION CORRECTIONS)
            # (CORRECTIONS HAVE ALREADY BEEN DERIVED FOR ALL OBJECTS,
            #  BASED ON NEIGHBORS, WHERE NECESSARY)
            ext = extdict.get(filt, 0)
            isocor = outcat.get(filtb+'cor')  # GET THOSE THAT CHANGED
            mag = where(maggood, mag + ext + isocor, mag)
            # NOW DO THE SAME FOR MAG UNCERTAINTIES OF NON-DETECTIONS
            magerr = where(undet, magerr + ext + isocor, magerr)

            if filt == detfilt:
                magerr = where(maggood, deterrauto, magerr)
            else:
                # NOW ADD THE ISO-CORRECTION UNCERTAINTIES TO THE MAG UNCERTAINTIES (IN QUADRATURE)
                magerr2 = hypot(magerr, outcat.get('d'+filtb+'cor'))
                magerr = where(maggood, magerr2, magerr)
    
        outcat.set(filt, mag)
        outcat.set('d'+filt, magerr)


    # SAVE
    outcat.save('sexseg.cat', format=format)
    #outcat.save(string.join(filts, '')+'.cat', labels=labels2)
    outcat.save(outfile, labels=labels2, format=format)
    if not os.path.exists('isocors.cat'):
        corcat.save('isocors.cat')
