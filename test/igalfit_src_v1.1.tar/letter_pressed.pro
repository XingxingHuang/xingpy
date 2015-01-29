pro letter_pressed,event
;this procedure handles if a letter was pressed in the window


if event.release ne 0 then return  ;only do something when button is pressed!

;char=string(byte(event.ch))        ;convert the event to a character

;NOTE: event.ch is the ascii code, so to
;add more entries here, you need to look up the code for the character 
;you wish to add to.  Above is the line to convert, but certain 
;characters (delete for example) do not have a character.  So working 
;with the ascii codes means you can use such characters (in this case 
;we are using delete).

;do something for each letter. 
case event.ch of
   43: begin                    ;plus sign
      ;Zooming in
      widget_control,event.top,get_uval=state
      widget_control,(*state).wzoomin,set_button=1b
      zoom_image,state,1./(*state).zoomfactor
      update_zoomdisp,state,/pulldown
      widget_control,(*state).wzoomin,set_button=0b
   end
   45: begin                    ;minus sign
      ;Zooming out
      widget_control,event.top,get_uval=state
      widget_control,(*state).wzoomout,set_button=1b
      zoom_image,state,(*state).zoomfactor
      update_zoomdisp,state,/pulldown
      widget_control,(*state).wzoomout,set_button=0b
   end
   81: begin                    ;capital Q
      ;super close of iGalFit
      igalfit_close,event,/yes      
   end
   113: begin                   ;lowercase q
      ;close iGalFit
      igalfit_close,event
   end
   8: begin                     ;delete character hit!
      ;delete a region
      delete_selected_roi,event
   end


   ;the Following are to fucntion like imexamine in IRAF
   114: begin                   ;lowercase r
      ;make a radial plot
      radprof,event,redisplay=xregistered('radprof',/noshow),group=event.top
      widget_control,event.top,/show
   end
   99: begin                    ;lowercase c
      ;make a column plot
      lineplot,event,0,redisplay=xregistered('lineplot',/noshow),group=event.top
      widget_control,event.top,/show
   end
   108: begin                   ;lowercase l
      ;make a line plot
      lineplot,event,1,redisplay=xregistered('lineplot',/noshow),group=event.top
      widget_control,event.top,/show
   end
   109: begin                   ;lowercase m
      ;make image statistics 
      imstat,event,redisplay=xregistered('imstat',/noshow),group=event.top
      widget_control,event.top,/show
   end
   101: begin                   ;lowercase e
      ;contour plot
      contplot,event,redisplay=xregistered('contplot',/noshow),group=event.top
      widget_control,event.top,/show
   end
   104: begin                   ;lowercase h
      ;histogram
      histplot,event,redisplay=xregistered('histplot',/noshow),group=event.top
      widget_control,event.top,/show
   end
   else: return
endcase
end
