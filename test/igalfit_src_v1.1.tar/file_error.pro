function file_error,file,BLANK=blank
if keyword_set(BLANK) then begin
   t=dialog_message(['The '+file+' is just a blank character!',$
                     'Unable to proceed.'],/error,/center,$
                    title='Blank File')
endif else begin
   t=dialog_message(['The '+file+' is not found!',$
                     'Unable to proceed.'],/error,/center,$
                   title='File Not Found')
endelse
return,0b
end
