pro editfeedme_clean,wid
widget_control,wid,get_uvalue=state
ptr_free,state
end
pro savefeedme,state

openw,l,(*state).file,error=error,/get_lun
if error ne 0 then begin
   t=writefile_error('GalFit Feedme')
;   t=dialog_message(['Unable to open the GalFit file for writing!',$
;                     !error_state.msg,$
;                     !error_state.sys_msg],/err,/cent,$
;                    title='Feedme File Error')
   return
endif


widget_control,(*state).wtext,get_value=data
for i=0,n_elements(data)-1 do printf,l,data(i)
close,l & free_lun,l

(*state).saved=1b
end

pro closegui,state,topwid

if not (*state).saved then begin
   t=dialog_message('Do you want to exit without saving?',/cent,/ques,$
                    title='Save FeedMe?')
   if t(0) eq 'Yes' then widget_control,topwid,/destroy
endif else widget_control,topwid,/destroy
end

pro editfeedme_event,event
widget_control,event.id,get_uvalue=uval
widget_control,event.top,get_uvalue=state
case uval of
   'TEXTEDIT': if event.type le 2 then (*state).saved=0b
   'SAVE': savefeedme,state
   'SAVECLOSE': begin
      savefeedme,state
      closegui,state,event.top
   end
   'CLOSE': closegui,state,event.top
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='editfeed'
   else:
endcase
end

pro editfeedme,file,GROUP=group
if not file_exist(file) then begin
   t=file_error('FeedMe')
   return
endif
readfmt,file,'(A1000)',data,/silent & data=strtrim(data)


base=widget_base(title='Edit GalFit FeedMe File',group=group,mbar=mbar,/col)

filemenu=widget_button(mbar,value='File',/menu)
close=widget_button(filemenu,value='Close',uval='CLOSE')

helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uval='HELP')


wtext=widget_text(base,value=data,xsize=80,ysize=30,/editable,/scroll,$
                 uvalue='TEXTEDIT',/all_event)


row=widget_base(base,/row)
s=widget_button(row,value='Save',uvalue='SAVE')
sc=widget_button(row,value='Save and Close',uvalue='SAVECLOSE')
c=widget_button(row,value='Close',uvalue='CLOSE')

state={file:file,$
       wtext:wtext,$
       saved:1b}
state=ptr_new(state,/no_copy)
widget_control,base,set_uvalue=state
widget_control,base,/realize
xmanager,'editfeedme',base,cleanup='editfeedme_clean'


end
