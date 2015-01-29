pro cleanup,state
names=tag_names(*state)
for i=0,n_tags(*state)-1 do begin
   if names(i) ne 'IGALFIT' then begin
      case size((*state).(i),/tname) of
         'POINTER': ptr_free,(*state).(i)
         'OBJREF': obj_destroy,(*state).(i)
         else:
      endcase
   endif
endfor
ptr_free,state
end

pro mkconv_clean,wid
  widget_control,wid,get_uval=state
  cleanup,state
end


pro writeconv,event
widget_control,event.top,get_uvalue=state

openw,lun,(*state).confile,/get_lun,error=error
if error ne 0 then begin
   writefile_error,'Convolution Filter'
   return
endif
func=widget_info((*state).wfunc,/combobox_gettext)
widget_control,(*state).wscale,get_value=scale & scale=scale(0)
widget_control,(*state).wxsize,get_value=xsize & xsize=xsize(0)
widget_control,(*state).wysize,get_value=ysize & ysize=ysize(0)

sz=size(*(*state).conv,/dim)
nx=sz(0) & ny=sz(1)


printf,lun,'# Convolution file written by XXXXX'
printf,lun,'# '+func+' with scale='+scale+' and size='+xsize+','+ysize
printf,lun,'# made on '+systime()
printf,lun,'CONV NORM'
for i=0,nx-1 do begin
   d=(*(*state).conv)(i,*)
   printf,lun,strjoin(strcompress(string(d,f='(F8.5)'),/rem),' ')
endfor
close,lun & free_lun,lun


end

function rdconv,file

if not file_exist(file) then begin
   t=dialog_message('This file does not exist!',/error,/center)
   return,-1b
endif

print,'still working on this!'

end


function create_conv,state
widget_control,(*state).wscale,get_value=scale & scale=scale(0)
if isnumber(scale) eq 0 then return,type_error('scale')
scale=float(scale)

widget_control,(*state).wxsize,get_value=xsize & xsize=xsize(0)
if isnumber(xsize) ne 1 then return,type_error('X-size')
xsize=fix(xsize)

widget_control,(*state).wysize,get_value=ysize & ysize=ysize(0)
if isnumber(xsize) ne 1 then return,type_error('Y-size')
ysize=fix(ysize)


xim=(findgen(xsize)-(xsize-1)/2.) # replicate(1.,ysize)
yim=replicate(1.,xsize) # (findgen(ysize)-(ysize-1)/2.)
rim2=xim^2+yim^2
case widget_info((*state).wfunc,/combobox_gettext) of 
   'Gaussian':    conv=exp(-0.5*rim2/scale^2)
   'Mexican Hat': conv=(1.0-(rim2/scale^2))*exp(-0.5*rim2/scale^2)
   'Top Hat':     conv=(rim2 le scale^2)*1.
   'Delta':       conv=(rim2 eq min(rim2))*1.
   'User': begin
      t=dialog_message('This is not yet implemented!',/error,/center)
      conv=(rim2 eq min(rim2))*1.
   end
endcase

(*state).conv=ptr_new(conv/total(conv),/no_copy)  ;normalize

return,1b
end

pro mkconv_event,event
  widget_control,event.id,get_uvalue=uval
case uval of
   'CREATE': begin
      widget_control,event.top,get_uval=state      
      if create_conv(state) then begin
         geom=widget_info((*state).wdraw,/geom)
         tvscl,congrid((*(*state).conv),geom.xsize,geom.ysize)
      endif
   end
   'FUNCTIONS':begin
      widget_control,event.top,get_uval=state
      func=widget_info((*state).wfunc,/combobox_gettext)
      widget_control,(*state).wfofr,sens=(func eq 'User')
   end
   'LOAD': begin
      widget_control,event.top,get_uval=state
      t=dialog_pickfile(filter=['*conv'],/must_exist,/fix_filt)
      if t(0) ne '' then begin
         (*state).confile=t(0)
         (*(*state).conv)=rdconv((*state).confile)         
         geom=widget_info((*state).wdraw,/geom)
         tvscl,congrid((*(*state).conv),geom.xsize,geom.ysize)
      endif
   end
   'SAVE':  writeconv,event      
   'USER': print,'Not yet implemented'
   'CLOSE': widget_control,event.top,/destroy
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='sexconv'
   else: 
endcase


end

pro mkconv,CONFILE=confile,GROUP=group

if not keyword_set(CONFILE) then confile='default.conv'

base=widget_base(title='Make Convolution Filter',/column,mbar=mbar,group=group)
filemenu=widget_button(mbar,value='File',/menu)
ld=widget_button(filemenu,value='Load',uvalue='LOAD')
sv=widget_button(filemenu,value='Save',uvalue='SAVE')
close=widget_button(filemenu,value='Close',uvalue='CLOSE',/sep)
helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uvalue='HELP')

top=widget_base(base,/row)
lhs=widget_base(top,/col,/frame)
l=widget_label(lhs,value='Settings:')
r1=widget_base(lhs,/row)
l=widget_label(r1,value='Func:')
wfunc=widget_combobox(r1,value=['Gaussian','Mexican Hat','Top Hat','User'],$
                      xsize=102,uval='FUNCTIONS')

r5=widget_base(lhs,/row)
l=widget_label(r5,value='f(r)=')
wfofr=widget_text(r5,value='',sens=0b,xsize=14,/editable,uvalue='USER')

r2=widget_base(lhs,/row)
l=widget_label(r2,value='Scale')
wscale=widget_text(r2,value='',xsize=14,/editable,uvalue='SCALE')

r3=widget_base(lhs,/row)
l=widget_label(r3,value='Size ')
wxsize=widget_text(r3,value='',xsize=5,/editable,uvalue='XSIZE')
wysize=widget_text(r3,value='',xsize=5,/editable,uvalue='YSIZE')

r4=widget_base(lhs,/row)
t=widget_button(r4,value='Create',uvalue='CREATE')


rhs=widget_base(top,/col,/frame)
wdraw=widget_draw(rhs,xsize=210,ysize=210,uvalue='DRAW')


state={wfunc:wfunc,$
       wfofr:wfofr,$
       wscale:wscale,$
       wxsize:wxsize,$
       wysize:wysize,$
       wdraw:wdraw,$
       confile:confile,$
       conv:ptr_new()}

if keyword_set(GROUP) then place_widget,base,group

widget_control,base,set_uvalue=ptr_new(state,/no_copy)
widget_control,base,/realize

xmanager,'mkconv',base,cleanup='mkconv_clean'


end


pro sexparam_clean,wid
  ;clean up the sexparam GUI
  widget_control,wid,get_uval=state
  cleanup,state
end
pro sexparam_write,state
;write the sextractor parameters file

;get the buttons
buttons=(*state).buttons
nbut=n_tags(buttons)

;open a file
openw,lun,(*state).file,/get_lun,error=error
if error ne 0 then begin
   t=writefile_error('SEx Paramters')
   return
endif


printf,lun,'# SExtractor parameters file made by '+(*state).name+$
       ' on '+systime()
