pro scale_roi,state,oROI,xx,yy
if obj_valid(oROI) eq 0 then return

;convert coordinates
xy1=convertxy({x:xx,y:yy},state)
xy0=convertxy({x:(*state).xy(0),y:(*state).xy(1)},state)
dxy=xy1-xy0

;get properties of region
oROI->GetProperty,uvalue=prop
cent=[prop.x,prop.y]
oROI->RemoveData


;get corners in rotated frame:
case prop.shape of
   'circle': begin

      rad1=sqrt(total((cent-xy1)^2))
      rad0=sqrt(total((cent-xy0)^2))
      drad=rad1-rad0
      rad=prop.r+drad

      uvur=[+1,+1]*rad
      uvlr=[+1,-1]*rad
      uvll=[-1,-1]*rad
      uvul=[-1,+1]*rad
      duv=[1,1]*drad
   end
   'box': begin
      uvur=[+prop.dx,+prop.dy]/2.
      uvlr=[+prop.dx,-prop.dy]/2.
      uvll=[-prop.dx,-prop.dy]/2.
      uvul=[-prop.dx,+prop.dy]/2.

      pa=prop.t*!PI/180
      cc=cos(pa)
      ss=sin(pa)
      rot=[[cc,ss],[-ss,cc]]
      duv=rot##dxy
      
   end
   'ellipse': begin
      uvur=[+prop.a,+prop.b]
      uvlr=[+prop.a,-prop.b]
      uvll=[-prop.a,-prop.b]
      uvul=[-prop.a,+prop.b]
      pa=prop.t*!PI/180
      cc=cos(pa)
      ss=sin(pa)
      rot=[[cc,ss],[-ss,cc]]
      duv=rot##dxy
   end
   else: begin
      t=dialog_message('An unknown shape was encountered in SCALE_ROI.PRO',$
                       /center,/error,title='Shape Error')
      return
   end
endcase

;do something for each handle:
(*state).oSelHandle->GetProperty,name=hn
case hn of
   'LL': begin
      uvll=uvll+[+1,+1]*duv
      uvul=uvul+[+1,-1]*duv
      uvlr=uvlr+[-1,+1]*duv
      uvur=uvur+[-1,-1]*duv
   end
   'LR': begin
      uvlr=uvlr+[+1,+1]*duv
      uvur=uvur+[+1,-1]*duv
      uvll=uvll+[-1,+1]*duv
      uvul=uvul+[-1,-1]*duv
   end
   'UR': begin
      uvur=uvur+[+1,+1]*duv
      uvlr=uvlr+[+1,-1]*duv
      uvul=uvul+[-1,+1]*duv
      uvll=uvll+[-1,-1]*duv
   end
   'UL': begin
      uvul=uvul+[+1,+1]*duv
      uvll=uvll+[+1,-1]*duv
      uvur=uvur+[-1,+1]*duv
      uvlr=uvlr+[-1,-1]*duv
   end
   else: return
endcase

;remake the regions:
case prop.shape of
   'circle': begin
      ;new corners
      xyur=cent+uvur
      xyul=cent+uvul
      xylr=cent+uvlr
      xyll=cent+uvll

      ;update the data
      prop.r=rad
   end
   'ellipse': begin
      ;de-rotate: convert (u,v) coordinates of corners to (x,y)
      rot=[[cc,-ss],[ss,cc]]
      xyur=cent+rot##uvur
      xyul=cent+rot##uvul
      xylr=cent+rot##uvlr
      xyll=cent+rot##uvll

      ;update the ROI
      prop.a=abs(uvur(0)-uvul(0))/2.
      prop.b=abs(uvur(1)-uvlr(1))/2.
    end
   'box': begin
      ;de-rotate: convert (u,v) coordinates of corners to (x,y)
      rot=[[cc,-ss],[ss,cc]]
      xyur=cent+rot##uvur
      xyul=cent+rot##uvul
      xylr=cent+rot##uvlr
      xyll=cent+rot##uvll

      ;update the ROI
      prop.dx=abs(uvur(0)-uvul(0))
      prop.dy=abs(uvur(1)-uvlr(1))
   end
   else: begin
      t=dialog_message($
        'An unknown shape was encountered in SCALE_ROI.PRO',/center,/error)
      return
   end
endcase

;make the ROI
make_roi,prop,xx,yy,zz
oROI->SetProperty,data=transpose([[xx],[yy],[zz]])

;save the Data for the ROI
oROI->SetProperty,uvalue=prop

;update the fit section
update_fitsect,state,prop

;get the Visual data
(*state).oVisual->GetProperty,uvalue=sstate

;translate the visual handles
(*sstate).oScaleLL->Reset
(*sstate).oScaleLL->Translate, xyll(0),xyll(1),0
(*sstate).oScaleLR->Reset
(*sstate).oScaleLR->Translate, xylr(0),xylr(1),0
(*sstate).oScaleUL->Reset
(*sstate).oScaleUL->Translate, xyul(0),xyul(1),0
(*sstate).oScaleUR->Reset
(*sstate).oScaleUR->Translate, xyur(0),xyur(1),0

;update the corners
(*sstate).oScaleLL->SetProperty,uvalue=xyll
(*sstate).oScaleUR->SetProperty,uvalue=xyur
(*sstate).oScaleUL->SetProperty,uvalue=xyul
(*sstate).oScaleLR->SetProperty,uvalue=xylr

;Reset the translation box
(*sstate).oTransModel->Reset
(*sstate).oTransBoxOutline->SetProperty,data=[[xyll],[xylr],[xyur],[xyul]]


end
