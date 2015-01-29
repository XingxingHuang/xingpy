pro igalfit_error,type,UVAL=uval
if keyword_set(UVAL) then begin
  t=dialog_message(['Computational Error!',$
                    type+' event with unknown',$
                    'uval='+uval],$
                   /err,/cent,titl='Undefined UVAL')
endif else begin
  t=dialog_message(['Computational Error!',$
                    'Unknown Event type= '+type],$
                   /err,/cent,titl='Undefined Event')
endelse
end
pro igalfit_close,event,YES=yes
widget_control,event.top,get_uval=state

ans='Yes'
if not keyword_set(YES) then $
   ans=dialog_message('Are you sure you want to quit '+$
                      (*state).info.title+'?',title='Quit iGalFit?',$
                      /center,/question)


if ans eq 'Yes' then begin
   t=check_math()                    ;clear the errors
   !except=(*state).errors.except    ;reset the display state
   !quiet=(*state).errors.quiet      ;reset the display state
   widget_control,event.top,/destroy ;kill the widget
endif

end

pro igalfit_clean,wid
widget_control,wid,get_uval=state
if obj_valid((*state).oVisual) then begin
   (*state).oVisual->GetProperty,uval=sstate
   ptr_free,sstate
endif
for i=0,n_tags(*state)-1 do begin
   case size((*state).(i),/tname) of
      'POINTER': ptr_free,(*state).(i)
      'OBJREF': obj_destroy,(*state).(i)
      else:
   endcase
endfor
ptr_free,state
heap_gc                         ;Cleans up residual pointers and objects!
end

pro igalfit_event,event

;juggle event data:
widget_control,event.id,get_uvalue=uval  ;name of UVALUE of the event
eventtype=tag_names(event,/str)          ;event type
event1=(strsplit(eventtype,'_',/ext))(1) ;2nd element of event type


