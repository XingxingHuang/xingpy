function pa2gf,pa,FORMAT=format
  if not keyword_set(FMT) then format='(F6.2)'



  pa=(pa+90) mod 360.                                   ;regularize  
  if pa ge   0. and pa lt  90. then outpa=pa       ;quadrant I
  if pa ge  90. and pa lt 180. then outpa=pa-180.  ;quadrant II
  if pa ge 180. and pa lt 270. then outpa=180.-pa  ;quadrant III
  if pa ge 270. and pa lt 360. then outpa=360.-pa  ;quadrant IV
  
  return,strcompress(string(outpa,format=format),/rem)
end


function rangevalue,wid,def,param,val

widget_control,wid,get_value=val
if val(0) eq '' then begin
   val=def
   widget_control,wid,set_value=val
endif else begin
   val=val(0)
endelse

if isnumber(val) ne 1 then return,type_error(param) else return,1b
end

function mkgalfit,state

;get name of feedme file
openw,l,(*state).prefs.feedme,/get_lun,error=error
if error ne 0 then return,writefile_error('GalFit Feedme')

;redo the file names:
mkfilenames,state

;name of this routine
current=current_routine()



;check if the files are set
title='Make FeedMe File'
if (*state).setfile.sci eq '' then begin
   t=dialog_message(['Science file is not set.',$
                     'Cannot run GalFit!'],/error,/center,title=title)
   return,0b
endif
if (*state).setfile.unc eq '' then begin
   t=dialog_message(['Uncertainty file is not set.',$
                     'You really should set this!',$
                     'Should we proceed?'],/center,$
                    /ques,title=title)
   if t eq 'No' then return,0b
endif

if (*state).setfile.psf eq '' then begin
   t=dialog_message(['PSF file is not set.',$
                     'You really should set this!',$
                     'Should we proceed?'],/center,$
                    /ques,title=title)
   if t eq 'No' then return,0b
endif

;get the GalFit executable.  This error is fatal, so let's do it first
;widget_control,(*state).wgfexec,get_value=gfexec
gfexec=(*state).prefs.exec

;get ranges
if (file_which(getenv('PATH'),gfexec(0)))(0) eq '' then begin
   t=dialog_message(['The GalFit executable is not in your path!',$
                     'You must fix this before we can proceed.'],$
                    /error,/center)                    
   return,0b
endif


;get output file
widget_control,(*state).wout,get_value=outfile
if outfile(0) eq '' then begin
   outfile='imgblock.fits'      ;a default if left blank
   widget_control,(*state).wout,set_value=outfile
endif else outfile=outfile(0)

;get constraints file
widget_control,(*state).wconfile,get_value=confile
confile=(confile(0) ne '')?confile(0):'none'


;a short hand variable....
sz=size(*(*state).img,/dim)
imsize=strcompress(string(sz,f='(I6)'),/rem)
nx=imsize(0) & ny=imsize(1)

;get ranges
if not rangevalue((*state).wx0,'1','x0',x0) then return,0b
if not rangevalue((*state).wy0,'1','y0',y0) then return,0b
if not rangevalue((*state).wx1, nx,'x1',x1) then return,0b
if not rangevalue((*state).wy1, ny,'y1',y1) then return,0b

;get convolution box
if not rangevalue((*state).wdx, nx,'dx',dx) then return,0b
if not rangevalue((*state).wdy, ny,'dy',dy) then return,0b

;get zeropoint
widget_control,(*state).wzero,get_value=zero
zero=(zero(0) eq '')?'0.0':zero(0)
if isnumber(zero) eq 0 then return,type_error('zeropoint')

;get pixel scale
if ptr_valid((*state).ast) then begin
   getrot,(*(*state).ast),rot,pix
   pix=string(abs(pix)*3600.,f='(F5.3)')
endif else pix=['1','1']
widget_control,(*state).wpixx,get_value=pixx
widget_control,(*state).wpixy,get_value=pixy
if pixx(0) eq '' then begin
   pixx=pix(0)
   val=strcompress(string(pixx,f='(F5.3)'),/rem)
   widget_control,(*state).wpixx,set_value=temporary(val)
endif else begin
   pixx=pixx(0)
   if isnumber(pixx) ne 2 then return,type_error('x pixel scale')
endelse
if pixy(0) eq '' then begin
   pixy=pix(1)
   val=strcompress(string(pixy,f='(F5.3)'),/rem)
   widget_control,(*state).wpixy,set_value=temporary(val)
endif else begin
   pixy=pixy(0)
   if isnumber(pixy) ne 2 then return,type_error('y pixel scale')
endelse

;get exposure time
widget_control,(*state).wexptime,get_value=exptime
exptime=(exptime(0) ne '')?'1.':exptime(0)
if isnumber(exptime) eq 0 then return,type_error('exposure time')

