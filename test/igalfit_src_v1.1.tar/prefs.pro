
function mkcolorbutton,rgb
nx=25                         ;xsize of color button
ny=10                         ;ysize of color button
nn=1                          ;black border around button
t=bytarr(nx,ny,3)
for j=0,2 do t(nn:(nx-nn-1),nn:(ny-nn-1),j)=rgb(j)
return,t
end

pro prefs_setvalues,state
pstate=(*state).pstate
prefs=(*pstate).prefs

widget_control,(*state).wtemp,set_val=prefs.tempdir

;set the autoscale
widget_control,(*state).wlosig,set_value=string(prefs.losig,f='(F5.2)')
widget_control,(*state).whisig,set_value=string(prefs.hisig,f='(F5.2)')
widget_control,(*state).wsigma,set_value=string(prefs.sigma,f='(F5.2)')


;set double click
widget_control,(*state).wtime,set_value=$
               string(prefs.double_click_time,f='(F5.3)')

;sextractor things
widget_control,(*state).wacrit,set_value=string(prefs.acrit,f='(I4)')
widget_control,(*state).wrcrit,set_value=string(prefs.rcrit,f='(F5.2)')
widget_control,(*state).wdefmorph,get_val=val
g=(where(prefs.defmorph eq val))(0)
widget_control,(*state).wdefmorph,set_combobox_select=g

;set the galfit
widget_control,(*state).wgfexec,set_value=prefs.exec
widget_control,(*state).wfeedme,set_value=prefs.feedme

end
pro prefs_cleanup,wid
widget_control,wid,get_uval=state
ptr_free,state
end

function prefs_autoscale,state

  widget_control,(*state).wlosig,get_value=losig & losig=losig(0)
  widget_control,(*state).whisig,get_value=hisig & hisig=hisig(0)
  widget_control,(*state).wsigma,get_value=sigma & sigma=sigma(0)

  if isnumber(losig) eq 0 then return,type_error('Low Sigma')
  if isnumber(hisig) eq 0 then return,type_error('High Sigma')
  if isnumber(sigma) eq 0 then return,type_error('Sigma Threshold')

  (*state).prefs.losig=float(losig)
  (*state).prefs.hisig=float(hisig)
  (*state).prefs.sigma=float(sigma)

  autoscale,state
  return,1b
end
pro prefs_close,event
widget_control,event.top,get_uval=state
widget_control,event.top,/destroy
end

