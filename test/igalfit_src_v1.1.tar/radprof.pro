pro radprof_gauss,x,a,f,pder
;to fit a Gaussian
f=a(0)*exp(-0.5*(x/a(1))^2)+a(2)
if n_params() ge 4 then $
   pder=[[replicate(1.,n_elements(f))],$
         [exp(-0.5*(x/a(1))^2)],$
         [(a(0)/a(2))*(x/a(2))^2*exp(-0.5*(x/a(2))^2)]]
end
pro radprof_moffat,x,a,f,pder
;to fit a Moffat

f=a(0)*(1.+(x/a(1))^2)^(-a(2))+a(3)
if n_params() ge 4 then $
   pder=[[(1.+(x/a(1))^2)^(-a(2))],$
         [(a(2)/a(1))*(f-a(3))*(x/a(1))^2/(1+(x/a(1))^2)],$
         [-alog(1+(x/a(1))^2)*(f-a(3))],$
         [replicate(1.,n_elements(f))]]
end



pro radprof_event,event
widget_control,event.id,get_uval=uval
case uval of
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='radprof'
   'CLOSE': widget_control,event.top,/destroy
   else: message,uval,/continue
endcase
end

pro radprof,event,REDISPLAY=redisplay,GROUP=group

disp=180                        ;x/y size of mini-display
xs=60                           ;x size of widget_labels
ys=12                           ;y size of widget_labels

if not keyword_set(REDISPLAY) then begin
   base=widget_base(title='Radial Profile',mbar=mbar,group=group,/col)
   
   filemenu=widget_button(mbar,value='File',/menu)
   close=widget_button(filemenu,value='Close',uval='CLOSE')
   helpmenu=widget_button(mbar,value='Help',/menu,/help)
   help=widget_button(helpmenu,value='Help',uval='HELP')
  
   top=widget_base(base,/row)
   row1=widget_base(top,/col,/frame)
   wdraw=widget_draw(row1,scr_xsize=disp,scr_ysize=disp)

   row2=widget_base(top,/col)
   pos=widget_base(row2,/col,/frame)
   l=widget_label(pos,value='Position')
   wx=cw_label(pos,'x =',xsize=xs,ysize=ys,/align_left)
   wy=cw_label(pos,'y =',xsize=xs,ysize=ys,/align_left)


   gauss=widget_base(row2,/col,/frame)
   l=widget_label(gauss,value='Gaussian')
   wgmax=cw_label(gauss,'Peak  =',xsize=xs,ysize=ys,/align_left)
   wgwid=cw_label(gauss,'Width =',xsize=xs,ysize=ys,/align_left)
   wgsky=cw_label(gauss,'Sky   =',xsize=xs,ysize=ys,/align_left)
   

   row3=widget_base(top,/col)
   moffat=widget_base(row3,/col,/frame)
   l=widget_label(moffat,value='Moffat')
   wmmax=cw_label(moffat,'Peak  =',xsize=xs,ysize=ys,/align_left)
   wmwid=cw_label(moffat,'Width =',xsize=xs,ysize=ys,/align_left)
   wmexp=cw_label(moffat,'Shape =',xsize=xs,ysize=ys,/align_left)
   wmsky=cw_label(moffat,'Sky   =',xsize=xs,ysize=ys,/align_left)



   widget_control,event.top,get_uval=pstate


   state={pstate:pstate,$
          wdraw:wdraw,$
          wgmax:wgmax,$
          wgwid:wgwid,$
          wgsky:wgsky,$
          wmmax:wmmax,$
          wmwid:wmwid,$
          wmexp:wmexp,$
          wmsky:wmsky,$
          wx:wx,$
          wy:wy}
   state=ptr_new(state,/no_copy)
          
   widget_control,base,set_uvalue=state
   (*pstate).wiraf.radprof=base
   widget_control,base,/realize
   xmanager,'radprof',base,/no_block
   if keyword_set(GROUP) then place_widget,(*pstate).wiraf.radprof,group
endif else begin
   widget_control,event.top,get_uval=pstate
   widget_control,(*pstate).wiraf.radprof,get_uval=state   
endelse





;Now do the radial plot we all came here for!

;get the coordinates
xy=convertxy(event,pstate)
x0=xy(0) & y0=xy(1)

