pro expose,event

widget_control,event.top,get_uvalue=state
if (*state).draw_time gt 0.1 then widget_control,/hourglass

t1=systime(/second)
(*state).oWindow->Draw,(*state).oView
(*state).draw_time=systime(/second)-t1

end