pro prefs_event,event
widget_control,event.id,get_uval=uval
case uval of
   ;STUFF FOR VANE BAR
   'VANECOL': begin
      widget_control,event.top,get_uval=state
      g=where(event.id eq (*state).wvanecolors)
      widget_control,(*state).wvanecolor,/bitmap,$
                     set_value=mkcolorbutton((*state).rgb(g(0)).rgb),$
                     tooltip=(*state).rgb(g(0)).name
      pstate=(*state).pstate

      (*pstate).oVane->SetProperty,color=(*state).rgb(g(0)).rgb
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'VANESIZESLIDE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wvanesizeslide,get_value=val 
      widget_control,(*state).wvanesizevalue,$
                     set_value=string(val(0),$
                                      f=(*state).vanedata.sizefmt)
      pstate=(*state).pstate
      (*pstate).prefs.vanesize=float(val(0))
      compass,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'VANESIZEVALUE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wvanesizevalue,get_value=val & val=val(0)
      if isnumber(val) ne 0 then begin      
         val=(*state).vanedata.sizemin>float(val)<(*state).vanedata.sizemax
         widget_control,(*state).wvanesizeslide,set_val=val
         widget_control,(*state).wvanesizevalue,$
                        set_value=string(val(0),$
                                         f=(*state).vanedata.sizefmt)
      endif else begin
         widget_control,(*state).wvanesizeslide,get_value=val 
         widget_control,(*state).wvanesizevalue,$
                        set_value=string(val(0),$
                                         f=(*state).vanedata.sizefmt)
      endelse
      pstate=(*state).pstate
      (*pstate).prefs.vanesize=float(val(0))
      compass,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end

   'VANETHICKSLIDE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wvanethickslide,get_value=val 
      widget_control,(*state).wvanethickvalue,$
                     set_value=string(val(0),$
                                      f=(*state).vanedata.thickfmt)
      pstate=(*state).pstate
      (*pstate).prefs.vanethick=float(val(0))
      compass,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'VANETHICKVALUE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wvanethickvalue,get_value=val & val=val(0)
      if isnumber(val) ne 1 then begin      
         val=(*state).vanedata.thickmin>float(val)<(*state).vanedata.thickmax
         widget_control,(*state).wvanethickslide,set_val=val
         widget_control,(*state).wvanethickvalue,$
                        set_value=string(val(0),$
                                         f=(*state).vanedata.thickfmt)
      endif else begin
         widget_control,(*state).wvanethickslide,get_value=val 
         widget_control,(*state).wvanethickvalue,$
                        set_value=string(val(0),$
                                         f=(*state).vanedata.thickfmt)
      endelse
      pstate=(*state).pstate
      (*pstate).prefs.vanethick=float(val(0))
      compass,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end


   ;STUFF FOR SCALE BAR
   'SCALECOL': begin
      widget_control,event.top,get_uval=state
      g=where(event.id eq (*state).wscalecolors)
      widget_control,(*state).wscalecolor,/bitmap,$
                     set_value=mkcolorbutton((*state).rgb(g(0)).rgb),$
                     tooltip=(*state).rgb(g(0)).name
      pstate=(*state).pstate

      (*pstate).oScale->SetProperty,color=(*state).rgb(g(0)).rgb
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'SCALESIZESLIDE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wscalesizeslide,get_value=val 
      widget_control,(*state).wscalesizevalue,$
                     set_value=string(val(0),$
                                      f=(*state).scaledata.sizefmt)
      pstate=(*state).pstate
      (*pstate).prefs.scalesize=float(val(0))
      scalebar,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'SCALESIZEVALUE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wscalesizevalue,get_value=val & val=val(0)
      if isnumber(val) ne 0 then begin      
         val=(*state).scaledata.sizemin>float(val)<(*state).scaledata.sizemax
         widget_control,(*state).wscalesizeslide,set_val=val
         widget_control,(*state).wscalesizevalue,$
                        set_value=string(val(0),$
                                         f=(*state).scaledata.sizefmt)
      endif else begin
         widget_control,(*state).wscalesizeslide,get_value=val 
         widget_control,(*state).wscalesizevalue,$
                        set_value=string(val(0),$
                                         f=(*state).scaledata.sizefmt)
      endelse
      pstate=(*state).pstate
      (*pstate).prefs.scalesize=float(val(0))
      scalebar,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'SCALEUNIT': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      (*pstate).prefs.scaleunit=widget_info((*state).wscaleunit,/combobox_gette)
      scalebar,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end


   'SCALETHICKSLIDE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wscalethickslide,get_value=val 
      widget_control,(*state).wscalethickvalue,$
                     set_value=string(val(0),$
                                      f=(*state).scaledata.thickfmt)
      pstate=(*state).pstate
      (*pstate).prefs.scalethick=float(val(0))
      scalebar,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'SCALETHICKVALUE': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wscalethickvalue,get_value=val & val=val(0)
      if isnumber(val) ne 1 then begin      
         val=(*state).scaledata.thickmin>float(val)<(*state).scaledata.thickmax
         widget_control,(*state).wscalethickslide,set_val=val
         widget_control,(*state).wscalethickvalue,$
                        set_value=string(val(0),$
                                         f=(*state).scaledata.thickfmt)
      endif else begin
         widget_control,(*state).wscalethickslide,get_value=val 
         widget_control,(*state).wscalethickvalue,$
                        set_value=string(val(0),$
                                         f=(*state).scaledata.thickfmt)
      endelse
      pstate=(*state).pstate
      (*pstate).prefs.scalethick=float(val(0))
      scalebar,pstate
      (*pstate).oWindow->Draw,(*pstate).oView
   end






   'BACKCOL': begin
      widget_control,event.top,get_uval=state
      g=where(event.id eq (*state).wcol)
      widget_control,(*state).wbackcol,/bitmap,$
                     set_value=mkcolorbutton((*state).rgb(g(0)).rgb),$
                     tooltip=(*state).rgb(g(0)).name
      pstate=(*state).pstate
      (*pstate).oView->SetProperty,color=(*state).rgb(g(0)).rgb
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'DOUBLECLICK': begin
      widget_control,event.top,get_uvalue=state
      time=systime(/second)
      dtime=time-(*state).clicktime
      (*state).clicktime=temporary(time)
      if dtime le 1. then begin
         pstate=(*state).pstate
         widget_control,(*state).wtime,set_value=$
                        strcompress(string(dtime,f='(F5.3)'),/rem)
         (*(*state).pstate).prefs.double_click_time=dtime
      endif
   end
   'AUTO': begin
      widget_control,event.top,get_uval=state
      t=prefs_autoscale(state)
   end
   'SETVAL': begin
      widget_control,event.top,get_uval=state
      name=widget_info(event.id,/uname)
      if name eq '' then begin
         t=dialog_message('You need to set the UNAME for this widget!',$
                          /err,/cen,tit='No UNAME')
         return
      endif

      widget_control,event.id,get_value=val & val=val(0)
      if isnumber(val) eq 0 then begin
         t=type_error(name)
         return
      endif else begin
         cmd='(*(*state).pstate).prefs.'+name+'='+val(0)
         t=1b-execute(cmd,1b,1b)
         if t then t=dialog_message('Unable to set the parameter '+name,$
                                     /error,/center,title='Unknown Error')
      endelse
   end
   'TEMPDIR': begin
      widget_control,event.top,get_uval=state
      widget_control,(*state).wtemp,get_val=tempdir & tempdir=tempdir(0)
      if tempdir eq (file_search(tempdir))(0) then begin      
         psep=path_sep()
         if strmid(tempdir,strlen(tempdir)-1,1) ne psep then tempdir+=psep
         (*(*state).pstate).prefs.tempdir=tempdir
      endif else begin
         widget_control,(*state).wtemp,set_val=(*(*state).pstate).prefs.tempdir
         t=dialog_message('The temporary directory does not exist.',/err,$
                          /center,title='No Temp Dir.')
      endelse
   end
   'DEFMORPH': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      g=(where(event.id eq (*state).morphinfo.wid))(0)
      thismorph=(*state).morphinfo(g).type
      widget_control,(*state).wdefmorph,set_value=thismorph,$
                     tooltip=(*state).morphinfo(g).tip
      (*state).morphstate=thismorph            
      (*pstate).prefs.defmorph=thismorph
   end

   'MAXRAD': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).wmaxrad,get_value=maxrad & maxrad=maxrad(0)
      if isnumber(maxrad) ne 0 then begin
         (*pstate).prefs.iraf.maxrad=float(maxrad)
      endif else begin
         widget_control,(*state).wmaxrad,set_value=$
                        string((*pstate).prefs.iraf.maxrad,f='(F4.1)')
      endelse
   end
   'FWHM': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).wfwhm,get_value=fwhm & fwhm=fwhm(0)
      if isnumber(fwhm) ne 0 then begin
         (*pstate).prefs.iraf.fwhm=float(fwhm)
      endif else begin
         widget_control,(*state).wfwhm,set_value=$
                        string((*pstate).prefs.iraf.fwhm,f='(F3.1)')
      endelse
   end
   'WIDTH': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      (*pstate).prefs.iraf.width=fix(event.str)
   end

   'COMBINE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      (*pstate).prefs.iraf.combine=event.str
   end

   'RANGE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      (*pstate).prefs.iraf.range=event.str
   end
   'BOXSIZE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).wboxsize,get_value=boxsize & boxsize=boxsize(0)

      if isnumber(boxsize) eq 1 then begin
         (*pstate).prefs.iraf.boxsize=fix(boxsize)
      endif else begin
         widget_control,(*state).wboxsize,set_value=$
                        string((*pstate).prefs.iraf.boxsize,f='(I4)')
      endelse
   end

   'NLEVEL': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      (*pstate).prefs.iraf.nlevels=fix(event.str)
   end
   'NTICK': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      (*pstate).prefs.iraf.nticks=fix(event.str)
   end

   'CONSIZE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).wconsize,get_value=consize & consize=consize(0)

      if isnumber(consize) eq 1 then begin
         (*pstate).prefs.iraf.consize=fix(consize)
      endif else begin
         widget_control,(*state).wconsize,set_value=$
                        string((*pstate).prefs.iraf.consize,f='(I4)')
      endelse
   end


   'HISSIZE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).whissize,get_value=hissize & hissize=hissize(0)

      if isnumber(hissize) eq 1 then begin
         (*pstate).prefs.iraf.hissize=fix(hissize)
      endif else begin
         widget_control,(*state).whissize,set_value=$
                        string((*pstate).prefs.iraf.hissize,f='(I4)')
      endelse
   end
   'NBINS': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      widget_control,(*state).wnbins,get_value=nbins & nbins=nbins(0)

      if isnumber(nbins) eq 1 then begin
         (*pstate).prefs.iraf.nbins=fix(nbins)
      endif else begin
         widget_control,(*state).wnbins,set_value=$
                        string((*pstate).prefs.iraf.nbins,f='(I4)')
      endelse
   end


   'TAB': break
   'CLOSE': prefs_close,event
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='prefs'

