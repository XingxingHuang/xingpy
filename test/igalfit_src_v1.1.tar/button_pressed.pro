pro button_pressed,event
;procedure to deal with a button pressed in the draw widget


;get the state
widget_control,event.top,get_uvalue=state

;check for double-clicks
t=systime(/second)
dtime=t-(*state).click_time
(*state).click_time=temporary(t)
if temporary(dtime) le (*state).prefs.double_click_time then begin
   ;remove the image from the select
   (*state).oImage->SetProperty,/hide   
   ;check if selection visual was hit (ie. the handles)
   oSel=(*state).oWindow->Select((*state).oView,[event.x,event.y])
   if obj_valid(oSel(0)) then begin
      if not xregistered('reginfo',/noshow) then begin
         reginfo,state,group=event.top,base=editregbase,$
                 button=(*state).weditreg
         widget_control,event.top,/show
         (*state).weditregbase=editregbase
         widget_control,(*state).weditreg,set_button=1b         
      endif
   endif   
   ;restore the image
   (*state).oImage->SetProperty,hide=0b
endif


;convert from the viewport coordinates to image coordinates
;widget_control,(*state).wdraw,get_draw_view=view
xy=convertxy(event,state)
x=xy(0) & y=xy(1)
dim=[16,16]   ;distance from selection box

;change the cursor look
if event.modifiers mod 2 eq 1 then begin
   (*state).rotating=1b
   (*state).oWindow->SetCurrentCursor,image=$
      [0L, 0L, 57344L, 4096L, 2064L, 1040L, 1080L, 1148L,$
       1040L, 1040L, 2056L, 4100L, 57347L, 0L, 0L, 0L],hotspot=[8,8]   
endif else (*state).rotating=0b

;do something different depending on the type of pressing:
case event.press of
   1: begin  ;left mouse click (normal on Mac)
      ;first find out if a region was selected
      regselected=0b  ;a flag to see if we selected a region!
      
      ;check to see if the regions are allowed to be showing
      if not widget_info((*state).wregions,/button_set) then return

      ;hide the image and ROImodels from clicking
      (*state).oImage->SetProperty,/hide
      (*state).oROIModel->SetProperty,/hide

      ;check if selection visual was hit (ie. the handles)
      oSel=(*state).oWindow->Select((*state).oView,[event.x,event.y])
      if size(oSel,/type) eq 11 then begin
         ;yes a selection visual was hit!
         
         ;get the handles (little boxes)
         (*state).oSelHandle=oSel(0)
         oSel(0)->GetProperty,name=hn
         if hn eq 'LL' or hn eq 'LR' or hn eq 'UL' or hn eq 'UR' then begin
            oROI=(*state).oSelROI
            if obj_valid(oROI) then begin
               oROI->GetProperty,data=roi,roi_xr=xr,roi_yr=yr
               roi(0,*)=roi(0,*)-xr(0)
               roi(1,*)=roi(1,*)-yr(0)
               regselected=1b          ;selected a region handle
               (*state).button=11b     ;for a Handle
            endif
         endif
      endif else (*state).oSelHandle=obj_new()      
      (*state).oROIModel->SetProperty,hide=0b  ;restore the regions

      ;see if a visual wasn't hit:
      if not obj_valid((*state).oSelHandle) then begin
         (*state).oVisual->SetProperty,hide=1b
         oSel=(*state).oWindow->Select((*state).oView,[event.x,event.y],dim=dim)
         if size(oSel,/type) eq 11 then begin
            oROI=oSel(0)
            setroi,state,oROI,/setlist   ;selected a region edge!
            regselected=1b
            (*state).button=11b          ;for a visual
         endif else setroi,state,obj_new()
      endif
      (*state).oImage->SetProperty,hide=0b   ;restore the image
      (*state).xy=[event.x,event.y]          ;save the cursor position

;------------------------------------------------------------------

      if not regselected then begin
         ;if here, then no region was selected.
         ;presumably, we're going to draw something!
;         morph=widget_info((*state).wmorph,/combobox_gettext)
         morph=(*state).morphstate
         prop=define_region(morph,color)
         if size(prop,/type) eq 2 then stop

         if morph eq 'Fit Section' and (*state).fitsect then begin
            t=dialog_message(['You can one and ONLY one',$
                              'Fit Section per run!'],$
                             /error,/center,title='Fit Section Duplication')
            (*state).button=0b
            return
         endif


         ;from the button
;         oSelVisual=(*state).oSelVisual
;         if obj_valid(oSelVisual) then begin
;            oSelVisual->SetProperty,/hide
;            (*state).oSelVisual=obj_new()
;         endif

         ;some code from original button_pressed.pro should 
         ;go here, but omitting it to preserve colors


         oROI=obj_new('IDLgrROI',color=color,$
                      thick=prop.thick,line=prop.linestyle)
         oROI->SetProperty,uvalue=prop
         (*state).oCurrROI=oROI
         (*state).oModel->Add,oROI
         oROI->AppendData,[x,y,0]
         (*state).button=12b      ;drawing a region
         ;record some information
         (*state).xy=[x,y]
      endif

      (*state).oWindow->Draw,(*state).oView  ;re-draw the window
   end
   2: begin  ;center mouse click (option-click on Mac)
      ;this will recenter the image (a la ds9)
      
      ;x,y are the new center
      (*state).oView->GetProperty,view=view
      view(0)=x-view(2)/2
      view(1)=y-view(3)/2
      (*state).oView->SetProperty,view=view
      compass,state
      scalebar,state
      (*state).oWindow->Draw,(*state).oView

   end
   4: begin  ;Right mouse click  (command-click on Mac)
      ;this will interactively stretch the image (a la ds9)
      (*state).button=255b
   end
   else:return
endcase

end
