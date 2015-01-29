pro plotpixhist,state,pstate


ylog=widget_info((*state).wyscale,/combobox_gettext) eq 'Log'

yr=[(ylog?1.:0.),1.1*max(*(*pstate).hist)]

xr=(*state).binrange
plot,*(*pstate).bins,*(*pstate).hist,ps=10,xst=1,$
     xr=xr,ylog=ylog,yr=yr,yst=1,$
     xtit='Pixel Value',ytit='Number of Pixels',$
     pos=[0.14,0.15,0.99,0.98]

loadct,13,/silent
oplot,min(xr)>replicate((*pstate).lodisp,2)<(*pstate).hidisp,yr,col=255
oplot,(*pstate).lodisp>replicate((*pstate).hidisp,2)<max(xr),yr,col=155
loadct,0,/sil


end

pro pixhist_close,wid
widget_control,wid,get_uval=state
if widget_info((*state).wbutton,/valid_id) then $
   widget_control,(*state).wbutton,set_button=0b

end

pro setlimits,state,pstate,type

nl=n_elements((*state).limits)

;turn all the buttons off
for i=0,nl-1 do widget_control,(*state).wlimit(i),set_button=0b

;turn on the set button
g=(where((*state).limits eq type))(0)
widget_control,(*state).wlimit(g),set_button=1b

;save the type for later use
(*pstate).limit=type
end

pro pixhist_event,event,GROUP=group

widget_control,event.id,get_uvalue=uval

case uval of

   'DRAW': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      case event.type of 0: begin
            widget_control,(*state).wdraw,get_draw_view=view
            x=event.x+view(0) & y=event.y+view(1)
            c0=convert_coord((*pstate).lodisp,0.,/data,/to_device)
            c1=convert_coord((*pstate).hidisp,0.,/data,/to_device)

            dx0=abs(x-c0(0))
            dx1=abs(x-c1(0))

            if dx0 le 32 and dx0 le dx1 then (*state).grabbed=0
            if dx1 le 32 and dx0 ge dx1 then (*state).grabbed=1
         end
         1: begin
            case (*state).grabbed of
               0: begin                  
                  widget_control,(*state).wdraw,get_draw_view=view
                  x=event.x+view(0) & y=event.y+view(1)
                  newx=(convert_coord(x,0,/device,/to_data))(0)
                  val=(newx<(*pstate).hidisp)
                  (*pstate).lodisp=val
                  widget_control,(*state).wloimdisp,$
                                 set_value=string(newx,f='(E+11.4)')
                  plotpixhist,state,pstate
                  setlimits,state,pstate,'User'
                  (*state).grabbed=-1
                  display_image,pstate
                  if xregistered('stretchimage',/noshow) then begin
                     widget_control,(*pstate).wstretchbase,get_uval=sstate
                     widget_control,(*sstate).wminslide,set_value=val
                     widget_control,(*sstate).wminvalue,set_value=$
                                    string(val,f='(E+9.2)')
                  endif
               end
               1: begin
                  widget_control,(*state).wdraw,get_draw_view=view
                  x=event.x+view(0) & y=event.y+view(1)
                  newx=(convert_coord(x,0,/device,/to_data))(0)
                  val=(newx>(*pstate).lodisp)
                  (*pstate).hidisp=val
                  widget_control,(*state).whiimdisp,$
                                 set_value=string(newx,f='(E+11.4)')
                  setlimits,state,pstate,'User'
                  plotpixhist,state,pstate
                  (*state).grabbed=-1
                  display_image,pstate
                  if xregistered('stretchimage',/noshow) then begin
                     widget_control,(*pstate).wstretchbase,get_uval=sstate
                     widget_control,(*sstate).wmaxslide,set_value=val
                     widget_control,(*sstate).wmaxvalue,set_value=$
                                    string(val,f='(E+9.2)')
                  endif

               end
               else: break
            endcase
         end
         else: break
      endcase
   end
   'LOIMDISP':begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).wloimdisp,get_value=val & val=float(val(0))
      (*pstate).lodisp=val
      setlimits,state,pstate,'User'
      plotpixhist,state,pstate
      display_image,pstate      
      if xregistered('stretchimage',/noshow) then begin
         widget_control,(*pstate).wstretchbase,get_uval=sstate
         widget_control,(*sstate).wminslide,set_value=val
         widget_control,(*sstate).wminvalue,set_value=string(val,f='(E+9.2)')
      endif
   end
   'HIIMDISP': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).whiimdisp,get_value=val & val=float(val(0))
      (*pstate).hidisp=val
      setlimits,state,pstate,'User'
      plotpixhist,state,pstate
      display_image,pstate
      if xregistered('stretchimage',/noshow) then begin
         widget_control,(*pstate).wstretchbase,get_uval=sstate
         widget_control,(*sstate).wmaxslide,set_value=val
         widget_control,(*sstate).wmaxvalue,set_value=string(val,f='(E+9.2)')
      endif
   end

   'LOHISTDISP': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wlohistdisp,get_value=val
      (*state).binrange(0)=float(val)
      plotpixhist,state,(*state).pstate
   end
   'HIHISTDISP': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).whihistdisp,get_value=val
      (*state).binrange(1)=float(val)
      plotpixhist,state,(*state).pstate
   end
   'LOHIST':begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wlohist,get_val=val
      pstate=(*state).pstate
      (*pstate).histminx=float(val)
      (*pstate).hist=ptr_new(histogram(*(*pstate).img,locations=bin,$
                                       min=(*pstate).histminx,$
                                       max=(*pstate).histmaxx,$
                                       bin=(*pstate).histbinx))
      (*pstate).bins=ptr_new(temporary(bin))
      plotpixhist,state,pstate
   end
   'HIHIST':begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).whihist,get_val=val
      pstate=(*state).pstate
      (*pstate).histmaxx=float(val)
      (*pstate).hist=ptr_new(histogram(*(*pstate).img,locations=bin,$
                                       min=(*pstate).histminx,$
                                       max=(*pstate).histmaxx,$
                                       bin=(*pstate).histbinx))
      (*pstate).bins=ptr_new(temporary(bin))
      plotpixhist,state,pstate
   end
   'DXHIST':begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wdxhist,get_val=val
      pstate=(*state).pstate
      (*pstate).histbinx=float(val)
      (*pstate).hist=ptr_new(histogram(*(*pstate).img,locations=bin,$
                                       min=(*pstate).histminx,$
                                       max=(*pstate).histmaxx,$
                                       bin=(*pstate).histbinx))
      (*pstate).bins=ptr_new(temporary(bin))
      plotpixhist,state,pstate
   end
   'YSCALE': begin
      widget_control,event.top,get_uval=state
      plotpixhist,state,(*state).pstate
   end
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='pixhist'
   'LIMITS': begin
      widget_control,event.top,get_uval=state
      g=(where((*state).wlimit eq event.id))(0)
      
      n=n_elements((*state).limits)
