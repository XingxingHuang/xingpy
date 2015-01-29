function modify_roi,state

;get the parent state
pstate=(*state).pstate

;get the currently selected region
pos=widget_info((*state).wlist,/list_select)

;get the ROI
if pos ge 0 then begin
oROI=(*pstate).oROIModel->Get(pos=pos)
if obj_valid(oROI) then begin
   
   ;get the current values
   oROI->GetProperty,uval=oldprop,color=oldcolor

   ;get the new positions
   widget_control,(*state).wx,get_value=xx & xx=xx(0)
   if isnumber(xx) eq 0 then return,type_error('x')
   widget_control,(*state).wy,get_value=yy & yy=yy(0)
   if isnumber(yy) eq 0 then return,type_error('y')

   ;get the new sizes
   widget_control,(*state).wa,get_value=aa & aa=aa(0)
   if isnumber(aa) eq 0 then return,type_error('a')
   widget_control,(*state).wb,get_value=bb & bb=bb(0)
   if isnumber(bb) eq 0 then begin
      if bb eq 'N/A' then bb=aa else return,type_error('b')
   endif

   ;get the new PA
   widget_control,(*state).wt,get_value=tt & tt=tt(0)
   if isnumber(tt) eq 0 then begin
      if tt eq 'N/A' then tt='0.0' else return,type_error('t')
   endif

   ;get the new morphology
   morph=(*state).morphstate
;   morph=widget_info((*state).wmorph,/combobox_gettext)
   prop=define_region(morph,color)

   ;update the fitsection key
   if oldprop.type eq 'Fit Section' and prop.type ne 'Fit Section' then $
         (*pstate).fitsect=0b
   if prop.type eq 'Fit Section' then (*pstate).fitsect=1b

   ;do something for each shape
   case prop.shape of
      'ellipse': begin
         prop.x=xx
         prop.y=yy
         prop.a=aa
         prop.b=bb
         prop.t=tt
      end
      'circle': begin
         prop.x=xx
         prop.y=yy
         prop.r=aa
      end
      'box': begin
         prop.x=xx
         prop.y=yy
         prop.dx=aa
         prop.dy=bb
         prop.t=tt
      end
      else: stop
   endcase
   
   ;remove the old ROI
   (*pstate).oROIModel->Remove,oROI
   (*pstate).oROIGroup->Remove,oROI
   obj_destroy,oROI
   
   ;make the new ROI
   make_roi,prop,xx,yy,zz
   oROI=obj_new('IDLgrROI',color=color,style=2,$
                name=nameregion(*pstate),uval=prop,$
                line=prop.linestyle,thick=prop.thick)
   oROI->AppendData,xx,yy,zz
   (*pstate).oROIModel->Add,oROI
   (*pstate).oROIGroup->Add,oROI
   setroi,pstate,oROI,/update,/setlist,/reset
   
   ;redraw
   (*pstate).oWindow->Draw,(*pstate).oView
endif
endif


end
