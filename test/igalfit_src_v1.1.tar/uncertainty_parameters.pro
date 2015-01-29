pro uncertainty_parameters_event,event

widget_control,event.id,get_uval=uval
widget_control,event.top,get_uval=state
case uval of
   'RDNOISE': begin
      widget_control,(*state).wrdnoise,get_value=val & val=val(0)
      if isnumber(val) eq 0 then begin
         t=type_error('Read Noise')
         widget_control,(*state).wrdnoise,set_val=(*state).values.rdnoise
      endif else (*state).values.rdnoise=val
   end
   'GAIN': begin
      widget_control,(*state).wgain,get_value=val & val=val(0)
      if isnumber(val) eq 0 then begin
         t=type_error('Gain')
         widget_control,(*state).wgain,set_val=(*state).values.gain
      endif else (*state).values.gain=val
   end
   'NCOMBINE': begin
      widget_control,(*state).wncomb,get_value=val & val=val(0)
      if isnumber(val) ne 1 then begin
         t=type_error('N Combine')
         widget_control,(*state).wncomb,set_val=(*state).values.ncomb
      endif else (*state).values.ncomb=val
      print,(*state).values.ncomb
   end
   'CLOSE': widget_control,event.top,/destroy
   else:
endcase

end

;pro uncertainty_parameters_clean,wid
;  widget_control,wid,get_uval=state
;  ptr_free,state
;end

function uncertainty_parameters,group=group
  values={rdnoise:'5.2',gain:'7.0',ncomb:'1'}
  
  
  
  base=widget_base(group=group,/col,/align_center,title='Uncertainty')
  l=widget_label(base,value='Uncertainty Image Parameters')
  
  r=widget_base(base,/row)
  l=widget_label(r,value=' RDNOISE')
  wrdnoise=widget_text(r,value=values.rdnoise,/editable,xsize=8,uval='RDNOISE')
  
  r=widget_base(base,/row)
  l=widget_label(r,value='    GAIN')
  wgain=widget_text(r,value=values.gain,/editable,xsize=8,uval='GAIN')
  
  r=widget_base(base,/row)
  l=widget_label(r,value='NCOMBINE')
  wncomb=widget_text(r,value=values.ncomb,/editable,xsize=8,uval='NCOMBINE')
  
  r=widget_base(base,/row)
  c=widget_button(r,value='Close',uval='CLOSE')
   
  state={wrdnoise:wrdnoise,$
         wgain:wgain,$
         wncomb:wncomb,$
         values:values}
  state=ptr_new(state,/no_copy)
  if keyword_set(GROUP) then place_widget,base,group
  widget_control,base,/realize,set_uval=state

  widget_control,c,/input_focus,/show
  
  xmanager,'uncertainty_parameters',base

  if ptr_valid(state) then begin
     values=(*state).values
     ptr_free,state
  endif 


  return,values
end