;process events by type
case event1 of
   'KILL': igalfit_close,event  ;hit red X to close (from the window manager)
   'BASE': t=dialog_message('Resizing the window is currently not '+$
                            'operational.',/err,/cent,tit='Resizing')
   'BUTTON': begin
      case uval of
         ;---------------CONTROL THE SUBGUIs---------------------------
         'SEX':begin            ;SExtractor GUI
            widget_control,event.top,get_uvalue=state
            if xregistered('sex',/noshow) then begin
               widget_control,(*state).wsexbase,/destroy
               widget_control,(*state).wsex,set_button=0b
               (*state).wsexbase=-1L
            endif else begin
               sex,group=event.top,base=sexbase,igalfit=state,$
                   scifile=(*state).setfile.sci,button=(*state).wsex
               widget_control,event.top,/show
               (*state).wsexbase=sexbase
               widget_control,(*state).wsex,set_button=1b
            endelse
         end
         'PIXHIST': begin       ;Pixel Histogram GUI
            widget_control,event.top,get_uvalue=state
            if ptr_valid((*state).img) then begin
               if xregistered('pixhist',/noshow) then begin
                  widget_control,(*state).wpixhistbase,/destroy
                  widget_control,(*state).wpixhist,set_button=0b
                  (*state).wpixhistbase=-1L
               endif else begin
                  pixhist,state,base=pixhistbase,group=event.top,$
                          button=(*state).wpixhist
                  widget_control,event.top,/show
                  (*state).wpixhistbase=pixhistbase
                  widget_control,(*state).wpixhist,set_button=1b
               endelse
            endif else begin
               widget_control,(*state).wpixhist,set_button=0b
               t=dialog_message('There is no image loaded!',/error,/center)
            endelse
         end
         'STRETCHGUI': begin       ;Stretch GUI
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then begin
               if xregistered('stretchimage',/noshow) ne 0 then begin
                  widget_control,(*state).wstretchbase,/destroy
                  widget_control,(*state).wstretch,set_button=0b
                  (*state).wstretchbase=-1L
               endif else begin
                  stretchimage,state,group=event.top,base=stretchbase,$
                               button=(*state).wstretch
                  widget_control,event.top,/show
                  (*state).wstretchbase=stretchbase
                  widget_control,(*state).wstretch,set_button=1b
               endelse
            endif else begin
               widget_control,(*state).wstretch,set_button=0b
               t=dialog_message('There is no image loaded!',/error,/center)
            endelse
         end
         'PIXTAB': begin        ;display the pixel table
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then begin
               if xregistered('pixtab',/noshow) then begin
                  widget_control,(*state).wpixtabbase,/destroy
                  widget_control,(*state).wpixtab,set_button=0b
                  (*state).wpixtabbase=-1L
               endif else begin
                  pixtab,state,group=event.top,base=pixtabbase,$
                         button=(*state).wpixtab
                  (*state).wpixtabbase=pixtabbase
                  widget_control,(*state).wpixtab,set_button=1b
               endelse
            endif else begin
               widget_control,(*state).wpixtab,set_button=0b
               t=dialog_message('There is no image loaded!',/error,/center)
            endelse         
         end
         'PREFS': begin         ;open preferences subgui
            widget_control,event.top,get_uval=state
            if not xregistered('prefs') then prefs,state,group=event.top
         end
         
         'EDITREGIONS': begin   ;RegionInfo GUI
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then begin
               if xregistered('reginfo',/noshow) then begin
                  widget_control,(*state).weditregbase,/destroy
                  widget_control,(*state).weditreg,set_button=0b
                  (*state).weditregbase=-1L
               endif else begin
                  reginfo,state,group=event.top,base=editregbase,$
                          button=(*state).weditreg
                  widget_control,event.top,/show
                  (*state).weditregbase=editregbase
                  widget_control,(*state).weditreg,set_button=1b         
               endelse
            endif else begin
               widget_control,(*state).weditreg,set_button=0b
               t=dialog_message('There is no image loaded!',/error,/center)
            endelse
         end
         'ADDCON': begin        ;add a constraint
            widget_control,event.top,get_uval=state
            if xregistered('addconstraint',/noshow) then begin
               widget_control,(*state).waddconsbase,/destroy
               widget_control,(*state).waddcons,set_button=0b
               (*state).waddconsbase=-1L
            endif else begin
               addconstraint,state,group=event.top,base=base,$
                             button=(*state).waddcons
               (*state).waddconsbase=base
            endelse
         end
         
         
         'HELP': help_gui,redisplay=xregistered('help_gui',/noshow),$
                       group=event.top,load='igalfit'
               

         ;---------------------BASIC GUI STUFF-----------------------
         'SCALE': scalemenu,event     ;scale pulldown menu check boxes
         'DISPLAY': displaymenu,event ;display pulldown menu check boxes
         'ZOOMTO': zoommenu,event     ;zoom pulldown menu check boxes
         'STRETCH': stretchmenu,event ;stretch pulldown menu check boxes
         'ABOUT': begin               ;About this program splash screen
             widget_control,event.top,get_uval=state
             info=(*state).info
             t=dialog_message([info.title,'version: '+info.version,$
                               'Last released: '+info.date],/info,/center)
          end
         'SAVESET': begin       ;save an h5 file of the settings
            widget_control,event.top,get_uval=state      
            file=dialog_pickfile(group=event.top,file=(*state).savefile,$
                                 /write,/over)
            if file ne '' then saveset,file,state,event.top
         end
         'LOADSET': begin       ;load an h5 file of the settings
            widget_control,event.top,get_uval=state      
            file=dialog_pickfile(group=event.top,file=(*state).savefile)
            if file ne '' then loadset,file,state,event.top
         end
         'INSPECT': begin       ;inspect the h5 file of settings
            widget_control,event.top,get_uval=state      
            file=dialog_pickfile(group=event.top,file=(*state).savefile)
            if file ne '' then t=h5_browser(file)
         end
         
         'SAVEREG': begin       ;save the regions to a ds9 file
            widget_control,event.top,get_uval=state
            roi2reg,state
         end
         'LOADREG': begin       ;load the regions from a ds9 file
            widget_control,event.top,get_uval=state
            reg2roi,state
         end   
         'ZOOMIN': begin        ;zoom in
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then $
               zoom_image,state,1./(*state).zoomfactor
         end
         'ZOOMOUT': begin       ;zoom out
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then $
               zoom_image,state,(*state).zoomfactor
         end
         'RESETZOOM': begin     ;reset the zoom state
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then $
               zoom_image,state,1.,/reset
         end
         
         
         'DELETEALL': delete_all,event       ;delete all regions
         'DELETE': delete_selected_roi,event ;delete selected region
         'EDITFEEDME': begin                 ;edit feedme file
            widget_control,event.top,get_uvalue=state
            t=dialog_message(['There are no safety nets in place to ensure ',$
                              'any edits you make are acceptable to GalFit.',$
                              'Are you certain you want to do this?'],/center,$
                             /ques,title='Edit FeedMe File?')
            if t(0) eq 'Yes' then begin
               if mkgalfit(state) then begin
                  feedme=(*state).prefs.feedme
                  editfile,feedme,group=event.top,$
                           helpfile='editfeed',filetype='GalFit FeedMe'
               endif 
            endif  
            widget_control,(*state).weditfeedme,set_button=0b
         end
         'GALFIT': begin
            widget_control,event.top,get_uval=state
            widget_control,(*state).wgalfit,set_button=1b
            rungalfit,event
         end

         
         'REMOVE': begin        ;remove constraint
            widget_control,event.top,get_uval=state
            tblsel=reform((widget_info((*state).wcontable,/table_select))(1,*))
            widget_control,(*state).wcontable,get_val=constraints
            remove_constraints,state,constraints(tblsel)
            g=where(constraints ne '',n)      
            constraints=((n eq 0)?['']:constraints(g))
            widget_control,(*state).wcontable,set_val=constraints
         end
         'REMOVEALL': begin     ;remove all constraints
            widget_control,event.top,get_uval=state      
            widget_control,(*state).wcontable,get_val=constraints
            remove_constraints,state,constraints
            widget_control,(*state).wcontable,set_val=['']
         end
         
         
         'VIEWIMGBLOCK': begin  ;view the imgblock file
            widget_control,event.top,get_uval=state
            widget_control,(*state).wout,get_value=imgblock

            if imgblock(0) eq '' then begin ;check if file blank
               t=file_error('imgblock',/blank)
               return
            endif

            if not file_exist(imgblock(0)) then begin ;check if file exists
               t=file_error('imgblock')
               return
            endif
            
            widget_control,(*state).wgalfit,set_button=1b
            xreg=xregistered('galfit_results',/noshow)
            galfit_results,imgblock=imgblock(0),base=base,group=event.top,$
                           redisplay=xreg,button=(*state).wgalfit
            if not xreg then (*state).wresults=base
         end
         
         'EDITCONS': begin      ;edit the constraints file
            widget_control,event.top,get_uvalue=state            
            if widget_info((*state).weditcons,/button_set) then begin
               t=dialog_message(['There are no safety nets in place to '+$
                                 'ensure ','any edits you make are '+$
                                 'acceptable to GalFit.','Are you certain '+$
                                 'you want to do this?'],$
                                /center,/ques,title='Edit Constraints File?')
               edit=(t(0) eq 'Yes')
               widget_control,(*state).weditcons,set_button=edit
            endif else edit=0b
            widget_control,(*state).wcontable,editable=edit
         end
         
         'LOADSCI': begin       ;load science file
            scifile=dialog_pickfile(default_ext='fits',/read,group=event.top,$
                                    title='Pick a Science File')
            t=loadfits(event,scifile,'Science',/sci,/disp)
         end
         
         'LOADUNC': begin       ;load uncertainty file
            uncfile=dialog_pickfile(default_ext='fits',/read,group=event.top,$
                                    tit='Pick an Uncertainty File')
            t=loadfits(event,uncfile,'Uncertainty',/unc)
         end
         
         'LOADPSF': begin       ;load PSF file
            psffile=dialog_pickfile(default_ext='fits',/read,group=event.top,$
                                    tit='Pick a PSF File')
            t=loadfits(event,psffile,'PSF',/psf)
         end
         'COMPASS': begin       ;display the compass
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).ast) then begin
               set=widget_info((*state).wcompass,/button_set)
               widget_control,(*state).wcompass,set_button=1b-set
               (*state).oVane->SetProperty,hide=set
               (*state).oWindow->Draw,(*state).oView
            endif else t=dialog_message(['Unable to display a compass.',$
                                         'This frame does not have',$
                                         'a valid WCS.'],/err,$
                                        tit='Compass Error',$
                                        dialog_parent=event.top)
         end
         'SCALEBAR': begin       ;display the compass
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).ast) then begin
               set=widget_info((*state).wscalebar,/button_set)
               widget_control,(*state).wscalebar,set_button=1b-set
               (*state).oScale->SetProperty,hide=set
               (*state).oWindow->Draw,(*state).oView
            endif else t=dialog_message(['Unable to display a scalebar ',$
                                         'This frame does not have',$
                                         'a valid WCS.'],/err,$
                                        tit='Scale Error',$
                                        dialog_parent=event.top)
         end
         'REGIONS': begin       ;display the regions
            widget_control,event.top,get_uval=state
            set=widget_info((*state).wregions,/button_set)
            widget_control,(*state).wregions,set_button=1b-set
            (*state).oROIModel->SetProperty,hide=set
            (*state).oVisual->SetProperty,hide=1b
            (*state).oWindow->Draw,(*state).oView
         end
         'SKY0': begin          ;fit a sky level
            widget_control,event.top,get_uval=state
            widget_control,(*state).wsky0,sens=$
                           widget_info((*state).wfitsky0,/button_set)
         end
         'DSDX': begin          ;fit a ds/dx term to sky
            widget_control,event.top,get_uval=state
            widget_control,(*state).wdsdx,sens=$
                           widget_info((*state).wfitdsdx,/button_set)
         end
         'DSDY': begin          ;fit a ds/dy term to sky
            widget_control,event.top,get_uval=state
            widget_control,(*state).wdsdy,sens=$
                           widget_info((*state).wfitdsdy,/button_set)
         end         
         'MORPH': begin         ;set the morphology/region type
            widget_control,event.top,get_uval=state
            g=(where(event.id eq (*state).morphinfo.wid))(0)
            thismorph=(*state).morphinfo(g).type
            widget_control,(*state).wmorph,set_value=thismorph,$
                           tooltip=(*state).morphinfo(g).tip
            (*state).morphstate=thismorph            
         end

         'QUIT': igalfit_close,event ;close the GUI

         'FINDISP': return      ;flag to load display when done with GF
         'SILENT': return       ;flag to suppress info to terminal
         'CLEAN': return        ;flag to clean up when done with GF
         'MKBPX': return        ;Flag to make the BPX file
         'SHOT': return         ;include the shot noise in Unc map
         else: igalfit_error,eventtype,uval=uval
      endcase
   end

   'TEXT': begin
      case uval of
         ;---------------------STUFF FOR GALFIT-----------------------

         'ZERO': begin          ;adjust the zeropoint 
            widget_control,event.top,get_uval=state
            widget_control,(*state).wzero,get_val=zero
            if isnumber(zero(0)) eq 0 then t=type_error('Zeropoint') else $
               (*state).magzero=float(zero(0))
         end
         
         'CONSFILE': begin      ;name of constraint file
            widget_control,event.top,get_uval=state
            update_contab,state
         end
         'OUTNAME': return      ;name of output file
         'BPXNAME': return      ;name of BPX file
         'EXPTIME': return      ;the exposure time
         else: igalfit_error,eventtype,uval=uval
      endcase
   end
   
   'DRAW': begin
      case uval of
         'MAINDRAW': begin      ;events in the draw window    
            widget_control,event.top,get_uval=state
            if ptr_valid((*state).img) then begin ;only draw if img is loaded
               case event.type of
                  0: button_pressed,event  ;a button was pressed
                  1: button_released,event ;a button was released
                  2: mouse_moved,event     ;the mouse was moved
                  3: viewport,event        ;the viewport was changed
                  4: expose,event          ;must re-expose the viewport
                  5: letter_pressed,event  ;a letter was pressed
                  6: move_cursor,event     ;an arrow was pressed
                  else:                    ;some other type, ignore those.
               endcase
            endif
         end
         else: igalfit_error,eventtype,ual=uval
      endcase
   end
   'TAB': return                ;widget_tab events?

   'COMBOBOX': begin
      case uval of
         'GFTYPE': return       ;the GalFit run-type
         'DISPTYPE': return     ;the GalFit display-type
         'UNITS': return        ;the units of the images
         else: igalfit_error,eventtype,ual=uval
      endcase
   end
   

   'TABLE': begin
      case uval of
         'CONTABLE': return
         else: igalfit_error,eventtype,ual=uval
      end 
   endcase
   else: igalfit_error,eventtype
