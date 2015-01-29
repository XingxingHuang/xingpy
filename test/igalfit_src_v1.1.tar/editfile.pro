pro editfile_clean,wid
widget_control,wid,get_uvalue=state
ptr_free,state
end
pro editfile_save,state

openw,l,(*state).file,error=error,/get_lun
if error ne 0 then begin
   t=writefile_error((*state).filetype)
   return
endif


widget_control,(*state).wtext,get_value=data
for i=0,n_elements(data)-1 do printf,l,data(i)
close,l & free_lun,l

(*state).saved=1b
end

pro editfile_close,state,topwid

if not (*state).saved then begin
   t=dialog_message('Do you want to exit without saving?',/cent,/ques,$
                    title='Save '+(*state).filetype)
   if t(0) eq 'Yes' then widget_control,topwid,/destroy
endif else widget_control,topwid,/destroy
end

pro editfile_event,event
widget_control,event.id,get_uvalue=uval
widget_control,event.top,get_uvalue=state
case uval of
   'TEXTEDIT': if event.type le 2 then (*state).saved=0b
   'SAVE': editfile_save,state
   'SAVECLOSE': begin
      editfile_save,state
      editfile_close,state,event.top
   end
   'CLOSE': editfile_close,state,event.top
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load=(*state).helpfile
   else:
endcase
end

pro editfile,file,GROUP=group,HELPFILE=helpfile,FILETYPE=filetype

if not keyword_set(HELPFILE) then helpfile='editfeed'
if not keyword_set(FILETYPE) then filetype='GalFit Feedme'

if not file_exist(file) then begin
   t=file_error(filetype)
   return
endif
readfmt,file,'(A1000)',data,/silent
data=strtrim(data)


base=widget_base(title='Edit '+filetype,group=group,mbar=mbar,/col)

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
       helpfile:helpfile,$
       filetype:filetype,$
       saved:1b}
state=ptr_new(state,/no_copy)
widget_control,base,set_uvalue=state
widget_control,base,/realize
xmanager,'editfile',base,cleanup='editfile_clean'


end
