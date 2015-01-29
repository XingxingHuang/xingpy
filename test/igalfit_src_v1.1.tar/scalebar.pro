pro scalebar,state

;got to have a valid astrometry
if not ptr_valid((*state).ast) then begin
   widget_control,(*state).wscalebar,sens=0b
   return
endif else widget_control,(*state).wscalebar,sens=1b

x0=10
y0=10
length=(*state).prefs.scalesize
unit=(*state).prefs.scaleunit




;basic scalebar
x=[-3,-2,-3,-2,-3,+3,+2,+3,+2,+3]
y=[ 0,-1, 0,+1, 0, 0,-1, 0,+1, 0]
nv=n_elements(x)

;rescale scalebar
scl=2.0*max(abs(x))
x=float(x)/scl
y=float(y)/scl


;compute pixel scale
getrot,(*(*state).ast),ang,cdelt
case unit of
   'arcsec': begin
      fac=3600.
      label='"'
   end
   'arcmin': begin
      fac=60.
      label="'"
   end
   'degree': begin
      fac=1.
      label=string(176b)
   end
endcase
pixscl=abs(cdelt(0))*fac        ;units per pixel


;compute scale factors
zoomfac=((size((*state).zoomstate,/type) eq 0)?1.0:(*state).zoomstate)
xscl=(length/pixscl)
yscl=(length/pixscl)


;get property of the window & view
(*state).oView->GetProperty,view=view
win=widget_info((*state).wdraw,/geom)

sx=(view(2)/win.draw_xsize)
sy=(view(3)/win.draw_ysize)

;set the new positions
xx=view(0)+x*xscl+(abs(min(x)))*xscl+x0*zoomfac
yy=view(1)+y*yscl+(abs(min(y)))*yscl+y0*zoomfac
zz=replicate(0.0,nv)

;update the state
(*state).oScale->ReplaceData,xx,yy,zz,start=0,finish=nv-1
(*state).oScale->SetProperty,thick=(*state).prefs.scalethick,uval='scalebar'


end
