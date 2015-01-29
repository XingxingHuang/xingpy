pro viewport,event
widget_control,event.top,get_uvalue=state

;get the size of the draw window:
;geom=widget_info((*state).wdraw,/geom)
;xs=geom.xsize<geom.draw_xsize
;ys=geom.ysize<geom.draw_ysize
(*state).oView->GetProperty,viewplane=view
xs=view(2) & ys=view(3)


;update the view port
(*state).oView->Setproperty,viewplane_rect=[event.x,event.y,xs,ys]

;show the hourglass if it takes a long time:
if (*state).draw_time gt 0.1 then widget_control,/hourglass

;redraw the viewport
(*state).oWindow->Draw, (*state).oView

end
