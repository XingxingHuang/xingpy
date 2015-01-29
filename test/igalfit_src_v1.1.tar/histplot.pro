pro histplot_event,event
widget_control,event.id,get_uval=uval
case uval of
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='histplot'
   'CLOSE': widget_control,event.top,/destroy
   else: message,uval,/continue
endcase


end

pro histplot,event,REDISPLAY=redisplay,GROUP=group


if not keyword_set(REDISPLAY) then begin

   base=widget_base(title='Histogram Plot',mbar=mbar,group=group,/col)
   
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
   (*pstate).wiraf.histplot=base
   xmanager,'histplot',base,/no_block
   if keyword_set(GROUP) then place_widget,(*pstate).wiraf.histplot,group
endif else begin
   widget_control,event.top,get_uval=pstate
   widget_control,(*pstate).wiraf.histplot,get_uval=state
endelse
   



;get the coordinates
xy=convertxy(event,pstate)
x=xy(0) & y=xy(1)

;cut the stamp
sub=cutstamp(*(*pstate).img,x,y,(*pstate).prefs.iraf.hissize)
if n_elements(sub) eq 1 then return

nticks=(*pstate).prefs.iraf.nticks
ticks=(findgen(nticks)-(nticks-1)/2)
ticks=ticks/max(ticks)*(*pstate).prefs.iraf.consize
xticks=string(x+ticks,f='(I3)')
yticks=string(y+ticks,f='(I3)')

;compute histogram
h=histogram(sub,locations=b,nbin=(*pstate).prefs.iraf.nbins,/nan)

;wset,(*state).wdraw

;display the graph
widget_control,(*state).wdraw,get_value=win
wset,win
pos=[0.18,0.18,0.97,0.97]
plot,b,h,pos=pos,xtit='Pixel Brightness',ytit='Number (pix)',ps=10



end
