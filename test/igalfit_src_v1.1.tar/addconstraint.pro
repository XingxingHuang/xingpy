pro make_constraint,pstate,cons,name
  
 
  delim=' '                     ;delimiter

  ;ranges
  lo=strcompress(string(cons.lo,f='(F8.3)'),/rem)
  hi=strcompress(string(cons.hi,f='(F8.3)'),/rem)  

  ;sort out if it's a relative or absolute constraint
  parshort=name+delim+cons.param
  sep=(cons.type eq 'relative')?' ':' to '
  newcon=parshort+delim+lo+sep+hi

  ;add it to the list
  widget_control,(*pstate).wcontable,get_value=constraints
  constraints=reform(constraints)
  ncon=n_elements(constraints)
  
  ;test if the constraint already exists
  testcons=strarr(ncon)
  for i=0,ncon-1 do begin
     c=strsplit(constraints(i),delim,/ext,count=n)
     if n gt 1 then testcons(i)=strjoin(c(0:2),delim)
  endfor

  ;test if it exists
  gg=(where(testcons eq parshort,nn))(0)
  if nn eq 1 and 1b-cons.set then constraints(gg)=''            ;remove it
  if nn eq 1 and cons.set then constraints(gg)=newcon           ;replace it
  if nn eq 0 and cons.set then constraints=[constraints,newcon] ;add it

  ;update the widget as necessary
  gg=where(constraints ne '',nn)
  widget_control,(*pstate).wcontable,$
                 set_val=((nn eq 0)?['']:reform(constraints(gg),1,nn)),$
                 ysize=(nn>(*pstate).nrow)  
end

pro constrain_roi_event,event

widget_control,event.id,get_uval=uval
case uval of
   'SET': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      names=getregnames(pstate)
      pos=(where((*state).regname eq names))(0)

      oROI=(*pstate).oROIModel->Get(pos=pos)

      oROI->GetProperty,uvalue=prop
      g=(where(prop.cons.wid eq event.id))(0)
      prop.cons(g).set=1b-prop.cons(g).set
      oROI->SetProperty,uvalue=prop

      make_constraint,pstate,prop.cons(g),(*state).regname

   end
   'TYPE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      names=getregnames(pstate)
      pos=(where((*state).regname eq names))(0)
      oROI=(*pstate).oROIModel->Get(pos=pos)
      oROI->GetProperty,uvalue=prop
      g=(where((*state).wtype eq event.id))(0)
      
      prop.cons(g).type=widget_info(event.id,/combobox_gettext)
      oROI->SetProperty,uvalue=prop
      
      if prop.cons(g).set then $
         make_constraint,pstate,prop.cons(g),(*state).regname
   end
   'LOLIMIT': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate      
      names=getregnames(pstate)
      pos=(where((*state).regname eq names))(0)
      oROI=(*pstate).oROIModel->Get(pos=pos)
      oROI->GetProperty,uvalue=prop
      g=(where((*state).wlo eq event.id))(0)
      
      widget_control,event.id,get_value=val & val=val(0)
      if isnumber(val) eq 0 then $
         val=strcompress(string(prop.cons(g).lo,f='(F6.2)'),/rem)
      prop.cons(g).lo=float(val)

      widget_control,event.id,set_value=val
      oROI->SetProperty,uvalue=prop      

      if prop.cons(g).set then $
         make_constraint,pstate,prop.cons(g),(*state).regname
  end

   'HILIMIT': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      names=getregnames(pstate)
      pos=(where((*state).regname eq names))(0)
      oROI=(*pstate).oROIModel->Get(pos=pos)
      oROI->GetProperty,uvalue=prop
      g=(where((*state).whi eq event.id))(0)
      
      widget_control,event.id,get_value=val & val=val(0)
      if isnumber(val) eq 0 then $
         val=strcompress(string(prop.cons(g).hi,f='(F6.2)'),/rem)
      prop.cons(g).hi=float(val)

      widget_control,event.id,set_value=val
      oROI->SetProperty,uvalue=prop      

      if prop.cons(g).set then $
         make_constraint,pstate,prop.cons(g),(*state).regname
   end
   else:
endcase
  
end
pro constrain_roi_clean,wid
widget_control,wid,get_uval=state
ptr_free,state
end


pro constrain_roi,pstate,regname,GROUP=group

