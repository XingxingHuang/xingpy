pro displaymenu,event
widget_control,event.top,get_uvalue=state

;find the one they clicked on
g=(where((*state).wimage eq event.id))(0)

;now do something per each item:
type=(*state).images(g)
case type of
   'Science': res=loadfits(event,(*state).setfile.sci,type,/display)
   'Uncertainty': res=loadfits(event,(*state).setfile.unc,type,/display)
   'PSF': begin
      res=loadfits(event,(*state).setfile.psf,type,/display)
      if res then (*state).oROIModel->SetProperty,hide=1b
   end
   'BPX': begin
      widget_control,(*state).wbpx,get_value=file & file=file(0)
      if not file_exist(file) then begin
         res=0b
         t=dialog_message('The BPX file does not exist.',/error,/center)
      endif else res=loadfits(event,file,type,/display)
   end
   'Model': begin
      widget_control,(*state).wout,get_value=file & file=file(0)
      if not file_exist(file) then begin
         res=0b
         t=dialog_message('The OUTPUT file does not exist.',/error,/cent)
      endif else res=loadfits(event,file,type,/display,ext=2)
   end
   'Residuals': begin
      widget_control,(*state).wout,get_value=file & file=file(0)
      if not file_exist(file) then begin
         res=0b
         t=dialog_message('The OUTPUT file does not exist.',/error,/cent)
      endif else res=loadfits(event,file,type,/display,ext=3)
   end
   else: res=0b
endcase

;if the loading succeeded, then update the buttons
if res then begin
   ;uncheck all the buttons
   n=n_elements((*state).images)
   for i=0,n-1 do widget_control,(*state).wimage(i),set_button=0b

   ;check the one they did pick
   widget_control,(*state).wimage(g),set_button=1b
endif


end
