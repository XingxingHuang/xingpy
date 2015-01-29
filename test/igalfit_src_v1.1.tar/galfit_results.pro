pro galfit_results_clean,wid
widget_control,wid,get_uval=state
for i=0,n_tags(*state)-1 do begin
   case size((*state).(i),/tname) of
      'POINTER': ptr_free,(*state).(i)
      'OBJREF': obj_destroy,(*state).(i)
      else:
   endcase
endfor
if widget_info((*state).button,/valid) then $
   widget_control,(*state).button,set_button=0b
ptr_free,state
heap_gc                         ;Cleans up residual pointers and objects!
end


pro this_button_pressed,event
widget_control,event.top,get_uval=state
case event.press of
   0: begin                     ;some press?
   end
   1: begin                     ;left mouse button
   end 
   2: begin                     ;center mouse button
   end
   4: begin                     ;right mouse button
      (*state).mousemode=255b
   end
   else: message,string(event.press,f='(I5)'),/continue
endcase
end


pro this_button_released,event
widget_control,event.top,get_uvalue=state
case event.release of
   0: begin                     ;some release?
   end
   1: begin                     ;left mouse button
   end
   2: begin                     ;center mouse button
   end
   4: begin                     ;right mouse button
      (*state).mousemode=0b
   end
   else: message,string(event.release,f='(I5)'),/continue
endcase
end

pro this_mouse_moved,event
widget_control,event.top,get_uval=state
case (*state).mousemode of 
   0b: begin
      ;just moving around
       oView=((*state).oWindow->Select((*state).oScene,[event.x,event.y]))(0)
       if obj_valid(oView) then begin

          
          imsize=(*state).imsize;(*(*state).astr).naxis
          oView->GetProperty,uvalue=frame,location=loc
          xy=[event.x,event.y]
          xy=(xy-loc)*float(imsize)/(*state).winsize

          g=(where(frame eq (*state).imgnames))(0)
          if xy(0) gt 0 and xy(0) le imsize(0)-1 and $
             xy(1) gt 0 and xy(1) le imsize(1)-1 and $
             g ne -1 then begin
             pp=(*((*state).images(g)))(xy(0),xy(1))
             pp=strcompress(string(pp,f='(E+10.3)'),/rem)
             xs=strcompress(string(xy(0),f='(I5)'),/rem)
             ys=strcompress(string(xy(1),f='(I5)'),/rem)

             widget_control,(*state).wx,set_val=xs
             widget_control,(*state).wy,set_val=ys
             widget_control,(*state).wp,set_val=pp
             widget_control,(*state).wf,set_val=frame
             if ptr_valid((*state).astr) then begin

                xy2ad,xy(0),xy(1),*(*state).astr,a,d
                a=sixty(a/15.)        ;put into Segsidecimal
                sign=(d lt 0)?'-':'+' ;get the sign
                d=sixty(abs(d))       ;put into Segsidecimal
                
                
                widget_control,(*state).wr,set_value=' '+$
                               string(a(0),f='(I02)')+':'+$
                               string(a(1),f='(I02)')+':'+$
                               string(a(2),f='(F05.2)')
                               
                
                widget_control,(*state).wd,set_value=sign+$
                               string(d(0),f='(I02)')+':'+$
                               string(d(1),f='(I02)')+':'+$
                               string(d(2),f='(F06.3)')
             endif 
          endif
       endif
    end
   255b: begin
      ;right clicking to scale
      wind=widget_info((*state).wdraw,/geom)
      (*state).bias=(0.001>(event.x/wind.xsize)<1.0)
      (*state).cont=(0.001>(event.y/wind.ysize)<1.0)*20.
      display_imgblock,state
   end
   else: break
endcase
end





function gf2idl,hdr,keyword,val,err
  outstr=sxpar(hdr,keyword,count=n)

  case n of
     0: return,'Missing from header.'
     else: begin
        first=strmid(outstr,0,1)
        case first of
           '*': begin           ;parameter hit numerical inaccuracies
           end
           '[': begin           ;parameter held fixed
              outstr=strcompress(outstr,/rem)     
              val=strmid(outstr,1,strlen(outstr)-2)
              err=!values.f_nan     
           end
           else: begin          ;good value
              outstr=strsplit(outstr,'\+/\-',/ext,/reg)
              val=float(outstr(0))
              err=float(outstr(1))
              outstr=strcompress(outstr,/rem)
              outstr=strjoin(outstr,' '+string(177b)+' ')
           end
        endcase
     end
  endcase
  return,outstr