for i=0,nbut-1 do begin
   if widget_info(buttons.(i),/button_set) then begin
      ;if a button is set, get the UVAL. It contains the SEx keyword name(s).
      widget_control,buttons.(i),get_uvalue=val
      ;put all the UVALs in a file
      for j=0,n_elements(val)-1 do printf,lun,val(j)
   endif
endfor
close,lun & free_lun,lun   ;close the file
end


pro sexparam_event,event,GROUP=group
;event handler for the sexparam subGUI

widget_control,event.id,get_uvalue=uval
case uval(0) of
   'SAVE': begin
      widget_control,event.top,get_uvalue=state
      sexparam_write,state
   end
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='sexpars'
   'RESET': begin
      widget_control,event.top,get_uvalue=state
      buttons=(*state).buttons 
      for j=0,n_tags(buttons)-1 do widget_control,buttons.(j),set_button=0b     
      defaults=(*state).defaults
      for j=0,n_elements(defaults)-1 do widget_control,defaults(j),set_button=1b
   end

   'CLOSE': widget_control,event.top,/destroy
   else: break
endcase


end
pro sexparam,file,GROUP=group,NOGUI=nogui
;sextractor parameters subGUI


if size(file,/type) eq 0 then file='sex.param'  ;default file

base=widget_base(title='SExtractor Parameters',/row,mbar=mbar,$
                 group=group)

filemenu=widget_button(mbar,value='File',/menu)
ss=widget_button(filemenu,value='Save',uvalue='SAVE')
rr=widget_button(filemenu,value='Reset',uvalue='RESET')
cc=widget_button(filemenu,value='Close',uvalue='CLOSE',/sep)
helpmenu=widget_button(mbar,value='Help',/menu,/help)
hh=widget_button(helpmenu,value='Help',uvalue='HELP')

c1=widget_base(base,/col)

misc=widget_base(c1,/column,/frame)
l=widget_label(misc,val='MISCELLANEOUS:',/align_left)
miscrow=widget_base(misc,/row)
misc1=widget_base(miscrow,/col,/non)
number=widget_button(misc1,val='NUMBER',uval='NUMBER')
thresh=widget_button(misc1,val='THRESHOLD',uval='THRESHOLD')
fluxmax=widget_button(misc1,val='FLUX_MAX',uval='FLUX_MAX')
mumax=widget_button(misc1,val='MU_MAX',uval='MU_MAX')
misc2=widget_base(miscrow,/col,/non)
isoareaimage=widget_button(misc2,val='ISOAREA_IMAGE',uval='ISOAREA_IMAGE')
isoareaworld=widget_button(misc2,val='ISOAREA_WORLD',uval='ISOAREA_WORLD')
background=widget_button(misc2,val='BACKGROUND',uval='BACKGROUND')
xyminmax=widget_button(misc2,val='XYMINMAX',$
                       uval=['XMIN','YMIN','XMAX','YMAX']+'_IMAGE')
         
pos=widget_base(c1,/column,/frame)
l=widget_label(pos,val='POSITIONS:',/align_left)
posrow=widget_base(pos,/row)
pos1=widget_base(posrow,/col,/non)
xyimage=widget_button(pos1,val='XY_IMAGE',uval=['X','Y']+'_IMAGE')
xyworld=widget_button(pos1,val='XY_WORLD',uval=['X','Y']+'_WORLD')
pos2=widget_base(posrow,/col,/non)
rdsky=widget_button(pos2,val='RD_SKY',uval=['ALPHA','DELTA']+'_SKY')
rdj2000=widget_button(pos2,val='RD_J2000',uval=['ALPHA','DELTA']+'_J2000')
rdb1950=widget_button(pos2,val='RD_B1950',uval=['ALPHA','DELTA']+'_B1950')


c2=widget_base(base,/col)
mag=widget_base(c2,/column,/frame)
l=widget_label(mag,val='MAGNITUDES:',/align_left)
magrow=widget_base(mag,/row)
mag1=widget_base(magrow,/col,/non)
isomag=widget_button(mag1,val='ISO',uval='MAG'+['','ERR']+'_ISO')
isocormag=widget_button(mag1,val='ISOCOR',uval='MAG'+['','ERR']+'_ISOCOR')
apermag=widget_button(mag1,val='APER',uval='MAG'+['','ERR']+'_APER')
mag2=widget_base(magrow,/col,/non)
automag=widget_button(mag2,val='AUTO',uval='MAG'+['','ERR']+'_AUTO')
bestmag=widget_button(mag2,val='BEST',uval='MAG'+['','ERR']+'_BEST')
petromag=widget_button(mag2,val='PETRO',uval='MAG'+['','ERR']+'_PETRO')

flux=widget_base(c2,/column,/frame)
l=widget_label(flux,val='FLUXES:',/align_left)
fluxrow=widget_base(flux,/row)
flux1=widget_base(fluxrow,/col,/non)
isoflux=widget_button(flux1,val='ISO',uval='FLUX'+['','ERR']+'_ISO')
isocorflux=widget_button(flux1,val='ISOCOR',uval='FLUX'+['','ERR']+'_ISOCOR')
aperflux=widget_button(flux1,val='APER',uval='FLUX'+['','ERR']+'_APER')
flux2=widget_base(fluxrow,/col,/non)
autoflux=widget_button(flux2,val='AUTO',uval='FLUX'+['','ERR']+'_AUTO')
bestflux=widget_button(flux2,val='BEST',uval='FLUX'+['','ERR']+'_BEST')
petroflux=widget_button(flux2,val='PETRO',uval='FLUX'+['','ERR']+'_PETRO')

sizes=widget_base(c2,/column,/frame)
l=widget_label(sizes,val='SIZES:',/align_left)
sizesrow=widget_base(sizes,/row)
sizes1=widget_base(sizesrow,/col,/non)
fluxradius=widget_button(sizes1,val='FLUX_RADIUS',uval='FLUX_RADIUS')
kronradius=widget_button(sizes1,val='KRON_RADIUS',uval='KRON_RADIUS')
fwhmimage=widget_button(sizes1,val='FWHM_IMAGE',uval='FWHM_IMAGE')
fwhmworld=widget_button(sizes1,val='FWHM_WORLD',uval='FWHM_WORLD')


c3=widget_base(base,/col)
ell=widget_base(c3,/column,/frame)
l=widget_label(ell,val='ELLIPSE:',/align_left)
ellrow=widget_base(ell,/row)
ell1=widget_base(ellrow,/col,/non)
abimage=widget_button(ell1,val='AB_IMAGE',uval=['A','B']+'_IMAGE')
abworld=widget_button(ell1,val='AB_WORLD',uval=['A','B']+'_WORLD')
elong=widget_button(ell1,val='ELONGATION',uval='ELONGATION')
ellip=widget_button(ell1,val='ELLIPTICITY',uval='ELLIPTICITY')
ell2=widget_base(ellrow,/col,/non)
thetaimage=widget_button(ell2,val='THETA_IMAGE',uval='THETA_IMAGE')
thetaworld=widget_button(ell2,val='THETA_WORLD',uval='THETA_WORLD')
thetasky=widget_button(ell2,val='THETA_SKY',uval='THETA_SKY')
thetaj2000=widget_button(ell2,val='THETA_J2000',uval='THETA_J2000')
thetab1950=widget_button(ell2,val='THETA_B1950',uval='THETA_B1950')


