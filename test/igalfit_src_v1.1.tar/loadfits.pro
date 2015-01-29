function loadfits,event,filename,type,$
                  EXTENSION=extension,$
                  DISPLAY=display,$
                  SCIENCE=science,$
                  UNCERTAINTY=uncertainty,$
                  PSF=psf

if not keyword_set(EXTENSION) then extension=0

;check for blank file
if filename eq '' then return,file_error(type,/blank)

;check if file exists
if not file_exist(filename) then return,file_error(type)

;if here then the file is valid
widget_control,event.top,get_uvalue=state

if keyword_set(DISPLAY) then begin
   widget_control,hourglass=1b   ;turn on an hourglass

   ;okay, so the file exists, but let's make sure it's a valid fits file
   img=readfits(filename,hdr,/sil,ext=extension)
   if n_elements(img) eq 1 then return,0b
   sz=sxpar(hdr,'NAXIS*')       ;size of image

   ;save to the state
   (*state).img=ptr_new(temporary(img),/no_copy)


   ;okay, let's check for an array of header keywords..
   (*state).magzero=find_key(hdr,['MAG_ZERO','ZEROPT','MAGZERO','ZEROMAG',$
                                  'MAG_ZPT','ZERO_MAG'],0.0,/sil)

   ;compute some stuff for a quick display
   autoscale,state & (*state).limit='Auto' ;set default limits
   (*state).scale='Linear'                    ;set default scale

   ;update the scale buttons
   widget_control,(*state).wscale((where((*state).scales eq $
                                         (*state).scale))(0)),set_button=1b

   ;get the astrometry (for later usage)
   extast,hdr,ast,noparam
   if noparam ge 0 then begin
      getrot,ast,rot,cdelt & pix=abs(cdelt)*3600.
      widget_control,(*state).wpixx,set_val=string(pix(0),f='(F5.3)')
      widget_control,(*state).wpixy,set_val=string(pix(1),f='(F5.3)')
      (*state).ast=ptr_new(ast,/no_copy)
      widget_control,(*state).wcompass,set_button=1b
      widget_control,(*state).wscalebar,set_button=1b
   endif

   ;update the viewport
   draw=widget_info((*state).wdraw,/geometry)
   (*state).oView->GetProperty,view=view
   dx=draw.xsize<draw.draw_xsize
   dy=draw.ysize<draw.draw_ysize
   (*state).oView->SetProperty,view=[(sz(0)-dx)/2,(sz(1)-dy)/2,dx,dy]

   ;draw the directional compass
   compass,state
   
   ;draw the scale bar
   scalebar,state
                                               
   ;draw the gal-darn image already!
   display_image,state

   ;draw the selected region if need be
   if obj_valid((*state).oSelROI) then setroi,state,(*state).oSelROI
   
   ;update the display setting
   nn=n_elements((*state).images)
   for i=0,nn-1 do widget_control,(*state).wimage(i),set_button=0b
   g=(where((*state).images eq type))(0)
   widget_control,(*state).wimage(g),set_button=1b
     
   widget_control,hourglass=0b ;turn off hourglass
endif


;put it in the data
if keyword_set(SCIENCE) then begin
   widget_control,(*state).wsci,set_value=filename
   (*state).setfile.sci=filename
   return,1b
endif

if keyword_set(UNCERTAINTY) then begin
   widget_control,(*state).wunc,set_value=filename
   (*state).setfile.unc=filename
   return,1b
endif

if keyword_set(PSF) then begin
   widget_control,(*state).wpsf,set_value=filename
   (*state).setfile.psf=filename
   return,1b
endif


return,1b
end