endcase
end

pro prefs,pstate,GROUP=group

base=widget_base(title='iGalFit Preferences',GROUP=group,mbar=mbar)

filemenu=widget_button(mbar,value='File',/menu)
close=widget_button(filemenu,value='Close',uval='CLOSE')
helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uval='HELP')

;get list of colors
define_rgb,rgb
ncol=n_elements(rgb)

;start the tab widget
wtab=widget_tab(base,uval='TAB',xsize=350)

;the display data (vane and scalebar)
wdisplay=widget_base(wtab,title='Display',/col)
top=widget_base(wdisplay,/row)
lhs=widget_base(top,/col)
comp=widget_base(lhs,/col,frame=1)
l=widget_label(comp,value='Compass')

r=widget_base(comp,/row)
l=widget_label(r,value='Color')
(*pstate).oVane->GetProperty,color=vane
g=(where(rgb.rgb(0) eq vane(0) and $
         rgb.rgb(1) eq vane(1) and $
         rgb.rgb(2) eq vane(2)))(0) 
wvanecolor=widget_button(r,/bitmap,value=mkcolorbutton(rgb(g).rgb),/menu,$
                         tooltip=rgb(g).name)
wvanecolors=lonarr(ncol)
for i=0,ncol-1 do wvanecolors(i)=widget_button(wvanecolor,/bitmap,$
                                               uval='VANECOL',$
                                               value=mkcolorbutton(rgb(i).rgb))