mom=widget_base(c3,/column,/frame)
l=widget_label(mom,val='MOMENTS:',/align_left)
momrow=widget_base(mom,/row)
mom1=widget_base(momrow,/col,/non)
xy2image=widget_button(mom1,val='XY2_IMAGE',uval=['X2','Y2','XY']+'_IMAGE')
xy2world=widget_button(mom1,val='XY2_WORLD',uval=['X2','Y2','XY']+'_WORLD')
mom2=widget_base(momrow,/col,/non)
cxy2image=widget_button(mom2,val='CXY2_IMAGE',uva='C'+['XX','YY','XY']+'_IMAGE')
cxy2world=widget_button(mom2,val='CXY2_WORLD',uva='C'+['XX','YY','XY']+'_WORLD')


flags=widget_base(c3,/column,/frame)
l=widget_label(flags,val='FLAGS:',/align_left)
flagsrow=widget_base(flags,/row)
flags1=widget_base(flagsrow,/col,/non)
flags=widget_button(flags1,val='FLAGS',uval='FLAGS')
imaflags=widget_button(flags1,val='IMAFLAGS_ISO',uval='IMAFLAGS_ISO')
nimaflags=widget_button(flags1,val='NIMAFLAGS_ISO',uvalu='NIMAFLAGS_ISO')

;set which buttons we have
buttons={number:number,thresh:thresh,fluxmax:fluxmax,mumax:mumax,$
         isoareaimage:isoareaimage,isoareaworld:isoareaworld,$
         background:background,xyminmax:xyminmax,$
         xyimage:xyimage,xyworld:xyworld,rdsky:rdsky,rdj2000:rdj2000,$
         rdb1950:rdb1950,isomag:isomag,isocormag:isocormag,apermag:apermag,$
         automag:automag,bestmag:bestmag,petromag:petromag,$
         isoflux:isoflux,isocorflux:isocorflux,aperflux:aperflux,$
         autoflux:autoflux,bestflux:bestflux,petroflux:petroflux,$
         fluxradius:fluxradius,kronradius:kronradius,fwhmimage:fwhmimage,$
         fwhmworld:fwhmworld,abimage:abimage,abworld:abworld,elong:elong,$
         ellip:ellip,thetaimage:thetaimage,thetaworld:thetaworld,$
         thetasky:thetasky,thetaj2000:thetaj2000,thetab1950:thetab1950,$
         xy2image:xy2image,xy2world:xy2world,cxy2image:cxy2image,$
         cxy2world:cxy2world,flags:flags,imaflags:imaflags,$
         nimaflags:nimaflags}


;Set Default parameters:
defaults=[number,xyimage,automag,abimage,flags,thetaimage,isoareaimage]
;defaults=[number,xyimage,automag,abimage,flags,thetaimage,rdj2000,isoareaimage]
for j=0,n_elements(defaults)-1 do widget_control,defaults(j),set_button=1b

;the state structure (NOT using pointers here)
state={file:file,$
       defaults:defaults,$
       buttons:buttons,$
       name:current_routine()}
state=ptr_new(state,/no_copy)

;if not running in GUI mode
if keyword_set(NOGUI) then begin
   sexparam_write,state
   return
end

;offset this from the primary gui
if keyword_set(GROUP) then place_widget,base,group

widget_control,base,map=1b
widget_control,base,set_uval=state
widget_control,base,/realize

xmanager,'sexparam',base,/no_block,cleanup='sexparam_clean'
end

function sex_images,state,cmd
;get the data for the input/output for sextractor GUI

widget_control,(*state).wmeasimg,get_value=measimg & measimg=measimg(0)
widget_control,(*state).wmeaswht,get_value=measwht & measwht=measwht(0)
measwhttype=widget_info((*state).wmeaswhttype,/combobox_gettext)
widget_control,(*state).wdetimg,get_value=detimg & detimg=detimg(0)
widget_control,(*state).wdetwht,get_value=detwht & detwht=detwht(0)
detwhttype=widget_info((*state).wdetwhttype,/combobox_gettext)

;ignore if measurement is missing
if not file_exist(measimg) then return,file_error('Measurement image')

if file_exist(measwht) and measwhttype ne 'NONE' then begin
   ;using a wht map for measurement
   if not file_exist(detimg) then return,file_error('Detection image')
   if not file_exist(detwht) then return,file_error('Detection weight image')
   if detwhttype eq 'NONE' then return,file_error('Detection weight type')
   cmd=detimg+','+measimg+' -WEIGHT_IMAGE '+detwht+','+measwht+$
       ' -WEIGHT_TYPE '+detwhttype+','+measwhttype
endif else begin
   ;not using wht map for measurement
   if file_exist(detimg) then begin ;using det image
      cmd=detimg+','+measimg
   endif else begin                 ;not using det image
      cmd=measimg
   endelse
endelse

return,1b
end

function sex_catalog,state,cmd
;get the stuff for the catalog info in the sextractor GUI

widget_control,(*state).wcatname,get_value=catname & catname=catname(0)
cattype=widget_info((*state).wcattype,/combobox_gettext)
widget_control,(*state).wparname,get_value=parname & parname=parname(0)
;if parname is blank, use default
if parname eq '' then begin
   parname=state.defaults.parname
   sexparam,parname,/nogui
endif
;if not blank and not found, then make one
if not file_exist(parname) then sexparam,parname,/nogui

;if not file_exist(parname) then return,file_error('PARAMETERS_NAME')

cmd=['#---------------------- Catalog ------------------------',$
     string('CATALOG_NAME',f='(A-17)')+catname,$
     string('CATALOG_TYPE',f='(A-17)')+cattype,$
     string('PARAMETERS_NAME',f='(A-17)')+parname]
return,1b
end

function sex_extraction,state,cmd
;get the info for the extraction in the sextractor gui

dettype=widget_info((*state).wdettype,/combobox_gettext)
widget_control,(*state).wdetminarea,get_va=detminarea & detminarea=detminarea(0)
widget_control,(*state).wdetthresh,get_val=detthresh & detthresh=detthresh(0)
widget_control,(*state).wanalthresh,get_va=analthresh & analthresh=analthresh(0)
filter=widget_info((*state).wfilty,/button_set)?'Y':'N'
clean=widget_info((*state).wcleany,/button_set)?'Y':'N'
widget_control,(*state).wcleanparam,get_va=cleanparam & cleanparam=cleanparam(0)
widget_control,(*state).wdebnthresh,get_va=debnthresh & debnthresh=debnthresh(0)
widget_control,(*state).wdebmincont,get_va=debmincont & debmincont=debmincont(0)
masktype=widget_info((*state).wmasktype,/combobox_gettext)

