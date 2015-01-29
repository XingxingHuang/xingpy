pro resize_gui,state,event

;attempt to resize the window?
device,get_screen_size=screen
newx=(*state).dimen(0)>event.x<screen(0)
newy=screen(1)<(event.y-((*state).dimen(1)-450))>450.
print,newx,newy

goto,skip
;force to be the same size
win=widget_info((*state).wdraw,/geom)
newx=(*state).dimen(0)
newy=(*state).dimen(1)
newx=win.draw_xsize
newy=win.draw_ysize
skip:

;update
widget_control,(*state).wdraw,draw_xsize=newx,draw_ysize=newy

;redraw
(*state).oWindow->Draw,(*state).oView

end