endcase

end



pro igalfit,LOADSETTINGS=loadsettings,$ ;a settings file
            SCIFILE=scifile,$           ;science image to fit
            UNCFILE=uncfile,$           ;uncertainty image
            PSFFILE=psffile,$           ;PSF image to use
            BPXFILE=bpxfile,$           ;Bad pixel file to use
            IMGFILE=imgfile,$           ;output imgblock.fits file
            REGFILE=regfile,$           ;region file (see documentation)
            EXPTIME=exptime,$           ;exposure time (in seconds)
            MAGZERO=magzero,$           ;magnitude zero point
            ZOOM0=zoom0,$               ;initial zoom (I prefer 0.25)
            RELOAD=reload,$             ;reload the GUI with new settings?
            CENTER=center               ;center the GUI in the display?

;release information
info={title:'iGalFit',version:'1.1',date:'Oct. 18, 2011'}

;hide the error messages!
errors={except:!except,quiet:!quiet} ;save what the User had initially
!except=0b & !quiet=1b               ;be vewy vewy quiet, I'm hunting wabbits

;test for multiple instances:
ninst=xregistered('igalfit',/noshow)
if (ninst ge 1) and (~keyword_set(RELOAD)) then begin
   if ninst gt 1 then t={verb:'are',let:'s'} else t={verb:'is',let:''}
   num=strcompress(string(ninst,f='(I3)'),/rem)
   t=dialog_message(['There '+t.verb+' '+num+' instance'+t.let+$
                     ' of iGalFit already running.',$
                     'It is NOT recommended having multiples!',$
                     'Are you sure you want to proceed?'],/center,/ques,$
                    /default_no)
   if t eq 'No' then return else delvarx,t
endif

;sizes
xdisp=575
ydisp=450