if isnumber(detminarea) ne 1 then return,type_error('DETECT_MINAREA')
if isnumber(detthresh)  eq 0 then return,type_error('DETECT_THRESHOLD')
if isnumber(analthresh) eq 0 then return,type_error('ANALYSIS_THRESHOLD')
if isnumber(debnthresh) ne 1 then return,type_error('DEBLEND_NTHRESHOLD')
if isnumber(debmincont) eq 0 then return,type_error('DEBLEND_MINCONT')

cmd=['#---------------------- Extraction ------------------------',$
     string('DETECT_MINAREA',f='(A-17)')+detminarea,$
     string('DETECT_THRESH',f='(A-17)')+detthresh,$
     string('ANALYSIS_THRESH',f='(A-17)')+analthresh,$
     string('DEBLEND_NTHRESH',f='(A-17)')+debnthresh,$
     string('DEBLEND_MINCONT',f='(A-17)')+debmincont]
if clean eq 'Y' then begin
   if isnumber(cleanparam) eq 0 then return,type_error('CLEAN_PARAMTER')
   cmd=[cmd,$
        string('CLEAN',f='(A-17)')+'Y',$
        string('CLEAN_PARAM',f='(A-17)')+cleanparam]
endif
if filter eq 'Y' then begin
   widget_control,(*state).wfiltname,get_val=filtname
   if file_exist(filtname(0)) then begin
      cmd=[cmd,$
           string('FILTER',f='(A-17)')+'Y',$
           string('FILTER_NAME',f='(A-17)')+filtname(0)]
   endif else cmd=[cmd,string('FILTER',f='(A-17)')+'N']
endif else cmd=[cmd,string('FILTER',f='(A-17)')+'N']
return,1b
end


function sex_photometry,state,cmd
;get the stuff for the photometry part of the sextractor GUI

widget_control,(*state).wphotaper,get_value=photaper & photaper=photaper(0)
widget_control,(*state).wphotauto,get_value=photauto & photauto=photauto(0)
widget_control,(*state).wphotpetro,get_value=photpetro & photpetro=photpetro(0)
widget_control,(*state).wphotsatur,get_value=photsatur & photsatur=photsatur(0)
widget_control,(*state).wmagzero,get_value=magzero & magzero=magzero(0)
widget_control,(*state).wmaggamma,get_value=maggamma & maggamma=maggamma(0)
widget_control,(*state).wgain,get_value=gain & gain=gain(0)
widget_control,(*state).wpixscl,get_value=pixscl & pixscl=pixscl(0)


if isnumber(photsatur) eq 0 then return,type_error('SATUR_LEVEL')
if isnumber(magzero)   eq 0 then return,type_error('MAG_ZEROPOINT')
if isnumber(maggamma)  eq 0 then return,type_error('MAG_GAMMA')
if isnumber(gain)      eq 0 then return,type_error('GAIN')
if isnumber(pixscl)    eq 0 then return,type_error('PIXEL_SCALE')

cmd=['#---------------------- Photometry ------------------------',$
     string('PHOT_APERTURES',f='(A-17)')+photaper,$
     string('PHOT_AUTOPARAMS',f='(A-17)')+photauto,$
     string('PHOT_PETROPARAMS',f='(A-17)')+photpetro,$
     string('SATUR_LEVEL',f='(A-17)')+photsatur,$
     string('MAG_ZEROPOINT',f='(A-17)')+magzero,$
     string('MAG_GAMMA',f='(A-17)')+maggamma,$
     string('GAIN',f='(A-17)')+gain,$
     string('PIXEL_SCALE',f='(A-17)')+pixscl]
return,1b
end

function sex_stargalaxy,state,cmd
;get the stuff for star/galaxy separation for sextractor GUI

widget_control,(*state).wsee,get_value=see & see=see(0)
widget_control,(*state).wstarnnw,get_value=starnnw & starnnw=starnnw(0)

if isnumber(see) eq 0 then return,type_error('SEEING_FWHM')
if not file_exist(starnnw) then return,file_error('STARNNW_NAME')
cmd=['#-------------------- Star/Galaxy Separation------------------',$
     string('SEEING_FWHM',f='(A-17)')+see,$
     string('STARNNW_NAME',f='(A-17)')+starnnw]
return,1b
end

function sex_background,state,cmd
widget_control,(*state).wbacksize,get_value=backsize & backsize=backsize(0)
widget_control,(*state).wbackfiltersize,get_value=backfiltersize
backfiltersize=backfiltersize(0)
backphototype=widget_info((*state).wbackphoto,/combobox_gettext)
if isnumber(backsize)       ne 1 then return,type_error('BACK_SIZE')
if isnumber(backfiltersize) ne 1 then return,type_error('BACK_FILTERSIZE')
cmd=['#---------------------- Background ------------------------',$
     string('BACK_SIZE',f='(A-17)')+backsize,$
     string('BACK_FILTERSIZE',f='(A-17)')+backfiltersize,$
     string('BACKPHOTO_TYPE',f='(A-17)')+backphototype]
return,1b
end


function sex_checkimages,state,cmd
;get info for the checkimages for SExtractor GUI

widget_control,(*state).wcheckroot,get_value=checkroot & checkroot=checkroot(0)
if checkroot ne '' then checkroot=checkroot+'-'

type=[''] & name=['']
if widget_info((*state).wback,/button_set) then begin
   type=[type,'BACKGROUND']
   name=[name,'back']
endif
if widget_info((*state).wbackrms,/button_set) then begin
   type=[type,'BACKGROUND_RMS']
   name=[name,'backrms']
endif
if widget_info((*state).wminiback,/button_set) then begin
   type=[type,'MINIBACKGROUND']
   name=[name,'miniback']
endif
if widget_info((*state).wminibackrms,/button_set) then begin
   type=[type,'MINIBACK_RMS']
   name=[name,'minibackrms']
endif
if widget_info((*state).wsubback,/button_set) then begin
   type=[type,'-BACKGROUND']
   name=[name,'subback']
endif
if widget_info((*state).wfiltered,/button_set) then begin
   type=[type,'FILTERED']
   name=[name,'filtered']
endif
if widget_info((*state).wobjects,/button_set) then begin
   type=[type,'OBJECTS']
   name=[name,'objects']
endif
if widget_info((*state).wsubobjects,/button_set) then begin
   type=[type,'-OBJECTS']
   name=[name,'subobjects']
endif
if widget_info((*state).wsegment,/button_set) then begin
   type=[type,'SEGMENTATION']
   name=[name,'segment']
endif
if widget_info((*state).wapertures,/button_set) then begin
   type=[type,'APERTURES']
   name=[name,'apertures']
endif

g=where(type ne '',n)
cmd=['#-------------------- Check Images  ------------------------']
if n ge 1 then begin
   cmd=[cmd,string('CHECKIMAGE_TYPE',f='(A-17)')+strjoin(type(g),','),$
        string('CHECKIMAGE_NAMES',f='(A-17)')+strjoin(checkroot+name(g),',')]
   return,1b
endif else cmd=[cmd,string('CHECKIMAGE_TYPE',f='(A-17)')+'NONE']

return,1b
end

