pro delete_all,event

widget_control,event.top,get_uval=state

 nreg=(*state).oROIModel->Count()
 for i=0,nreg-1 do begin
    oROI=(*state).oROIModel->Get(pos=0)
    (*state).oROIModel->Remove,oROI
    (*state).oROIGroup->Remove,oROI
    obj_destroy,oROI
 endfor

if xregistered('reginfo',/noshow) then begin
   widget_control,(*state).weditregbase,get_uval=sstate
   setroi,state,obj_new(),/update
   setdata,sstate,/clear
endif

;clear the fit section
(*state).fitsect=0b

;reset the regions
(*state).oSelROI=obj_new()
(*state).oVisual->SetProperty,hide=1b

;redraw the screen
(*state).oWindow->Draw,(*state).oView

end
