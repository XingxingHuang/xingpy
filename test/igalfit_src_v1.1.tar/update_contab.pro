pro update_contab,state


  widget_control,(*state).wconfile,get_value=file
  file=strcompress(strlowcase(file(0)),/rem)
  if file eq '' then widget_control,(*state).wconfile,set_value='none'
  sens=(file ne 'none') and (file ne '')

;  widget_control,(*state).wlinkcons,sens=sens
  widget_control,(*state).waddcons,sens=sens
;  widget_control,(*state).weditcons,sens=sens
  widget_control,(*state).wremcon,sens=sens
  widget_control,(*state).wremallcon,sens=sens




end    