function sex_memory,state,cmd
;get the stuff for the memory usage for sextractor GUI

widget_control,(*state).wmemobj,get_value=memobj & memobj=memobj(0)
widget_control,(*state).wmempix,get_value=mempix & mempix=mempix(0)
widget_control,(*state).wmembuf,get_value=membuf & membuf=membuf(0)

if isnumber(memobj) ne 1 then return,type_error('MEMORY_OBJSTACK')
if isnumber(mempix) ne 1 then return,type_error('MEMORY_PIXSTACK')
if isnumber(membuf) ne 1 then return,type_error('MEMORY_BUFSIZE')
cmd=['#----------------- Memory (change with caution!) ---------------------',$
     string('MEMORY_OBJSTACK',f='(A-17)')+memobj,$
     string('MEMORY_PIXSTACK',f='(A-17)')+mempix,$
     string('MEMORY_BUFSIZE',f='(A-17)')+membuf]
return,1b
end

function sex_misc,state,cmd
;get miscellaneous data for sextractor GUI

verb=widget_info((*state).wverb,/combobox_gettext)
xml=widget_info((*state).wxmly,/button_set)?'Y':'N'
cmd=['#------------------------- Miscellaneous -----------------------------',$
     string('VERBOSE_TYPE',f='(A-17)')+verb,$
     string('WRITE_XML',f='(A-17)')+xml]

if xml eq 'Y' then begin
   widget_control,(*state).wxmlname,get_value=xmlname
   cmd=[cmd,string('XML_NAME',f='(A-17)')+xmlname(0)]
endif

return,1b
end


pro sex_event,event,GROUP=group
;event handler for sextractor GUI

widget_control,event.id,get_uvalue=uval
if size(uval,/type) ne 0 then begin
   widget_control,event.top,get_uvalue=state
   case uval of
      'CATTYPE': t=dialog_message(['Just a warning.',$
                                   "If you're using this with iGalFit, ",$
                                   'you must use the "ASCII_HEAD" option!'],$
                                  /info,/center,title='SEx Catalog Warning')
      'CLEAN': begin
         widget_control,event.id,get_value=v
         widget_control,(*state).wcleanparam,sensitive=(v eq 'Y')
      end
      'FILTER': begin
         widget_control,event.id,get_value=v
         widget_control,(*state).wfiltname,sensitive=(v eq 'Y')
         widget_control,(*state).wmkfilt,sensitive=(v eq 'Y')
         widget_control,(*state).wldfilt,sensitive=(v eq 'Y')
      end
      'XMLY': widget_control,(*state).wxmlname,sensitive=1b
      'XMLN': widget_control,(*state).wxmlname,sensitive=0b

      'SETPAR': begin
         widget_control,(*state).wparname,get_value=parname
         sexparam,parname,group=event.top
      end
      'MAKEFILTER': begin
         widget_control,(*state).wfiltname,get_value=filtname
         mkconv,confile=filtname,group=event.top
      end
      'LOADFILTER': begin
         t=dialog_pickfile(file='default.conv',filter=['*conv'],$
                           /must_exist,/fix_filter)
         if t(0) ne '' then widget_control,(*state).wfiltname,set_value=t(0)
      end
      'SAVE': begin
         t=dialog_message('Not functional',/error,/center)

      end
      'LOAD': begin
         t=dialog_message('Not functional',/error,/center)

      end
      'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                       group=event.top,load='runsex'
      'SEX': begin
         widget_control,(*state).wsex,get_value=sexexec & sexexec=sexexec(0)
         res=(file_which(getenv('PATH'),sexexec))(0)

         if res ne '' then begin
            if not sex_images(state,imgcmd)        then break ;Images Settings
            if not sex_catalog(state,catcmd)       then break ;Catalog Settings
            if not sex_extraction(state,extcmd)    then break ;Extract. Settings
            if not sex_photometry(state,photcmd)   then break ;Photom. Settings
;            if not sex_stargalaxy(state,sgcmd)     then break ;S/G Settings
            if not sex_background(state,backcmd)   then break ;Back Settings
            if not sex_checkimages(state,checkcmd) then break ;Check Settings
            if not sex_memory(state,memcmd)        then break ;Memory Settings
            if not sex_misc(state,misccmd)         then break ;Misc Settings

            widget_control,(*state).wconfigfile,get_value=config
            openw,l,config(0),/get_lun,error=error
            if error ne 0 then begin
               t=writefile_error('SEx Configuration File')
               return
            endif

            printf,l,'# SExtractor configuration file made by '+(*state).name+$
                   ' on '+systime()
            for i=0,n_elements(catcmd)-1   do printf,l,catcmd(i)
            for i=0,n_elements(extcmd)-1   do printf,l,extcmd(i)
            for i=0,n_elements(photcmd)-1  do printf,l,photcmd(i)
;            for i=0,n_elements(sgcmd)-1    do printf,l,sgcmd(i)
            for i=0,n_elements(backcmd)-1  do printf,l,backcmd(i)
            for i=0,n_elements(checkcmd)-1 do printf,l,checkcmd(i)
            for i=0,n_elements(memcmd)-1   do printf,l,memcmd(i)
            for i=0,n_elements(misccmd)-1  do printf,l,misccmd(i)
            close,l & free_lun,l

            cmd=sexexec+' -c '+config(0)+' '+imgcmd
            
            widget_control,hourglass=1b     ;disable the IDL pointer
            ;ok, ok.  Let's run sextractor:
            spawn,cmd,exit_status=stat

            ;check if you gave it a parent state
            widget_control,event.top,get_uval=state
            if size((*state).igalfit,/type) eq 10 then begin
               ;in principle, need more error checking here.
               ;in practice, if you set the igalfit keyword in 
               ;             the main SEx GUI, then I'll assume 
               ;             you're smart enough.

               ;get the name of the sexcat
               widget_control,(*state).wcatname,get_valu=cat & cat=cat(0)

               ;add to the ROIs
               if file_exist(cat) then sex2roi,(*state).igalfit,$
                                               rdsexcat(cat,/sil,/conv)
            endif

            ;clean up if necessary
            for i=0,n_elements((*state).wsave)-1 do begin
               if not widget_info((*state).wsave(i),/button_set) then begin
                  case (*state).files(i) of 
                     'Config': wid=(*state).wconfigfile
                     'Param': wid=(*state).wparname
                     'Catalog': wid=(*state).wcatname
                     'Filter': wid=(*state).wfiltname
                     'XML': wid=(*state).wxmlname
                     else: stop
                  endcase                     
                  widget_control,wid,get_value=file2delete
                  file_delete,file2delete(0),/allow_nonexist
               endif
            endfor
            
            widget_control,hourglass=0b    ;disable the hourglass
         endif else t=file_error('SEx executable')
      end
      'DELETE': break   ;do nothing
      'CLOSE': widget_control,event.top,/destroy
      else: print,uval
   endcase
endif   
end


pro sex_settings,state,set
;set the information in the SEXtractor GUI

