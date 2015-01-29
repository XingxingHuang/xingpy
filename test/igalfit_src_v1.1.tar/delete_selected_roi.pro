pro delete_selected_roi,event
widget_control,event.top,get_uvalue=state
oSelROI=(*state).oSelROI
if obj_valid(oSelROI) then begin
   ;set new ROI
   nreg=(*state).oROIModel->Count()
   res=(*state).oROIModel->IsContained(oSelROI,pos=pos)   


   ;first Check if it was a fitting section!
   oSelROI->GetProperty,uvalue=prop
   if prop.type eq 'Fit Section' then (*state).fitsect=0b
   

   ;delete the region
   obj_destroy,oSelROI
   (*state).oSelROI=obj_new()
   (*state).oVisual->SetProperty,hide=1b

   (*state).oWindow->Draw,(*state).oView ;Re-draw

   ;update the registry
   if nreg eq 1 then begin
      if xregistered('reginfo',/noshow) then begin
         widget_control,(*state).weditregbase,get_uval=sstate
         setroi,state,obj_new(),/update
         setdata,sstate,/clear
      endif
   endif else begin
      oROI=(*state).oROIModel->Get(pos=(pos-1)>0)
      setroi,state,oROI,/update,/setlist
   endelse
endif


end
