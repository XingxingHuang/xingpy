function lineplot_combine,data,combine
n=n_elements(data)
center=(n mod 2)+(n/2)-1
case combine of
   'none': ret=data(cent)       ;center value
   'total': ret=total(data)     ;the total
   'median': ret=median(data)   ;the median
   'average': ret=avg(data)     ;the average
   'sigclip':  resistant_mean,data,3.,ret  ;sigma-cliped
   'stddev': ret=stdev(data)               ;std. dev.
   'stddevclip': ret=robust_sigma(data)    ;sig-clip std.dev
   else: ret=data(cent)
endcase
return,ret
end

pro lineplot_event,event
  widget_control,event.id,get_uval=uval
  case uval of
     'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                      group=event.top,load='lineplot'
     'CLOSE': widget_control,event.top,/destroy
     else: message,uval,/continue
  endcase
end

pro lineplot_clean,wid
  widget_control,wid,get_uval=state
  ptr_free,state
end

pro lineplot,event,orient,WIDTH=width,COMBINE=combine,RANGE=range,$
             REDISPLAY=redisplay,GROUP=group

if not keyword_set(WIDTH) then width=1
;if not keyword_set(COMBINE) then combine='total'
;if not keyword_set(RANGE) then range='full'

disp=180                        ;x and y size of mini-display
xs=65                           ;x size of widget_labels
ys=12                           ;y size of widget_labels
sunken=0b                       ;sunken look

if not keyword_set(REDISPLAY) then begin
   base=widget_base(title='Line Plot',mbar=mbar,group=group,/col)
  
   filemenu=widget_button(mbar,value='File',/menu)
   close=widget_button(filemenu,value='Close',uval='CLOSE')
   helpmenu=widget_button(mbar,value='Help',/menu,/help)
   help=widget_button(helpmenu,value='Help',uval='HELP')

   top=widget_base(base,/row)

   lhs=widget_base(top,/col,/frame)
   wdraw=widget_draw(lhs,scr_xsize=disp,scr_ysize=disp)

   rhs=widget_base(top,/column,/align_left,/frame)
   worient=cw_label(rhs,' Orient =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wwid=cw_label(rhs,'  Width =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wcomb=cw_label(rhs,'Combine =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   wrange=cw_label(rhs,'  Range =',xsize=xs,ysize=ys,sunken=sunken,/align_left)
   widget_control,event.top,get_uval=pstate
   state={pstate:pstate,$
          wdraw:wdraw,$
          worient:worient,$
          wwid:wwid,$
          wcomb:wcomb,$
          wrange:wrange}

   state=ptr_new(state,/no)
   (*pstate).wiraf.lineplot=base
   widget_control,base,/realize,set_uval=state
   xmanager,'lineplot',base,/no_block,clean='lineplot_clean'
   if keyword_set(GROUP) then place_widget,(*pstate).wiraf.lineplot,group
endif else begin
   widget_control,event.top,get_uval=pstate
   widget_control,(*pstate).wiraf.lineplot,get_uval=state
endelse




;Now display the statistics we all came here for
;get the coordinates
xy=convertxy(event,pstate)
x=fix(xy(0)) & y=fix(xy(1))

;image size
sz=size(*(*pstate).img,/dim)

;check to see if out of range
if x lt 0 or x gt sz(0)-1 or $
   y lt 0 or y gt sz(1)-1 then return


;do something based on the orientation
case orient of
   0: begin                     ;vertical cut

      x0=(x-((*pstate).prefs.iraf.width-1)/2)>0
      x1=(x+((*pstate).prefs.iraf.width-1)/2)<(sz(0)-1)
      
      case (*pstate).prefs.iraf.range of
         'full': begin
            y0=0
            y1=sz(1)-1
         end
         'viewable': begin
            (*pstate).oView->GetProperty,view=view
            y0=(floor(view(1)))>0
            y1=(y0+ceil(view(3)))<(sz(1)-1)
         end
      endcase
      ny=y1-y0
      xx=indgen(ny)+y0
      yy=fltarr(ny)
      for i=y0,y1-1 do begin
         ii=i-y0         
         yy(ii)=lineplot_combine((*(*pstate).img)(x0:x1,i),$
                                 (*pstate).prefs.iraf.combine)
      endfor

      type='vertical'
      xtit='Column (pix)'
   end
   1: begin                     ;horizontal cut
      y0=(y-((*pstate).prefs.iraf.width-1)/2)>0
      y1=(y+((*pstate).prefs.iraf.width-1)/2)<(sz(1)-1)
      
      case (*pstate).prefs.iraf.range of
         'full': begin
            x0=0
            x1=sz(0)-1
         end
         'viewable':begin
            (*pstate).oView->GetProperty,view=view
            x0=(floor(view(0)))>0
            x1=(x0+ceil(view(2)))<(sz(0)-1)
         end
      endcase
      nx=x1-x0
      xx=indgen(nx)+x0
      yy=fltarr(nx)
      for i=x0,x1-1 do begin
         ii=i-x0         
         yy(ii)=lineplot_combine((*(*pstate).img)(i,y0:y1),$
                                 (*pstate).prefs.iraf.combine)
      endfor

      type='Horizontal'
      xtit='Row (pix)'
   end
   else:
endcase

;now plot
xr=minmax(xx)
yr=minmax(yy)
pos=[0.22,0.18,0.95,0.95]

widget_control,(*state).wdraw,get_val=wind
wset,wind

plot,[0],[0],xr=xr,yr=yr,xst=5,yst=5,pos=pos
oplot,xx,yy

plot,[0],[0],xr=xr,yr=yr,xst=1,yst=1,pos=pos,$
     /noerase
xyouts,(pos(0)+pos(2))/2.,0.02,xtit,align=0.5,/normal
xyouts,0.05,(pos(1)+pos(3))/2.,'Flux',align=0.5,orient=90,/normal

;update the display
widget_control,(*state).worient,set_value=type
widget_control,(*state).wwid,set_value=strcompress(string($
               (*pstate).prefs.iraf.width,f='(I6)'),/rem)
widget_control,(*state).wcomb,set_value=(*pstate).prefs.iraf.combine
widget_control,(*state).wrange,set_value=(*pstate).prefs.iraf.range


end