end


function load_imgblock,state

if ~file_exist((*state).imgblock) then return,file_error('GalFit output file')




;read the data
data=readfits((*state).imgblock,ext=1,hdata,/silent)
model=readfits((*state).imgblock,ext=2,hmodel,/silent)
resid=readfits((*state).imgblock,ext=3,hresid,/silent)

;deal with the mask
maskfile=strcompress(sxpar(hmodel,'MASK'),/rem)
if maskfile ne 'none' then begin
   if file_exist(maskfile) then begin
      mask=bytscl(1b-readfits(maskfile,/sil))
      for i=0,n_elements((*state).oView)-1 do begin
         ((*state).oMask(i))->SetProperty,data=mask,alpha=(*state).alpha,$
                                               blend=[3,4]
      endfor
   endif
endif

;check for flags
flags=sxpar(hmodel,'FLAGS')
if size(flags,/type) eq 7 then begin
   flags=strsplit(flags,' ',/ext)
   msgs=galfit_flags(flags)
   widget_control,(*state).wflags,set_value=msgs
endif



;record the size
(*state).imsize=size(data,/dim)

;get the fitsect data
fitsect=sxpar(hmodel,'FITSECT')
fitsect=strsplit(strmid(fitsect,1,strlen(fitsect)-2),',',/ext)
fitx=fix(strsplit(fitsect(0),':',/ext))-1
fity=fix(strsplit(fitsect(1),':',/ext))-1

;record the aspect ratio
(*state).aspect=float(sxpar(hdata,'NAXIS1'))/float(sxpar(hdata,'NAXIS2'))

;get the astrometry
extast,hdata,ast,noast

if noast ne -1 then begin       ;astrometry found, let's use it.
   ;record the astrometry
   (*state).astr=ptr_new(ast,/no_copy)
endif else begin                ;if no astrometry
;   data=data(fitx(0):fitx(1),fity(0):fity(1))
;   model=model(fitx(0):fitx(1),fity(0):fity(1))
;   resid=resid(fitx(0):fitx(1),fity(0):fity(1))
endelse

;record the images
(*state).images(0)=ptr_new(data,/no_copy) & (*state).imgnames(0)='Science'
(*state).images(1)=ptr_new(model,/no_copy) & (*state).imgnames(1)='Model'
(*state).images(2)=ptr_new(resid,/no_copy) & (*state).imgnames(2)='Residual'

;update the views
charsize=5
char=((*state).aspect lt 1)?[1,(*state).aspect]:[1./(*state).aspect,1]

for i=0,n_elements((*state).imgnames)-1 do begin
   ((*state).oView(i))->SetProperty,uvalue=(*state).imgnames(i)
   ((*state).oText(i))->SetProperty,string=(*state).imgnames(i),$
                                         color=[255,0,0b],loc=[2,2],$
                                         char_dim=char*charsize

   ((*state).oImage(i))->SetProperty,dim=(*state).imsize
   ((*state).oMask(i))->SetProperty,dim=(*state).imsize
   ((*state).oView(i))->GetProperty,view=view
   view=[0,0,(*state).imsize]
   ((*state).oView(i))->SetProperty,view=view
endfor

;now set the Chi2 data
chi2=strcompress(string(sxpar(hmodel,'CHI2NU'),f='(F5.2)'),/rem)
widget_control,(*state).wchi2,set_value=chi2
nfree=strcompress(string(sxpar(hmodel,'NFREE'),f='(I6)'),/rem)
widget_control,(*state).wnfree,set_value=nfree
ndof=strcompress(string(sxpar(hmodel,'NDOF'),f='(I6)'),/rem)
widget_control,(*state).wndof,set_value=ndof
nfix=strcompress(string(sxpar(hmodel,'NFIX'),f='(I6)'),/rem)
widget_control,(*state).wnfix,set_value=nfix

