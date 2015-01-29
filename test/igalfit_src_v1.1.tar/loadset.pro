pro loadset,file,state,top

;test file type
if not h5f_is_hdf5(file) then begin
   t=dialog_message('The file is not in the HDF format!',$
                    /err,/cen,title='Unable to Load')
   return
endif

;read the data
data=h5_parse(file,/read)
if not tag_exist(data,'igalfit') then begin
   t=dialog_message(['The File is not a valid iGalFit save file',$
                     'in the H5 format.'],/err,/cent,title='Unable to Load')
   return
endif
data=data.igalfit._data


if tag_exist(data,'files') then begin
   f=data.files
   if tag_exist(f,'sci') then begin
      (*state).setfile.sci=strtrim(f.sci)
      widget_control,(*state).wsci,set_value=(*state).setfile.sci
   endif
   if tag_exist(f,'unc') then begin
      (*state).setfile.unc=strtrim(f.unc)
      widget_control,(*state).wunc,set_value=(*state).setfile.unc
   endif
   if tag_exist(f,'psf') then begin
      (*state).setfile.psf=strtrim(f.psf)
      widget_control,(*state).wpsf,set_value=(*state).setfile.psf
   endif
   if tag_exist(f,'out') then widget_control,(*state).wout,set_va=strtrim(f.out)
   if tag_exist(f,'bpx') then widget_control,(*state).wbpx,set_va=strtrim(f.bpx)
   if tag_exist(f,'mkbpx') then widget_control,(*state).wmkbpx,set_but=f.mkbpx
   delvarx,f
endif

if tag_exist(data,'constraint') then begin
   c=data.constraint
   if tag_exist(c,'file') then widget_control,(*state).wconfile,$
      set_value=strtrim(c.file)
   if tag_exist(c,'sens') then begin
      widget_control,(*state).weditcons,sens=c.sens
      widget_control,(*state).wbasiccons,sens=c.sens
      widget_control,(*state).wlinkcons,sens=c.sens
      widget_control,(*state).wremcon,sens=c.sens
      widget_control,(*state).wremallcon,sens=c.sens
      widget_control,(*state).wconlist,sens=c.sens
      if tag_exist(c,'names') then begin
         if c.names(0) ne '' then begin
            (*state).consnames=ptr_new(c.names,/no_copy)
            widget_control,(*state).wconlist,set_val=c.names
         endif else (*state).consnames=ptr_new()
      endif
      
      delvarx,c
   endif
endif

if tag_exist(data,'ranges') then begin
   r=data.ranges
   if tag_exist(r,'x0') then widget_control,(*state).wx0,set_val=r.x0
   if tag_exist(r,'x1') then widget_control,(*state).wx1,set_val=r.x1
   if tag_exist(r,'y0') then widget_control,(*state).wy0,set_val=r.y0
   if tag_exist(r,'y1') then widget_control,(*state).wy1,set_val=r.y1
   if tag_exist(r,'dx') then widget_control,(*state).wdx,set_val=r.dx
   if tag_exist(r,'dy') then widget_control,(*state).wdy,set_val=r.dy
   delvarx,r
endif

if tag_exist(data,'props') then begin
   p=data.props
   if tag_exist(p,'zero') then begin
      widget_control,(*state).wzero,set_val=p.zero
      (*state).magzero=float(p.zero)
   endif
   if tag_exist(p,'pixx') then widget_control,(*state).wpixx,set_val=p.pixx
   if tag_exist(p,'pixy') then widget_control,(*state).wpixy,set_val=p.pixy
   if tag_exist(p,'expt') then widget_control,(*state).wexptime,set_val=p.expt
   if tag_exist(p,'units') then set_combobox,(*state).wunits,p.units
   if tag_exist(p,'shot') then widget_control,(*state).wshot,set_but=p.shot
   delvarx,p
endif

if tag_exist(data,'sky') then begin
   sky=data.sky
   if tag_exist(sky,'sky0') then begin
      s=sky.sky0
      if tag_exist(s,'fit') then widget_control,(*state).wfitsky0,set_but=s.fit
      if tag_exist(s,'val') then widget_control,(*state).wsky0,set_val=s.val
      if tag_exist(s,'sens') then widget_control,(*state).wsky0,sens=s.sens
      delvarx,s
   endif
   if tag_exist(sky,'dsdx') then begin
      s=sky.dsdx
      if tag_exist(s,'fit') then widget_control,(*state).wfitdsdx,set_but=s.fit
      if tag_exist(s,'val') then widget_control,(*state).wdsdx,set_val=s.val
      if tag_exist(s,'sens') then widget_control,(*state).wdsdx,sens=s.sens
      delvarx,s
   endif
   if tag_exist(sky,'dsdy') then begin
      s=sky.dsdy
      if tag_exist(s,'fit') then widget_control,(*state).wfitdsdy,set_but=s.fit
      if tag_exist(s,'val') then widget_control,(*state).wdsdy,set_val=s.val
      if tag_exist(s,'sens') then widget_control,(*state).wdsdy,sens=s.sens
      delvarx,s
   endif
   delvarx,sky
