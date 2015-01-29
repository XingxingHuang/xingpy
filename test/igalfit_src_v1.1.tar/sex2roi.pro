pro sex2roi,state,cat,DEFMORPH=defmorph

if size(cat,/type) ne 8 then begin
   t=dialog_message(['The SExtractor catalog did not','contain'+$
                     'any valid objects.'],/err,/cent,tit='No SEx Objects')
   return
endif

;set parameters to be resolved
minarea=25
minrad=1.5

;set default morphology
if not keyword_set(DEFMORPH) then defmorph='Sersic'

;check for mandatory keywords
mand=['X_IMAGE','Y_IMAGE','A_IMAGE','B_IMAGE','THETA_IMAGE','ISOAREA_IMAGE']
for i=0,n_elements(mand)-1 do begin
   if not tag_exist(cat,mand(i)) then begin
      t=dialog_message(['The SEx catalog is missing '+mand(i)+'!',$
                        'Cannot create the ROIs'],/error,/center)
      return
   endif
endfor

;SEx starts counting pixels at (1,1), but IDL does (0,0)
cat.x_image-=0.5
cat.y_image-=0.5

;linestyle for SExtractor drawn regions:
line=2                          ;2-dashed

;for each entry in the catalog:
nreg=n_elements(cat)
for i=0,nreg-1 do begin
   morph=defmorph               ;default morphology

   ;do a Star/galaxy/CR split.
   area=cat(i).isoarea_image
   rad=sqrt(!PI*cat(i).a_image*cat(i).b_image)
   if area lt minarea and rad gt minrad then morph='PSF'
   if area lt minarea and rad lt minrad then morph='Mask'

   ;convert angle from SEx:
   pa=cat(i).theta_image
   case strlowcase(morph) of 
      'sersic': begin
         ;define the region
         prop=define_region('Sersic',color,line=line)
         prop.x=cat(i).x_image
         prop.y=cat(i).y_image
         prop.a=cat(i).a_image*3
         prop.b=cat(i).b_image*3
         prop.t=pa

     end
      'psf': begin
          ;define the region
          prop=define_region('Empirical',color,line=line)
          prop.x=cat(i).x_image
          prop.y=cat(i).y_image
          prop.r=cat(i).a_image*3
       end
      'devauc': begin
         ;define the region
         prop=define_region('DeVauc',color,line=line)
         prop.x=cat(i).x_image
         prop.y=cat(i).y_image
         prop.a=cat(i).a_image
         prop.b=cat(i).b_image
         prop.t=pa
      end
      'expdisk': begin
         ;define the region
         prop=define_region('ExpDisk',color,line=line)
         prop.x=cat(i).x_image
         prop.y=cat(i).y_image
         prop.a=cat(i).a_image
         prop.b=cat(i).b_image
         prop.t=pa
      end
      'mask': begin
         masksize=7             ;size to mask an object
         
         prop=define_region('Rectangle',color,line=line)
         prop.x=cat(i).x_image
         prop.y=cat(i).y_image
         prop.dx=masksize
         prop.dy=masksize
         prop.t=0.
      end
      else: begin
         t=dialog_message(['An unknown shape was encountered in SEX2ROI.PRO',$
                           morph+'.'],/center,/error,titl='SEX2ROI')
         return
      end
   endcase
   make_roi,prop,xx,yy,zz

   oROI=obj_new('IDLgrROI',color=color,style=2,$
                name=nameregion(*state),uvalue=prop,$
                line=prop.linestyle,thick=prop.thick)
   oROI->AppendData,xx,yy,zz
   (*state).oROIModel->Add,oROI
   (*state).oROIGroup->Add,oROI
   setroi,state,oROI,/update,/setlist,/reset
endfor

;re-draw
(*state).oWindow->Draw,(*state).oView


end