;images
widget_control,(*state).wmeasimg,set_value=set.img
widget_control,(*state).wmeaswht,set_value=set.imgwht
widget_control,(*state).wmeaswhttype,get_value=val
widget_control,(*state).wmeaswhttype,$
               set_combobox_select=(where(set.imgwhttype eq val))(0)
widget_control,(*state).wdetimg,set_value=set.det
widget_control,(*state).wdetwht,set_value=set.detwht
widget_control,(*state).wdetwhttype,get_value=val
widget_control,(*state).wdetwhttype,$
               set_combobox_select=(where(set.detwhttype eq val))(0)

;catalogs
widget_control,(*state).wcatname,set_value=set.cat
widget_control,(*state).wcattype,get_value=val
widget_control,(*state).wcattype,$
   set_combobox_select=(where(set.cattype eq val))(0)
widget_control,(*state).wparname,set_value=set.parname

;extraction
widget_control,(*state).wdettype,get_value=val
widget_control,(*state).wdettype,$
   set_combobox_select=(where(set.dettype eq val))(0)
widget_control,(*state).wdetminarea,set_value=set.minarea
widget_control,(*state).wdetthresh,set_value=set.detthresh
widget_control,(*state).wanalthresh,set_value=set.analthresh
widget_control,(*state).wdebnthresh,set_value=set.nthresh
widget_control,(*state).wdebmincont,set_value=set.mincont

widget_control,(*state).wfilty,set_button=(set.filter eq 'Y')
widget_control,(*state).wfiltn,set_button=(set.filter eq 'N')
widget_control,(*state).wfiltname,set_value=set.filtername,$
               sensitive=(set.filter eq 'Y')
widget_control,(*state).wcleany,set_button=(set.clean eq 'Y')
widget_control,(*state).wcleann,set_button=(set.clean eq 'N')
widget_control,(*state).wcleanparam,set_value=set.cleanparam,$
               sensitive=(set.clean eq 'Y')
widget_control,(*state).wmasktype,get_value=val
widget_control,(*state).wmasktype,$
   set_combobox_select=(where(set.masktype eq val))(0)

;photometry
widget_control,(*state).wphotaper,set_value=set.apers
widget_control,(*state).wphotauto,set_value=set.autoparams
widget_control,(*state).wphotpetro,set_value=set.petroparams
widget_control,(*state).wphotsatur,set_value=set.satur
widget_control,(*state).wmagzero,set_value=set.zero
widget_control,(*state).wgain,set_value=set.gain
widget_control,(*state).wpixscl,set_value=set.pixscl

;background
widget_control,(*state).wbacksize,set_value=set.backsize
widget_control,(*state).wbackfiltersize,set_value=set.backfiltersize
widget_control,(*state).wbackphoto,get_value=val
widget_control,(*state).wbackphoto,$
               set_combobox_select=(where(set.backphototype eq val))(0)

;checkimages
widget_control,(*state).wback,set_button=set.back
widget_control,(*state).wbackrms,set_button=set.backrms
widget_control,(*state).wminiback,set_button=set.miniback
widget_control,(*state).wminibackrms,set_button=set.minibackrms
widget_control,(*state).wsubback,set_button=set.subback
widget_control,(*state).wfiltered,set_button=set.filtered
widget_control,(*state).wobjects,set_button=set.objects
widget_control,(*state).wsubobjects,set_button=set.subobjects
widget_control,(*state).wsegment,set_button=set.seg
widget_control,(*state).wapertures,set_button=set.aper
widget_control,(*state).wcheckroot,set_value=set.croot

;memory
widget_control,(*state).wmemobj,set_value=set.memobj
widget_control,(*state).wmempix,set_value=set.mempix
widget_control,(*state).wmembuf,set_value=set.membuf

;miscellaneous
widget_control,(*state).wverb,get_value=val
widget_control,(*state).wverb,$
   set_combobox_select=(where(set.verb eq val))(0)
widget_control,(*state).wxmly,set_button=(set.xml eq 'Y')
widget_control,(*state).wxmln,set_button=(set.xml eq 'N')
widget_control,(*state).wxmlname,set_value=set.xmlname,$
   sensitive=(set.xml eq 'Y')
for i=0,n_elements((*state).files)-1 do begin
   widget_control,(*state).wsave(i),set_button=(set.save(i) eq 'Y')
endfor


;basic stuff
widget_control,(*state).wsex,set_value=set.sex
widget_control,(*state).wconfigfile,set_value=set.config
end

pro sex_clean,wid
widget_control,wid,get_uval=state

;unset the SEx button in main GUI
if widget_info((*state).wbutton,/valid_id) then $
   widget_control,(*state).wbutton,set_button=0b

cleanup,state
end


pro sex,SCIFILE=scifile,$
        GROUP=group,$
        BASE=base,$
        IGALFIT=igalfit,$
        BUTTON=button

;the sextractor GUI


if not keyword_set(SCIFILE) then sci='' else sci=scifile
if not keyword_set(IGALFIT) then igalfit=0b

;Auxiliary files you can delete:
files=['Config','Param','Catalog','Filter','XML']

;import some settings from iGalFit if necessary
if keyword_set(IGALFIT) then begin
   zero=strcompress(string((*igalfit).magzero,f='(F7.3)'),/rem)
endif else begin
   zero='0.0'
endelse


;default settings
defaults={img:sci,imgwht:'',imgwhttype:'NONE',det:'',detwht:'',detwhttype:'',$
          cat:'sex.cat',cattype:'ASCII_HEAD',parname:'sex.param',$
          dettype:'CCD',minarea:'5',detthresh:'4.5',analthresh:'4.5',$
          nthresh:'32',mincont:'0.005',filter:'Y',filtername:'default.conv',$
          clean:'Y',cleanparam:'1.0',masktype:'NONE',$
          apers:'5',autoparams:'2.5,3.5',petroparams:'2.0,3.5',satur:'50000',$
          zero:zero,gamma:'4.0',gain:'1.0',pixscl:'0',$
          backsize:'64',backfiltersize:'3',backphototype:'GLOBAL',$
          back:0b,backrms:0b,miniback:0b,minibackrms:0b,subback:0b,$
          filtered:0b,objects:0b,subobjects:0b,seg:0b,aper:0b,croot:'',$
          memobj:'3000',mempix:'300000',membuf:'1024',$
          verb:'NORMAL',xml:'N',xmlname:'sex.xml',$
          save:replicate('N',n_elements(files)),$
          sex:'sex',config:'sex.config'}

if not keyword_set(BUTTON) then button=-1L

base=widget_base(title='SExtractor',/column,mbar=mbar,$
                 group=group,xsize=390)
                 
filemenu=widget_button(mbar,value='File',/menu)
s=widget_button(filemenu,value='Save',uvalue='SAVE')
l=widget_button(filemenu,value='Load',uvalue='LOAD')
c=widget_button(filemenu,value='Close',uvalue='CLOSE',/sep)

helpmenu=widget_button(mbar,value='Help',/menu,/help)
h=widget_button(helpmenu,value='Help',uvalue='HELP')

tab=widget_tab(base,location=0,xsize=600,multiline=4)