endif

if tag_exist(data,'add') then begin
   a=data.add
   if tag_exist(a,'disptype') then set_combobox,(*state).wdisptype,a.disptype
   if tag_exist(a,'gftype') then set_combobox,(*state).wgftype,a.gftype
   if tag_exist(a,'fine') then widget_control,(*state).wfine,set_val=a.fine
   if tag_exist(a,'erase') then widget_control,(*state).wclean,set_but=a.erase
   if tag_exist(a,'silent') then widget_control,(*state).wsilent,$
      set_but=a.silent
   if tag_exist(a,'display') then widget_control,(*state).wdisp,$
      set_but=a.display
   delvarx,a
endif


if tag_exist(data,'histo') then begin
   h=data.histo
   if tag_exist(h,'hist') then $
      (*state).hist=(size(h.hist,/type) ne 7)?ptr_new(h.hist):ptr_new()
   if tag_exist(h,'bins') then $
      (*state).bins=(size(h.bins,/type) ne 7)?ptr_new(h.bins):ptr_new()
   if tag_exist(h,'histmaxx') then (*state).histmaxx=h.histmaxx
   if tag_exist(h,'histminx') then (*state).histminx=h.histminx
   if tag_exist(h,'histbinx') then (*state).histbinx=h.histbinx
   delvarx,h
endif

if tag_exist(data,'display') then begin
   d=data.display
   if tag_exist(d,'lodisp') then (*state).lodisp=d.lodisp
   if tag_exist(d,'hidisp') then (*state).hidisp=d.hidisp
   if tag_exist(d,'bias') then (*state).bias=d.bias
   if tag_exist(d,'cont') then (*state).cont=d.cont
   if tag_exist(d,'fitsect') then (*state).fitsect=d.fitsect
   delvarx,d
endif

if tag_exist(data,'mouse') then begin
   m=data.mouse
   if tag_exist(m,'xy') then (*state).xy=m.xy
   if tag_exist(m,'zoomstate') then (*state).zoomstate=m.zoomstate
   if tag_exist(m,'button') then (*state).button=m.button
   delvarx,m
endif

if tag_exist(data,'prefs') then begin
   p=data.prefs
   newnames=tag_names(p)
   oldnames=tag_names((*state).prefs)
   for i=0,n_elements(oldnames)-1 do begin
      g=(where(oldnames(i) eq newnames))(0)
      if g ne -1 then (*state).prefs.(i)=p.(g)
   endfor
   delvarx,p,newnames,oldnames
endif

if tag_exist(data,'image') then begin
   i=data.image
   if tag_exist(i,'ast') then (*state).ast=ptr_new(i.ast,/no_copy)
   if tag_exist(i,'set') then displaymenu,{top:top,id:(*state).wimage(i.set)}
   if tag_exist(i,'zoom') then zoommenu,{top:top,id:(*state).wzoom(i.zoom)}
   if tag_exist(i,'img') then $
      if n_elements(i.img) gt 1 then (*state).img=ptr_new(i.img,/no_copy)
   if tag_exist(i,'view') then (*state).oView->SetProperty,view=i.view
   if tag_exist(i,'scale') then scalemenu,{top:top,id:(*state).wscale(i.scale)}
   delvarx,i
endif



if tag_exist(data,'nreg') then begin
   nreg=data.nreg
   define_rgb,colors
   for i=0,nreg-1 do begin
      ii=strcompress(string(i+1,f='(I6)'),/rem)
      r1=execute('props=data.reg'+ii)
      r2=execute('color=data.rgb'+ii)
      if r1 and r2 then begin
         make_roi,props,xx,yy,zz
         oROI=obj_new('IDLgrROI',color=color,style=2,$
                      name=nameregion(*state),uvalue=props,$
                      line=props.linestyle,thick=props.thick)
         oROI->AppendData,xx,yy,zz
         (*state).oROIModel->Add,oROI
         (*state).oROIGroup->Add,oROI
         setroi,state,oROI,/update,/setlist,/reset
      endif
   endfor
endif


;do SUBGUIs last!!!
if tag_exist(data,'subguis') then begin
   s=data.subguis
   for i=0,n_elements(s)-1 do begin
      case s.name of

         
         else:
      endcase
   endfor
   delvarx,s
endif
end



(*state).oWindow->Draw,(*state).oView

end
