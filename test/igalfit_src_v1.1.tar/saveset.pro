function menuset,wids
;find which menu is checked

for i=0,n_elements(wids)-1 do begin
   if widget_info(wids(i),/button_set) then set=i
endfor
return,set
end


pro saveset,file,state,top


;check if I can write here:
openw,lun,'t.t',/delete,/get_lun,error=error
if error ne 0 then begin
   t=writefile_error('Save File')
   return
endif
close,lun & free_lun,lun 


;Data from GalFit Tabs
;file IO
widget_control,(*state).wout,get_val=outfile & outfile=outfile(0)
widget_control,(*state).wbpx,get_val=bpxfile & bpxfile=bpxfile(0)
mkbpx=widget_info((*state).wmkbpx,/button_set)
files={sci:(*state).setfile.sci,$   ;sci file
       psf:(*state).setfile.psf,$   ;PSF file
       unc:(*state).setfile.unc,$   ;unc file
       out:outfile,$                ;imgblock file
       bpx:bpxfile,$                ;bad pixel file
       mkbpx:mkbpx}                 ;make bpx




;constraints
widget_control,(*state).wconfile,get_val=confile & confile=confile(0)
conssens=widget_info((*state).wremcon,/sens)
consnames=ptr_valid((*state).consnames)?*(*state).consnames:''
constraint={file:file,$         ;constraint file
            sens:conssens,$     ;sensitive?
            names:consnames}

;ranges
widget_control,(*state).wx0,get_val=x0 & x0=x0(0)
widget_control,(*state).wx1,get_val=x1 & x1=x1(0)
widget_control,(*state).wy0,get_val=y0 & y0=y0(0)
widget_control,(*state).wy1,get_val=y1 & y1=y1(0)
widget_control,(*state).wdx,get_val=dx & dx=dx(0)
widget_control,(*state).wdy,get_val=dy & dy=dy(0)
ranges={x0:x0,$                 ;x0 in range
        x1:x1,$                 ;x1 in range
        y0:y0,$                 ;y0 in range
        y1:y1,$                 ;y1 in range
        dx:dx,$                 ;dx in convolution
        dy:dy}                  ;dx in convolution
        

;Image Props
widget_control,(*state).wzero,get_val=zero & zero=zero(0)
widget_control,(*state).wpixx,get_val=pixx & pixx=pixx(0)
widget_control,(*state).wpixy,get_val=pixy & pixy=pixy(0)
widget_control,(*state).wexptime,get_val=expt & expt=expt(0)
units=widget_info((*state).wunits,/combobox_gettext)
shot=widget_info((*state).wshot,/button_set)
props={zero:zero,$                            ;zeropoint
       pixx:pixx,$                            ;x-pix scl
       pixy:pixy,$                            ;y-pix scl
       expt:expt,$                            ;exptime
       units:units,$                          ;units of images
       shot:shot}                             ;include shot noise?

;Sky Model
fitsky0=widget_info((*state).wfitsky0,/button_set)
widget_control,(*state).wsky0,get_val=sky0 & sky0=sky0(0)
sky0sens=widget_info((*state).wsky0,/sens)
fitdsdx=widget_info((*state).wfitdsdx,/button_set)
widget_control,(*state).wdsdx,get_val=dsdx & dsdx=dsdx(0)
dsdxsens=widget_info((*state).wdsdx,/sens)
fitdsdy=widget_info((*state).wfitdsdy,/button_set)
widget_control,(*state).wdsdy,get_val=dsdy & dsdy=dsdy(0)
dsdysens=widget_info((*state).wdsdy,/sens)
sky={sky0:{fit:fitsky0,val:sky0,sens:sky0sens},$
     dsdx:{fit:fitdsdx,val:dsdx,sens:dsdxsens},$
     dsdy:{fit:fitdsdy,val:dsdy,sens:dsdysens}}


;additionals
disptype=widget_info((*state).wdisptype,/combobox_gettext)
gftype=widget_info((*state).wgftype,/combobox_gettext)
widget_control,(*state).wfine,get_value=fine & fine=fine(0)
erase=widget_info((*state).wclean,/button_set)
silent=widget_info((*state).wsilent,/button_set)
display=widget_info((*state).wdisp,/button_set)
add={disptype:disptype,$             ;type of GF display
     gftype:gftype, $                ;type of GF running
     fine:fine,$                     ;fine sampling factor
     erase:erase, $                  ;clean up afterward?
     silent:silent, $                ;suppress terminal?
     display:display}                ;display when done?    

     

;get the image and astrometry?
(*state).oView->GetProperty,view=view
img=ptr_valid((*state).img)?*(*state).img:''
ast=ptr_valid((*state).ast)?*(*state).ast:''
image={img:img,$
       ast:ast,$
       set:menuset((*state).wimage),$
       zoom:menuset((*state).wzoom),$
       scale:menuset((*state).wscale),$
       view:view}
       

;histogram
hist=ptr_valid((*state).hist)?*(*state).hist:''
bins=ptr_valid((*state).bins)?*(*state).bins:''
histo={hist:hist,$
       bins:bins,$
       histmaxx:(*state).histmaxx,$   ;histogram max
       histminx:(*state).histminx,$   ;histogram min
       histbinx:(*state).histbinx}    ;histogtram bin
       

;display data

display={lodisp:(*state).lodisp,$    ;lo display value
         hidisp:(*state).hidisp,$    ;hi display valu
         bias:(*state).bias,$        ;bias value
         cont:(*state).cont,$        ;cont value
         fitsect:(*state).fitsect}   ;fit section?
        
;GUI state info
mouse={xy:(*state).xy,$                ;xy of last click
       zoomstate:(*state).zoomstate,$  ;zoom state
       button:(*state).button}         ;button state
  


;save subGUI info
guis=['imstat','radprof','reginfo','linking_constraints',$
      'basic_constraints','pixtab','pixhist','stretch_image',$
      'sex','help_gui']
guis=guis(reverse(sort(strlen(guis))))
ngui=n_elements(guis)
subguis=replicate({name:'',open:0b},ngui)
for i=0,ngui-1 do begin
   subguis(i).name=guis(i)
   subguis(i).open=xregistered(guis(i),/noshow)
endfor

            


;get the regions
oROIs=(*state).oROIModel->Get(/all,count=nreg)


struct={files:files, $          ;input files
        constraint:constraint,$ ;constraint data
        ranges:ranges,$         ;ranges for fitting
        props:props,$           ;image properties
        sky:sky,$               ;sky model settings
        add:add,$               ;additional settings
        image:image,$           ;image data
        histo:histo,$           ;histogram data
        display:display,$       ;display settings
        mouse:mouse,$           ;mouse state
        subguis:subguis,$       ;subguis
        prefs:(*state).prefs,$  ;preferences
        nreg:nreg}              ;number of regions

;okay, now add all the regions
define_rgb,colors
for i=0,nreg-1 do begin
   ii=strcompress(string(i+1,f='(I6)'),/rem)

   name='reg'+ii
   oROIs(i)->GetProperty,uval=props,color=color
   struct=add_tag(struct,props,name)

   name='rgb'+ii
   g=(where(color(0) eq colors.rgb(0) and $
            color(1) eq colors.rgb(1) and $
            color(2) eq colors.rgb(2)))(0)
   struct=add_tag(struct,colors(g).rgb,name)
endfor

;now write the HDF5 file
write_h5,file,struct,'iGalFit'



end