imgtab=widget_base(tab,title='Inputs',/column)
l=widget_label(imgtab,value='Primary Inputs')

img1=widget_base(imgtab,/row)
l=widget_label(img1,value='measurement image ')
wmeasimg=widget_text(img1,value='',/edit,xsize=20)
img2=widget_base(imgtab,/row)
l=widget_label(img2,value='measurement weight')
wmeaswht=widget_text(img2,value='',/edit,xsize=20)
wmeaswhttype=widget_combobox(img2,value=['NONE','BACKGROUND','MAP_RMS',$
                                        'MAP_VAR','MAP_WEIGHT'],xsize=100)



img3=widget_base(imgtab,/row)
l=widget_label(img3,value='detection image   ')
wdetimg=widget_text(img3,value='',/edit,xsize=20)
img4=widget_base(imgtab,/row)
l=widget_label(img4,value='detection weight  ')
wdetwht=widget_text(img4,value='',/edit,xsize=20)
wdetwhttype=widget_combobox(img4,value=['NONE','BACKGROUND','MAP_RMS',$
                                        'MAP_VAR','MAP_WEIGHT'],xsize=100)

img4=widget_base(imgtab,/row)
l=widget_label(img4,value='Configuration File')
wconfigfile=widget_text(img4,value='default.sex',xsize=20,/editable)




cattab=widget_base(tab,title='Catalog',/column)
l=widget_label(cattab,value='Catalog Settings')
cat1=widget_base(cattab,/row)
l=widget_label(cat1,value='CATALOG_NAME   ')
wcatname=widget_text(cat1,value='sex.cat',xsize=20,/editable)
cat2=widget_base(cattab,/row)
l=widget_label(cat2,value='CATALOG_TYPE   ')
wcattype=widget_combobox(cat2,value=['NONE','ASCII','ASCII_HEAD',$
                                     'ASCII_SKYCAT','ASCII_VOTABLE',$
                                     'FITS_1.0','FITS_LDAC'],uval='CATTYPE')
cat3=widget_base(cattab,/row)
l=widget_label(cat3,val='PARAMETERS_NAME')
wparname=widget_text(cat3,value='sex.param',xsize=20,/editable)
catt3=widget_base(cat3,/nonexclu)
wparamset=widget_button(cat3,value='Set Parameters',uvalue='SETPAR')

exttab=widget_base(tab,title='Extraction',/column)
l=widget_label(exttab,value='Extraction Settings')
extrow=widget_base(exttab,/row)
lhs=widget_base(extrow,/column)
lhs1=widget_base(lhs,/row)
l=widget_label(lhs1,value='DETECT_TYPE    ')
wdettype=widget_combobox(lhs1,value=['CCD','PHOTO'],xsize=70)

lhs2=widget_base(lhs,/row)
l=widget_label(lhs2,value='DETECT_MINAREA ')
wdetminarea=widget_text(lhs2,value='5',xsize=7,/edit)

lhs3=widget_base(lhs,/row)
l=widget_label(lhs3,value='DETECT_THRESH  ')
wdetthresh=widget_text(lhs3,value='1.5',xsize=7,/edit)

lhs4=widget_base(lhs,/row)
l=widget_label(lhs4,value='ANALYSIS_THRESH')
wanalthresh=widget_text(lhs4,value='1.5',xsize=7,/edit)

lhs5=widget_base(lhs,/row)
l=widget_label(lhs5,value='DEBLEND_NTHRESH')
wdebnthresh=widget_text(lhs5,value='32',/edit,xsize=7)
lhs6=widget_base(lhs,/row)
l=widget_label(lhs6,value='DEBLEND_MINCONT')
wdebmincont=widget_text(lhs6,value='0.005',/edit,xsize=7)


mid=widget_base(extrow,/column)

lhs5=widget_base(mid,/row)
l=widget_label(lhs5,value='FILTER')
lhs5but=widget_base(lhs5,/exclusive,/row)
wfilty=widget_button(lhs5but,value='Y',uval='FILTER')
wfiltn=widget_button(lhs5but,value='N',uval='FILTER')
lhs6=widget_base(mid,/row)
l=widget_label(lhs6,value='FILTER_NAME')
wfiltname=widget_text(lhs6,value='default.conv',/edit,xsize=12)
lhs7=widget_base(mid,/row)
wmkfilt=widget_button(lhs7,value='Make Filter',uvalue='MAKEFILTER')
wldfilt=widget_button(lhs7,value='Load Filter',uvalue='LOADFILTER')

rhs3=widget_base(mid,/row)
l=widget_label(rhs3,value='CLEAN')
rhs3but=widget_base(rhs3,/exclusive,/row)
wcleany=widget_button(rhs3but,value='Y',uval='CLEAN')
wcleann=widget_button(rhs3but,value='N',uval='CLEAN')
rhs4=widget_base(mid,/row)
l=widget_label(rhs4,value='CLEAN_PARAM')
wcleanparam=widget_text(rhs4,value='1.0',/edit,xsize=5)

rhs5=widget_base(mid,/row)
l=widget_label(rhs5,value='MASK_TYPE  ')
wmasktype=widget_combobox(rhs5,value=['NONE','CORRECT','BLANK'],xsize=80)



phottab=widget_base(tab,title='Photometry',/column)
l=widget_label(phottab,value='Photometry Settings')
photrow=widget_base(phottab,/row)
lhs=widget_base(photrow,/column)

lhs1=widget_base(lhs,/row)
l=widget_label(lhs1,value='PHOT_APERTURES  ')
wphotaper=widget_text(lhs1,value='5',/edit,xsize=10)

lhs2=widget_base(lhs,/row)
l=widget_label(lhs2,value='PHOT_AUTOPARAMS ')
wphotauto=widget_text(lhs2,value='2.5,3.5',/edit,xsize=10)

lhs3=widget_base(lhs,/row)
l=widget_label(lhs3,value='PHOT_PETROPARAMS')
wphotpetro=widget_text(lhs3,value='2.0,3.5',/edit,xsize=10)

lhs4=widget_base(lhs,/row)
l=widget_label(lhs4,value='SATUR_LEVEL     ')
wphotsatur=widget_text(lhs4,value='50000',/edit,xsize=10)


rhs=widget_base(photrow,/column)
rhs1=widget_base(rhs,/row)
l=widget_label(rhs1,value='MAG_ZEROPOINT')
wmagzero=widget_text(rhs1,value='',/edit,xsize=10)


rhs2=widget_base(rhs,/row)
l=widget_label(rhs2,value='MAG_GAMMA    ')
wmaggamma=widget_text(rhs2,value='4.0',/edit,xsize=10)

rhs3=widget_base(rhs,/row)
l=widget_label(rhs3,value='GAIN         ')
wgain=widget_text(rhs3,value='1.0',/edit,xsize=10)

rhs4=widget_base(rhs,/row)
l=widget_label(rhs4,value='PIXEL_SCALE  ')
wpixscl=widget_text(rhs4,value='0',/edit,xsize=10)

