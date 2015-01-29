pro update_display,state,x,y
;procedure to update the (x,y), (r,d), and pix display



;get the size of the image
(*state).oImage->GetProperty,dimensions=dim

dim=fix(dim)
x=fix(x)
y=fix(y)
if x ge 0 and x le dim(0)-1 and y ge 0 and y le dim(1)-1 then begin
   ;if the mouse is in the image:

   ;pixel value
   p=(*(*state).img)(x,y)  

   ;update the (x,y) and pixel setting:
   widget_control,(*state).wx,set_value=strcompress(string(x,f='(I5)'),/rem)
   widget_control,(*state).wy,set_value=strcompress(string(y,f='(I5)'),/rem)
   widget_control,(*state).wp,set_value=strcompress(string(p,f='(E+10.3)'),/rem)

   ;if a valid astrometry structure is loaded, then let's use it
   if ptr_valid((*state).ast) then begin
      ;convert (x,y) to (r,d)
      xy2ad,x,y,*(*state).ast,a,d
      a=sixty(a/15.)            ;put into Segsidecimal
      sign=(d lt 0)?'-':'+'
      d=sixty(abs(d))

      ;update the displays
      widget_control,(*state).wr,set_value=' '+string(a(0),f='(I02)')+':'+$
                     string(a(1),f='(I02)')+':'+string(a(2),f='(F05.2)')

      widget_control,(*state).wd,set_value=sign+string(d(0),f='(I02)')+':'+$
                     string(d(1),f='(I02)')+':'+string(d(2),f='(F06.3)')
   endif
   
   ;if the pixel table is open, let's populate it
   if xregistered('pixtab',/noshow) then begin
      widget_control,(*state).wpixtabbase,get_uval=sstate

      geom=widget_info((*sstate).wtable,/geom)
      nx=fix(geom.xsize) & ny=fix(geom.ysize)

      i0=x-(nx-1)/2 & i1=x+(nx-1)/2
      j0=y-(ny-1)/2 & j1=y+(ny-1)/2


      ii0=(i0 lt 0)?abs(i0):0
      jj0=(j0 lt 0)?abs(j0):0
      ii1=(i1 gt (dim(0)-1))?(nx-1-(i1-(dim(0)-1))):(nx-1)
      jj1=(j1 gt (dim(1)-1))?(ny-1-(j1-(dim(1)-1))):(ny-1)
      

      i0=i0>0 & i1=i1<(dim(0)-1)
      j0=j0>0 & j1=j1<(dim(1)-1)


      disp=strarr(nx,ny)
      disp(ii0:ii1,jj0:jj1)=string((*(*state).img)(i0:i1,j0:j1),f='(E+10.3)')

      xlab=strcompress(string(indgen(nx)-(nx/2)+fix(x),f='(I5)'),/rem)
      ylab=strcompress(string(indgen(ny)-(ny/2)+fix(y),f='(I5)'),/rem)


      widget_control,(*sstate).wtable,set_value=rotate(disp,7),$
                     column_labels=xlab,row_label=reverse(ylab),$
                     set_table_select=([nx,ny,nx,ny]-1)/2,$
                     set_text_select=([nx,ny]-1)/2
   endif

endif


end
