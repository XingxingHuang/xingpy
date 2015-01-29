pro loadhelp,state,wid
  widget_control,wid,/set_tree_visible,/set_tree_select

  file=state.helpdir+widget_info(wid,/uname)+'.help'
  if file_exist(file) then begin
     readfmt,file,'(A1000)',data,/silent
     widget_control,state.wtext,set_value=strtrim(data)
  endif else begin
     widget_control,wid,get_value=tree
     t=dialog_message('There is no help file for '+tree+'.',/err,/cent)
  endelse  
end

pro help_gui_event,event
widget_control,event.id,get_uval=uval
case uval of
   'HELP': begin
      widget_control,event.top,get_uvalue=state
      loadhelp,state,event.id
   end
   'CLOSE': widget_control,event.top,/destroy
   else:break
endcase
end

pro help_gui,REDISPLAY=redisplay,HELPDIR=helpdir,LOAD=load,$
             BASE=base,GROUP=group

if not keyword_set(HELPDIR) then begin
   findpro,current_routine(),dir=dir,/noprint
   helpdir=dir(0)+'help/'
endif

;NOTES: Use the widget_tree.pro to give the User a list of help
;topics.  All help widgets have the same UVALUE (so we execute the
;same piece of code every time), but have different UNAME (which
;encodes the name of the help file).  The file loader (loadhelp.pro)
;is included here, and will be used if help_gui.pro is already instantiated.


if not keyword_set(REDISPLAY) then begin
   base=widget_base(title='Help Files',/col,mbar=mbar,GROUP=group)

   filemenu=widget_button(mbar,value='File',/menu)
   close=widget_button(filemenu,value='Close',uval='CLOSE')
   
   top=widget_base(base,/row)
   lhs=widget_base(top,/col)
   wtree=widget_tree(lhs,/mask,xsize=200,ysize=300)
   wroot=widget_tree(wtree,value='iGalFit',/folder,/expanded,uval='HELP',$
                     uname='igalfit')
   
   wcont=widget_tree(wroot,value='Controls',uval='HELP',$
                     uname='igalfit_controls')
   wpref=widget_tree(wroot,value='Preferences',uval='HELP',$
                     uname='prefs')
   wgf=widget_tree(wroot,value='GalFit',/folder,uval='HELP',uname='galfit')
   wgfset=widget_tree(wgf,value='Settings',uval='HELP',uname='galfit_settings')
   wgfres=widget_tree(wgf,value='Results',uval='HELP',uname='galfit_results')
   wgfcon=widget_tree(wgf,value='Constraints',uval='HELP',uname='galfit_const')
   
   
   wsex=widget_tree(wroot,value='SExtractor (SEx)',/folder,uval='HELP',$
                    uname='sex')
   wsexmain=widget_tree(wsex,value='Running SEx',uval='HELP',uname='runsex')
   wsexpars=widget_tree(wsex,value='SEx Parameters',uval='HELP',uname='sexpars')
   wsexconv=widget_tree(wsex,value='Convolution',uval='HELP',uname='sexconv')
   
   
   wadd=widget_tree(wroot,value='Additional Tools',/folder,uvalue='HELP',$
                    uname='addtools')
   wreginfo=widget_tree(wadd,value='Region Info',uval='HELP',uname='reginfo')
   wstretch=widget_tree(wadd,value='Stretch Image',uval='HELP',$
                        uname='stretchimage')
   wpixhist=widget_tree(wadd,value='Pixel Histogram',uval='HELP',$
                        uname='pixhist')
   wpixtab=widget_tree(wadd,value='Pixel Table',uval='HELP',uname='pixtab')
   weditfeed=widget_tree(wadd,value='Edit FeedMe',uval='HELP',uname='editfeed')
   
   
   wimexam=widget_tree(wroot,value='ImExamine Tasks',/folder,uval='HELP',$
                       uname='imexamine')
   wimexamstat=widget_tree(wimexam,value='Statistics',uval='HELP',$
                           uname='imstat')
   wimexamrad=widget_tree(wimexam,value='Radial Profile',uval='HELP',$
                          uname='radprof')
   wimexamline=widget_tree(wimexam,value='Line Plots',uval='HELP',$
                           uname='lineplot')
   wimexamcont=widget_tree(wimexam,value='Contour Plot',uval='HELP',$
                           uname='contplot')
   wimexamhist=widget_tree(wimexam,value='Histogram',uval='HELP',$
                           uname='histplot')
   
   
   rhs=widget_base(top,/col)
   wtext=widget_text(rhs,xsize=80,ysize=20,/scroll)
   
   
   state={wtree:wtree,$
          wroot:wroot,$
          wcont:wcont,$
          wpref:wpref,$
          wgf:wgf,$
          wgfset:wgfset,$
          wgfres:wgfres,$
          wgfcon:wgfcon,$
          wsex:wsex,$
          wsexmain:wsexmain,$
          wsexpars:wsexpars,$
          wsexconv:wsexconv,$
          wadd:wadd,$
          wreginfo:wreginfo,$
          wstretch:wstretch,$
          wpixhist:wpixhist,$
          wpixtab:wpixtab,$
          weditfeed:weditfeed,$
          wimexam:wimexam,$
          wimexamstat:wimexamstat,$
          wimexamrad:wimexamrad,$
          wimexamline:wimexamline,$
          wimexamcont:wimexamcont,$
          wimexamhist:wimexamhist,$
          wtext:wtext,$
          helpdir:helpdir}
   
   ;okay, this is clunky, I admit. But it is very hard to do this 
   ;right, and will require lots of new programming!
   defsysv,'!igalfit_help',base

   ;store the data, realize the GUI, and pass of to xmanager.
   widget_control,base,set_uval=state
   widget_control,base,/realize
   xmanager,'help_gui',base,/no_block
endif else begin
   ;ok, so the GUI exists, now just redefine!
   widget_control,!igalfit_help,get_uval=state
   widget_control,!igalfit_help,/show
endelse

;load the help
if keyword_set(LOAD) then begin
   for i=0,n_tags(state)-1 do begin ;check all the keys
      if size(state.(i),/type) eq 3 then begin
         if load eq widget_info(state.(i),/uname) then wid=state.(i)
      endif
   endfor
   loadhelp,state,wid                         ;load the help menu
endif else loadhelp,state,wroot               ;load the default help






end
