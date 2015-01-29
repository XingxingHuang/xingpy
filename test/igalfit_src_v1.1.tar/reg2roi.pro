pro reg2roi,state,FILE=file

;do some quick error checking
if ~ptr_valid((*state).img) then begin
   ans=dialog_message(['There is no image loaded!','Are you sure you want '+$
                     'to load regions?'],/question,/center,$
                    title='Load Region File')
   if ans eq 'No' then return
endif


;get the file
if not keyword_set(FILE) then begin
   file=strlowcase((*state).info.title)+'.reg'
   file=dialog_pickfile(file=file,title='Read Region File',filter=['*.reg'])
   if file eq '' then return    ;must have hit 'CANCEL'
endif else begin
   f=file_search(file,count=count)
   case count of
      0: begin
         t=dialog_message('The region file does not exist',$
                          title='Load Region File'/center,/error)
         return
      end
      1: 
      else: begin
         t=dialog_message(['Multiple region files?','I am confused?'],$
                          title='Load Region File',/center,/info)
         return
      end
   endcase
endelse

;shapes we'll test for:
shapes=['circle','box','ellipse'] 
nshapes=n_elements(shapes)

;linestyle of ds9-style catalog:
line=1                          ;1-dotted

nreg=0L                         ;start a counter
openr,lun,file,/get_lun         ;open a file
while not eof(lun) do begin

   ;read one line of data
   data=''
   readf,lun,data

   for j=0,nshapes-1 do begin

      ;test for certain supported shapes
      s=strsplit(data,shapes(j),/ext,/regex,/preserve_null,count=nn)

      if nn eq 2 then begin
         ;ok, this is the shape we're working with
         
         ;get the color
         c=strsplit(data,'color=',/regex,/ext,/preserve_null,count=nn)
         color=(nn eq 1)?'green':(strsplit(c(nn-1),' ',/ext))(0)

         ;now get the data
         ll=strpos(data,'(')
         rr=strpos(data,')')
         vals=float(strsplit(strmid(data,ll+1,rr-ll-1),',',/ext))

         case shapes(j) of
            'ellipse': begin
               ;define the morphology on the color
               case color of
                  'green': type='Sersic'
                  'red'  : type='DeVauc'
                  'blue' : type='ExpDisk'
                  'skyblue' : type='Nuker'
                  'cyan': type='Edge-on Disk'
                  'khaki': type='Ferrer'
                  'seagreen': type='King'
                  'orange': type='Gaussian'
                  'maroon': type='Moffat'
                  'black': type='Ellipse'
                  else: goto,badregion
               endcase

               ;make the region
               prop=define_region(type,color,line=line)

               ;record the properties
               prop.x=vals(0)
               prop.y=vals(1)
               prop.a=vals(2)
               prop.b=vals(3)
               prop.t=vals(4)
            end
            'circle': begin
               ;sort out the morphology based on the color
               case color of
                  'magenta': type='Empirical'
                  'black': type='Circle'
                  else: goto,badregion
               endcase

               ;make the region
               prop=define_region(type,color,line=line)

               ;record the properties
               prop.x=vals(0)
               prop.y=vals(1)
               prop.r=vals(2)                     
            end
            'box': begin
               ;sort out based on color
               case color of
                  'black': type='Rectangle'
                  'yellow': type='Fit Section'
                  else: goto,badregion
               endcase
               
               ;make the region
               prop=define_region(type,color,line=line)

               ;record the properties
               prop.x=vals(0)
               prop.y=vals(1)
               prop.dx=vals(2)
               prop.dy=vals(3)
               prop.t=vals(4)
            end
         endcase
         make_roi,prop,xx,yy,zz
         
         ;add it to the ROIs
         oROI=obj_new('IDLgrROI',color=color,style=2,$
                      name=nameregion(*state),uval=prop,$
                      line=prop.linestyle,thick=prop.thick)
         oROI->AppendData,xx,yy,zz
         (*state).oROIModel->Add,oROI
         (*state).oROIGroup->Add,oROI
         setroi,state,oROI,/update,/setlist,/reset

         ++nreg                 ;update the counter
      endif
   endfor
   badregion:
endwhile
close,lun & free_lun,lun        ;close the file

if nreg eq 0 then begin
   ;display a warning message if we loaded no regions
   t=dialog_message(['The region file ',file,+$
                     'does not contain any valid regions.'],/center,$
                    title='No Regions')
endif else begin
   ;only redraw if we loaded some regions
   (*state).oWindow->Draw,(*state).oView
endelse


end
