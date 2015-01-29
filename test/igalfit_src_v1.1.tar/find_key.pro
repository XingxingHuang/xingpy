function find_key,hdr,testkeys,defvalue,SILENT=silent
value=defvalue

ntest=n_elements(testkeys)

;set initial conditions of the while statement:
i=0l
while value ne defvalue and i lt ntest-1 do begin
   t=sxpar(hdr,testkeys(i),count=n)
   case n of
      0:
      1:begin 
         if not keyword_set(SILENT) then message,$
            'Found keyword with '+testkeys(i),/continue

      end
      else: begin
         if not keyword_set(SILENT) then message,$
            'Multiple instances of the keyword, '+testkeys(i)+$
         '.  Using the first.',/continue
         value=t(0)
      end
   endcase
   i=i+1
endwhile


return,value
end
