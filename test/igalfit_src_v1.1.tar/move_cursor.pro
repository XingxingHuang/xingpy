pro move_cursor,event
;procedure to move the cursor


if event.release ne 0 then return  ;return on a release
widget_control,event.top,get_uval=state

;get the current ROI
oSelROI=(*state).oSelROI
if obj_valid(oSelROI) then begin
   ;compute stepsize
   stepsize=(*state).zoomstate
   ;get deltas
   case event.key of
      5: delta=[-stepsize,0.]                        ;left
      6: delta=[+stepsize,0.]                        ;right
      7: delta=[0.,+stepsize]                        ;up
      8: delta=[0.,-stepsize]                        ;down
      else: return
   endcase
   ;translate the ROI
   trans_roi,state,oSelROI,delta(0),delta(1),/deltas

   ;redraw the window....
   (*state).oWindow->Draw,(*state).oView
endif
end