;set the BPX file name
mkbpx=widget_info((*state).wmkbpx,/button_set)
widget_control,(*state).wbpx,get_value=bpxfile & bpxfile=bpxfile(0)
if mkbpx then begin
   ;meaning let's make abpx file from the regions
   if bpxfile eq '' then begin  ;you didn't name it, so I will 
      bpxfile='bpx.fits'        
      widget_control,(*state).wbpx,set_value=bpxfile
   endif
   bpx=bytarr(imsize)
endif else begin
   if file_exist(bpxfile) then begin
      ;okay, you specified a file, and it exists.  I'm using it.
      bpx=readfits(bpxfile,/silent)
   endif else begin
      ;uh oh, you spceficed a file that does not exst.
      t=dialog_message(['The BPX file, '+bpxfile+', is not found.',$
                        'not using any file at all.'],/error,/center)
      bpxfile='none'
      widget_control,(*state).wbpx,set_value=bpxfile
   endelse
endelse

;get GF types
disptype=widget_info((*state).wdisptype,/combobox_gettext)
widget_control,(*state).wgftype,get_value=val
gftype=string((where(val eq widget_info((*state).wgftype,$
                                        /combobox_gettext)))(0),f='(I1)')
clean=widget_info((*state).wclean,/button_set)


;make the data for the feedme file.  but don't write it yet
models=['']         ;an array containing the data for the feedme file

;need to get the science image to multiply by the gain
;check if it's set, if so, use it.  if not, read it
nn=n_elements((*state).images)
set=bytarr(nn)
for i=0,nn-1 do set(i)=widget_info((*state).wimage(i),/button_set)
set=(where(set))(0) 
display=(set eq -1)?'none':(*state).images(set)   ;name of the image set

;okay, now read it or grab it
if display eq 'Science' then begin
   im=(*(*state).img)
endif else begin
   im=readfits((*state).setfile.sci,h,/sil)
endelse

;get the fine sampling factor
widget_control,(*state).wfine,get_value=fine & fine=fine(0)
if isnumber(fine) eq 0 then begin
   t=type_error('Fine Sampling')
   fine='1.0'
endif

;get the colors
;define_rgb,colors

