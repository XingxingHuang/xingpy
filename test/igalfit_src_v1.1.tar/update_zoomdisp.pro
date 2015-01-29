pro update_zoomdisp,state,PULLDOWN=pulldown
;update the zoom pull down menu

;number of preset zooms
nz=n_elements((*state).zooms)

if keyword_set(PULLDOWN) then begin

   ;uncheck all boxes
   for i=0,nz-1 do widget_control,(*state).wzoom(i),set_button=0b

   ;obtain the preset values:
   zoomval=fltarr(nz)
   for i=0,nz-1 do begin
      s=strsplit((*state).zooms(i),'/',/ext)
      case n_elements(s) of
         1: zoomval(i)=float(s)
         else: t=execute('zoomval(i)='+s(0)+'./'+s(1)+'.')
      endcase
   endfor
   
   ;check one, if it's a preset:
   g=(where((*state).zoomstate eq zoomval))(0)
   if g ne -1 then widget_control,(*state).wzoom(g),set_button=1b
   
endif

;update the display
if (*state).zoomstate lt 1 then begin
   zz=1./(*state).zoomstate
   zz='1/'+strcompress(string(zz,f='(I5)'),/rem)
endif else zz=strcompress(string((*state).zoomstate,f='(I5)'),/rem)
widget_control,(*state).wz,set_value=zz




end