;      isset=bytarr(n)
;      for i=0,n-1 do isset(i)=widget_info((*state).wlimit(i),/button_set)
;      g=(where(isset))(0)
      if g ne -1 then begin
         pstate=(*state).pstate
         setlimits,state,pstate,(*state).limits(g)
         
         case strupcase((*state).limits(g)) of
            'MINMAX': begin
                ;do the minmax
               (*pstate).lodisp=min(*(*pstate).img,/nan)
               (*pstate).hidisp=max(*(*pstate).img,/nan)
            end
            '99%': begin
               print,'not yet functional'
            end
            '90%': begin
               print,'not yet functional'
            end
            '68%': begin
               print,'not yet functional'
            end
            '50%': begin
               print,'not yet functional'
            end
            'USER': begin
               
            end
            'AUTO': autoscale,pstate
            else: break
         endcase
         ;update the widget
         widget_control,(*state).wloimdisp,$
                        set_value=string((*pstate).lodisp,f='(E+11.4)')
         widget_control,(*state).whiimdisp,$
                        set_value=string((*pstate).hidisp,f='(E+11.4)')


         ;replot and redraw
         plotpixhist,state,(*state).pstate
         display_image,(*state).pstate
      endif
   end
   'CLOSE': widget_control,event.top,/destroy
   else: print,uval
endcase

end

pro pixhist,pstate,group=group,BUTTON=button,BASE=base

if not ptr_valid((*pstate).hist) then begin
   ;the data are set to initial values
   dif=(*pstate).hidisp-(*pstate).lodisp
   (*pstate).histminx=(*pstate).lodisp-dif/2.
   (*pstate).histmaxx=(*pstate).hidisp+dif/2.
   (*pstate).histbinx=((*pstate).histmaxx-(*pstate).histminx)/1000.
   binrange=[(*pstate).histminx,(*pstate).histmaxx]
endif else binrange=minmax(*(*pstate).bins)

xsize=375
ysize=200

base=widget_base(group=group,title='Pixel Histogram',mbar=mbar,/column)

filemenu=widget_button(mbar,value='File',/menu)
close=widget_button(filemenu,value='Close',uval='CLOSE')