base=widget_base(title='Constrain '+regname,group=group,/col)
names=getregnames(pstate)
pos=(where(names eq regname))(0)

oROI=(*pstate).oROIModel->Get(pos=pos)
oROI->GetProperty,uvalue=prop

types=['relative','absolute']

n=n_elements(prop.cons)
wtype=lonarr(n)
wlo=lonarr(n)
whi=lonarr(n)

fmt='(A-'+strcompress(string(max(strlen(prop.cons.param)),f='(I6)'),/rem)+')'



top=widget_base(base,/col,/frame)
l=widget_label(top,value='Region')







bot=widget_base(base,/col,/frame)
for i=0,n-1 do begin
   r=widget_base(bot,/row)
   ex=widget_base(r,/row,/non)

   name=string(prop.cons(i).param,f=fmt)
   prop.cons(i).wid=widget_button(ex,value=name,uvalue='SET')
   widget_control,prop.cons(i).wid,set_button=prop.cons(i).set
   wtype(i)=widget_combobox(r,value=types,$
                            uvalue='TYPE',xsize=85)
   widget_control,wtype(i),set_combobox_select=$
                  (where(prop.cons(i).type eq types))(0)
   f='(F6.2)'
   wlo(i)=widget_text(r,/edit,xsize=6,uval='LOLIMIT',$
                      value=strcompress(string(prop.cons(i).lo,f=f),/rem))
   whi(i)=widget_text(r,/edit,xsize=6,uval='HILIMIT',$
                      value=strcompress(string(prop.cons(i).hi,f=f),/rem))
endfor
oROI->SetProperty,uvalue=prop

state={pstate:pstate,$
       regname:regname,$
       name:name,$
       wtype:wtype,$
       wlo:wlo,$
       whi:whi}
state=ptr_new(state,/no_copy)
widget_control,base,set_uval=state


widget_control,base,/realize
xmanager,'constrain_roi',base,clean='constrain_roi_clean'

end

pro addconstraint_event,event
widget_control,event.id,get_uval=uval
case uval of
   'CLOSE': widget_control,event.top,/destroy
   'HELP': 
   'TAB':
   'CONSTRAIN': begin
      widget_control,event.top,get_uval=pstate      
      thisname=widget_info(event.id,/uname)
      constrain_roi,pstate,thisname,GROUP=event.top
   end
   else:
endcase

end


pro addconstraint,pstate,GROUP=group,BASE=base,BUTTON=button

xsize=350 & ysize=400
fmt={name:'(A-12)',type:'(A-12)',delim:' '}


base=widget_base(title='Constraint Editor',group=group,$
                 scr_xsize=xsize+10,scr_ysize=ysize+25,$
                 /col,mbar=mbar)
filemenu=widget_button(mbar,value='File',/menu)
close=widget_button(filemenu,value='Close',uvalue='CLOSE')
helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uval='HELP')

names=getregnames(pstate,nreg=nreg)
if nreg eq 0 then begin
   base=-1L
   t=dialog_message(['There are no Regions set.',$
                     'You need to draw regions before ',$
                     'you can constrain them.'],$
                     /center,/error,title='No Regions')
   return
endif

oROIs=(*pstate).oROIModel->Get(/all)

;tab=widget_tab(base,uval='TAB')


;wsingle=widget_base(tab,title='Single',/row,/scroll,$
;                    scr_xsize=xsize,scr_ysize=ysize)
wsingle=widget_base(base,/row,/scroll,$
                    scr_xsize=xsize,scr_ysize=ysize)

ncol=4
unames=strarr(nreg)
sing=widget_base(base,/col)
for i=0,nreg-1 do begin
   oROIs(i)->GetProperty,uval=props
   if tag_exist(props,'cons') then unames(i)=names(i)
endfor


unames=unames(where(unames ne '',nreg))
wbuttons=lonarr(nreg)
nrow=ceil(float(nreg)/ncol)
for i=0,nreg-1 do begin
   if i mod nrow eq 0 then r=widget_base(wsingle,/col)
   wbuttons(i)=widget_button(r,value=unames(i),uval='CONSTRAIN',uname=unames(i))
endfor

;wcombo=widget_base(tab,title='Combine',/row)




widget_control,base,set_uval=pstate
widget_control,base,/realize
xmanager,'addconstraint',base


end
