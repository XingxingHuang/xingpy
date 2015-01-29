pro imstat_event,event
widget_control,event.id,get_uval=uval
case uval of
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='imstat'
   'CLOSE': widget_control,event.top,/destroy
   else: message,uval,/continue
endcase
end

pro imstat_clean,wid
  widget_control,wid,get_uval=state
  ptr_free,state
end

pro imstat,event,BOXSIZE=boxsize,$
           REDISPLAY=redisplay,GROUP=group

disp=180                        ;x and y size of mini-display
xs=65                           ;x size of widget_labels
ys=12                           ;y size of widget_labels
sunken=0b                       ;sunken look

if not keyword_set(REDISPLAY) then begin
   base=widget_base(TITLE='Image Statistics',MBAR=mbar,GROUP=group,/col)
   
   filemenu=widget_button(mbar,value='File',/menu)
   close=widget_button(filemenu,value='Close',uval='CLOSE')
   helpmenu=widget_button(mbar,value='Help',/menu,/help)
   help=widget_button(helpmenu,value='Help',uval='HELP')
   
   top=widget_base(base,/row)
   lhs=widget_base(top,/col,/frame)
   wdraw=widget_draw(lhs,scr_xsize=disp,scr_ysize=disp)
   
   mid=widget_base(top,/column,/align_left,/frame)
   wtot=cw_label(mid,'Total=',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wmin=cw_label(mid,'Min  =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wmax=cw_label(mid,'Max  =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wxr=cw_label(mid,'xr   =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wyr=cw_label(mid,'yr   =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wnpix=cw_label(mid,'Npix =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   
   rhs=widget_base(top,/column,/align_left,/frame)
   wave=cw_label(rhs,'Ave   =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wmed=cw_label(rhs,'Med   =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wrave=cw_label(rhs,'ResAve=',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wstd=cw_label(rhs,'Std   =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wrstd=cw_label(rhs,'ResStd=',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wskew=cw_label(rhs,'Skew  =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wkurt=cw_label(rhs,'Kurt  =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   
;   widget_control,base,/realize
   widget_control,event.top,get_uval=pstate

   state={pstate:pstate,$
          wtot:wtot,$
          wmin:wmin,$
          wmax:wmax,$
          wxr:wxr,$
          wyr:wyr,$
          wnpix:wnpix,$
          wave:wave,$
          wmed:wmed,$
          wrave:wrave,$
          wstd:wstd,$
          wrstd:wrstd,$
          wskew:wskew,$
          wkurt:wkurt,$
          wdraw:wdraw}
   state=ptr_new(state,/no_copy)
   
   (*pstate).wiraf.imstat=base
   widget_control,base,/realize,set_uval=state  
   xmanager,'imstat',base,/no_block,clean='imstat_clean'
   if keyword_set(GROUP) then place_widget,(*pstate).wiraf.imstat,group
endif else begin
   widget_control,event.top,get_uval=pstate
   widget_control,(*pstate).wiraf.imstat,get_uval=state   
endelse


;Now display the statistics we all came here for
;get the coordinates
xy=convertxy(event,pstate)
x=fix(xy(0)) & y=fix(xy(1))

;;cut out the subimage
;sz=size(*(*pstate).img,/dim)
;
;;guard against clicking outside the image!
;if x gt sz(0)-1 or x lt 0 or y gt sz(1)-1 or y lt 0 then return

sub=cutstamp(*(*pstate).img,x,y,(*pstate).prefs.iraf.boxsize,$
             i0=i0,i1=i1,j0=j0,j1=j1)
if n_elements(sub) eq 1 then return

;only compute stats for the region with actual data!
g=where(sub ne 0 and finite(sub),npix)
if npix lt 10 then return

;ranges
xr=strcompress('['+string(i0,f='(I6)')+','+string(i1,f='(I6)')+']',/rem)
yr=strcompress('['+string(j0,f='(I6)')+','+string(j1,f='(I6)')+']',/rem)


fltfmt='(E+10.3)'

if not keyword_set(NSIG) then nsig=3 

;Zeroth moment things:
tot=total(sub(g))               ;total flux
widget_control,(*state).wtot,set_val=strcompress(string(tot,f=fltfmt),/rem)
;npix=n_elements(sub)            ;number of pixels
widget_control,(*state).wnpix,set_val=strcompress(string(npix,f='(I7)'),/rem)
minval=min(sub(g))              ;min value
widget_control,(*state).wmin,set_val=strcompress(string(minval,f=fltfmt),/rem)
maxval=max(sub(g))              ;max value
widget_control,(*state).wmax,set_val=strcompress(string(maxval,f=fltfmt),/rem)

;ranges
widget_control,(*state).wxr,set_val=xr
widget_control,(*state).wyr,set_val=yr

;First moment things:
ave=tot/npix                    ;average value
widget_control,(*state).wave,set_val=strcompress(string(ave,f=fltfmt),/rem)
med=median(sub(g))              ;median value
widget_control,(*state).wmed,set_val=strcompress(string(med,f=fltfmt),/rem)
resistant_mean,sub(g),nsig,rave ;outlier resistant average
widget_control,(*state).wrave,set_val=strcompress(string(rave,f=fltfmt),/rem)

;Second moment things:
std=stdev(sub(g))               ;standard deviation
widget_control,(*state).wstd,set_val=strcompress(string(std,f=fltfmt),/rem)
rstd=robust_sigma(sub(g))       ;outlier resistant std. dev.
widget_control,(*state).wrstd,set_val=strcompress(string(rstd,f=fltfmt),/rem)

;Higher order moments:
sub=temporary(sub)-ave
skew=avg(sub(g)^3)/avg(sub(g)^2)^(1.5) ;skewness
widget_control,(*state).wskew,set_val=strcompress(string(skew,f=fltfmt),/rem)
kurt=(avg(sub(g)^4)/avg(sub(g)^2)^2)-3. ;kurtosis
widget_control,(*state).wkurt,set_val=strcompress(string(kurt,f=fltfmt),/rem)

;display the image
geom=widget_info((*state).wdraw,/geom)
tv,255b-bytscl(congrid(sub,geom.xsize,geom.ysize),$
               rave-3*rstd,rave+10*rstd)


end