limitmenu=widget_button(mbar,value='Limits',/menu)
limits=(*pstate).limits;['MinMax','99%','90%','68%','50%','Auto','User']
wlimit=lonarr(n_elements(limits))
for i=0,n_elements(limits)-1 do $
   wlimit(i)=widget_button(limitmenu,value=limits(i),/checked,uval='LIMITS')


h=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(h,value='Help',uvalue='HELP')


wdraw=widget_draw(base,xsize=xsize,ysize=ysize,uval='DRAW',frame=5,/button)

ctrl=widget_base(base,/column,xsize=xsize)
row=widget_base(ctrl,/row,/align_center)

imgdisp=widget_base(row,/column,/frame)
t=widget_label(imgdisp,value='Image Display')
imgdisp1=widget_base(imgdisp,/row)
l=widget_label(imgdisp1,value='Lo:')
wloimdisp=widget_text(imgdisp1,value=string((*pstate).lodisp,f='(E+11.4)'),$
                      /edit,xsize=11,uvalue='LOIMDISP')
               
imgdisp2=widget_base(imgdisp,/row)
l=widget_label(imgdisp2,value='Hi:')
whiimdisp=widget_text(imgdisp2,value=string((*pstate).hidisp,f='(E+11.4)'),$
                      /edit,xsize=11,uvalue='HIIMDISP')




histdisp=widget_base(row,/column,/frame)
t=widget_label(histdisp,value='Hist Display')
histdisp1=widget_base(histdisp,/row)
l=widget_label(histdisp1,value='Lo:')
wlohistdisp=widget_text(histdisp1,value=string(binrange(0),f='(E+11.4)'),$
                        /edit,xsize=11,uvalue='LOHISTDISP')
               
histdisp2=widget_base(histdisp,/row)
l=widget_label(histdisp2,value='Hi:')
whihistdisp=widget_text(histdisp2,value=string(binrange(1),f='(E+11.4)'),$
                        /edit,xsize=11,uvalue='HIHISTDISP')
histdisp3=widget_base(histdisp,/row)
l=widget_label(histdisp3,value='YScl:')
wyscale=widget_combobox(histdisp3,value=['Linear','Log'],$
                        xsize=70,UVAL='YSCALE')

histset=widget_base(row,/column,/frame)
l=widget_label(histset,value='Hist Settings')
histset1=widget_base(histset,/row)
l=widget_label(histset1,value='Lo:')
wlohist=widget_text(histset1,value=string((*pstate).histminx,f='(E+11.4)'),$
                        /editable,xsize=11,uvalue='LOHIST')
histset2=widget_base(histset,/row)
l=widget_label(histset2,value='Hi:')
whihist=widget_text(histset2,value=string((*pstate).histmaxx,f='(E+11.4)'),$
                        /editable,xsize=11,uval='HIHIST')
histset3=widget_base(histset,/row)
l=widget_label(histset3,value='dx:')
wdxhist=widget_text(histset3,value=string((*pstate).histbinx,f='(E+11.4)'),$
                        /edit,xsize=11,uvalue='DXHIST')
        


state={pstate:pstate,$            ;state of the parent widget
       wdraw:wdraw,$              ;draw widget
       binrange:binrange,$        ;xrange of plot
       wloimdisp:wloimdisp,$      ;Img disp lo box
       whiimdisp:whiimdisp,$      ;Img disp hi box
       wlohistdisp:wlohistdisp,$  ;hist disp lo box
       whihistdisp:whihistdisp,$  ;hist disp hi box
       wyscale:wyscale,$          ;y-scale combobox
       wlohist:wlohist,$          ;hist lo val
       whihist:whihist,$          ;hist hi val
       wdxhist:wdxhist,$          ;hist binsize
       limits:limits,$              ;limits
       wlimit:wlimit,$            ;widget IDs of limits
       grabbed:-1,$               ;do have a limit-line selected
       wbutton:button}            ;widget id of the button from main GUI      

state=ptr_new(state,/no_copy)
widget_control,base,set_uvalue=state


;set initial state
setlimits,state,pstate,(*pstate).limit

;reposition the widget
if keyword_set(GROUP) then place_widget,base,group

widget_control,base,/realize

;plot
(*pstate).hist=ptr_new(histogram(*(*pstate).img,locations=bin,$
                                 min=(*pstate).histminx,$
                                 max=(*pstate).histmaxx,$
                                 bin=(*pstate).histbinx))
(*pstate).bins=ptr_new(temporary(bin))
plotpixhist,state,pstate
setlimits,state,pstate,(*pstate).limit

;hand off to the xmanager
xmanager,'pixhist',base,/no_block,cleanup='pixhist_close'

end