;set some defaults
magzero=keyword_set(MAGZERO)?string(magzero,f='(F6.3)'):'0.0'
exptime=keyword_set(EXPTIME)?string(exptime,f='(E10.4)'):'1.0'
bpxfile=keyword_set(BPXFILE)?bpxfile:''
imgfile=keyword_set(IMGFILE)?imgfile:''
if not keyword_set(ZOOM0) then zoom0=1.0
savefile='igalfit_save.h5'      ;default name of save file

;set up the colors
define_rgb,rgb
backcolor=rgb((where(rgb.name eq 'white'))(0)).rgb
vanecolor=rgb((where(rgb.name eq 'black'))(0)).rgb
scalecolor=rgb((where(rgb.name eq 'black'))(0)).rgb

;get the salient directories
findpro,current_routine(),dir=dir,/noprint
bitmapdir=dir(0)+'bitmaps/'
helpdir=dir(0)+'help/'


if keyword_set(RELOAD) and (ninst ge 1) then begin
   
   ;get the state variable
   base=!igalfit_base
   widget_control,base,get_uvalue=state


   ;set the input variables to the GUI
   widget_control,(*state).wbpx,set_value=bpxfile
   widget_control,(*state).wout,set_value=imgfile
   widget_control,(*state).wexptime,set_value=exptime
   widget_control,(*state).wzero,set_value=magzero
   if bpxfile ne 'none' then widget_control,(*state).wmkbpx,set_button=1b
   delete_all,{top:base}        ;delete the regions
   (*state).zoomstate=1.0       ;set to default.

   ;reset the morphology button
   t=morph_pdmenu(-1L,morphinfo,morphstate,/default)

   g=(where((*state).morphinfo.type eq morphstate))(0)
   widget_control,(*state).wmorph,set_value=morphstate,$
                  tool=(*state).morphinfo(g).tip
   (*state).morphstate=morphstate
   
   (*state).bias=0.33
   (*state).cont=0.80