row=widget_base(comp,/row)

sizebase=widget_base(row,/col)
vanedata={sizemin:0.1,sizemax:99.9,sizefmt:'(F4.1)',$
          thickmin:1,thickmax:10,thickfmt:'(I2)'}

l=widget_label(sizebase,value='Size')
wvanesizeslide=cw_fslider(sizebase,/vert,/drag,/supp,/edit,$
                          min=vanedata.sizemin,$
                          max=vanedata.sizemax,$
                          value=(*pstate).prefs.vanesize,uval='VANESIZESLIDE')
wvanesizevalue=widget_text(sizebase,xsize=4,/edit,uval='VANESIZEVALUE',$
                           value=string((*pstate).prefs.vanesize,$
                                        f=vanedata.sizefmt))

thickbase=widget_base(row,/col)
l=widget_label(thickbase,value='Thick')
wvanethickslide=cw_fslider(thickbase,/vert,/drag,/supp,/edit,$
                           min=vanedata.thickmin,$
                           max=vanedata.thickmax,$
                           value=(*pstate).prefs.vanethick,$
                           uval='VANETHICKSLIDE')
wvanethickvalue=widget_text(thickbase,xsize=2,/edit,uval='VANETHICKVALUE',$
                           value=string((*pstate).prefs.vanethick,$4
                                        f=vanedata.thickfmt))

