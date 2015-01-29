function morph_button,morph
;Experimental code.....

xsize=120
ysize=13
x0=0.05 & y0=0.2
t=define_region(morph,rgb)

grey=192b
window,0,/pixmap,xsize=xsize*5,ysize=ysize*5

polyfill,[0,1,1,0],[0,0,1,1],/normal,color=convert_rgb(replicate(grey,3))

device,decomposed=1

xyouts,x0,y0,morph,/normal,charsize=6,charthick=6,$
       color=0,align=0,width=width
plots,[x0+width+0.1,1-x0],[0.45,0.45],thick=10,/normal,$
      color=convert_rgb(rgb)
im=tvrd(true=3)
device,decomposed=1
wdelete,0
im(*,0,*)=grey
out=bytarr(xsize,ysize,3)
out(*,*,0)=congrid(im(*,*,0),xsize,ysize)
out(*,*,1)=congrid(im(*,*,1),xsize,ysize)
out(*,*,2)=congrid(im(*,*,2),xsize,ysize)


return,out
end

function morph_pdmenu,base,morphinfo,morphstate,UVALUE=uvalue,DEFAULT=default
if not keyword_set(UVALUE) then uvalue='MORPH'
xsize=80

;initial morphology state
morphstate='Sersic'
tooltip='Sersic Profile'
if keyword_set(DEFAULT) then return,-1L





;main widget button
wmorph=widget_button(base,xsize=xsize,value=morphstate,$
                         /align_left,/menu,tooltip=tooltip)

;the extended source buttons
wext=widget_button(wmorph,value='Extended Source',/menu)
wser=widget_button(wext,value='Sersic',uvalue=uvalue)
wexp=widget_button(wext,value='ExpDisk',uvalue=uvalue)
wdev=widget_button(wext,value='DeVauc',uvalue=uvalue)
wnuk=widget_button(wext,value='Nuker',uvalue=uvalue)
wedg=widget_button(wext,value='Edge-on Disk',uvalue=uvalue)
wfer=widget_button(wext,value='Ferrer',uvalue=uvalue)
wkin=widget_button(wext,value='King',uvalue=uvalue)

;the point source buttons
wpsf=widget_button(wmorph,value='Point Source',/menu)
wemp=widget_button(wpsf,value='Empirical',uvalue=uvalue)
wgau=widget_button(wpsf,value='Gaussian',uvalue=uvalue)
wmof=widget_button(wpsf,value='Moffat',uvalue=uvalue)

;the mask buttons
wmask=widget_button(wmorph,value='Masks',/menu)
wexcl=widget_button(wmask,value='Exclude',/menu)
wrect=widget_button(wexcl,value='Rectangle',uvalue=uvalue)
wcirc=widget_button(wexcl,value='Circle',uvalue=uvalue)
welli=widget_button(wexcl,value='Ellipse',uvalue=uvalue)
wfits=widget_button(wmask,value='Fit Section',uvalue=uvalue)

;save the morphology info
morph={morph,type:'',wid:0L,tip:''} ;dummy variable
morphinfo=[{morph,'Sersic',wser,tooltip},                      $
           {morph,'ExpDisk',wexp,'Exponential Profile'},       $
           {morph,'DeVauc',wdev,'de Vaucouleurs Profile'},     $
           {morph,'Nuker',wnuk,'Nuker Profile'},               $
           {morph,'Edge-on Disk',wedg,'Edge-on Disk Profile'}, $
           {morph,'Ferrer',wfer,'Ferrer Profile'},             $
           {morph,'King',wkin,'King Profile'},                 $
           {morph,'Empirical',wemp,'Empirical PSF'},           $
           {morph,'Gaussian',wgau,'Gaussian Profile'},         $
           {morph,'Moffat',wmof,'Moffat Profile'},             $
           {morph,'Rectangle',wrect,'Rectangular Mask'},       $
           {morph,'Circle',wcirc,'Circular Mask'},             $
           {morph,'Ellipse',welli,'Elliptical Mask'},          $
           {morph,'Fit Section',wfits,'Allow Fitting Region'}]




return,wmorph

end
