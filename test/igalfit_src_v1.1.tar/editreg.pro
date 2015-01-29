pro mkfittab,state



props=['flux','mag','SB','Npix']
npar=n_elements(props)

if widget_info((*state).fitbase,/valid_id) then $
   widget_control,(*state).fitbase,/destroy

(*state).fitbase=widget_base((*state).fitpar,/non,/col)
wfit=lonarr(npar)
for i=0,npar-1 do wfit(i)=widget_button((*state).fitbase,value=props(i))
(*state).wfit=ptr_new(wfit,/no_copy)


end


pro editreg_event,event





end

pro editreg,pstate,BUTTON=button,BASE=base,GROUP=group
if not keyword_set(BUTTON) then button=-1L


names=getregnames(pstate)       ;get names of ROIs
xsize=6                         ;size of text boxes

base=widget_base(title='Edit Regions',group=group,/col,mbar=mbar)

;menubar
filemenu=widget_button(mbar,value='File',/menu)
save=widget_button(filemenu,value='Save Regions',uval='SAVE')
close=widget_button(filemenu,value='Close',uval='CLOSE',/sep)
helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uvalu='HELP')


top=widget_base(base,/row)

col1=widget_base(top,/col)
listbase=widget_base(col1,/col,frame=1)
l=widget_label(listbase,value='Region'+string(10b)+'List',/align_left)
wlist=widget_list(listbase,xsize=10,ysize=12,value=names,uval='LIST')

butbase=widget_base(col1,/col,/align_center)
wdel=widget_button(butbase,value='Delete Region',uval='DELETE')
wmorph=morph_pdmenu(butbase,morphinfo,morphstate,uval='MORPH')


col2=widget_base(top,/col)

ell=widget_base(col2,/col,frame=1)
l=widget_label(ell,value='Ellipse'+string(10b)+'Parameters',/align_left)

r=widget_base(ell,/row)
l=widget_label(r,value='x')
wx=widget_text(r,/edit,xsize=xsize,uval='MODIFY')
r=widget_base(ell,/row)
l=widget_label(r,value='y')
wy=widget_text(r,/edit,xsize=xsize,uval='MODIFY')
r=widget_base(ell,/row)
l=widget_label(r,value='a')
wa=widget_text(r,/edit,xsize=xsize,uval='MODIFY')
r=widget_base(ell,/row)
l=widget_label(r,value='b')
wb=widget_text(r,/edit,xsize=xsize,uval='MODIFY')
r=widget_base(ell,/row)
l=widget_label(r,value='t')
wt=widget_text(r,/edit,xsize=xsize,uval='MODIFY')

data=widget_base(col2,/col,frame=1)
props=['flux','mag','SB','Npix']
wprop=lonarr(n_elements(props))
fmt='(A'+strcompress(string(max(strlen(props)),f='(I2)'),/rem)+')'
for i=0,n_elements(props)-1 do begin
   r=widget_base(data,/row)
   l=widget_label(r,value=string(props(i),f=fmt)+' =')
   wprop(i)=widget_label(r,value='',xsize=80,ysize=12,/align_left)
endfor





col3=widget_base(top,/col)
fitpar=widget_base(col3,/col,/frame)
l=widget_label(fitpar,value='Fit'+string(10b)+'Parameters',/align_left)


;set the data to pass
state={pstate:pstate,$
       wlist:wlist,$
       wx:wx,$
       wy:wy,$
       wa:wa,$
       wb:wb,$
       wt:wt,$
       wmorph:wmorph,$
       morphinfo:morphinfo,$
       morphstate:morphstate,$
       wdel:wdel,$
       wprop:wprop,$
       props:props,$
       fitpar:fitpar,$
       fitbase:-1L,$
       wfit:ptr_new(),$
       button:button} 
state=ptr_new(state,/no_copy)
mkfittab,state





widget_control,base,/realize


end

