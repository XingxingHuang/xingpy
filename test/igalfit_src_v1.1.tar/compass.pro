pro compass,state
padding=5.
scl=(*state).prefs.vanesize

;got to have a valid astrometry
if not ptr_valid((*state).ast) then begin
   widget_control,(*state).wcompass,sens=0b
   return
endif else widget_control,(*state).wcompass,sens=1b

;basic weather vane:
x=[-3,-4,-3,-4, 0, 0,-0.5, 0,+0.5, 0, 0,-4,-3]
y=[-0.5, 0,+0.5, 0, 0,+4,+3,+4,+3,+4, 0, 0,-0.5]
nv=n_elements(x)

;compute rotation info
getrot,(*(*state).ast),ang,cdelt
c=cos(ang*!PI/180.)
s=sin(ang*!PI/180.)

;compute sizes
zoomfac=((size((*state).zoomstate,/type) eq 0)?1.0:(*state).zoomstate)
xscl=scl*zoomfac
yscl=scl*zoomfac

;compute the positions
(*state).oView->GetProperty,view=view
win=widget_info((*state).wdraw,/geom)
sx=view(2)/win.draw_xsize
sy=view(3)/win.draw_ysize

;initial positions
r0=((max(x)*xscl/sx)>(max(y)*yscl/sy))
x0=win.draw_xsize-r0-padding
y0=r0+padding
z0=0.0

;new positions
xx=view(0)+sx*x0+x*xscl*c-y*yscl*s
yy=view(1)+sy*y0+x*xscl*s+y*yscl*c
zz=replicate(z0,nv)



;update the state
(*state).oVane->ReplaceData,xx,yy,zz,start=0,finish=nv-1
(*state).oVane->SetProperty,thick=(*state).prefs.vanethick,uval='compass'

end
