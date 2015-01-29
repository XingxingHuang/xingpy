pro reshape,state,oROI

if obj_valid(oROI) eq 0 then begin
   if obj_valid((*state).oSelVisual) ne 0 then $
      (*state).oSelVisual->SetProperty,/hide
   return
endif


oROI->GetProperty,uvalue=prop
if (size(prop,/type) eq 8) then begin
   ;only process if the region has a structure for the uvalue

   ;center of the region
   cent=[prop.x,prop.y]


   ;get the Visual data
   (*state).oVisual->GetProperty,uval=sstate

   ;polygon data of little handles
   (*sstate).oScaleBox->GetProperty,data=handle

   ;changes to be like ds9.
   case prop.shape of
      'circle': begin
         
         r=prop.r
         xyur=[+r,+r]+cent
         xyul=[-r,+r]+cent
         xylr=[+r,-r]+cent
         xyll=[-r,-r]+cent
      end
      'ellipse': begin
         dx=prop.a
         dy=prop.b
         
         theta=prop.t*!PI/180.
         cc=cos(theta)
         ss=sin(theta)
         rot=[[cc,-ss],[ss,cc]]
         xyur=cent+reform(rot##[+dx,+dy])
         xylr=cent+reform(rot##[+dx,-dy])
         xyll=cent+reform(rot##[-dx,-dy])
         xyul=cent+reform(rot##[-dx,+dy])
         
         ;new handles
         x2=+cc*handle(0,*)+ss*handle(1,*)
         y2=-ss*handle(0,*)+cc*handle(1,*)
         newhandle=[x2,y2]*(*state).zoomstate
         
      end
      'box': begin
         
         dx=prop.dx/2.
         dy=prop.dy/2.
         
         theta=prop.t*!PI/180.
         cc=cos(theta)
         ss=sin(theta)
         rot=[[cc,-ss],[ss,cc]]
         xyur=cent+(rot##[+dx,+dy])
         xylr=cent+(rot##[+dx,-dy])
         xyll=cent+(rot##[-dx,-dy])
         xyul=cent+(rot##[-dx,+dy])
         
         ;new handles
         x2=+cc*handle(0,*)+ss*handle(1,*)
         y2=-ss*handle(0,*)+cc*handle(1,*)
         newhandle=[x2,y2]*(*state).zoomstate
      end
      else: begin
         t=dialog_message($
           'An unknown shape was encountered in RESHAPE.PRO.',/center,/error)
         return
      end
   endcase
   
   ;newhandle=handle

   ;set the Visual to the old color
   oROI->GetProperty,color=thiscolor
   (*sstate).oTransBoxOutline->SetProperty,color=thiscolor 
   ;(*sstate).oScaleBoxOutline->SetProperty,color=thiscolor
   (*sstate).oScaleBox->SetProperty,color=thiscolor

   ;change the size and rotation of the visual handles
   (*sstate).oScaleBox->SetProperty,data=handle*(*state).zoomstate

   ;set the corner info:
   (*sstate).oTransModel->Reset
   (*sstate).oTransBoxOutline->SetProperty,data=[[xyll,0],[xylr,0],$
                                                 [xyur,0],[xyul,0]]
   (*sstate).oScaleLL->Reset
   (*sstate).oScaleLL->Translate,xyll(0),xyll(1),0
   (*sstate).oScaleLR->Reset
   (*sstate).oScaleLR->Translate,xylr(0),xylr(1),0
   (*sstate).oScaleUL->Reset
   (*sstate).oScaleUL->Translate,xyul(0),xyul(1),0
   (*sstate).oScaleUR->Reset
   (*sstate).oScaleUR->Translate,xyur(0),xyur(1),0
   (*sstate).oScaleLL->SetProperty,uvalue=xyll
   (*sstate).oScaleLR->SetProperty,uvalue=xylr
   (*sstate).oScaleUR->SetProperty,uvalue=xyur
   (*sstate).oScaleUL->SetProperty,uvalue=xyul
   (*state).oVisual->SetProperty,hide=0
   
   
   ;reset to default
   (*sstate).oScaleBox->SetProperty,data=handle

endif

end