rhs=widget_base(top,/col)

scalebase=widget_base(rhs,/col,frame=1)
l=widget_label(scalebase,value='Scalebar')

r=widget_base(scalebase,/row)
l=widget_label(r,value='Color')
(*pstate).oScale->GetProperty,color=scale
g=(where(rgb.rgb(0) eq scale(0) and $
         rgb.rgb(1) eq scale(1) and $
         rgb.rgb(2) eq scale(2)))(0) 
wscalecolor=widget_button(r,/bitmap,value=mkcolorbutton(rgb(g).rgb),/menu,$
                          tooltip=rgb(g).name)
wscalecolors=lonarr(ncol)
for i=0,ncol-1 do wscalecolors(i)=widget_button(wscalecolor,/bitmap,$
                                                uval='SCALECOL',$
                                                val=mkcolorbutton(rgb(i).rgb))

row=widget_base(scalebase,/row)

sizebase=widget_base(row,/col)
l=widget_label(sizebase,value='Size')
scaledata={sizemin:0.1,sizemax:59.9,sizefmt:'(F4.1)',$
           thickmin:1,thickmax:10,thickfmt:'(I2)'}
wscalesizeslide=cw_fslider(sizebase,/vert,/drag,/supp,/edit,$
                           min=scaledata.sizemin,$
                           max=scaledata.sizemax,$
                           value=(*pstate).prefs.scalesize,$
                           uval='SCALESIZESLIDE')
wscalesizevalue=widget_text(sizebase,xsize=4,/edit,uval='SCALESIZEVALUE',$
                            value=string((*pstate).prefs.scalesize,$
                                         f=scaledata.sizefmt))


thickbase=widget_base(row,/col)
l=widget_label(thickbase,value='Thick')
wscalethickslide=cw_fslider(thickbase,/vert,/drag,/supp,/edit,$
                            min=scaledata.thickmin,$
                            max=scaledata.thickmax,$
                            value=(*pstate).prefs.scalethick,$
                            uval='SCALETHICKSLIDE')
wscalethickvalue=widget_text(thickbase,xsize=2,/edit,uval='SCALETHICKVALUE',$
                           value=string((*pstate).prefs.scalethick,$
                                        f=scaledata.thickfmt))

r=widget_base(scalebase,/row)
units=['arcsec','arcmin','degree']
wscaleunit=widget_combobox(r,value=units,xsize=70,uval='SCALEUNIT')
widget_control,wscaleunit,set_combobox_select=$
               (where(units eq (*pstate).prefs.scaleunit))(0)



wigalfit=widget_base(wtab,title='iGalFit',/col)
top=widget_base(wigalfit,/row)


lhs=widget_base(top,/column)
misc=widget_base(lhs,/col,frame=1)
l=widget_label(misc,value='Misc. Settings')

r=widget_base(misc,/row)
(*pstate).oView->GetProperty,color=back


l=widget_label(r,value='Background')

wcol=lonarr(ncol)

g=(where(rgb.rgb(0) eq back(0) and $
         rgb.rgb(1) eq back(1) and $
         rgb.rgb(2) eq back(2)))(0) 

wbackcol=widget_button(r,/bitmap,value=mkcolorbutton(rgb(g).rgb),/menu,$
                       tooltip=rgb(g).name)
for i=0,ncol-1 do wcol(i)=widget_button(wbackcol,/bitmap,uval='BACKCOL',$
                                        value=mkcolorbutton(rgb(i).rgb))
r=widget_base(misc,/row)
l=widget_label(r,value='Temp dir.')
wtemp=widget_text(r,/edit,xsize=6,uval='TEMPDIR')


wdoub=widget_base(lhs,/col,/frame,/align_center)
l=widget_label(wdoub,value='Double Click')
r=widget_base(wdoub,/row,/align_center)
w=widget_button(r,value=(*pstate).bitmapdir+'hourglass.bmp',/bitmap,$
                uval='DOUBLECLICK',xsize=28,tool='Double Click')
