pro roi2reg,state

;get the widget information
;widget_control,event.top,get_uvalue=state

;error check
nreg=(*state).oROIModel->Count()
if nreg eq 0 then begin
   t=dialog_message('There are no regions to save.',/center,/info,$
                   title='Save Region Error')
   return
endif

;get the file
file=strlowcase((*state).info.title)+'.reg'
outfile=dialog_pickfile(file=file,/write,/overwrite,title='Save Region File')
if outfile eq '' then return    ;must have hit 'CANCEL'


;set up some color info
define_rgb,colors

;physical and ds9
hdr='global dashlist=8 3 width=1 font="helvetica 10 normal" '+$
    'select=1 highlite=1 dash=0 edit=1 move=1 delete=1 include=1 source=1'
coord='image'



;open file
openw,lun,outfile,/get_lun,error=error
if error ne 0 then begin
   ;error checking:
   t=writefile_error('Region File')
   return
endif

;print the header info into the file
printf,lun,'# Region file made by '+(*state).info.title+' on '+systime()+'.'
printf,lun,'# Filename: '+(*state).setfile.sci
printf,lun,hdr                      ;put on the header
printf,lun,coord                    ;coordinate system

;do each region now:
for i=0,nreg-1 do begin

   ;get the data from the ROIs
   oROI=(*state).oROIModel->Get(pos=i)
   oROI->GetProperty,uvalue=prop,color=color

   ;get the colorname
   g=(where(colors.rgb(0) eq color(0) and $
            colors.rgb(1) eq color(1) and $
            colors.rgb(2) eq color(2)))(0)
   colorname=colors(g).name

   ;get the data for each shape
   case prop.shape of
      'ellipse': begin
         ;make data:
         x=strcompress(string(prop.x,f='(F9.3)'),/rem)
         y=strcompress(string(prop.y,f='(F9.3)'),/rem)
         a=strcompress(string(prop.a,f='(F9.3)'),/rem)
         b=strcompress(string(prop.b,f='(F9.3)'),/rem)
         t=strcompress(string(prop.t,f='(F7.3)'),/rem)
         data=strjoin([x,y,a,b,t],',')

         ;set the shape
         shape=prop.shape
      end
      'box': begin
         ;make data:
         x=strcompress(string(prop.x,f='(F9.3)'),/rem)
         y=strcompress(string(prop.y,f='(F9.3)'),/rem)
         dx=strcompress(string(prop.dx,f='(F9.3)'),/rem)
         dy=strcompress(string(prop.dy,f='(F9.3)'),/rem)
         t=strcompress(string(prop.t,f='(F7.3)'),/rem)
         data=strjoin([x,y,dx,dy,t],',')

         ;set the shape
         shape='-'+prop.shape
      end
      'circle': begin
         ;make data:
         x=strcompress(string(prop.x,f='(F9.3)'),/rem)
         y=strcompress(string(prop.y,f='(F9.3)'),/rem)
         r=strcompress(string(prop.r,f='(F9.3)'),/rem)
         data=strjoin([x,y,r],',')

         ;set the shape
         shape=prop.shape
      end
      else: begin
         t=dialog_message('An unknown shape was encountered in ROI2DS9.PRO',$
                          /center,/error)
      end
   endcase

   ;write to the file
   printf,lun,shape+'('+data+') # color='+colorname
endfor

close,lun & free_lun,lun    ;close file


end
