pro display_image,pstate

a=1000.    ;some number from ds9.  Will add changeability in future
ncol=256   ;number of colors. Lot's of coding to allow this to vary!!

;build the colormap
cmap=0>(((indgen(ncol)-(ncol-1)*(*pstate).bias)*(*pstate).cont)+$
     0.5*(ncol-1))<(ncol-1)

;note the copious use of "temporary" hopefully that'll gain us some speed!
case (*pstate).scale of
   'Linear': cmap=byte(ncol-1)-bytscl(temporary(cmap))
   'Log': cmap=byte(ncol-1)-bytscl(alog10(a*temporary(cmap)+1)/alog10(a))
;   'HistEq': cmap=
   else: begin
      ;Do some error checking for an unsupported scaling
      cmap=byte(ncol-1)-bytscl(temporary(cmap))
      t=dialog_message(['The scale, '+(*pstate).scale+', is unsupported.',$
                        'Defaulting to Linear.'],/error,/center)
;      (*pstate).scale='Linear'   ;set to default

      ;set all buttons to non-checked
      n=n_elements((*pstate).scales)
      for i=0,n-1 do widget_control,(*pstate).wscale(i),set_button=0b

      ;check the default button
      g=(where((*pstate).scales eq (*pstate).scale))(0)
      widget_control,(*pstate).wscale(g),set_button=1b
   end
endcase

;reset the data
(*pstate).oImage->SetProperty,data=cmap(bytscl(*(*pstate).img,$
                                               (*pstate).lodisp,$
                                               (*pstate).hidisp))

;redraw the data
(*pstate).oWindow->Draw,(*pstate).oView         
                  
end