endif else begin

   ;start building the GUI
   base=widget_base(title=info.title+' v'+info.version,/column,mbar=mbar,$
                    /tlb_kill_request_events,/tlb_size_events)


   ;File menu:
   filemenu=widget_button(mbar,value='File',/menu)
   aboutbutton=widget_button(filemenu,value='About',uvalue='ABOUT')
   
   prefbutton=widget_button(filemenu,value='Preferences',uval='PREFS',/sep)
   loadbutton=widget_button(filemenu,value='Load',/menu)
   scibutton=widget_button(loadbutton,value='Science',uval='LOADSCI',$
                           accel='Ctrl+s')
   rmsbutton=widget_button(loadbutton,value='Uncertainty',uval='LOADUNC',$
                           accel='Ctrl+u')
   psfbutton=widget_button(loadbutton,value='PSF',uval='LOADPSF',$
                           accel='Ctrl+p')
   setbutton=widget_button(filemenu,value='Settings',/menu)
   loadsetbutton=widget_button(setbutton,value='Load',uval='LOADSET',$
                               accel='Ctrl+l')
   savesetbutton=widget_button(setbutton,value='Save',uval='SAVESET',$
                               accel='Ctrl+s')
   exitbutton=widget_button(filemenu,value='Quit',/sep,uval='QUIT',$
                            accel='Ctrl+q')

   ;Display menu
   dispmenu=widget_button(mbar,value='Display',/menu)
   images=['Science','Uncertainty','PSF','BPX','Model','Residuals']
   wimage=lonarr(n_elements(images))
   for i=0,n_elements(images)-1 do $
      wimage(i)=widget_button(dispmenu,value=images(i),/checked,$
                              uvalue='DISPLAY',$
                              accel='Alt+'+strlowcase(strmid(images(i),0,1)))

   ;Show menu
   showmenu=widget_button(mbar,value='Show',/menu)
   wcompass=widget_button(showmenu,value='Compass',/checked,uval='COMPASS')
   wscalebar=widget_button(showmenu,value='Scale Bar',/checked,uval='SCALEBAR')
   wregions=widget_button(showmenu,value='Regions',/checked,uval='REGIONS')
   widget_control,wregions,set_button=1b


   ;Scale menu
   scalemenu=widget_button(mbar,value='Scale',/menu)
   scales=['Linear','Log']
   ;scales=['Linear','Log','PowerLaw','SquareRoot','Square','HistoEq','Asinh']
   wscale=lonarr(n_elements(scales))
   for i=0,n_elements(scales)-1 do $
      wscale(i)=widget_button(scalemenu,value=scales(i),/checked,uvalue='SCALE')

   limits=['Auto','Minmax','User']
   wlimit=lonarr(n_elements(limits))
   


   
   ;zoom menu
   zoommenu=widget_button(mbar,value='Zoom',/menu)
   zooms=['32','16','8','4','2','1','1/2','1/4','1/8','1/16','1/32']
   wzoom=lonarr(n_elements(zooms))
   for i=0,n_elements(zooms)-1 do $
      wzoom(i)=widget_button(zoommenu,value=zooms(i),/checked,uval='ZOOMTO')
   wresetzoom=widget_button(zoommenu,value='Reset Zoom',uvalue='RESETZOOM',/sep)
   widget_control,wzoom((where(zooms eq '1'))(0)),set_button=1b
   
   
   ;Regions menu
   regmenu=widget_button(mbar,value='Regions',/menu)
   d=widget_button(regmenu,value='Delete All',uval='DELETEALL')
   s=widget_button(regmenu,value='Save',uval='SAVEREG')
   l=widget_button(regmenu,value='Load',uval='LOADREG')
   
   ;Help Menu
   helpmenu=widget_button(mbar,value='Help',/menu,/help)
   helpbutton=widget_button(helpmenu,value='Help',uval='HELP',accel='Ctrl+h')
   
   ;the top display
   top=widget_base(base,/row,/frame)
   sunken=1b

   ;the File names box:
   disp=widget_base(top,/column)
   names=widget_base(disp,/column,/frame)
   r1=widget_base(names,/row)
   t=widget_label(r1,value='Sci:')
   wsci=widget_label(r1,val='',ysize=13,xsize=132,/align_left,sunken=sunken)
   r2=widget_base(names,/row)
   t=widget_label(r2,value='Unc:')
   wunc=widget_label(r2,val='',ysize=13,xsize=132,/align_left,sunken=sunken)
   r3=widget_base(names,/row)
   t=widget_label(r3,value='PSF:')
   wpsf=widget_label(r3,val='',ysize=13,xsize=132,/align_left,sunken=sunken)
   
   ;the pixel info box
   vbase=widget_base(disp,/column,/frame)
   line1=widget_base(vbase,/row)
   t=widget_label(line1,value='x:')
   wx=widget_label(line1,value='',xsize=40,ysize=12,/align_left,sunken=sunken)
   t=widget_label(line1,value='r:')
   wr=widget_label(line1,value='',xsize=80,ysize=12,/align_left,sunken=sunken)
   line2=widget_base(vbase,/row)
   t=widget_label(line2,value='y:')
   wy=widget_label(line2,value='',xsize=40,ysize=12,/align_left,sunken=sunken)
   t=widget_label(line2,value='d:')
   wd=widget_label(line2,value='',xsize=80,ysize=12,/align_left,sunken=sunken)
   line3=widget_base(vbase,/row)
   t=widget_label(line3,value='p:')
   wp=widget_label(line3,value='',xsize=70,ysize=12,/align_left,sunken=sunken)
   t=widget_label(line3,value='Z:')
   wz=widget_label(line3,value='1',xsize=50,ysize=12,/align_left,sunken=sunken)


   ;the GalFIt control box:
   gf=widget_base(top,/column)
   tab=widget_tab(gf,location=0,xsize=xdisp-190,ysize=150,UVAL='TAB')

   ;File input/output tab
   iotab=widget_base(tab,title='File I/O',/column)
   l=widget_label(iotab,value='File Input/Output')
   io1=widget_base(iotab,/row)
   l=widget_label(io1,value='B) Output Image  ')
   wout=widget_text(io1,value=imgfile,xsize=20,/editable,uval='OUTNAME')
   w=widget_button(io1,value='Inspect File',uval='VIEWIMGBLOCK',$
                   tooltip='View the GalFit output file')
   io2=widget_base(iotab,/row)
   l=widget_label(io2,value='F) Bad Pixel Mask')
   wbpx=widget_text(io2,value=bpxfile,xsize=20,/editable,uval='BPXNAME')
   mkbpx=widget_base(io2,/row,/non)
   wmkbpx=widget_button(mkbpx,value='Make BPX',uval='MKBPX',$
                        tooltip='Make the Bad Pixel Mask?')
   if bpxfile ne 'none' then widget_control,wmkbpx,set_button=1b
   
   ;the constraints tab
   contab=widget_base(tab,title='Constraints',/column)

   top=widget_base(contab,/row)
   lhs=widget_base(top,/column,/align_center)
   r=widget_base(lhs,/row)
   l=widget_label(r,value='File')
   wconfile=widget_text(r,/editable,xsize=16,value='none',$
                        uval='CONSFILE',/all_events)
   
   waddcons=widget_button(lhs,value='Add Constraint',uval='ADDCON')
   wremcon=widget_button(lhs,value='Remove',uval='REMOVE')
   wremallcon=widget_button(lhs,value='Remove All',uval='REMOVEALL')
   
   rhs=widget_base(top,/col,/align_center)
   nrow=6
   wcontable=widget_table(rhs,/no_column_headers,/no_row_headers,/scroll,$
                          xsize=1,scr_xsize=210,column_width=187,$
                          uval='CONTABLE',/disjoint_selection,ysize=nrow)
   
   ;the ranges tab
   rangetab=widget_base(tab,title='Ranges',/column)
   l=widget_label(rangetab,value='Ranges for Calculations')
   rangerow=widget_base(rangetab,/row)
   fitrange=widget_base(rangerow,/column,/frame)
   l=widget_label(fitrange,value='Fitting Range:')
   ran1=widget_base(fitrange,/row)
   l=widget_label(ran1,value='x0')
   wx0=widget_text(ran1,value='',/edit,xsize=6)
   l=widget_label(ran1,value='x1')
   wx1=widget_text(ran1,value='',/edit,xsize=6)
   ran2=widget_base(fitrange,/row)
   l=widget_label(ran2,value='y0')
   wy0=widget_text(ran2,value='',/edit,xsize=6)
   l=widget_label(ran2,value='y1')
   wy1=widget_text(ran2,value='',/edit,xsize=6)
   conrange=widget_base(rangerow,/column,/frame)
   l=widget_label(conrange,value='Convolution Box:')
   ran3=widget_base(conrange,/row)
   l=widget_label(ran3,value='dx')
   wdx=widget_text(ran3,value='',/edit,xsize=6)
   l=widget_label(ran3,value='dy')
   wdy=widget_text(ran3,value='',/edit,xsize=6)
   
   ;the image properties tab
   imagetab=widget_base(tab,title='Image Prop.',/column)
   l=widget_label(imagetab,value='Image Properties')
   top=widget_base(imagetab,/row)
   
   lhs=widget_base(top,/col)
   img1=widget_base(lhs,/row)
   l=widget_label(img1,value='Zeropoint')
   wzero=widget_text(img1,value=magzero,xsize=10,/editable,uval='ZERO')
   img3=widget_base(lhs,/row)
   l=widget_label(img3,value='Exp Time ')
   wexptime=widget_text(img3,value=exptime,xsize=10,/editable,uval='EXPTIME')
   r=widget_base(lhs,/row)
   l=widget_label(r,value='Img Units')
   wunits=widget_combobox(r,value=['cts','cts/s'],uval='UNITS',xsize=78)   

   rhs=widget_base(top,/col)   
   pix=widget_base(rhs,/col,/frame)
   l=widget_label(pix,value='Pixel Scale')
   r=widget_base(pix,/row)
   l=widget_label(r,val='x')
   wpixx=widget_text(r,value='',xsize=6,/editable)
   l=widget_label(r,val='y')
   wpixy=widget_text(r,value='',xsize=6,/editable)
   r=widget_base(rhs,/row,/non,/frame)
   wshot=widget_button(r,value='Include shot noise'+string(10b)+$
                       'in uncertainty image?',uval='SHOT')
   widget_control,wunits,set_combobox_select=1
   widget_control,wshot,set_button=1b
   

   ;the sky model tab
   skytab=widget_base(tab,title='Sky',/column)
   l=widget_label(skytab,value='Sky Model')
   row=widget_base(skytab,/row)
   sky=widget_base(row,/row,/non)
   wfitsky0=widget_button(sky,value='Fit Sky0 ',uvalue='SKY0')
   wsky0=widget_text(row,value='',/editable,xsize=8)
   widget_control,wfitsky0,set_button=1b & widget_control,wsky0,set_value='0.0'
   row=widget_base(skytab,/row)
   sky=widget_base(row,/row,/non)
   wfitdsdx=widget_button(sky,value='Fit dS/dx',uvalue='DSDX')
   wdsdx=widget_text(row,value='',/editable,xsize=8,sens=0b)
   widget_control,wfitdsdx,set_button=0b
   row=widget_base(skytab,/row)
   sky=widget_base(row,/row,/non)
   wfitdsdy=widget_button(sky,value='Fit dS/dy',uvalue='DSDY')
   wdsdy=widget_text(row,value='',/editable,xsize=8,sens=0b)
   widget_control,wfitdsdy,set_button=0b
   
   ;additional galfit settings
   addtab=widget_base(tab,title='Add.',/column)
   l=widget_label(addtab,value='Additional GalFit Settings')
   top=widget_base(addtab,/row)
   lhs=widget_base(top,/column)
   
   add1=widget_base(lhs,/row)
   l=widget_label(add1,value='Display Type ')
   wdisptype=widget_combobox(add1,value=['regular','curses','both'],xsize=85,$
                             uval='DISPTYPE')
   add2=widget_base(lhs,/row)
   l=widget_label(add2,value='GalFit Type  ')
   gftype=['Optimize','Model','ImgBlock','SubComps']
   wgftype=widget_combobox(add2,value=gftype,xsize=85,uval='GFTYPE')
   add3=widget_base(lhs,/row)
   l=widget_label(add3,value='Fine Sampling')
   wfine=widget_text(add3,value='1.0',/editable,xsize=11)
   rhs=widget_base(row,/column)
   
   rhs=widget_base(top,/column)
   buttons=widget_base(rhs,/column,/non)
   wclean=widget_button(buttons,value='Erase files when finished',uval='CLEAN')
   wsilent=widget_button(buttons,val='Suppress info to terminal',uval='SILENT')
   wdisp=widget_button(buttons,value='Display when finished',uval='FINDISP')
   widget_control,wclean,set_button=1b
   widget_control,wsilent,set_button=0b
   widget_control,wdisp,set_button=1b
   
   
   ;the toolbar:
   toolbar=widget_base(base,/row,/frame)
   
   ;file I/O
   io=widget_base(toolbar,/row,/toolbar)
   wopen=widget_button(io,/bitmap,tooltip='Load Settings',uval='LOADSET',$
                       value=bitmapdir+'open.bmp')
   wsave=widget_button(io,/bitmap,tooltip='Save Settings',uval='SAVESET',$
                       value=bitmapdir+'save.bmp')
   winsp=widget_button(io,/bitmap,tooltip='Inspect Settings',uval='INSPECT',$
                       value=bitmapdir+'hdf.bmp')
   
   ;the morphology button
   col=bytarr(80,13,3)
   col(*,*,0)=255b
   mbutton=widget_base(toolbar,/row,/toolbar) ;base widget to hold morphology
   wmorph=morph_pdmenu(mbutton,morphinfo,morphstate)
   
   ;the delete button
   wdelete=widget_base(toolbar,/row,/toolbar)
   delete=widget_button(wdelete,/bitmap,tooltip='Delete Selected Region',$
                        uval='DELETE',value=bitmapdir+'delete.bmp')
   

   ;zoom buttons
   buttools=widget_base(toolbar,/row,/toolbar)
   wzoomin=widget_button(buttools,/bitmap,tooltip='Zoom In',uval='ZOOMIN',$
                         value=bitmapdir+'zoom_in.bmp')
   wzoomout=widget_button(buttools,/bitmap,tooltip='Zoom Out',uval='ZOOMOUT',$
                          value=bitmapdir+'zoom_out.bmp')
   wzoomres=widget_button(buttools,/bitmap,tool='Reset Zoom',uval='RESETZOOM',$
                          value=bitmapdir+'zoom.bmp')



   ;Sub-GUIs
   guitools=widget_base(toolbar,/row,/toolbar,/nonexclus)
   wpixhist=widget_button(guitools,value=bitmapdir+'hist.bmp',$
                          tooltip='Pixel Histogram',uvalue='PIXHIST',/bitmap)
   wpixtab=widget_button(guitools,value=bitmapdir+'dm.bmp',$
                         tooltip='Pixel Table',uvalue='PIXTAB',/bitmap)
   wstretch=widget_button(guitools,value=bitmapdir+'colorbar.bmp',$
                          tooltip='Image Stretch',uvalue='STRETCHGUI',$
                          /bitmap)
   weditfeedme=widget_button(guitools,value=bitmapdir+'text.bmp',$
                             tooltip='Edit Feedme',uvalue='EDITFEEDME',/bitmap)
   weditreg=widget_button(guitools,value=bitmapdir+'drawing.bmp',$
                          tooltip='Edit Regions',uvalue='EDITREGIONS',/bitmap)
   wgalfit=widget_button(guitools,value=bitmapdir+'galfit.bmp',$
                         tooltip='Run GalFit',uvalue='GALFIT',/bitmap)
   wsex=widget_button(guitools,value=bitmapdir+'sex.bmp',$
                      tooltip='Run SExtractor',uvalue='SEX',/bitmap)
   
   ;the main draw window   
   bot=widget_base(base,/row,/frame)
   wdraw=widget_draw(bot,xsize=xdisp,ysize=ydisp,$
                     /button,/motion,/view,/expose,keyboard=2,$
                     retain=2,graphics=2,uval='MAINDRAW',frame=5)

   ;dimensions
   geom=widget_info(base,/geom)
   dimen=[geom.xsize,geom.ysize]
   

   ;center the GUI
   if keyword_set(CENTER) then begin
      device,get_screen_size=sz
      widget_control,base,$
                     tlb_set_xoffset=(sz(0)<((sz(0)-geom.scr_xsize)/2.)>0),$
                     tlb_set_yoffset=(sz(1)<((sz(1)-geom.scr_ysize)/2.)>0)
   endif


   ;draw the GUI
   widget_control,/realize,base


   ;do some Object stuff
   widget_control,wdraw,get_value=oWindow ;window object
   oImage=obj_new('IDLgrImage')
   oView=OBJ_NEW('IDLgrView', VIEWPLANE_RECT=[0,0,xdisp,ydisp],color=backcolor)
   oModel = OBJ_NEW('IDLgrModel')
   oView->Add, oModel
   oModel->Add, oImage

   ;build the ROI containers
   oROIModel = OBJ_NEW('IDLgrModel')
   oROIGroup = OBJ_NEW('IDLanROIGroup')
   oModel->Add, oROIModel
   
   ;add the compass:
   vanethick=2
   oVane=OBJ_NEW('IDLgrROI',color=vanecolor,thick=vanethick)
   oModel->Add,oVane

   ;add the scale bar
   scalethick=2
   oScale=OBJ_NEW('IDLgrROI',color=scalecolor,thick=scalethick)
   oModel->Add,oScale
   
   ;the region boxes
   oVisual=roi_visual()
   oModel->Add,oVisual
   
   ;a place holder
   file={sci:'',$               ;name of science file
         unc:'',$               ;name of uncertainty file
         psf:''}                ;name of PSF file

   ;set the preferences
   prefs={backcolor:backcolor,$    ;background color
          vanesize:10.,$           ;weather vane size
          vanethick:vanethick,$    ;weather vane thickness
          scalesize:1.,$           ;scale bar size
          scalethick:scalethick,$  ;scale bar thickness
          scaleunit:'arcsec',$     ;scale bar units
          tempdir:'/tmp/',$        ;temp directory
          losig:3.,$               ;N of lo sig in autoscale.pro
          hisig:10.,$              ;N of hi sig in autoscale.pro
          sigma:5.,$               ;N of sigma in resistant_mean
          double_click_time:0.25,$ ;double click time
          acrit:25,$               ;minimum ISOAREA to be extended
          rcrit:1.5,$              ;minimun circularized radius to be real
          defmorph:'Sersic',$      ;default morpholog
          sersic:{n:2.5},$         ;Sersic function defaults
          nuker:{alpha:1.2,$       ;Nuker function defaults
                 beta:0.5,$
                 gamma:0.7},$ 
          moffat:{fwhm:0.5,$       ;Moffat Function defaults
                  alpha:1.5},$
          ferrer:{alpha:4.,$       ;Ferrer Function defaults
                  beta:2.},$
          gaussian:{fwhm:0.5},$    ;Gaussian Function defaults
          king:{rt:2.,$            ;King Function defaults
                alpha:2.},$
          exec:'galfit',$          ;GalFit executable
          feedme:'galfit.feedme',$ ;feedme file
          iraf:{maxrad:10.,$       ;maxradius
                fwhm:3.0,$         ;FWHM
                width:'1',$        ;width
                combine:'total',$  ;combine type
                range:'full',$     ;range
                boxsize:100,$      ;boxsize
                consize:20,$
                nticks:5,$
                nlevels:5,$
                hissize:20,$
                nbins:100}}
  
   ;iraf sub-gui bases
   wiraf={imstat:-1L,$          ;image statistics
          lineplot:-1L,$        ;line plot
          contplot:-1L,$        ;contour plot
          histplot:-1L,$        ;histogram plot
          radprof:-1L}          ;radial profile

   ;save the data for event handler:
   state={oWindow:oWindow,$       ;window object
          oImage:oImage,$         ;image object
          oModel:oModel,$         ;image model object
          oView:oView,$           ;viewport object
          oROIModel:oROIModel,$   ;ROI model object
          oROIGroup:oROIGroup,$   ;ROI group object
          oCurrROI:obj_new(),$    ;current ROI object
          oSelROI:obj_new(),$     ;selected ROI object
          oVisual:oVisual,$       ;box and squares object
          oSelVisual:obj_new(),$  ;selected visual object
          oSelHandle:obj_new(),$  ;Selected handle object
          oVane:oVane,$           ;Weathervane ROI object
          oScale:oScale,$         ;scale bar ROI object
          wx:wx,$                 ;x coordinate text widget
          wy:wy,$                 ;y coordinate text widget
          wr:wr,$                 ;RA coordinate text widget
          wd:wd,$                 ;Dec coordinate text widget
          wp:wp,$                 ;Pix value text widget
          wz:wz,$                 ;Zoom value text widget
          wdraw:wdraw,$           ;the draw widget
          wscale:wscale,$         ;scales widget
          scales:scales,$         ;name of scales
          scale:'Linear',$        ;selected scale
          ;wstretch:wstretch,$     ;stretch widgets
          ;stretches:stretches,$   ;name of stretches
          ;stretch:'auto-scale',$  ;selected stretch
          zooms:zooms,$           ;Zoom values
          wzoom:wzoom,$           ;zoom widgets
          wzoomin:wzoomin,$       ;zoom in button
          wzoomout:wzoomout,$     ;zoom out button
          morphinfo:morphinfo,$   ;the morphology information
          morphstate:morphstate,$ ;the current morphology state
          wmorph:wmorph,$         ;morphology & color combobox widget
          weditreg:weditreg,$     ;'EDIT REGION' button
          weditregbase:-1L,$      ;'EDIT_REGION' base widget
          weditfeedme:weditfeedme,$ ;'EDIT FEEDME' button
          waddcons:waddcons,$       ;'ADD CONSTRAINT' button
          waddconsbase:-1L,$        ;'ADD CONSTRAINT' base
          wpixtab:wpixtab,$         ;'PIXEL TABLE' button
          wpixtabbase:-1L,$         ;'PIXEL TABLE' base widget
          wpixhist:wpixhist,$       ;'PIXEL HISTOGRAM' button
          wpixhistbase:-1L,$        ;'PIXEL HISTOGRAM' base widget
          wstretch:wstretch,$       ;'STRETCH IMAGE' button
          wstretchbase:-1L,$          ;'STRETCH IMAGE' base widget
          wsex:wsex,$               ;'SEXTRACTOR' button
          wsexbase:-1L,$            ;'SEXTRACTOR' base widget
          wresults:-1L,$            ;'GALFIT_RESULTS' base widget
          whelpbase:-1L,$           ;'HELP_GUI' base widget
          wcompass:wcompass,$       ;show compass button
          wscalebar:wscalebar,$     ;show scalebar button
          wregions:wregions,$       ;show regions button
          wsci:wsci,$               ;science image name widget
          wunc:wunc,$               ;uncertainty image name widget
          wpsf:wpsf,$               ;PSF image name widget
          wout:wout,$               ;output image name widget
          wbpx:wbpx,$               ;bad pixel image name widget
          wmkbpx:wmkbpx,$           ;make a bad pixel file?
          wconfile:wconfile,$       ;the constraints name widget
          wcontable:wcontable,$     ;constraints table
          wremcon:wremcon,$         ;remove selected constraint button
          wremallcon:wremallcon,$   ;remove all constraints button
          wx0:wx0,$                 ;x0 for fitting text widget
          wx1:wx1,$                 ;x1 for fitting text widget
          wy0:wy0,$                 ;y0 for fitting text widget
          wy1:wy1,$                 ;y1 for fitting text widget
          wdx:wdx,$                 ;Dx for convolution text widget
          wdy:wdy,$                 ;Dy for convolution text widget
          wfitsky0:wfitsky0,$       ;Fit flat sky button (Y/N)
          wsky0:wsky0,$             ;flat sky value widgeth
          wfitdsdx:wfitdsdx,$       ;fit x-gradient button (Y/N)
          wdsdx:wdsdx,$             ;x-gradeint value
          wfitdsdy:wfitdsdy,$       ;fit y-gradient button (Y/N)
          wdsdy:wdsdy,$             ;y-gradient value
          wzero:wzero,$             ;mag zeropoint text widget
          wpixx:wpixx,$             ;x pixel scale text widget
          wpixy:wpixy,$             ;y pixel scale text widget
          wfine:wfine,$             ;fine sampling factor text
          wexptime:wexptime,$       ;exposure time (in seconds) widget
          wunits:wunits,$           ;units combobox
          wshot:wshot,$             ;shotnoise radio button
          wdisptype:wdisptype,$     ;display type pulldown box
          wgftype:wgftype,$         ;galfit type pulldown box
          wclean:wclean,$           ;erase galfit files when finished (Y/N)
          wsilent:wsilent,$         ;suppress galfit to terminal (Y/N)
          wdisp:wdisp,$             ;run display GUI when finished
          wgalfit:wgalfit,$         ;the GalFit button
          info:info,$               ;the info about this package
          wimage:wimage,$           ;images menu widgets
          wiraf:wiraf,$             ;IRAF subGUI base widget IDS
          images:images,$           ;names of images
          xy:[0L,0L],$              ;last (x,y) pair clicked
          hist:ptr_new(),$          ;pointer to histogram data
          bins:ptr_new(),$          ;pointer to bins of histogram data
          histminx:0.,$             ;histogram lower bound
          histmaxx:0.,$             ;histogram upper bound
          histbinx:0.,$             ;histogram bin width
          limit:'',$                ;name of limit type
          limits:limits,$           ;
          wlimit:wlimit,$
          lodisp:0.,$               ;min pixel brightness of display
          hidisp:0.,$               ;max pixel brightness of display
          bias:0.33,$               ;default image bias
          cont:0.80,$               ;default image contrast
          img:ptr_new(),$           ;pointer to the displayed image
          ast:ptr_new(),$           ;pointer to the astrometry structure
          magzero:float(magzero),$  ;magnitude zeropoint
          bitmapdir:bitmapdir,$     ;directory for bitmaps
          helpdir:helpdir,$         ;directory for help files
          backcolor:backcolor,$     ;color of background (white by default)
          button:0b,$               ;Which mouse button is clicked.
          fitsect:0b,$              ;is a fitting section defined?
          nrow:nrow,$               ;number of rows in constraints table
          sky:{ave:0.0,sig:0.0},$   ;global sky props (for quick-look photo.)
          zoomstate:1.0,$           ;current zoom state
          zoomfactor:2.,$           ;current zoom factor
          rotating:0b,$             ;rotating state
          draw_time:0.,$            ;time to redraw
          click_time:systime(/sec),$ ;time for double-clicking
          usefile:file,$             ;full name to the files which are used
          setfile:file,$             ;full name to the files as set
          errors:errors,$            ;the default error state info
          dimen:dimen,$              ;the size of the GUI
          savefile:savefile,$        ;default name of save file
          prefs:prefs}               ;the preferences
   
   state=ptr_new(state,/no_copy)     ;convert that stuff to a pointer
   widget_control,base,set_uvalue=state ;save it to the base
   update_contab,state

   ;define a variable
   defsysv,'!igalfit_base',base

   ;set the initial value of the viewport
   ;viewport,{ID:wdraw,TOP:base,HANDLER:base,TYPE:3,X:0,Y:0}
