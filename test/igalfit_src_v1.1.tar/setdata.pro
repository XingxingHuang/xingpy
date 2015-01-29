pro setdata,state,oROI,CLEAR=clear


if keyword_set(CLEAR) then begin
   ;clear all the widgets:
   widget_control,(*state).wx,set_value=''
   widget_control,(*state).wy,set_value=''
   widget_control,(*state).wa,set_value=''
   widget_control,(*state).wb,set_value=''
   widget_control,(*state).wt,set_value=''
   for i=0,n_elements((*state).wprop)-1 do $
      widget_control,(*state).wprop(i),set_value=''
   widget_control,(*state).wmorph,sens=0b
   return
endif

;sensitize the pulldown menu
if (*(*state).pstate).oROIModel->Count() ge 1 then $
   widget_control,(*state).wmorph,sens=1b


;get size of image
imsize=size((*(*(*state).pstate).img),/dim)

;get the data about the region in question
mask=((oROI->ComputeMask(dim=imsize)) eq 255)
oROI->GetProperty,uval=prop,color=color

;formatting for strings many strings to come
fmt='(F6.1)'

;set the data in the boxes
;nplace=floor(alog10(prop.x>prop.y))+1
widget_control,(*state).wx,set_value=string(prop.x,f=fmt)
widget_control,(*state).wy,set_value=string(prop.y,f=fmt)
case prop.shape of
   'ellipse': begin
      a=strcompress(string(prop.a,f=fmt),/rem)
      b=strcompress(string(prop.b,f=fmt),/rem)
      t=strcompress(string(prop.t mod 360,f=fmt),/rem)
   end
   'circle': begin
      a=strcompress(string(prop.r,f=fmt),/rem)
      b='N/A'
      t='N/A'
  end
   'box': begin
      a=strcompress(string(prop.dx,f=fmt),/rem)
      b=strcompress(string(prop.dy,f=fmt),/rem)
      t=strcompress(string(prop.t mod 360,f=fmt),/rem)
   end
endcase
widget_control,(*state).wa,set_value=a
widget_control,(*state).wb,set_value=b
widget_control,(*state).wt,set_value=t


;update the combobox
widget_control,(*state).wmorph,get_value=morphs
g=(where(prop.type eq morphs))(0)
if g(0) ne -1 then widget_control,(*state).wmorph,set_combobox_select=g

;compute the stuff for the display
g=where(mask,npix)
if npix le 3 then return

pstate=(*state).pstate
img=*(*pstate).img

flux=total(img(g)-(*pstate).sky.ave)
var=avg(img(g)^2)-avg(img(g))^2+(*pstate).sky.sig*(*pstate).sky.sig

mag=(flux gt 0.)?(-2.5*alog10(flux)+(*pstate).magzero):!values.f_infinity
sb=(var gt 0.)?(-1.25*alog10(var)+(*pstate).magzero):!values.f_infinity


flux=strcompress(string(flux,f='(E+10.3)'),/rem)
g=(where((*state).props eq 'flux'))(0)
widget_control,(*state).wprop(g),set_value=flux

mag=strcompress(string(mag,f='(F7.3)'),/rem)
g=(where((*state).props eq 'mag'))(0)
widget_control,(*state).wprop(g),set_value=mag

sb=strcompress(string(sb,f='(F7.3)'),/rem)
g=(where((*state).props eq 'SB'))(0)
widget_control,(*state).wprop(g),set_value=sb

npix=strcompress(string(npix,f='(I6)'),/rem)
g=(where((*state).props eq 'Npix'))(0)
widget_control,(*state).wprop(g),set_value=npix






end
