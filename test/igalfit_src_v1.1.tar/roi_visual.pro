function roi_visual,COLOR=color

;build a model
oModel=obj_new('IDLgrModel',/hide)

;fill it with transparency:
white=bytarr(4,2,2)
white(0:2,*,*)=255b
white(3,*,*)=0b
oTranspImage=obj_new('IDLgrImage',white,interleave=0b,/hide)
oModel->Add,oTranspImage

;little polygons around the regions
xx=[-1,1,1,-1]*2.0
yy=[-1,-1,1,1]*2.0
oScaleBox=obj_new('IDLgrPolygon',xx,yy,name='SCALE_BOX', color=color)

;this is a line around the handle
;oScaleBoxOutline = OBJ_NEW('IDLgrPolygon', xx,yy,$
;                           style=1, name='SCALE_BOX_OUTLINE', COLOR=color)


;corners of the handles
;lower-left
oScaleLL = OBJ_NEW('IDLgrModel',/select_targ, name='LL')
oScaleLL->Add, oScaleBox
;oScaleLL->Add, oScaleBoxOutline
oModel->Add, oScaleLL

;lower-right
oScaleLR = OBJ_NEW('IDLgrModel',/select_targ,name='LR')
oScaleLR->Add, oScaleBox,/alias
;oScaleLR->Add, oScaleBoxOutline,/alias
oModel->Add, oScaleLR

;upper-right
oScaleUR = OBJ_NEW('IDLgrModel',/select_targ,name='UR')
oScaleUR->Add, oScaleBox,/alias
;oScaleUR->Add, oScaleBoxOutline,/alias
oModel->Add, oScaleUR

;upper-left
oScaleUL = OBJ_NEW('IDLgrModel',/select_targ,name='UL')
oScaleUL->Add, oScaleBox,/alias
;oScaleUL->Add, oScaleBoxOutline,/alias
oModel->Add, oScaleUL

;translation
oTransModel = OBJ_NEW('IDLgrModel',/select_targ,name='TRANSLATE')
oTransBoxOutline = OBJ_NEW('IDLgrPolygon', style=1, linestyl=2,$
                           name='TRANSLATE_BOX_OUTLINE',  color=color)
;oTransModel->Add, oTransBoxOutline
oModel->Add, oTransModel

;save the data for use later
state={oScaleLL: oScaleLL,$
       oScaleLR: oScaleLR,$
       oScaleUL: oScaleUL,$
       oScaleUR: oScaleUR,$
       oScaleBox: oScaleBox,$
;       oScaleBoxOutline: oScaleBoxOutline, $
       oTransModel: oTransModel, $
       oTransBoxOutline:oTransBoxOutline}
oModel->SetProperty,uvalue=ptr_new(state,/no_copy)

return,oModel
end