;sgtab=widget_base(tab,title='Star/Galaxy Sep.',/column)
;l=widget_label(sgtab,value='Star/Galaxy Separation Settings')
;sg1=widget_base(sgtab,/row)
;l=widget_label(sg1,value='SEEING_FWHM')
;wsee=widget_text(sg1,value='1.2',/edit,xsize=10)
;sg2=widget_base(sgtab,/row)
;l=widget_label(sg2,value='STARNNW_NAME')
;wstarnnw=widget_text(sg2,value='default.nnw',/edit,xsize=10)


backtab=widget_base(tab,title='Background',/column)
l=widget_label(backtab,value='Background Settings')
back1=widget_base(backtab,/row)
l=widget_label(back1,value='BACK_SIZE      ')
wbacksize=widget_text(back1,value='64',/edit,xsize=4)

back2=widget_base(backtab,/row)
l=widget_label(back2,value='BACK_FILTERSIZE')
wbackfiltersize=widget_text(back2,value='3',/edit,xsize=2)

back3=widget_base(backtab,/row)
l=widget_label(back3,value='BACKPHOTO_TYPE ')
wbackphoto=widget_combobox(back3,value=['GLOBAL','LOCAL'],xsize=70)


checktab=widget_base(tab,title='Check Images',/column)
l=widget_label(checktab,value='Check Image Settings')
but=widget_base(checktab,/row)
lbut=widget_base(but,/column,/non)
wback=widget_button(lbut,value='BACKGROUND')
wbackrms=widget_button(lbut,value='BACKGROUND_RMS')
wminiback=widget_button(lbut,value='MINIBACKGROUND')
wminibackrms=widget_button(lbut,value='MINIBACKGROUND_RMS')
wsubback=widget_button(lbut,value='-BACKGROUND')
rbut=widget_base(but,/column,/non)
wfiltered=widget_button(rbut,value='FILTERED')
wobjects=widget_button(rbut,value='OBJECTS')
wsubobjects=widget_button(rbut,value='-OBJECTS')
wsegment=widget_button(rbut,value='SEGMENTATION')
wapertures=widget_button(rbut,value='APERTURES')
b=widget_base(checktab,/row)
l=widget_label(b,value='checkimage root')
wcheckroot=widget_text(b,value='',/edit,xsize=20)

memorytab=widget_base(tab,title='Memory',/column)
l=widget_label(memorytab,value='Memory Settings')
mem1=widget_base(memorytab,/row)
l=widget_label(mem1,value='MEMORY_OBJSTACK')
wmemobj=widget_text(mem1,value='3000',/edit,xsize=5)

mem2=widget_base(memorytab,/row)
l=widget_label(mem2,value='MEMORY_PIXSTACK')
wmempix=widget_text(mem2,value='300000',/edit,xsize=7)

mem3=widget_base(memorytab,/row)
l=widget_label(mem3,value='MEMORY_BUFSIZE ')
wmembuf=widget_text(mem3,value='1024',/edit,xsize=5)

misctab=widget_base(tab,title='Miscellaneous',/column)
l=widget_label(misctab,value='Miscellaneous Settings')
top=widget_base(misctab,/row)

lhs=widget_base(top,/column,/frame)
l=widget_label(lhs,value='SEx Settings')
misc1=widget_base(lhs,/row)
l=widget_label(misc1,value='VERBOSE_TYPE')
wverb=widget_combobox(misc1,value=['QUIET','NORMAL','FULL'],xsize=70)
misc2=widget_base(lhs,/row)
l=widget_label(misc2,value='WRITE_XML')
misc2but=widget_base(misc2,/exclusive,/row)
wxmly=widget_button(misc2but,value='Y',uval='XMLY')
wxmln=widget_button(misc2but,value='N',uval='XMLN')

misc3=widget_base(lhs,/row)
l=widget_label(misc3,value='XML_NAME')
wxmlname=widget_text(misc3,value='sex.xml',/edit,xsize=12)

rhs=widget_base(top,/column,/frame)
l=widget_label(rhs,value='Save Auxiliary Files')
buttons=cw_bgroup(rhs,files,col=2,/nonexclusive,ids=wsave,uval='DELETE')

bot=widget_base(base,/column,/frame)

bot2=widget_base(bot,/row)
l=widget_label(bot2,value='SEx executable')
wsex=widget_text(bot2,/edit,xsize=12)
b=widget_button(bot2,value='Run SExtractor',uvalue='SEX')







state={defaults:defaults,$
       igalfit:igalfit,$
       wdetimg:wdetimg,$
       wdetwht:wdetwht,$
       wdetwhttype:wdetwhttype,$
       wmeasimg:wmeasimg,$
       wmeaswht:wmeaswht,$
       wmeaswhttype:wmeaswhttype,$
       wcatname:wcatname,$
       wcattype:wcattype,$
       wparname:wparname,$
       wdettype:wdettype,$
       wdetminarea:wdetminarea,$
       wdetthresh:wdetthresh,$
       wanalthresh:wanalthresh,$
       wfilty:wfilty,$
       wfiltn:wfiltn,$
       wfiltname:wfiltname,$
       wcleany:wcleany,$
       wcleann:wcleann,$
       wcleanparam:wcleanparam,$
       wdebnthresh:wdebnthresh,$
       wdebmincont:wdebmincont,$
       wmasktype:wmasktype,$
       wphotaper:wphotaper,$
       wphotauto:wphotauto,$
       wphotpetro:wphotpetro,$
       wphotsatur:wphotsatur,$
       wmagzero:wmagzero,$
       wmaggamma:wmaggamma,$
       wgain:wgain,$
       wpixscl:wpixscl,$
;       wsee:wsee,$
;       wstarnnw:wstarnnw,$
       wbacksize:wbacksize,$
       wbackfiltersize:wbackfiltersize,$
       wbackphoto:wbackphoto,$
       wback:wback,$
       wbackrms:wbackrms,$
       wminiback:wminiback,$
       wminibackrms:wminibackrms,$
       wsubback:wsubback,$
       wfiltered:wfiltered,$
       wobjects:wobjects,$
       wsubobjects:wsubobjects,$
       wsegment:wsegment,$
       wapertures:wapertures,$       
       wcheckroot:wcheckroot,$
       wmemobj:wmemobj,$
       wmempix:wmempix,$
       wmembuf:wmembuf,$       
       wverb:wverb,$
       wxmly:wxmly,$
       wxmln:wxmln,$
       wxmlname:wxmlname,$
       files:files,$
       wsave:wsave,$
       wmkfilt:wmkfilt,$
       wldfilt:wldfilt,$
       wbutton:button,$
       wsex:wsex,$
       wconfigfile:wconfigfile,$
       name:current_routine()}

state=ptr_new(state,/no_copy)
sex_settings,state,defaults

if keyword_set(GROUP) then place_widget,base,group

widget_control,base,/realize,set_uval=state

;r=widget_base(bot2,/row,map=0b)
;bb=widget_button(r,value='Run SExtractor',uvalue='SEX',/menu)
;bbb=widget_button(bb,value='Run SExtractor',uvalue='SEX',accel='Return')




xmanager,'sex',base,/no_block,cleanup='sex_clean'




end