;recenter to the nearest star!
cntrd,*(*pstate).img,x0,y0,xx,yy,(*pstate).prefs.iraf.fwhm,/silent
if xx eq -1 or finite(xx) eq 0 then begin
   t=dialog_message('Unable to centroid in x-axis!',/info,/cent,$
                    title='Centroid Error')
   return
endif
if yy eq -1 or finite(yy) eq 0 then begin
   t=dialog_message('Unable to centroid in y-axis!',/info,/cent,$
                    title='Centroid Error')
   return
endif
;present the recenter values
widget_control,(*state).wx,set_value=strcompress(string(xx,f='(F8.3)'),/rem)
widget_control,(*state).wy,set_value=strcompress(string(yy,f='(F8.3)'),/rem)

;extract a subimage
sz=size(*(*pstate).img,/dim)
nx=sz(0) & ny=sz(1)
len=((*pstate).prefs.iraf.maxrad+((*pstate).prefs.iraf.maxrad mod 2))
lxx=floor(xx) & lyy=floor(yy)
xx0=(lxx-len)>0 & xx1=(lxx+len-1)<(nx-1)
yy0=(lyy-len)>0 & yy1=(lyy+len-1)<(ny-1)
subim=(*(*pstate).img)(xx0:xx1,yy0:yy1)

;compute the sky level 
sky=(*pstate).sky.ave

;now build the X and Y-images
sz=size(subim,/dim)
nx=sz(0) & ny=sz(1)
xim=(findgen(nx)-(len-lxx+xx)) # replicate(1,ny)
yim=replicate(1,nx) # (findgen(ny)-(len-lyy+yy))

;now x,y are the vectors to plot!
x=reform(sqrt(xim*xim+yim*yim),nx*ny)
y=reform(subim,nx*ny)
w=fltarr(n_elements(y))+1.

;fitting vector
n=100
xfit=findgen(n)/(n-1)*(*pstate).prefs.iraf.maxrad

;Fit a Gaussian and update it's data
ag=[max(y),1.5,sky]
gres=curvefit(x,y,w,ag,func='radprof_gauss',status=gstat,/double)
radprof_gauss,xfit,ag,ygauss
widget_control,(*state).wgmax,set_value=strcompress(string(ag(0),f='(E8.2)'),/rem)
widget_control,(*state).wgwid,set_value=$
               strcompress(string(abs(ag(1)),f='(F6.3)'),/rem)
widget_control,(*state).wgsky,set_value=strcompress(string(ag(2),f='(E9.2)'),/rem)


;Fit a Moffat and update it's data
am=[max(y),1.5,2.,sky]
gmof=curvefit(x,y,w,am,func='radprof_moffat',status=gmof,/double)
radprof_moffat,xfit,am,ymoffat
widget_control,(*state).wmmax,set_value=strcompress(string(am(0),f='(E8.2)'),/rem)
widget_control,(*state).wmwid,set_value=$
               strcompress(string(abs(am(1)),f='(F6.3)'),/rem)
widget_control,(*state).wmexp,set_value=$
               strcompress(string(am(2),f='(F6.3)'),/rem)
widget_control,(*state).wmsky,set_value=strcompress(string(am(3),f='(E9.2)'),/rem)


;stuff for the plot
xr=[0,(*pstate).prefs.iraf.maxrad]
yr=[floor(min(y)),ceil(max(y))]
pos=[0.18,0.15,0.96,0.98]

widget_control,(*state).wdraw,get_val=wind
wset,wind

;definte the coordinate system
plot,[0],[0],xr=xr,yr=yr,xst=5,yst=5,pos=pos

;plot the models
loadct,39,/sil
oplot,xfit,ygauss,line=0,color=155,thick=2
oplot,xfit,ymoffat,line=2,color=254,thick=2
legend,['Gaussian','Moffat'],/right,box=0,margin=-0.3,line=[0,2],$
       color=[155,254],textcolor=255,thick=2
loadct,0,/sil

;plot the data
oplot,x,y,ps=4

;draw the axes
plot,[0],[0],xr=xr,yr=yr,xst=1,yst=1,pos=pos,/noerase,$
     xtit='Radius (pix)',ytit='Flux (inst.)',charsize=0.9,charthick=1


end
