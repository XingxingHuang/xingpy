pro zoom_image,state,zoom,ZOOMTO=zoomto,RESETZOOM=resetzoom
;widget_control,event.top,get_uval=state


;update the zoom state
if keyword_set(ZOOMTO) then begin
   newzoom=zoom/(*state).zoomstate
   (*state).zoomstate=zoom      ;record the zoom state
   zoom=temporary(newzoom)
endif else begin
   newzoom=(*state).zoomstate*zoom
   if newzoom le 1.0d-5 or newzoom ge 1.0d5 then return
   (*state).zoomstate=temporary(newzoom) ;record the zoom state
endelse
  
;get the view
(*state).oView->GetProperty,view=view
draw=widget_info((*state).wdraw,/geom)
event={x:draw.xsize/2.,y:draw.ysize/2.}    
xy=convertxy(event,state)


if keyword_set(RESETZOOM) then begin
   ;reset the zoom to default   
   dx=draw.xsize<draw.draw_xsize
   dy=draw.ysize<draw.draw_ysize
   sz=size(*(*state).img,/dim)
   view=[(sz(0)-dx)/2,(sz(1)-dy)/2,dx,dy]
   (*state).zoomstate=1.0      
endif else begin
   ;Here's the zooming!
   dx=view(2)*zoom
   dy=view(3)*zoom  
   view=[xy(0)-dx/2,xy(1)-dy/2,dx,dy]
endelse
  
;reset the view
(*state).oView->Setproperty,viewplane_rect=view
 
;draw the compass
compass,state

;draw the scale bar
scalebar,state

;update the draw window
(*state).oWindow->Draw, (*state).oView

;update the zoom display parameters
update_zoomdisp,state,pulldown=(1b-keyword_set(ZOOMTO))



end