endelse


;if images were given, set that stuff now:
if keyword_set(SCIFILE) then begin
   if file_exist(scifile) then begin
      event={ID:base,TOP:base,HANDLER:base,TYPE:0}
      t=loadfits(event,scifile,'Science',/sci,/disp)
      zoom_image,state,zoom0,/zoomto

   endif else begin
      t=dialog_message('SCIFILE does not exist.',/error,/center)
   endelse
endif
if keyword_set(UNCFILE) then begin
   if file_exist(uncfile) then begin
      event={ID:base,TOP:base,HANDLER:base,TYPE:0}
      t=loadfits(event,uncfile,'Uncertainty',/unc)
   endif else begin
      t=dialog_message('UNCFILE does not exist.',/error,/center)
   endelse
endif
if keyword_set(PSFFILE) then begin
   if file_exist(psffile) then begin
      event={ID:base,TOP:base,HANDLER:base,TYPE:0}
      t=loadfits(event,psffile,'PSF',/psf)
   endif else begin
      t=dialog_message('PSFFILE does not exist.',/error,/center)
   endelse
endif

;open any subGUIs






;load the regions?
if keyword_set(REGFILE) then reg2roi,state,file=regfile

;load settings?
if keyword_set(LOADSETTINGS) then $
   if file_exist(loadsettings) then loadset,loadsettings,state,base


;send to the event-handler
xmanager,'igalfit',base,/no_block,cleanup='igalfit_clean'

end
