pro setroi,state,oROI,UPDATE=update,SETLIST=setlist,RESET=reset

;test if ROI Info dialog box is realized

reginfo_open=xregistered('reginfo',/noshow)
if reginfo_open then widget_control,(*state).weditregbase,get_uvalue=sstate


;get the names
if keyword_set(UPDATE) and reginfo_open then $
   widget_control,(*sstate).wlist,set_value=getregnames(state)



;newly selected ROI
if obj_valid(oROI) then begin
   ;reshape as necessary
   reshape,state,oROI
   
   if reginfo_open then begin
      oROI->GetProperty,name=name
      if keyword_set(SETLIST) ne 0 then begin
         res=(*state).oROIModel->IsContained(oROI,position=pos)
         if res ne 0 then begin
            widget_control,(*sstate).wlist,set_list_select=pos
            setdata,sstate,oROI
         endif
      endif
      
      widget_control,(*sstate).wdelete,/sensitive
   endif 
endif else begin
   if reginfo_open then begin
      widget_control,(*sstate).wdelete,sens=0
      widget_control,(*sstate).wlist,set_list_select=-1
      setdata,sstate,oROI,/clear
   endif
   
   if obj_valid((*state).oSelVisual) ne 0 then $
      (*state).oSelVisual->SetProperty,/hide

endelse
if not keyword_set(RESET) then (*state).oSelROI=oROI

;udate the INFO boxes
if reginfo_open and obj_valid(oROI) then setdata,sstate,oROI



end
