function make_cons,param
  n=n_elements(param)
  cons=replicate({param:'',wid:-1L,set:0b,type:'relative',lo:0.,hi:0.},n)
  cons.param=param
return,cons
end
function make_fit,param
  cmd=strjoin("'"+param+"','1'",',')
  t=execute('fit=create_struct('+cmd+')')
return,fit
end

function define_region,type,rgb,MORPHS=morphs,$
                       THICK=thick,LINESTYLE=linestyle
                       

;this function returns a structure of region properties

;set some defaults
if not keyword_set(THICK) then thick=2.0       ;thickness of region
if not keyword_set(LINESTYLE) then linestyle=0 ;linestyle of region


;possible colors
define_rgb,colors

;allowable morphologies
if keyword_set(MORPHS) then return,['Sersic','Nuker','DeVauc','ExpDisk',$
                                    'EdgeDisk','Moffat','Ferrer','Gaussian',$
                                    'King','Empirical','Rectangular Mask',$
                                    'FitSect']


;for each type
case type of
   ;------------------RESOLVED MODELS----------------------
   'Sersic': begin
      param=['x','y','mag','re','n','pa','q']
      color='green'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'Nuker': begin
      param=['x','y','mub','rb','alpha','beta','gamma','pa','q']
      color='skyblue'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'DeVauc': begin
      param=['x','y','mag','re','pa','q']
      color='red'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'ExpDisk': begin
      param=['x','y','mag','re','pa','q']
      color='blue'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'Edge-on Disk': begin
      param=['x','y','mu0','hs','rs','pa']
      color='cyan'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'Ferrer': begin
      param=['x','y','mu0','rad','alpha','beta','q','pa']
      color='khaki'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'King': begin
      param=['x','y','mu0','rc','rt','alpha','q','pa']
      color='seagreen'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,$
            canrotate:1b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end


   ;----------------PSF MODELS ---------------------
   'Empirical': begin
      param=['x','y','mag']
      color='magenta'
      data={x:0.0,y:0.0,r:0.0,shape:'circle',type:type,$
            canrotate:0b,thick:thick,linestyle:linestyle,skip:'0',$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'Gaussian': begin
      param=['x','y','mag','fwhm','q','pa']
      color='orange'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,skip:'0',$
            canrotate:1b,thick:thick,linestyle:linestyle,$
            cons:make_cons(param),fit:make_fit(param)}
   end
   'Moffat': begin
      param=['x','y','mag','fwhm','alpha','q','pa']
      color='maroon'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:type,skip:'0',$
            canrotate:1b,thick:thick,linestyle:linestyle,$
            cons:make_cons(param),fit:make_fit(param)}
   end


   ;----------------MASK MODELS----------------------
   'Rectangle': begin
      color='black'
      data={x:0.0,y:0.0,dx:0.0,dy:0.0,t:0.0,shape:'box',type:'Mask',$
           canrotate:1b,thick:thick,linestyle:linestyle}
   end
   'Circle': begin
      color='black'
      data={x:0.0,y:0.0,r:0.0,shape:'circle',type:'Mask',$
           canrotate:0b,thick:thick,linestyle:linestyle}
   end
   'Ellipse': begin
      color='black'
      data={x:0.0,y:0.0,a:0.0,b:0.0,t:0.0,shape:'ellipse',type:'Mask',$
           canrotate:1b,thick:thick,linestyle:linestyle}
   end
   'Fit Section': begin
      color='yellow'
      data={x:0.0,y:0.0,dx:0.0,dy:0.0,t:0.0,shape:'box',type:type,$
           canrotate:0b,thick:thick,linestyle:linestyle}
   end
   else: return,-1    ;nothing recognized?
endcase

colorid=(where(colors.name eq color))(0)

;return the good color
rgb=colors(colorid).rgb


return,data
end