;label the components
comp=strcompress(sxpar(hmodel,'COMP_*'),/rem)
g=where(comp ne 'sky',nrow)
ncomp=n_elements(comp)
;nrow=ncomp
ncol=11


linestyle=0
unit=1.0

if nrow gt 0 then begin
   tabdata=replicate('',ncol,nrow)
   tablabels=replicate('',ncol,nrow)
   widget_control,(*state).wtable1,table_ysize=nrow
endif


;convert GF PA to IDL PA
gf_angle=90.0


for i=0,ncomp-1 do begin
   ii=strcompress(string(i+1,f='(I6)'),/rem)
   
   case comp(i) of
      'sersic': begin
         tabdata(0,i)='sersic'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MAG')
         tabdata(4,i)=gf2idl(hmodel,ii+'_RE',re)
         tabdata(5,i)=gf2idl(hmodel,ii+'_N')
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
            
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Total Magnitude (mag)'
         tablabels(4,i)='Effective Radius (pix)'
         tablabels(5,i)='Sersic Index'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
                  
         prop=define_region('Sersic',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=re
         prop.b=re*rat
         prop.t=pa+gf_angle
         
      end
      'devauc': begin
         tabdata(0,i)='devauc'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MAG')
         tabdata(4,i)=gf2idl(hmodel,ii+'_RE',re)
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Total Magnitude (mag)'
         tablabels(4,i)='Effective Radius'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
         
         prop=define_region('DeVauc',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=re
         prop.b=re*rat
         prop.t=pa+gf_angle
         
      end
      'expdisk': begin
         tabdata(0,i)='expdisk'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MAG')
         tabdata(4,i)=gf2idl(hmodel,ii+'_RS',re)
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Total Magnitude (mag)'
         tablabels(4,i)='Effective Radius (pix)'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
         
         prop=define_region('ExpDisk',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=re
         prop.b=re*rat
         prop.t=pa+gf_angle
         
      end
      'psf': begin
         tabdata(0,i)='psf'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MAG')
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Total Magnitude (mag)'
         
         prop=define_region('Empirical',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.r=3.0
         
      end
      'sky': begin
         widget_control,(*state).wsky0,set_value=gf2idl(hmodel,ii+'_SKY')
         widget_control,(*state).wdsdx,set_value=gf2idl(hmodel,ii+'_DSDX')
         widget_control,(*state).wdsdy,set_value=gf2idl(hmodel,ii+'_DSDY')
      end
      'nuker': begin
         tabdata(0,i)='nuker'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MU')
         tabdata(4,i)=gf2idl(hmodel,ii+'_RB',rb)
         tabdata(5,i)=gf2idl(hmodel,ii+'_ALPHA')
         tabdata(6,i)=gf2idl(hmodel,ii+'_BETA')
         tabdata(7,i)=gf2idl(hmodel,ii+'_GAMMA')
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Central Surf. Bright. (mag/arcsec2)'
         tablabels(4,i)='Break Radius (pix)'
         tablabels(5,i)='alpha'
         tablabels(6,i)='beta'
         tablabels(7,i)='gamma'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
                  
         prop=define_region('Nuker',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=re
         prop.b=rb*rat
         prop.t=pa+gf_angle
         
      end
         
      'edgedisk': begin
         tabdata(0,i)='edge-on'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MU_0')
         tabdata(4,i)=gf2idl(hmodel,ii+'_HS',hs)    ;scale height
         tabdata(5,i)=gf2idl(hmodel,ii+'_RS',rs)    ;scale length
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Central Surf. Bright. (mag/arcsec2)'
         tablabels(4,i)='Scale Height (pix)'
         tablabels(5,i)='Scale Length (pix)'
         tablabels(10,i)='Position Angle (deg)'
         
         prop=define_region('Edge-on Disk',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=(rs>hs)
         prop.b=(rs<hs)
         prop.t=pa+gf_angle
      end
      'moffat': begin
         
         tabdata(0,i)='Moffat'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MAG')
         tabdata(4,i)=gf2idl(hmodel,ii+'_FWHM',fwhm)
         tabdata(5,i)=gf2idl(hmodel,ii+'_C')
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Total Magnitude (mag)'
         tablabels(4,i)='FWHM (pix)'
         tablabels(5,i)='Power-Law Index'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
         
         prop=define_region('Moffat',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=fwhm
         prop.b=fwhm*rat
         prop.t=pa+gf_angle
      end
      'ferrer': begin
         

         stop
         
         prop=define_region('Ferrer',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=rad
         prop.b=rad*rat
         prop.t=pa+gf_angle
         
      end
      
      'gaussian': begin
         
         tabdata(0,i)='Gaussian'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MAG')
         tabdata(4,i)=gf2idl(hmodel,ii+'_FWHM',fwhm)
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Total Magnitude (mag)'
         tablabels(4,i)='FWHM (pix)'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
         
         prop=define_region('Gaussian',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=fwhm
         prop.b=fwhm*rat
         prop.t=pa+gf_angle
      end
      'king': begin
         
         tabdata(0,i)='King'
         tabdata(1,i)=gf2idl(hmodel,ii+'_XC',x)
         tabdata(2,i)=gf2idl(hmodel,ii+'_YC',y)
         tabdata(3,i)=gf2idl(hmodel,ii+'_MU')
         tabdata(4,i)=gf2idl(hmodel,ii+'_RC',rc)
         tabdata(5,i)=gf2idl(hmodel,ii+'_RT',rt)
         tabdata(6,i)=gf2idl(hmodel,ii+'_ALPHA')
         tabdata(9,i)=gf2idl(hmodel,ii+'_AR',rat)
         tabdata(10,i)=gf2idl(hmodel,ii+'_PA',pa)
         
         tablabels(0,i)='Function'
         tablabels(1,i)='x (pix)'
         tablabels(2,i)='y (pix)'
         tablabels(3,i)='Central Surf. Bright (mag/arcsec2)'
         tablabels(4,i)='Rc (pix)'
         tablabels(5,i)='Rt (pix)'
         tablabels(6,i)='alpha'
         tablabels(9,i)='Axis Ratio'
         tablabels(10,i)='Position Angle (deg)'
                  
         prop=define_region('King',rgb,linestyle=linestyle)
         prop.x=x-fitx(0)-unit
         prop.y=y-fity(0)-unit
         prop.a=rc
         prop.b=rc*rat
         prop.t=pa+gf_angle
         
      end
      else: begin
         print,'Unknown component.'
         stop
      end
   endcase
   
   

   ;reset the colors and draw region
   if comp(i) ne 'sky' then begin

      ;compute the luminosity
      lum=total((*state).rgbwht*rgb)

      ;reset the table color
      widget_control,(*state).wtable1,background_color=rgb,$
                     use_table_select=[0,i,ncol-1,i]
      
      ;make the region
      make_roi,prop,xx,yy,zz
      
      for ii=0,(*state).nimages(0)-1 do begin
         for jj=0,(*state).nimages(1)-1 do begin
            oROI=obj_new('IDLgrROI',color=rgb,style=2,uvalue=prop,$
                         line=prop.linestyle,thick=prop.thick)
            oROI->AppendData,xx,yy,zz
            ((*state).oROIModel(ii,jj))->Add,oROI
            ((*state).oROIGroup(ii,jj))->Add,oROI
         endfor
      endfor
   endif
   
endfor
if nrow ne 0 then widget_control,(*state).wtable1,set_value=tabdata



(*state).imgloaded=1b
(*state).tablabels=ptr_new(tablabels,/no_copy)
file=reverse(strsplit((*state).imgblock,'/',/ext))
widget_control,(*state).wfile,set_value=file(0)


;now display the results
display_imgblock,state,/loadimage


return,1b
end


pro display_imgblock,state,LOADIMAGE=loadimage
  draw=widget_info((*state).wdraw,/geom)

  ncol=256
  cmap=0>(((indgen(ncol)-(ncol-1)*(*state).bias)*(*state).cont)+$
          0.5*(ncol-1))<(ncol-1)
  cmap=byte(ncol-1)-bytscl(temporary(cmap))
  for i=0,n_elements((*state).oView)-1 do begin
     ((*state).oImage(i))->SetProperty,data=cmap(bytscl(*((*state).images(i))))



     if keyword_set(LOADIMAGE) then begin
        ((*state).oView(i))->GetProperty,view=view
        if (*state).aspect lt 1 then $
           view(2)=view(2)/(*state).aspect $
        else view(3)=view(3)*(*state).aspect
           
        ((*state).oView(i))->SetProperty,view=view
     endif
  endfor

  (*state).oWindow->Draw,(*state).oScene
end


pro galfit_results_event,event
widget_control,event.id,get_uvalue=uval

case uval of
   'DRAW': begin
      widget_control,event.top,get_uvalue=state
      if (*state).imgloaded then begin
         case event.type of
            0: this_button_pressed,event
            1: this_button_released,event
            2: this_mouse_moved,event
            else: break
         endcase
      endif
   end
   'TRANS': begin
      widget_control,event.top,get_uval=state
      for i=0,n_elements((*state).oView)-1 do begin
         widget_control,(*state).wtrans,get_val=val 
         ((*state).oMask(i))->SetProperty,alpha=val
      endfor
      (*state).oWindow->Draw,(*state).oScene

   end

   'TABLE1': begin
      case tag_names(event,/struct) of
         'WIDGET_CONTEXT': begin
            widget_control,event.top,get_uval=state
            tablabels=*(*state).tablabels
            sz=size(tablabels,/dim)
            if n_elements(sz) eq 1 then sz=[sz,1]
            if event.col lt sz(0) and event.row lt sz(1) and $
               event.col ge 0     and event.row ge 0 then begin
               label=tablabels(event.col,event.row)
               if label ne '' then begin
                  widget_control,(*state).wcontextlabel,set_value=label,$
                                 xsize=strlen(label)
                  widget_displaycontextmenu,event.id,event.x,event.y,$
                                            (*state).wcontext
               endif
            endif
         end
         else: 
      endcase      
   end
   'LOAD': begin
      widget_control,event.top,get_uvalue=state
      t=dialog_pickfile(file='imgblock.fits',/fix_filt,$
                        filter=['*fits;*fits.gz','*fit;*fit.gz'],/must_exist)
                        
      if t(0) ne '' then begin
         (*state).imgblock=t(0)
         t=load_imgblock(state)
      endif
   end
   'LABEL': begin
      widget_control,event.top,get_uval=state
      set=widget_info((*state).wlabel,/button_set)
      for i=0,(*state).nimages(0)-1 do begin
         for j=0,(*state).nimages(1)-1 do begin
            ((*state).oText(i,j))->SetProperty,hide=set
         endfor
      endfor
      widget_control,(*state).wlabel,set_button=1b-set
      display_imgblock,state
   end
   'REGION':begin
      widget_control,event.top,get_uval=state
      set=widget_info((*state).wregion,/button_set)
      for ii=0,(*state).nimages(0)-1 do begin
         for jj=0,(*state).nimages(1)-1 do begin
            ((*state).oROIModel(ii,jj))->SetProperty,hide=set
         endfor
      endfor

      widget_control,(*state).wregion,set_button=1b-set
      display_imgblock,state
   end

   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='galfit_results'
   'CLOSE': widget_control,event.top,/destroy

   else:
endcase
end



pro galfit_results,IMGBLOCK=imgblock,BASE=base,GROUP=group,REDISPLAY=redisplay,$
                   BUTTON=button

if not keyword_set(IMGBLOCK) then imgblock='imgblock.fits'
if not keyword_set(BUTTON) then button=-1L
if not keyword_set(REDISPLAY) then begin



   ;weights for the colors
   rgbwht=[0.212,0.715,0.073]

   ;initial opacity
   alpha=0.2

   ;lay out of displays:
   nx=3
   ny=1

   ;sizes of displays:
   xdisp=300
   ydisp=300
   margin=6
   dim=[xdisp,ydisp]

   ;size of *THE* display
   xsize=nx*xdisp+(nx+1)*margin
   ysize=ny*ydisp+(ny+1)*margin
   
   ;default settings for the table
   columns='('+strcompress(string(indgen(11),f='(I2)'),/rem)+')'
   nrow=2*n_elements(columns)
   
   xtext=110
   ytext=13
   
   base=widget_base(title='GalFit Results',group=group,mbar=mbar,/column)
   
   wcontext=widget_base(base,/context_menu,uname='CONTEXT')
   wcontextlabel=widget_button(wcontext,xsize=12,/align_center,$
                               uval='CONTEXTLABEL')

   filemenu=widget_button(mbar,value='File',/menu)
   load=widget_button(filemenu,value='Load',uval='LOAD')
   close=widget_button(filemenu,value='Close',uval='CLOSE',/sep)
   dispmenu=widget_button(mbar,value='Display',/menu)
   wlabel=widget_button(dispmenu,value='Labels',/checked,uval='LABEL')
   wregion=widget_button(dispmenu,value='Regions',/checked,uval='REGION')
   widget_control,wlabel,set_button=1b
   widget_control,wregion,set_button=1b

   helpmenu=widget_button(mbar,value='Help',/menu,/help)
   help=widget_button(helpmenu,value='Help',uval='HELP')
   
   top=widget_base(base,/row)
   
   disp=widget_base(top,/column,/frame)
   r=widget_base(disp,/row)
   sunk=1b
   wfile=widget_label(r,value='',xsize=148,ysize=ytext+2,/align_cent,sunk=sunk)
   
   r=widget_base(disp,/row)
   l=widget_label(r,value='x:')
   wx=widget_label(r,value='',xsize=20,ysize=ytext,/align_left,sunk=sunk)
   l=widget_label(r,value='r:')
   wr=widget_label(r,value='',xsize=85,ysize=ytext,/align_left,sunk=sunk)
   
   r=widget_base(disp,/row)
   l=widget_label(r,value='y:')
   wy=widget_label(r,value='',xsize=20,ysize=ytext,/align_left,sunk=sunk)
   l=widget_label(r,value='d:')
   wd=widget_label(r,value='',xsize=85,ysize=ytext,/align_left,sunk=sunk)
   
   r=widget_base(disp,/row)
   l=widget_label(r,value='p:')
   wp=widget_label(r,value='',xsize=70,ysize=ytext,/align_left,sunk=sunk)
   wf=widget_label(r,value='',xsize=55,ysize=ytext,/align_left,sunk=sunk)


   r=widget_base(disp,/row)
   l=widget_label(r,value='Mask')
   wtrans=cw_fslider(r,/drag,format='(F3.1)',max=1,min=0.,uval='TRANS',$
                     value=alpha,/suppress,xsize=120)
   
   
   
   tables=widget_base(top,/column,/frame)
   
   pars=['chi'+string(178b),'Nfree','Ndof','Nfix','sky0','dS/dx','dS/dy']
 ;  background_color=table_colors(nrow)
   row=widget_base(tables,/row)
   
   data=widget_base(row,/column)
   wchi2=cw_label(data,'Chi'+string(178b)+'/nu =',/align_left,xsi=xtext,$
                  ysi=ytext,value='')
   wnfree=cw_label(data,'  Nfree =',/align_left,xsi=xtext,ysi=ytext,value='')
   wndof=cw_label(data,'   Ndof =',/align_left,xsi=xtext,ysi=ytext,value='')
   wnfix=cw_label(data,'   Nfix =',/align_left,xsi=xtext,ysi=ytext,value='')
   wsky0=cw_label(data,'   Sky0 =',/align_left,xsi=xtext,ysi=ytext,value='')
   wdsdx=cw_label(data,'  dS/dx =',/align_left,xsi=xtext,ysi=ytext,value='')
   wdsdy=cw_label(data,'  dS/dy =',/align_left,xsi=xtext,ysi=ytext,value='')
   

   wtable1=widget_table(row,xsize=11,ysize=0,/scroll,$
                        /resizeable_column,column_label=columns,$
                        ;background_color=background_color,$
                        scr_xsize=400,$
                        column_widths=154,$
                        uvalue='TABLE1',/context_events)
   
   wflags=widget_list(row,xsize=11,ysize=0,uvalue='FLAGS',scr_xsize=150)

   
   mid=widget_base(base,/row)
   
   wdraw=widget_draw(mid,xsize=xsize,ysize=ysize,/frame,$
                     uval='DRAW',graphics=2,$
                     /button,/motion,keyboard=2)
   
   oScene=obj_new('IDLgrScene',color=[192b,192b,192b])
   oImage=objarr(nx,ny)
   oMask=objarr(nx,ny)
   oView=objarr(nx,ny)
   oModel=objarr(nx,ny)
   oText=objarr(nx,ny)
   oROIModel=objarr(nx,ny)
   oROIGroup=objarr(nx,ny)
   view=[0,0,dim]

;   oPalette=obj_new('IDLgrPalette')
;   oPalette->Loadct,13

   for i=0,nx-1 do begin
      for j=0,ny-1 do begin
         viewloc=[i,j]*([xdisp,ydisp]+margin)+margin
         oImage(i,j)=obj_new('IDLgrImage')
         oMask(i,j)=obj_new('IDLgrImage',alpha=alpha,blend=[3,4])
;palette=oPalette,$

         oView(i,j)=obj_new('IDLgrView',loc=viewloc,dim=dim,view=view)

         oModel(i,j)=obj_new('IDLgrModel')
         oText(i,j)=obj_new('IDLgrText')
         oROIModel(i,j)=obj_new('IDLgrModel')
         oROIGroup(i,j)=obj_new('IDLanROIGroup')         

         oView(i,j)->Add,oModel(i,j)
         oModel(i,j)->Add,oImage(i,j)
         oModel(i,j)->Add,oMask(i,j)
         oModel(i,j)->Add,oText(i,j)
         oModel(i,j)->Add,oROIModel(i,j)

         oScene->Add,oView(i,j)
      endfor
   endfor
   


   
   widget_control,base,/realize
   widget_control,wdraw,get_value=oWindow
   oWindow->Draw,oScene
   
   state={oWindow:oWindow,$
          oView:oView,$
          oModel:oModel,$
          oImage:oImage,$
          oMask:oMask,$
          oText:oText,$
          oScene:oScene,$
          oROIModel:oROIModel,$
          oROIGroup:oROIGroup,$
          viewloc:viewloc,$
          wlabel:wlabel,$
          wregion:wregion,$
          wdraw:wdraw,$
          wtable1:wtable1,$
          wflags:wflags,$
          wfile:wfile,$
          wx:wx,$
          wy:wy,$
          wr:wr,$
          wd:wd,$
          wp:wp,$
          wf:wf,$
          wchi2:wchi2,$
          wnfree:wnfree,$
          wnfix:wnfix,$
          wndof:wndof,$
          wsky0:wsky0,$
          wdsdx:wdsdx,$
          wdsdy:wdsdy,$
          wtrans:wtrans,$
          wcontext:wcontext,$
          wcontextlabel:wcontextlabel,$
          alpha:alpha,$
          rgbwht:rgbwht,$
          imsize:[0,0],$
          tablabels:ptr_new(),$
          nimages:[nx,ny],$
          images:ptrarr(nx,ny),$
          imgnames:strarr(nx,ny),$
          astr:ptr_new(),$
          cont:0.8,$
          bias:0.3,$
          mousemode:0b,$
          aspect:0.0,$
          winsize:dim,$
          button:button,$
          mask:0b,$
          imgblock:imgblock,$
          imgloaded:0b}
   state=ptr_new(state,/no_copy)
   widget_control,base,set_uvalue=state
   
   xmanager,'galfit_results',base,/no_block,clean='galfit_results_clean'
endif else begin
   widget_control,group,get_uval=pstate
   widget_control,(*pstate).wresults,get_uval=state


   (*state).imgblock=imgblock

   ;delete any existing regions
   nreg=(*pstate).oROIModel->count()
   for i=0l,nreg-1 do begin

      for ii=0,(*state).nimages(0)-1 do begin
         for jj=0,(*state).nimages(1)-1 do begin
            oROI=((*state).oROIModel(ii,jj))->Get(pos=i)
            ((*state).oROIModel(ii,jj))->Remove,oROI
            ((*state).oROIGroup(ii,jj))->Remove,oROI
         endfor
      endfor
   endfor
   
   widget_control,(*state).wflags,set_value=''
endelse



;load the image?
if file_exist(imgblock) then t=load_imgblock(state)

end
