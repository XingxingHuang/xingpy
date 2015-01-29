function cutstamp,img,x,y,rad,DEFVAL=defval,$
                  I0=i0,I1=i1,J0=j0,J1=j1,$
                  II0=ii0,II1=ii1,JJ0=jj0,JJ1=jj1

if not keyword_set(DEFVAL) then defval=!values.f_nan

;get size of image
sz=size(img,/dim)

;check if it's a good x,y pair
if x gt sz(0)-1 or x lt 0 or y gt sz(1)-1 or y lt 0 then return,-1


;get coordinates in big image
i0=round(x)-rad & i1=round(x)+rad-1
j0=round(y)-rad & j1=round(y)+rad-1

;get coordinates in stamp 
ii0=(i0 lt 0)?abs(i0):0
jj0=(j0 lt 0)?abs(j0):0
ii1=(i1 gt (sz(0)-1))?(2*rad-1-(i1-(sz(0)-1))):(2*rad-1)
jj1=(j1 gt (sz(1)-1))?(2*rad-1-(j1-(sz(1)-1))):(2*rad-1)

;restrict the coordinates in the big image
i0=i0>0 & i1=i1<(sz(0)-1)
j0=j0>0 & j1=j1<(sz(1)-1)

;make stamp
stamp=replicate(defval,2*rad,2*rad)

;populate the stamp
stamp(ii0:ii1,jj0:jj1)=img(i0:i1,j0:j1)

return,stamp
end
