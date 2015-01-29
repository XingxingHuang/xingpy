function prepare_images,state,GROUP=group

psep=path_sep()
mycomment=' added by '+(*state).info.title

;read science file
if file_exist((*state).setfile.sci) then begin
   img=readfits((*state).setfile.sci,h,/silent)
   sci={img:temporary(img),hdr:temporary(h)}
endif else return,file_error('Science')

;read uncertainty file
if file_exist((*state).setfile.unc) then begin
   img=readfits((*state).setfile.unc,h,/silent)
   unc={img:temporary(img),hdr:temporary(h)}

   userunc=1b
endif else begin
   ;if don't have one, then galfit will build one.  But need to seet 
   ;RDNOISE, GAIN, and NCOMBINE keywords in the sci.hdr
   values=uncertainty_parameters(group=group)
   sxaddpar,sci.hdr,'RDNOISE',float(values.rdnoise),mycomment
   sxaddpar,sci.hdr,'GAIN',float(values.gain),mycomment
   sxaddpar,sci.hdr,'NCOMBINE',fix(values.ncomb),mycomment
   
   userunc=0b
endelse



;find out the units of the images
units=widget_info((*state).wunits,/combobox_gettext)
case units of
   'cts': begin
      sxaddpar,sci.hdr,'EXPTIME',1.0,mycomment
      if userunc then sxaddpar,unc.hdr,'EXPTIME',1.0,mycomment
   end
   'cts/s': begin
      widget_control,(*state).wexptime,get_val=exptime & exptime=exptime(0)
      if isnumber(exptime) eq 0 then begin
         exptime='1.0'
         widget_control,(*state).wexptime,set_val=exptime
      endif
      etime=float(exptime)

      ;multiply by exposure time!!
      sci.img=sci.img*etime
      sxaddpar,sci.hdr,'EXPTIME',etime,mycomment

      if userunc then begin
         unc.img=unc.img*etime
         sxaddpar,unc.hdr,'EXPTIME',etime,mycomment
      endif
   end 
   else:
endcase


;include shot noise?
if widget_info((*state).wshot,/button_set) and userunc then $
   unc.img=sqrt(abs(sci.img)+unc.img*unc.img)

;write the images
writefits,(*state).usefile.sci,sci.img,sci.hdr
if userunc then writefits,(*state).usefile.unc,unc.img,unc.hdr


return,1b
end
