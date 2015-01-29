function current_routine,HELP=help,UPPERCASE=uppercase
if keyword_set(HELP) then message,'This returns the name of working routine',/continue

;get the names of the routines
help,calls=t & t=t(1)

;Parse the names
tt=strpos(t,' ')

;change the case
if keyword_set(UPPERCASE) then code=strmid(t,0,tt) else code=strlowcase(strmid(t,0,tt))

;just in case you ran in the "MAIN" as R.E.Ryan so often does
if code eq '$main$' then begin
   tt=strsplit((strsplit(t,' ',/extract))(1),'/',/extract)
   code=(strsplit(tt(n_elements(tt)-1),'.',/extract))(0)
endif


return,code
end

