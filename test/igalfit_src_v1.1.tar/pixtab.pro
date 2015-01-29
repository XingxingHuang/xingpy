pro pixtab_clean,wid
widget_control,wid,get_uval=state
if widget_info((*state).wbutton,/valid_id) then $
   widget_control,(*state).wbutton,set_button=0b

names=tag_names(*state)
for i=0,n_tags(*state)-1 do begin
   if names(i) ne 'PSTATE' then begin
      case size((*state).(i),/tname) of
         'POINTER': ptr_free,(*state).(i)
         'OBJREF': obj_destroy,(*state).(i)
         else:
      endcase
   endif
endfor
ptr_free,state

end
pro pixtab_event,event
widget_control,event.id,get_uvalue=uval
case uval of
   'CLOSE': widget_control,event.top,/destroy
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='pixtab'
   else:
endcase
end

pro pixtab,pstate,GROUP=group,BASE=base,BUTTON=button
if not keyword_set(BUTTON) then button=-1L
nrow=5 & xsize=405
ncol=5 & ysize=132
data=fltarr(nrow,ncol)

base=widget_base(title='Pixel Table',group=group,mbar=mbar,/col)

filemenu=widget_button(mbar,value='File',/menu)
close=widget_button(filemenu,value='Close',uval='CLOSE')
helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uval='HELP')

wtable=widget_table(base,value=data,xsize=nrow,ysize=ncol,$
                    scr_xsize=xsize,scr_ysize=ysize)
widget_control,wtable,set_table_select=([nrow,ncol,nrow,ncol]-1)/2,$
               set_text_select=([nrow,ncol]-1)/2

state={pstate:pstate,$
       wtable:wtable,$
       wbutton:button}
state=ptr_new(state,/no_copy)
widget_control,base,set_uvalue=state


if keyword_set(GROUP) then place_widget,base,group  



widget_control,base,/realize
xmanager,'pixtab',base,/no_block,cleanup='pixtab_clean'


end
