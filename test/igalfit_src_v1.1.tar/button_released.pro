pro logroi,state,oROI,accept

if accept then begin
    ;ok, it's a good region
   oROI->SetProperty,name=nameregion(*state)             ;name that region
   (*state).oModel->Remove,oROI                          ;take out the model
   (*state).oROIModel->Add,oROI                          ;add to container
   (*state).oROIGroup->Add,oROI                          ;add to container
   (*state).oCurrROI=obj_new()                           ;ready for new region
   setroi,state,oROI,/update,/setlist,/reset             ;update the setting
   
   ;okay, so you drew a region.  
   ;If it was a Fit Section, then let's reset the state
   if (*state).morphstate eq 'Fit Section' then begin
      thismorph=(*state).morphinfo(0).type
      widget_control,(*state).wmorph,set_value=thismorph,$
                     tooltip=(*state).morphinfo(0).tip
      (*state).morphstate=thismorph            
      (*state).fitsect=1b
   endif
endif else begin
   ;oops the region was too small
   (*state).oModel->Remove,oROI            ;remove it
   obj_destroy,oROI                        ;erase it
   (*state).oCurrROI=obj_new()             ;reset default

   ;re-draw
   (*state).oWindow->Draw,(*state).oView
endelse
end



pro button_released,event
;procudure to handle when buttons are released
;get the state
widget_control,event.top,get_uvalue=state

;convert from viewport coord to image coord
xy=convertxy(event,state)
x=xy(0) & y=xy(1)

;reset cursor?
if (*state).rotating then begin
   (*state).oWindow->SetCurrentCursor,'CROSSHAIR'
   (*state).rotating=0b
endif

case event.release of
   1: begin     ;left mouse click

      ;do something different depending on which button we have se
      case (*state).button of
         0b:                    ;null clicking
         10b: begin
            ;grabbed a handle

            ;EXTRA?
;            oSelVisual=(*state).oSelVisual
;           if obj_valid(oSelVisual) then begin
;;              oSelVisual->SetProperty,hide=1b
;;              (*state).oSelVisual=obj_new()
;;           endif
;;           (*state).oSelVisual=(*state).oVisual
;            reshape,state,(*state).oSelROI
            
            ;stuff here to update the region widget
            
;            if ptr_valid((*state).pSavedROIData) then $
;               ptr_free,(*state).pSavedROIData
;            (*state).pSavedROIData=ptr_new()
            (*state).button=0b
            
         end

         11b: begin
            ;grabed a visual

            ;EXTRA?
;            oSelVisual=(*state).oSelVisual
;            if obj_valid(oSelVisual) then begin
;               oSelVisual->SetProperty,hide=1b
;               (*state).oSelVisual=obj_new()
;            endif
;            (*state).oSelVisual=(*state).oVisual
;            reshape,state,(*state).oSelROI
            
;            if ptr_valid((*state).pSavedROIData) then $
;               ptr_free,(*state).pSavedROIData
;            (*state).pSavedROIData=ptr_new()
            (*state).button=0b
         end
         


         12b: begin
            ;a region was drawn
            ;EXTRA? from the button
;            oSelVisual=(*state).oSelVisual
;            if obj_valid(oSelVisual) then begin
;               oSelVisual->SetProperty,/hide
;               (*state).oSelVisual=obj_new()
;            endif
                

            ;reset the button stuff
            (*state).button=0b
            
            oROI=(*state).oCurrROI
            if not obj_valid(oROI) then return
            
            ;check if the region is large enough
            oROI->GetProperty,uval=prop
            case prop.shape of
               'box': logroi,state,oROI,prop.dx gt 2 and prop.dy gt 2
               'ellipse': logroi,state,oROI,prop.a gt 2 and prop.b gt 1
               'circle': logroi,state,oROI,prop.r gt 2
            end
         end
         2b: begin
            ;ok, that's why 2.  We are translating or rotating.  
            ;might set rotating to another value

            ;EXTRA?
;            oSelVisual=(*state).oSelVisual
;            if obj_valid(oSelVisual) ne 0 then begin
;               oSelVisual->SetProperty,/hide
;               (*state).oSelVisual=obj_new()
;            endif
;            ;visualize the translate/shape option
;            (*state).oSelVisual=(*state).oVisual
;            reshape,state,(*state).oSelROI


            if xregistered('reginfo',/noshow) then begin
               widget_control,(*state).wreginfobase,get_uvalue=sstate
               setdata,sstate,(*state).oSelROI
            endif
            
            ;free the pointers
;            if ptr_valid((*state).pSavedROIData) then $
;               ptr_free,(*state).pSavedROIData
;            
;            ;reset to defaults
;            (*state).pSavedROIData=ptr_new()
            (*state).button=0b
         end
         255: (*state).button=0b
         else: print,'BUTTON_RELEASED encountered an unknown button type:',$
                     (*state).button
      endcase
      
   end
   4: (*state).button=0b        ;reset the button
;(*state).button=(*state).prevbutton  ;right mouse click
   else: return
endcase



end
