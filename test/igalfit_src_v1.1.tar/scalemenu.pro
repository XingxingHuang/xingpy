pro scalemenu,event
widget_control,event.top,get_uval=state

;find the box that got checked
g=(where((*state).wscale eq event.id))(0)
(*state).scale=(*state).scales(g)      

;uncheck all the boxes
n=n_elements((*state).scales)
for i=0,n-1 do widget_control,(*state).wscale(i),set_button=0b

;recheck the one they clicked on
widget_control,(*state).wscale(g),set_button=1b

;display the image
display_image,state

end