r=widget_base(wdoub,/row)
l=widget_label(r,value='Time =')
wtime=widget_label(r,xsize=30)
l=widget_label(r,value='s')

rhs=widget_base(top,/col)

auto=widget_base(rhs,/col,/frame)
l=widget_label(auto,value='Auto-scale')

r=widget_base(auto,/row)
l=widget_label(r,value='Lo Sig')
wlosig=widget_text(r,/edit,xsize=6,uval='AUTO')
r=widget_base(auto,/row)
l=widget_label(r,value='Hi Sig')
whisig=widget_text(r,/edit,xsize=6,uval='AUTO')
r=widget_base(auto,/row)
l=widget_label(r,value=' Sigma')
wsigma=widget_text(r,/edit,xsize=6,uval='AUTO')






wsex=widget_base(wtab,title='SExtractor',/col)
top=widget_base(wsex,/row)
lhs=widget_base(top,/col)
r=widget_base(lhs,/row)
l=widget_label(r,value='Acrit')
wacrit=widget_text(r,value='25',/edit,uval='SETVAL',xsize=4,uname='acrit')
r=widget_base(lhs,/row)
l=widget_label(r,value='Rcrit')
wrcrit=widget_text(r,value='1.5',/edit,uval='SETVAL',xsize=4,uname='rcrit')

rhs=widget_base(top,/col)
r=widget_base(rhs,/row)
l=widget_label(r,value='Def. Morph')
wdefmorph=morph_pdmenu(r,morphinfo,morphstate,uval='DEFMORPH')


;default morphology values
wmorph=widget_base(wtab,title='Morphology',/col)
top=widget_base(wmorph,/row)
col1=widget_base(top,/col)


;Moffat Function
wmoffat=widget_base(col1,/col,frame=1)
l=widget_label(wmoffat,value='Moffat')

r=widget_base(wmoffat,/row)
l=widget_label(r,value='FWHM (4)')
wfwhm=widget_text(r,/edit,xsize=4,uval='FWHM',$
                     value=string((*pstate).prefs.moffat.fwhm,f='(F4.1)'))
                     
r=widget_base(wmoffat,/row)
l=widget_label(r,value='Slope (5)')
walpha=widget_text(r,/edit,xsize=4,uval='SLOPE',$
                   value=string((*pstate).prefs.moffat.alpha,f='(F4.1)'))
moffat={wfwhm:wfwhm,walpha:walpha}


;Gaussian Function
wgauss=widget_base(col1,/col,frame=1)
l=widget_label(wgauss,value='Gaussian')

r=widget_base(wgauss,/row)
l=widget_label(r,value='FWHM (4)')
wfwhm=widget_text(r,/edit,xsize=4,uval='FWHM',$
                  value=string((*pstate).prefs.gaussian.fwhm,f='(F4.1)'))
gaussian={wfwhm:wfwhm}


;Nuker Function
nuker=widget_base(col1,/col,frame=1)
l=widget_label(nuker,value='Nuker')

r=widget_base(nuker,/row)
l=widget_label(r,value='alpha (5)')
walpha=widget_text(r,value=string((*pstate).prefs.nuker.alpha,f='(F4.1)'),$
                   xsize=4)
r=widget_base(nuker,/row)
l=widget_label(r,value='beta (6)')
wbeta=widget_text(r,value=string((*pstate).prefs.nuker.beta,f='(F4.1)'),$
                  xsize=4)
r=widget_base(nuker,/row)
l=widget_label(r,value='gamma (7)')
wgamma=widget_text(r,value=string((*pstate).prefs.nuker.gamma,f='(F4.1)'),$
                   xsize=4)
nuker={walpha:walpha,wbeta:wbeta,wgamma:wgamma}





col2=widget_base(top,/col)
;Ferrer Function
wferrer=widget_base(col2,/col,frame=1)
l=widget_label(wferrer,value='Ferrer')

r=widget_base(wferrer,/row)
l=widget_label(r,value='alpha (5)')
walpha=widget_text(r,value=string((*pstate).prefs.ferrer.alpha,f='(F4.1)'),$
                   xsize=4,uval='ALPHA')