;for each region
nreg=(*state).oROIModel->Count()
for i=0,nreg-1 do begin
   ;get the ROIs in order
   oROI=(*state).oROIModel->Get(pos=i)

   ;get the data on the ROI
   oROI->GetProperty,uvalue=prop;,color=color
   mask=((oROI->ComputeMask(dim=imsize)) eq 255)

   ;compute the flux and magnitude
   flux=total(im*mask)
   mag=strcompress(string(-2.5*alog10(flux)+float(zero),f='(F7.3)'),/rem)
   
   ;okay work with the data
   case prop.type of
      'Mask': if mkbpx then bpx=bpx or mask
      'Fit Section':      
      'Sersic': begin
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         aa=strcompress(string(prop.a,f='(F5.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y

         n0=string((*state).prefs.sersic.n,f='(F5.2)')
         models=[models,$
                 '0) sersic',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mag,$
                 '4) '+aa+' '+prop.fit.re,$
                 '5) '+n0+' '+prop.fit.n,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']   
   
      end
      'ExpDisk': begin
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         aa=strcompress(string(prop.a,f='(F5.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')      
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) expdisk',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mag,$
                 '4) '+aa+' '+prop.fit.re,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end
      'DeVauc': begin
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         aa=strcompress(string(prop.a,f='(F5.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) devauc',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mag,$
                 '4) '+aa+' '+prop.fit.re,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end
      'Nuker': begin
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         aa=strcompress(string(prop.a,f='(F5.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')         
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y

         a0=string((*state).prefs.nuker.alpha,f='(F5.2)')
         b0=string((*state).prefs.nuker.beta,f='(F5.2)')
         c0=string((*state).prefs.nuker.gamma,f='(F5.2)')
         models=[models,$
                 '0) nuker',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mub,$
                 '4) '+aa+' '+prop.fit.rb,$
                 '5) '+a0+' '+prop.fit.alpha,$
                 '6) '+b0+' '+prop.fit.beta,$
                 '7) '+c0+' '+prop.fit.gamma,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end
      'Edge-on Disk': begin
         rl=strcompress(string(prop.a,f='(F5.2)'),/rem)
         zh=strcompress(string(prop.b,f='(F5.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) edgedisk',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mu0,$
                 '4) '+zh+' '+prop.fit.hs,$
                 '5) '+rl+' '+prop.fit.rs,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end
      'Ferrer': begin
         alpha=string((*state).prefs.ferrer.alpha,f='(F5.2)')
         beta=string((*state).prefs.ferrer.beta,f='(F5.2)')

         aa=strcompress(string(prop.a,f='(F5.2)'),/rem)
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) ferrer',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mu0,$
                 '4) '+aa+' '+prop.fit.rad,$
                 '5) '+alpha+' '+prop.fit.alpha,$
                 '6) '+beta+' '+prop.fit.beta,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end
      'King': begin
         rc=strcompress(string(prop.a,f='(F5.2)'),/rem)
         rt=strcompress(string(prop.a*(*state).prefs.king.rt,f='(F5.2)'),/rem)
         alpha=string((*state).prefs.king.alpha,f='(F5.2)')
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y

         models=[models,$
                 '0) king',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mu0,$
                 '4) '+rc+' '+prop.fit.rc,$
                 '5) '+rt+' '+prop.fit.rt,$
                 '6) '+alpha+' '+prop.fit.alpha,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end


      ;---------PSF Models--------
      'Empirical': begin
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) psf',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mag,$
                 'Z) '+prop.skip,'']
      end
      'Gaussian': begin
         fwhm=strcompress(string(prop.a,f='(F5.2)'),/rem)
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) gaussian',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mag,$
                 '4) '+fwhm+' '+prop.fit.fwhm,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
         
      end
      'Moffat': begin
         alpha=string((*state).prefs.moffat.alpha,f='(F5.2)')

         fwhm=strcompress(string(prop.a,f='(F5.2)'),/rem)
         rat=strcompress(string(prop.b/prop.a,f='(F4.2)'),/rem)
         pa=pa2gf(prop.t,f='(F6.2)')
         xc=strcompress(string(prop.x,f='(F7.2)'),/rem)
         yc=strcompress(string(prop.y,f='(F7.2)'),/rem)
         xyfit=prop.fit.x+' '+prop.fit.y
         models=[models,$
                 '0) moffat',$
                 '1) '+xc+' '+yc+' '+xyfit,$
                 '3) '+mag+' '+prop.fit.mag,$
                 '4) '+fwhm+' '+prop.fit.fwhm,$
                 '5) '+alpha+' '+prop.fit.alpha,$
                 '9) '+rat+' '+prop.fit.q,$
                 '10) '+pa+' '+prop.fit.pa,$
                 'Z) '+prop.skip,'']
      end





      else: t=dialog_message('Encountered an unsupported morphology: '+$
                             prop.type,$
                             /err,/cen,tit='Unknown Morphology')
   endcase
endfor

;do we have a sky model?
sky0=widget_info((*state).wfitsky0,/button_set)
dsdx=widget_info((*state).wfitdsdx,/button_set)
dsdy=widget_info((*state).wfitdsdy,/button_set)
if sky0 or dsdx or dsdy then begin
   ;sort out the sky model
   
   if sky0 then begin           ;constant sky term
      widget_control,(*state).wsky0,get_value=val & val=val(0)
      if isnumber(val) eq 0 then begin
         val='0.0'
         widget_control,(*state).wsky0,set_value=val
      endif
      sky0model='1) '+temporary(val)+' 1'
   endif else sky0model='1) 0.0 0'

   if dsdx then begin           ;x-derivative term
      widget_control,(*state).wdsdx,get_value=val & val=val(0)
      if isnumber(val) eq 0 then begin
         val='0.0'
         widget_control,(*state).wdsdx,set_value=val
      endif
      dsdxmodel='1) '+temporary(val)+' 1'
   endif else dsdxmodel='2) 0.0 0'

   if dsdy then begin           ;y-derivative term
      widget_control,(*state).wdsdy,get_value=val & val=val(0)
      if isnumber(val) eq 0 then begin
         val='0.0'
         widget_control,(*state).wdsdy,set_value=val
      endif         
      dsdymodel='1) '+temporary(val)+' 1'
   endif else dsdymodel='3) 0.0 0'

   ;add it to the queue
   models=[models,$
           '0) sky',$
           sky0model,$
           dsdxmodel,$
           dsdymodel,$
           'Z) 0','']
endif



;write bpx file?
if bpxfile ne 'none' then begin
   g=where(bpx eq 1b,nmasked)
   if nmasked ne 0 then begin
      mkhdr,h,bpx
      putast,h,(*(*state).ast)
      writefits,bpxfile,temporary(bpx),temporary(h)
   endif else begin
      ;okay, if you said to make the BPX file, but didn't actually do 
      ;anything, then I'll just set it to "none" in galfit and proceed
      ;surely this is easier on GalFit, even if minor.
      bpxfile='none'
      widget_control,(*state).wbpx,set_value=bpxfile
      widget_control,(*state).wmkbpx,set_button=0b
   endelse
endif




;the GalFit data!!!
data=['#) Feedme file made by '+(*state).info.title+' on '+systime(),$
      'A) '+(*state).usefile.sci,$
      'B) '+outfile,$
      'C) '+(*state).usefile.unc,$
      'D) '+(*state).usefile.psf,$
      'E) '+fine,$
      'F) '+bpxfile,$
      'G) '+confile,$
      'H) '+x0+' '+x1+' '+y0+' '+y1,$
      'I) '+dx+' '+dy,$
      'J) '+zero,$
      'K) '+pixx+' '+pixy,$
      'O) '+disptype,$
      'P) '+gftype,$
      models]

;okay... Now write the stinkin' file..
for i=0,n_elements(data)-1 do printf,l,data(i)
close,l & free_lun,l



return,1b
end

