pro update_fitsect,state,prop
if prop.type eq 'Fit Section' then begin

   imsize=size(*(*state).img,/dim)

   ;NOTE, the +1 in each coordinate.  That's to convert IDL
   ;(0,0)-based to the GalFit (1,1)-based coordinate systems!
   
   x0=(prop.x-prop.dx/2.+1)>1
   x0=strcompress(string(x0,f='(I6)'),/rem)
   widget_control,(*state).wx0,set_value=x0
   
   x1=(prop.x+prop.dx/2.+1)<(imsize(0))
   x1=strcompress(string(x1,f='(I6)'),/rem)
   widget_control,(*state).wx1,set_value=x1
   
   y0=(prop.y-prop.dy/2.+1)>1
   y0=strcompress(string(y0,f='(I6)'),/rem)
   widget_control,(*state).wy0,set_value=y0  
   
   y1=(prop.y+prop.dy/2.+1)<(imsize(1))
   y1=strcompress(string(y1,f='(I6)'),/rem)
   widget_control,(*state).wy1,set_value=y1
endif   
end