r=widget_base(wferrer,/row)
l=widget_label(r,value='beta (6)')
wbeta=widget_text(r,value=string((*pstate).prefs.ferrer.beta,f='(F4.1)'),$
                   xsize=4,uval='BETA')
ferrer={walpha:walpha,wbeta:wbeta}

;King Function
wking=widget_base(col2,/col,frame=1)
l=widget_label(wking,value='King')

r=widget_base(wking,/row)
l=widget_label(r,value='Rt (5)')
wrt=widget_text(r,value=string((*pstate).prefs.king.rt,f='(F4.1)'),$
                xsize=4)
l=widget_label(r,value=string(215b)+' Rc (4)')

r=widget_base(wking,/row)
l=widget_label(r,value='alpha (6)')
walpha=widget_text(r,value=string((*pstate).prefs.king.alpha,f='(F4.1)'),$
                   xsize=4)
king={wrt:wrt,walpha:walpha}


;Sersic Function
wsersic=widget_base(col2,/col,frame=1)
l=widget_label(wsersic,value='Sersic')

r=widget_base(wsersic,/row)
l=widget_label(r,value='n (5)')
wn=widget_text(r,/edit,xsize=4,uval='SERSICN',$
               value=string((*pstate).prefs.sersic.n,f='(F4.1)'))
sersic={wn:wn}


;stuff for GalFit
wgalfit=widget_base(wtab,title='GalFit',/col)
top=widget_base(wgalfit,/row)
c1=widget_base(top,/col)
r=widget_base(c1,/col,/frame)
l=widget_label(r,value='exec.')
wgfexec=widget_text(r,xsize=14,/editable,value=(*pstate).prefs.exec)
r=widget_base(c1,/col,/frame)
l=widget_label(r,value='File')
wfeedme=widget_text(r,xsize=14,/editable,value=(*pstate).prefs.feedme)


;stuff for IRAF-like stuff:
wiraf=widget_base(wtab,title='IRAF',/col)
top=widget_base(wiraf,/row)
lhs=widget_base(top,/col)

wradprof=widget_base(lhs,/col,frame=1)
l=widget_label(wradprof,value='Radial Profile (r)')

r=widget_base(wradprof,/row)
l=widget_label(r,value='Max Radius')
wmaxrad=widget_text(r,/edit,uval='MAXRAD',xsize=4,$
                    value=string((*pstate).prefs.iraf.maxrad,f='(F4.1)'))

r=widget_base(wradprof,/row)
l=widget_label(r,value='FWHM')
wfwhm=widget_text(r,/edit,uval='FWHM',xsize=4,$
                  value=string((*pstate).prefs.iraf.fwhm,f='(F3.1)'))


wlineplot=widget_base(lhs,/col,frame=1)
l=widget_label(wlineplot,value='Line Plot (l or c)')

r=widget_base(wlineplot,/row)
l=widget_label(r,value='Width')
widths=['1','3','5','7','9','11']
wwidth=widget_combobox(r,value=widths,uval='WIDTH',xsize=50)
widget_control,wwidth,set_combobox_select=(where(widths eq $
                                                 (*pstate).prefs.iraf.width))(0)
              

r=widget_base(wlineplot,/row)
l=widget_label(r,value='Combine')
combinetypes=['none','total','median','average','sigclip','stddev','stddevclip']
wcombine=widget_combobox(r,value=combinetypes,uval='COMBINE',xsize=100)
widget_control,wcombine,$
               set_combobox_select=(where(combinetypes eq $
                                          (*pstate).prefs.iraf.combine))(0)

r=widget_base(wlineplot,/row)
l=widget_label(r,value='Range')
rangetypes=['full','viewable']
wrange=widget_combobox(r,value=rangetypes,uval='RANGE',xsize=90)
widget_control,wrange,set_combobox_select=(where(rangetypes eq $
                                                 (*pstate).prefs.iraf.range))(0)



wimstat=widget_base(lhs,/col,frame=1)
l=widget_label(wimstat,value='Image Stats (m)')

