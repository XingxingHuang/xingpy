pro make_roi,prop,xx,yy,zz,MINPTS=minpts

if not keyword_set(MINPTS) then minpts=16
case prop.shape of
   'ellipse': begin
      pa=prop.t
      cc=cos(pa*!PI/180.)
      ss=sin(pa*!PI/180.)
      
      npts=(4*ceil(prop.a))>minpts
      ang=findgen(npts)*2*!PI/(npts-1)
      cang=cos(ang)
      sang=sin(ang)
      xx=prop.x+cc*prop.a*cang-ss*prop.b*sang
      yy=prop.y+ss*prop.a*cang+cc*prop.b*sang

      
   end
   'circle': begin
      npts=(4*ceil(prop.r))>minpts
      ang=findgen(npts)*2*!PI/(npts-1)
      cang=cos(ang)
      sang=sin(ang)
      xx=prop.x+prop.r*cang
      yy=prop.y+prop.r*sang
   end
   'box': begin
      pa=prop.t
      cc=cos(pa*!PI/180.)
      ss=sin(pa*!PI/180.)
      
      xc=[-1,+1,+1,-1,-1]*prop.dx/2.
      yc=[-1,-1,+1,+1,-1]*prop.dy/2.
      
      xx=prop.x+cc*xc-ss*yc
      yy=prop.y+ss*xc+cc*yc
   end
   else: t=dialog_message('An unsupported shape was encountered!',$
                          /cen,/err,title='Shape Error')
endcase

zz=replicate(0.,n_elements(xx))




end
