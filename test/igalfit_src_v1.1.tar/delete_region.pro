pro delete_region,pstate

;do nothing if no regions available
nreg=(*pstate).oROIModel->count()
if nreg eq 0 then return

;do nothing if no regen is selected
oROI=(*pstate).oSelROI
if obj_valid(oROI) eq 0 then return

;get position of sleected
res=(*pstate).oROIModel->iscontained(oROI,position=pos)
if res eq 0 then return

;first Check if it was a fitting section!
oROI->GetProperty,uvalue=prop
if prop.type eq 'Fit Section' then (*state).fitsect=0b

;remove and destroy
(*pstate).oROIModel->Remove,oROI
(*pstate).oROIGroup->Remove,oROI
;if obj_valid((*pstate).oRegionsOut) then (*pstate).oRegionsOut->remove,oROI
if obj_valid((*pstate).oRegionsIn) then begin
   if (*pstate).oRegionsIn->iscontained(oROI) then begin
      if obj_valid((*pstate).oRejected) then (*pstate).oRejected->Add,oROI
   endif else obj_destroy,oROI
endif else obj_destroy,oROI

;pick a new region
if nreg eq 1 then begin
   setroi,pstate,obj_new(),/update
endif else begin
   oROI=(*pstate).oROIModel->get(position=((pos-1)>0))
   setroi,pstate,oROI,/update,/setlist
endelse


end
