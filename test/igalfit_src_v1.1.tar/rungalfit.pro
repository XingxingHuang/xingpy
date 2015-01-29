pro rungalfit,event
widget_control,event.top,get_uvalue=state


;first check if galfit is in the path
;widget_control,(*state).wgfexec,get_value=gfexec & gfexec=gfexec(0)
gfexec=(*state).prefs.exec
res=(file_which(getenv('PATH'),gfexec))(0)
if res eq '' then begin
   t=dialog_message('GalFit executable is not in your path!',/err,/center)
   return
endif

;okay, now build the feedme file
if not mkgalfit(state) then begin
   widget_control,(*state).wgalfit,set_button=0b
   return
endif

;okay, now build the constraint file
if not mkconstraints(state) then begin
   widget_control,(*state).wgalfit,set_button=0b
   return
endif

;build the GalFit Command
widget_control,hourglass=1b

;for the error message:
errtitle='GalFit Error'

;prepare the images
if not prepare_images(state,GROUP=event.top) then stop

cmd=gfexec+' '+(*state).prefs.feedme
if widget_info((*state).wsilent,/button_set) then cmd=cmd+' > /dev/null'
spawn,cmd,exit_status=stat      ;here's the call to galfit!!!!
case stat of
   0:
   100: begin
      t=dialog_message(atombomb(),/err,/cen,tit=errtitle)
      return
   end
   139: begin
      t=dialog_message('Segmentation Fault!',/err,/cen,tit=errtitle)
      return
   end
   else: t=dialog_message(['You have encountered an unexpected GalFit exit '+$
                           'code.','Please email this to Russell and a brief',$
                           'description of what was going on.','',$
                           'exit code: '+$
                           strcompress(string(stat,f='(I4)'),/rem)],/err,/cent,$
                          tit=errtitle)
   endcase
widget_control,hourglass=0b



;clean up?
if widget_info((*state).wclean,/button_set) then begin
   ;clean up the constraints file
   widget_control,(*state).wconfile,get_value=confile
   if confile(0) ne 'none' then file_delete,confile(0),/allow_non

   ;get last galfit file
   lastgalfit,gfrestart
   file_delete,'fit.log',gfrestart,/allow_non

   ;delete BPX?

   ;delete imgblock file?
   
   ;delete constraints file?

endif

;display results?
if widget_info((*state).wdisp,/button_set) then begin
   widget_control,(*state).wout,get_value=imgblock & imgblock=imgblock(0)
   if imgblock(0) eq '' then begin
         t=file_error('imgblock',/blank)
         return
      endif
   if not file_exist(imgblock(0)) then begin
      t=file_error('imgblock')
      return
   endif
   xr=xregistered('galfit_results')
   
   galfit_results,imgblock=imgblock(0),base=base,group=event.top,$
                  redisplay=xr,button=(*state).wgalfit
   if ~xr then (*state).wresults=base
endif





end
