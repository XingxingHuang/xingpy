pro rotate_roi,state,oroi,xx,yy

if obj_valid(oROI) eq 0 then return

;reject if a circle:
oROI->GetProperty,uvalue=prop
if not prop.canrotate then return

pa=prop.t                       ;PA of region


;Use Law of Cosines to find the angle through which we have just rotated

;the indices of the triangle
xy1=convertxy({x:xx,y:yy},state)
xy0=convertxy({x:(*state).xy(0),y:(*state).xy(1)},state)
xyc=[prop.x,prop.y]

;compute vector differences
dxy1=xy1-xyc
dxy0=xy0-xyc
dxyp=xy1-xy0

;three lengths in LoCs
a2=total(dxy1^2)
b2=total(dxy0^2)
c2=total(dxyp^2)

cost=(c2-a2-b2)/(2*sqrt(a2*b2)) ;Law of Cosines
dang=acos(cost)*180./!PI        ;angle in degrees

;now test if CCW vs. CW by going to Polar Coordinates
theta1=atan(dxy1(1),dxy1(0))
theta0=atan(dxy0(1),dxy0(0))
if theta1 gt theta0 then dang=180.-dang

;update the object data
prop.t=(prop.t+dang) mod 360.
oROI->SetProperty,uvalue=prop

;get the Visual Data:
(*state).oVisual->GetProperty,uvalue=sstate

;rotate the ROI
axis=[0,0,1]                    ;about the z-axis!
oROI->Rotate,axis,dang

;rotate the box
(*sstate).oTransModel->Rotate,axis,dang
(*sstate).oScaleLL->Rotate,axis,dang
(*sstate).oScaleLR->Rotate,axis,dang
(*sstate).oScaleUL->Rotate,axis,dang
(*sstate).oScaleUR->Rotate,axis,dang

;set up translation vector
r=oROI->ComputeGeometry(cent=xyc2)
dxy=xyc-xyc2(0:1)


;translate, since rotations are about (0,0)
oROI->Translate,dxy(0),dxy(1),0
(*sstate).oTransModel->Translate,dxy(0),dxy(1),0
(*sstate).oScaleLL->Translate,dxy(0),dxy(1),0
(*sstate).oScaleLR->Translate,dxy(0),dxy(1),0
(*sstate).oScaleUL->Translate,dxy(0),dxy(1),0
(*sstate).oScaleUR->Translate,dxy(0),dxy(1),0

;set up rotation matrix
cc=cos(dang*!PI/180.)
ss=sin(dang*!PI/180.)
rot=[[cc,ss],[-ss,cc]]

;update the positions of the corners
(*sstate).oScaleLL->GetProperty,uval=xyll
(*sstate).oScaleLR->GetProperty,uval=xylr
(*sstate).oScaleUL->GetProperty,uval=xyul
(*sstate).oScaleUR->GetProperty,uval=xyur
(*sstate).oScaleLL->SetProperty,uvalue=xyc+rot##(xyll-xyc)+dxy
(*sstate).oScaleLR->SetProperty,uvalue=xyc+rot##(xylr-xyc)+dxy
(*sstate).oScaleUL->SetProperty,uvalue=xyc+rot##(xyul-xyc)+dxy
(*sstate).oScaleUR->SetProperty,uvalue=xyc+rot##(xyur-xyc)+dxy




end

