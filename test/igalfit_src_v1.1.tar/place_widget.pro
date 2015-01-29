pro place_widget,base,group,RIGHT=right

basegeom=widget_info(base,/geom)
leadgeom=widget_info(group,/geom)
device,get_screen_size=sz

;to the right, by default
dx=leadgeom.scr_xsize(0)+leadgeom.xoffset
dy=leadgeom.yoffset


   
if keyword_set(RIGHT) then begin
   dx=leadgeom.scr_xsize(0)+leadgeom.xoffset
   dy=leadgeom.yoffset
endif



dx=dx<(sz(0)-basegeom.scr_xsize)>0
dy=dy<(sz(1)-basegeom.scr_ysize)>0

widget_control,base,tlb_set_xoffset=dx,tlb_set_yoffset=dy


end
