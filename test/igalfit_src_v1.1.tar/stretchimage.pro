pro stretchimage_clean,wid
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

pro stretchimage_event,event,GROUP=group

widget_control,event.id,get_uvalue=uval
widget_control,event.top,get_uval=state
pstate=(*state).pstate
case uval of
   'MINSLIDE': begin
      widget_control,(*state).wminslide,get_value=minval & minval=minval(0)
      widget_control,(*state).wmaxslide,get_value=maxval & maxval=maxval(0)
      if minval gt maxval then begin
         minval=maxval
         widget_control,(*state).wminslide,set_value=maxval
      endif
      widget_control,(*state).wminvalue,set_value=string(minval,f='(E+9.2)')
      (*pstate).lodisp=minval
      display_image,pstate
      if xregistered('pixhist',/noshow) then begin
         widget_control,(*pstate).wpixhist,get_uvalue=sstate
         plotpixhist,sstate,pstate
         widget_control,(*sstate).wloimdisp,set_val=string(minval,f='(E+11.4)')
       endif
   end
   'MAXSLIDE': begin
      widget_control,(*state).wminslide,get_value=minval & minval=minval(0)
      widget_control,(*state).wmaxslide,get_value=maxval & maxval=maxval(0)
      if maxval lt minval then begin
         maxval=minval
         widget_control,(*state).wmaxslide,set_value=minval
      endif
      widget_control,(*state).wmaxvalue,set_value=string(maxval,f='(E+9.2)')
      (*pstate).hidisp=maxval
      display_image,pstate
      if xregistered('pixhist',/noshow) then begin
         widget_control,(*pstate).wpixhist,get_uvalue=sstate
         plotpixhist,sstate,pstate
         widget_control,(*sstate).whiimdisp,set_val=string(maxval,f='(E+11.4)')
      endif
   end
   'BIASSLIDE': begin
      widget_control,(*state).wbiasslide,get_value=val & val=val(0)
      widget_control,(*state).wbiasvalue,set_value=string(val,f='(F4.2)')
      (*pstate).bias=val
      display_image,pstate
   end
   'CONSLIDE': begin
      widget_control,(*state).wconslide,get_value=val & val=val(0)
      widget_control,(*state).wconvalue,set_value=string(val,f='(F4.1)')
      (*pstate).cont=val
      display_image,pstate
   end


   'MINVALUE': begin      
      ismn=1b
      widget_control,(*state).wminvalue,get_value=minval & minval=minval(0)
      mnsep=strsplit(minval,'E',/extract)
      for i=0,n_elements(mnsep)-1 do ismn=ismn and (isnumber(mnsep(i)) ne 0)

      ismx=1b
      widget_control,(*state).wmaxvalue,get_value=maxval & maxval=maxval(0)
      mxsep=strsplit(maxval,'E',/extract)
      for i=0,n_elements(mxsep)-1 do ismx=ismx and (isnumber(mxsep(i)) ne 0)
      
      if ismn and ismx then begin
         minval=float(minval) & maxval=float(maxval)
         if minval gt maxval then begin
            minval=maxval
            widget_control,(*state).wminvalue,set_value=minval
         endif
         widget_control,(*state).wminslide,set_value=minval
         (*pstate).lodisp=minval
         display_image,pstate
         if xregistered('pixhist',/noshow) then begin
            print,minval
            widget_control,(*pstate).wpixhist,get_uvalue=sstate
            plotpixhist,sstate,pstate
            widget_control,(*sstate).wloimdisp,$
                           set_value=string(minval,f='(E+11.4)')
         endif
      endif
   end
   'MAXVALUE': begin
      ismn=1b
      widget_control,(*state).wminvalue,get_value=minval & minval=minval(0)
      mnsep=strsplit(minval,'E',/extract)
      for i=0,n_elements(mnsep)-1 do ismn=ismn and (isnumber(mnsep(i)) ne 0)

      ismx=1b
      widget_control,(*state).wmaxvalue,get_value=maxval & maxval=maxval(0)
      mxsep=strsplit(maxval,'E',/extract)
      for i=0,n_elements(mxsep)-1 do ismx=ismx and (isnumber(mxsep(i)) ne 0)
      
      if ismn and ismx then begin
         minval=float(minval) & maxval=float(maxval)
         if maxval lt minval then begin
            maxval=minval
            widget_control,(*state).wmaxvalue,set_value=maxval
         endif
         widget_control,(*state).wmaxslide,set_value=maxval
         (*pstate).hidisp=maxval
         display_image,pstate
         if xregistered('pixhist',/noshow) then begin
            widget_control,(*pstate).wpixhist,get_uvalue=sstate
            plotpixhist,sstate,pstate
            widget_control,(*sstate).whiimdisp,$
                           set_value=string(maxval,f='(E+11.4)')
         endif
      endif

   end
   'BIASVALUE': begin
      widget_control,(*state).wbiasvalue,get_value=val & val=val(0)
      if isnumber(val) ne 0 then begin
         val=float(val)
         if val lt 0. or val gt 1. then begin
            val=0.>val<1.
            widget_control,(*state).wbiasvalue,set_value=string(val,f='(F3.1)')
         endif
         widget_control,(*state).wbiasslide,set_value=val
         (*pstate).bias=val
         display_image,pstate
      endif
   end
   'CONVALUE': begin
      widget_control,(*state).wconvalue,get_value=val & val=val(0)
      if isnumber(val) ne 0 then begin
         val=float(val)
         if val lt 0. or val gt 1. then begin
            val=0.>val<1.
            widget_control,(*state).wconvalue,set_value=string(val,f='(F3.1)')
         endif
         widget_control,(*state).wconslide,set_value=val
         (*pstate).cont=val
         display_image,pstate
      endif
   end
   'CLOSE': widget_control,event.top,/destroy
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='stretchimage' 
   else: t=dialog_message(uval+' is not yet operational!',/error,/center)
