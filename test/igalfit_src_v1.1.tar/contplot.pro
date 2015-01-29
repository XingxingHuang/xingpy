pro contplot_event,event
widget_control,event.id,get_uval=uval
case uval of
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='contplot'
   'CLOSE': widget_control,event.top,/destroy
   else: message,uval,/continue
endcase


end

pro contplot,event,REDISPLAY=redisplay,GROUP=group

xs=60                           ;x size of widget_labels
ys=12                           ;y size of widget_labels

if not keyword_set(REDISPLAY) then begin

   base=widget_base(title='Contour Plot',mbar=mbar,group=group,/col)
   
   filemenu=widget_button(mbar,value='File',/menu)
   close=widget_button(filemenu,value='Close',uval='CLOSE')
   helpmenu=widget_button(mbar,value='Help',/menu,/help)
   help=widget_button(helpmenu,value='Help',uval='HELP')

   wdraw=widget_draw(base,xsize=200,ysize=200)

   widget_control,event.top,get_uval=pstate
   state={pstate:pstate,$
          wdraw:wdraw}

   state=ptr_new(state,/no_copy)
   widget_control,base,set_uval=state,/realize
   (*pstate).wiraf.contplot=base
   xmanager,'contplot',base,/no_block
   if keyword_set(GROUP) then place_widget,(*pstate).wiraf.contplot,group
endif else begin
   widget_control,event.top,get_uval=pstate
   widget_control,(*pstate).wiraf.contplot,get_uval=state
endelse
   



;get the coordinates
xy=convertxy(event,pstate)
x=xy(0) & y=xy(1)

;cut the stamp
sub=cutstamp(*(*pstate).img,x,y,(*pstate).prefs.iraf.consize)
if n_elements(sub) eq 1 then return

nticks=(*pstate).prefs.iraf.nticks
ticks=(findgen(nticks)-(nticks-1)/2)
ticks=ticks/max(ticks)*(*pstate).prefs.iraf.consize
xticks=string(x+ticks,f='(I3)')
yticks=string(y+ticks,f='(I3)')

;display the contour:
pos=[0.18,0.18,0.97,0.97]
widget_control,(*state).wdraw,get_val=win
wset,win
contour,sub,nlevels=(*pstate).prefs.iraf.nlevels,$
        xtit='Col (pix)',ytit='Row (pix)',pos=pos,$
        xtickname=xticks,xticks=nticks-1,$
        ytickname=yticks,yticks=nticks-1

;overplot the image boundaries
;sz=size(*(*pstate).img,/dim)
;loadct,13,/sil
;plots,0>([0,sz(0),sz(0),0,0]-x)<(2*(*pstate).prefs.iraf.consize),$
;      0>([0,0,sz(1),sz(1),0]-y)<(2*(*pstate).prefs.iraf.consize),$
;      line=0,colo=255
;loadct,0,/sil        

end