r=widget_base(wimstat,/row)
l=widget_label(r,value='Box Size')
wboxsize=widget_text(r,/edit,xsize=4,uval='BOXSIZE',$
                     value=string((*pstate).prefs.iraf.boxsize,f='(I4)'))


rhs=widget_base(top,/col)
wcontplot=widget_base(rhs,/col,frame=1)
l=widget_label(wcontplot,value='Contour Plot (e)')

r=widget_base(wcontplot,/row)
l=widget_label(r,value='Num. Levels')
nlevel=['3','4','5','6','7','8','9','10']
wnum=widget_combobox(r,value=nlevel,uval='NLEVEL',xsize=50)
widget_control,wnum,set_combobox_select=(where(nlevel eq $
                                               (*pstate).prefs.iraf.nlevels))(0)

r=widget_base(wcontplot,/row)
l=widget_label(r,value='Num. Ticks')
ntick=['0','1','2','3','4','5','6','7','8','9','10']
wtick=widget_combobox(r,value=ntick,uval='NTICK',xsize=50)
widget_control,wtick,set_combobox_select=(where(ntick eq $
                                                (*pstate).prefs.iraf.nticks))(0)

r=widget_base(wcontplot,/row)
l=widget_label(r,value='Box Size')
wconsize=widget_text(r,/edit,xsize=4,uval='CONSIZE',$
                     value=string((*pstate).prefs.iraf.consize,f='(I4)'))



whistplot=widget_base(rhs,/col,frame=1)
l=widget_label(whistplot,value='Histo Plot (h)')

r=widget_base(whistplot,/row)
l=widget_label(r,value='Box Size')
whissize=widget_text(r,/edit,xsize=4,uval='HISSIZE',$
                     value=string((*pstate).prefs.iraf.hissize,f='(I4)'))

r=widget_base(whistplot,/row)
l=widget_label(r,value='Num. of Bins')
wnbins=widget_text(r,/edit,xsize=4,uval='NBINS',$
                     value=string((*pstate).prefs.iraf.nbins,f='(I4)'))





state={pstate:pstate,$
       rgb:rgb,$

       wvanecolor:wvanecolor,$           ;weather vane selected color
       wvanecolors:wvanecolors,$         ;pulldown list of colors
       wvanesizeslide:wvanesizeslide,$   ;slider for vane size
       wvanesizevalue:wvanesizevalue,$   ;value for vane label
       wvanethickslide:wvanethickslide,$ ;slider for vane size
       wvanethickvalue:wvanethickvalue,$ ;value for vane label
       vanedata:vanedata,$               ;data structure for vane

       wscalecolor:wscalecolor,$           ;scalebar selected color
       wscalecolors:wscalecolors,$         ;pulldown list of colors
       wscalesizeslide:wscalesizeslide,$   ;slider for scale size
       wscalesizevalue:wscalesizevalue,$   ;value for scale label
       wscalethickslide:wscalethickslide,$ ;slider for scale size
       wscalethickvalue:wscalethickvalue,$ ;value for scale label
       wscaleunit:wscaleunit,$             ;unit for scale
       scaledata:scaledata,$               ;data structur for scalebar

       wbackcol:wbackcol,$
       wtemp:wtemp,$
       wcol:wcol,$
       wlosig:wlosig,$
       whisig:whisig,$
       wsigma:wsigma,$
       wacrit:wacrit,$
       wrcrit:wrcrit,$
       wdefmorph:wdefmorph,$
       morphinfo:morphinfo,$
       morphstate:morphstate,$
       wgfexec:wgfexec,$
       wfeedme:wfeedme,$
       wtime:wtime,$
       wmaxrad:wmaxrad,$
       wfwhm:wfwhm,$
       wboxsize:wboxsize,$
       wconsize:wconsize,$
       whissize:whissize,$
       wnbins:wnbins,$
       clicktime:systime(/seconds)}



state=ptr_new(state,/no_copy)
widget_control,base,set_uval=state

prefs_setvalues,state



widget_control,base,/realize
xmanager,'prefs',base,/no_block,cleanup='prefs_cleanup'


end