endcase

end

pro stretchimage,pstate,group=group,BASE=base,BUTTON=button


base=widget_base(title='Manual Stretch',/column,mbar=mbar,group=group)

filemenu=widget_button(mbar,value='File',/menu)
close=widget_button(filemenu,value='Close',uvalue='CLOSE')

helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uvalue='HELP')

sliders=widget_base(base,/row)

d1=widget_base(sliders,/column,/base_align_center,/frame)
t=widget_label(d1,value='Minium')
wminslide=cw_fslider(d1,/vert,/drag,/suppress,/edit,uvalue='MINSLIDE',$
                     min=min(*(*pstate).img),max=max(*(*pstate).img),$
                     value=(*pstate).lodisp)
wminvalue=widget_text(d1,xsize=9,/edit,uvalue='MINVALUE',$
                     value=string((*pstate).lodisp,f='(E+9.2)'))

d2=widget_base(sliders,/column,/base_align_center,/frame)
t=widget_label(d2,value='Maximum')
wmaxslide=cw_fslider(d2,/vert,/drag,/suppress,/edit,uvalue='MAXSLIDE',$
                     min=min(*(*pstate).img),max=max(*(*pstate).img),$
                     value=(*pstate).hidisp)
wmaxvalue=widget_text(d2,xsize=9,/edit,uvalue='MAXVALUE',$
                     value=string((*pstate).hidisp,f='(E+9.2)'))


d3=widget_base(sliders,/column,/base_align_center,/frame)
t=widget_label(d3,value='Bias')
wbiasslide=cw_fslider(d3,/vert,/drag,/suppress,/edit,min=0,max=1.,$
                      uvalue='BIASSLIDE',value=(*pstate).bias)
wbiasvalue=widget_text(d3,xsize=4,/edit,uvalue='BIASVALUE',$
                       value=string((*pstate).bias,f='(F4.2)'))

d4=widget_base(sliders,/column,/base_align_center,/frame)
t=widget_label(d4,value='Contrast')
wconslide=cw_fslider(d4,/vert,/drag,/suppress,/edit,min=0,max=20.,$
                     uvalue='CONSLIDE',value=(*pstate).cont)
wconvalue=widget_text(d4,xsize=4,/edit,uvalue='CONVALUE',$
                     value=string((*pstate).cont,f='(F4.1)'))

if keyword_set(GROUP) then place_widget,base,group


widget_control,base,/realize

state={pstate:pstate,$
       wminslide:wminslide,$
       wminvalue:wminvalue,$
       wmaxslide:wmaxslide,$
       wmaxvalue:wmaxvalue,$
       wbiasslide:wbiasslide,$
       wbiasvalue:wbiasvalue,$
       wconslide:wconslide,$
       wconvalue:wconvalue,$
       wbutton:button}

widget_control,base,set_uvalue=ptr_new(state,/no_copy)
xmanager,'stretchimage',base,/no_block,clean='stretchimage_clean'



end
