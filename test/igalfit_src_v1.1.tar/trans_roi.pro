pro trans_roi,state,oROI,xx,yy,DELTAS=deltas


if not obj_valid(oROI) then return

;deltas
if keyword_set(DELTAS) then begin   
   dx=xx
   dy=yy
endif else begin
   xy0=convertxy({x:xx,y:yy},state)
   xy1=convertxy({x:(*state).xy(0),y:(*state).xy(1)},state)
   dx=xy0(0)-xy1(0)
   dy=xy0(1)-xy1(1)
endelse

;translate
oROI->Translate,dx,dy

;get the data for the visual
(*state).oVisual->GetProperty,uval=sstate

;update the box
(*sstate).oTransModel->Translate,dx,dy,0
(*sstate).oScaleLL->Translate,dx,dy,0
(*sstate).oScaleLR->Translate,dx,dy,0
(*sstate).oScaleUL->Translate,dx,dy,0
(*sstate).oScaleUR->Translate,dx,dy,0

;corners
(*sstate).oScaleLL->GetProperty,uvalue=xy
(*sstate).oScaleLL->SetProperty,uvalue=xy+[dx,dy]
(*sstate).oScaleUR->GetProperty,uvalue=xy
(*sstate).oScaleUR->SetProperty,uvalue=xy+[dx,dy]
(*sstate).oScaleLR->GetProperty,uvalue=xy
(*sstate).oScaleLR->SetProperty,uvalue=xy+[dx,dy]
(*sstate).oScaleUL->GetProperty,uvalue=xy
(*sstate).oScaleUL->SetProperty,uvalue=xy+[dx,dy]

;update the object
oROI->GetProperty,uvalue=prop
prop.x=prop.x+dx
prop.y=prop.y+dy
oROI->SetProperty,uvalue=prop

;update the fit sections
update_fitsect,state,prop

end
