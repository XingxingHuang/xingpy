pro mouse_moved,event
;procedure to deal with the mouse moving within the draw window

;get the state
widget_control,event.top,get_uvalue=state

;convert from viewport coordinates to image coordinates
xy=convertxy(event,state)
x=xy(0) & y=xy(1)

;update the (x,y), (r,d), and p values:
update_display,state,x,y

case (*state).button of
   11b: begin
      ;A region was selected
      
      ;EXTRA?
;      oSelVisual=(*state).oSelVisual
;      if obj_valid(oSelVisual) then begin
;         oSelVisual->SetProperty,hide=1b
;         (*state).oSelVisual=obj_new()
;      endif
;      (*state).oSelVisual=(*state).oVisual
;      reshape,state,(*state).oSelROI


      oROI=(*state).oSelROI
      if xregistered('reginfo',/noshow) then begin
         widget_control,(*state).weditregbase,get_uvalue=sstate
         setdata,sstate,oROI
      endif
      ;did it occur on a region?
      oSelHandle=(*state).oSelHandle
      if obj_valid(oSelHandle) then begin
         oSelHandle->GetProperty,name=hn
         if hn eq 'TRANSLATE' then begin
            ;translate the regions
            trans_roi,state,oROI,event.x,event.y
         endif else begin
            if event.modifiers eq 1 then begin
               ;rotate the regions
               rotate_roi,state,oROI,event.x,event.y
            endif else begin
               ;rescale the regions
               scale_roi,state,oROI,event.x,event.y
            endelse
         endelse
      endif else begin
         ;translate the regions
         trans_roi,state,oROI,event.x,event.y
      endelse


      (*state).xy=[event.x,event.y]   
      ;redraw 
      (*state).oWindow->Draw,(*state).oView
   end
   12b: begin
      ;A region is being drawn

      ;EXTRA?
;      oSelVisual=(*state).oSelVisual
;      if obj_valid(oSelVisual) then begin
;         oSelVisual->SetProperty,/hide
;         (*state).oSelVisual=obj_new()
;      endif
      


      oROI=(*state).oCurrROI
      if obj_valid(oROI) eq 0 then return
      
      ;check morphology
      oROI->GetProperty,uvalue=prop
      case prop.shape of
         'box': begin
            x0=(*state).xy(0) & x1=x
            y0=(*state).xy(1) & y1=y
            

            ;sort out the shape
            if x0 eq x1 and y0 eq y1 then begin
               rect=[[x0,y0,0]]
               style=0
            endif
            if x0 eq x1 and y0 ne y1 then begin
               rect=[[x0,y0,0],[x0,y1,0]]
               style=1
            endif
            if x0 ne x1 and y0 eq y1 then begin
               rect=[[x0,y0,0],[x1,y0,0]]
               style=1
            endif         
            if x0 ne x1 and y0 ne y1 then begin
               rect=[[x0,y0,0],[x1,y0,0],[x1,y1,0],[x0,y1,0]]
               style=2
            endif
            
            ;update the ROI
            dx=abs(x1-x0) & dy=abs(y1-y0)
            prop.x=(x0+x1)/2. & prop.dx=dx
            prop.y=(y0+y1)/2. & prop.dy=dy

            prop.t=0.0
            oROI->SetProperty,uvalue=prop,style=style
            oROI->GetProperty,n_vert=nv
            oROI->ReplaceData,rect,start=0,finish=nv-1
            
            ;update the GalFit GUI
            update_fitsect,state,prop

         end
         'ellipse': begin
            x0=(*state).xy(0) & x1=x
            y0=(*state).xy(1) & y1=y
            
            pa=0.0              ;default PA
             if x0 eq x1 and y0 eq y1 then begin
               xx=[x0] & yy=[y0]           
               hh=0. & vv=0.0
               style=0
            endif
            if x0 eq x1 and y0 ne y1 then begin
               vv=abs(y1-y0)
               hh=0.
               xx=[x0,x0] & yy=[y0,y0]+vv*[-1,1]
               style=1
            endif
            if x0 ne x1 and y0 eq y1 then begin
               hh=abs(x1-x0)
               vv=0.0
               xx=[x0,x0]-hh*[-1,1] & yy=[y0,y0]
               style=1
            endif         
            if x0 ne x1 and y0 ne y1 then begin
               cc=cos(pa*!PI/180.)
               ss=sin(pa*!PI/180.)
               hh=abs(x1-x0)
               vv=abs(y1-y0)      
               npts=ceil(hh>vv)*4
               ang=findgen(npts)*2*!PI/(npts-1)            
               xx=x0+cc*hh*cos(ang)+ss*vv*sin(ang)
               yy=y0-ss*hh*cos(ang)+cc*vv*sin(ang)
               style=2
            endif
            zz=fltarr(size(xx,/dim))
            
            ;update the ROI
            prop.x=x0 & prop.a=hh
            prop.y=y0 & prop.b=vv
            prop.t=0.0
            oROI->SetProperty,uvalue=prop,style=style
            oROI->GetProperty,n_vert=nv
            oROI->ReplaceData,xx,yy,zz,start=0,finish=nv-1
         end
         'circle': begin
            x0=(*state).xy(0) & x1=x
            y0=(*state).xy(1) & y1=y
            rad=sqrt((x1-x0)^2+(y1-y0)^2)

            if x0 eq x1 and y0 eq y1 then begin
               xx=[x0] & yy=[y0]      
               hh=0. & vv=0.0
               style=0
            endif
            if x0 eq x1 and y0 ne y1 then begin
               vv=abs(y1-y0)
               xx=[x0,x0] & yy=[y0,y0]+vv*[-1,1]
               style=1
            endif
            if x0 ne x1 and y0 eq y1 then begin
               hh=abs(x1-x0)
               xx=[x0,x0]-hh*[-1,1] & yy=[y0,y0]
               style=1
            endif         
            if x0 ne x1 and y0 ne y1 then begin

               npts=4*ceil(rad)
               ang=findgen(npts)*2*!PI/(npts-1)
               xx=x0+rad*cos(ang)
               yy=y0+rad*sin(ang)
               style=2
            endif
            zz=fltarr(size(xx,/dim))
            
            ;update the ROI
            prop.x=x0
            prop.y=y0
            prop.r=rad
            oROI->SetProperty,uvalue=prop,style=style
            oROI->GetProperty,n_vert=nv
            oROI->ReplaceData,xx,yy,zz,start=0,finish=nv-1
         end
         else: return
      endcase
      ;draw
      (*state).oWindow->Draw,(*state).oView
   end


   255b: begin
      ;if interactively stretching the image:
      
      ;get the size of the draw
      wind=widget_info((*state).wdraw,/geom)
      (*state).bias=(0.001>(event.x/wind.xsize)<1.0)
      (*state).cont=(0.001>(event.y/wind.ysize)<1.0)*20.
      
      ;redisplay the image with new bias/contrast pair
      display_image,state

      if xregistered('stretchimage',/noshow) then begin
         ;if the stretching subGUI is open, update it
         widget_control,(*state).wstretchbase,get_uval=sstate
         widget_control,(*sstate).wbiasvalue,set_val=$
                        string((*state).bias,f='(F4.2)')
         widget_control,(*sstate).wbiasslide,set_value=(*state).bias
         widget_control,(*sstate).wconvalue,set_val=$
                        string((*state).cont,f='(F4.1)')
         widget_control,(*sstate).wconslide,set_value=(*state).cont
      endif
   end
   else: break
endcase


end
