pro reginfo_clean,wid
widget_control,wid,get_uval=state
if widget_info((*state).button,/valid_id) then $
   widget_control,(*state).button,set_button=0b
ptr_free,state
end

pro reginfo_event,event,GROUP=group
widget_control,event.id,get_uval=uval
case uval of
   'LIST': begin
      widget_control,event.top,get_uvalu=state
      pstate=(*state).pstate
      nreg=(*pstate).oROIModel->Count()
      if nreg eq 0 then begin
         setroi,pstate,obj_new()
         return
      endif
      oROI=(*pstate).oROIModel->Get(pos=event.index)
      setroi,pstate,oROI
      (*pstate).oWindow->Draw,(*pstate).oView
   end
   'MODIFY': begin
      widget_control,event.top,get_uval=state
      t=modify_roi(state)
   end
   'MORPH': begin
      widget_control,event.top,get_uval=state
      g=(where(event.id eq (*state).morphinfo.wid))(0)
      thismorph=(*state).morphinfo(g).type
      widget_control,(*state).wmorph,set_value=thismorph,$
                     tooltip=(*state).morphinfo(g).tip
      (*state).morphstate=thismorph     
      t=modify_roi(state)
   end
   'DELETE': begin
      widget_control,event.top,get_uval=state
      pstate=(*state).pstate
      nreg=(*pstate).oROIModel->Count()
      if nreg gt 0 then begin
         oROI=(*pstate).oSelROI
         if obj_valid(oROI) then begin
            res=(*pstate).oROIModel->IsContained(oROI,pos=pos)
            
            (*pstate).oROIModel->Remove,oROI
            (*pstate).oROIGroup->Remove,oROI
            obj_destroy,oROI
            
            if nreg eq 1 then begin
               setroi,pstate,obj_new(),/update
            endif else begin
               pos=(pos-1)>0
               widget_control,(*state).wlist,set_list_select=pos
               oROI=(*pstate).oROIModel->Get(pos=pos)
               setroi,pstate,oROI,/update,/setlist
            endelse
            (*pstate).oVisual->SetProperty,hide=1b
            (*pstate).oWindow->Draw,(*pstate).oView
         endif

      endif
   end
   'SAVE': begin
      widget_control,event.top,get_uval=state
      roi2reg,(*state).pstate
   end
   'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                    group=event.top,load='reginfo'
   'CLOSE': widget_control,event.top,/destroy
   else: t=dialog_message([current_routine(),$
                           uval+' is not functional.'],/error,/center)
endcase
end

pro reginfo,pstate,BUTTON=button,BASE=base,GROUP=group
if not keyword_set(BUTTON) then button=-1L

;the names of the ROIs
names=getregnames(pstate)


base=widget_base(title='Inspect Regions',group=group,/column,mbar=mbar)

filemenu=widget_button(mbar,value='File',/menu)
save=widget_button(filemenu,value='Save Regions',uval='SAVE')
close=widget_button(filemenu,value='Close',uval='CLOSE',/sep)
helpmenu=widget_button(mbar,value='Help',/menu,/help)
help=widget_button(helpmenu,value='Help',uvalu='HELP')

top=widget_base(base,/row)
lhs=widget_base(top,/column)
wlist=widget_list(lhs,xsize=10,ysize=15,value=names,uval='LIST')

mid=widget_base(top,/column)

xsize=6
row1=widget_base(mid,/row)
l=widget_label(row1,value='x')
wx=widget_text(row1,value='',/edit,xsize=xsize,uval='MODIFY')
l=widget_label(row1,value='y')
wy=widget_text(row1,value='',/edit,xsize=xsize,uval='MODIFY')

row2=widget_base(mid,/row)
l=widget_label(row2,value='a')
wa=widget_text(row2,value='',/edit,xsize=xsize,uval='MODIFY')
l=widget_label(row2,value='b')
wb=widget_text(row2,value='',/edit,xsize=xsize,uval='MODIFY')

row3=widget_base(mid,/row)
l=widget_label(row3,value='t')
wt=widget_text(row3,value='',/edit,xsize=xsize,uval='MODIFY')


;morphs=define_region(/morphs)
row4=widget_base(mid,/row)
l=widget_label(row4,value='Morph')
wmorph=morph_pdmenu(row4,morphinfo,morphstate,uval='MORPH')

data=widget_base(mid,/column,/frame)

props=['flux','mag','SB','Npix']
wprop=lonarr(n_elements(props))
fmt='(A'+strcompress(string(max(strlen(props)),f='(I2)'),/rem)+')'
for i=0,n_elements(props)-1 do begin
   r=widget_base(data,/row)
   l=widget_label(r,value=string(props(i),f=fmt)+' =')
   wprop(i)=widget_label(r,value='',xsize=80,ysize=12,/align_left)
endfor

bot=widget_base(base,/row)
wdelete=widget_button(bot,value='Delete Region',uvalue='DELETE')

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
       wdelete:wdelete,$
       wprop:wprop,$
       props:props,$
       group:group,$
       button:button}
state=ptr_new(state,/no_copy)
widget_control,base,set_uval=state

if keyword_set(GROUP) then place_widget,base,group
       
widget_control,base,/realize


;set the intial state:
oSelROI=(*pstate).oSelROI
if obj_valid(oSelROI) then begin
   res=(*pstate).oROIModel->IsContained(oSelROI,pos=pos)
   widget_control,wlist,set_list_select=pos
   setdata,state,oSelROI   
endif else begin
   nreg=(*pstate).oROIModel->Count()
   if nreg ge 1 then begin
      pos=0
      widget_control,wlist,set_list_select=pos
      setdata,state,(*pstate).oROIModel->Get(pos=pos)
   endif
endelse



xmanager,'reginfo',base,/no_block,cleanup='reginfo_clean'



end
