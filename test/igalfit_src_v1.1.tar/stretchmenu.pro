pro stretchmenu,event
widget_control,event.top,get_uval=state

if ~ptr_valid((*state).img) then begin
   t=dialog_message(['There is no image loaded.',$
                     'Load an image before you stretch one.'],/error,$
                    /center,tit='Stetch Image')
   return
endif


;find the box that got checked
g=(where((*state).wstretch eq event.id))(0)
(*state).stretch=(*state).stretches(g)

;uncheck all the boxesk
for i=0,n_elements((*state).stretches)-1 do $
   widget_control,(*state).wstretch(i),set_button=0b

;recheck the one that was clicked
widget_control,(*state).wstretch(g),set_button=1b

;set the new stretch
case (*state).stretch of
   'auto-scale': begin
      autoscale,state
      if xregistered('stretchimage',/noshow) then begin

      endif
   end
   'minmax': begin
      (*state).lodisp=min(*(*state).img,/nan)
      (*state).hidisp=max(*(*state).img,/nan)
      if xregistered('stretchimage',/noshow) then begin

      endif
   end
   'User': begin
      if xregistered('stretchimage') eq 0 then begin
         stretchimage,state,group=event.top,base=stretchbase,$
                      button=(*state).wuserstretch
         widget_control,event.top,/show
         (*state).wstretchbase=stretchbase
         widget_control,(*state).wuserstretch,set_button=1b
      endif
   end
   else: begin
      t=dialog_message(['Encountered an unknown stretch',$
                        'Defaulting to autoscale'],/center,/error,$
                       title='Unknown Stretch')
      autoscale,state
   end
end

;display the image
display_image,state

end
