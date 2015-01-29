function convertxy,event,state

;get the draw size:
geom=widget_info((*state).wdraw,/geom)

;get the view
(*state).oView->GetProperty,view=view

;scale and translate the (x,y) position
x=view(0)+event.x*(view(2)/geom.xsize)
y=view(1)+event.y*(view(3)/geom.ysize)

;return the new (x,y)
return,[x,y]
end
