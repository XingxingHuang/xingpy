pro zoommenu,event
widget_control,event.top,get_uval=state

;find out which box was checked
g=(where((*state).wzoom eq event.id))(0)


;un check them all!
for i=0,n_elements((*state).zooms)-1 do $
   widget_control,(*state).wzoom(i),set_button=0b

;recheck all but the one
widget_control,(*state).wzoom(g),set_button=1b

;okay, now gotta do the zooming

;compute the zoom:
s=strsplit((*state).zooms(g),'/',/ext)
if n_elements(s) eq 1 then zoom=float(s) else $
   t=execute('zoom='+s(0)+'./'+s(1)+'.')

;zoom to the center of the display:
;geom=widget_info((*state).wdraw,/geom)
;event={top:event.top,x:geom.xsize/2.,y:geom.ysize/2.}    

;now zoom the image:
zoom_image,state,zoom,/zoomto


end
