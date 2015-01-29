function mkconstraints,state

delim=' '
;open the file for writing
widget_control,(*state).wconfile,get_value=file & file=file(0)
if file eq 'none' then return,1b

openw,lun,file,error=error,/get_lun
if error ne 0 then return,writefile_error('Constraints File')

;get the regions
oROIs=(*state).oROIModel->Get(/all,count=nreg)

cons=['# Constraints file made on '+systime()]
for i=0,nreg-1 do begin
   oROIs(i)->GetProperty,uval=prop
   if tag_exist(prop,'cons') then begin

      g=where(prop.cons.set,nset)
      if nset gt 0 then begin
         lo=strcompress(string(prop.cons(g).lo,f='(F8.3)'),/rem)
         hi=strcompress(string(prop.cons(g).hi,f='(F8.3)'),/rem)
         
         type=replicate(delim,nset)
         gg=where(prop.cons.set and prop.cons.type eq 'absolute')     
         if gg(0) ne -1 then type(gg)=' to '
         
         id=strcompress(string(i+1,f='(I8)'),/rem)
         
         cons=[cons,id+delim+prop.cons(g).param+delim+lo+type+hi]
      endif
   endif
endfor

ncons=n_elements(cons)
if ncons gt 1 then for i=0,ncons-1 do printf,lun,cons(i)
close,lun & free_lun,lun


return,1b
end
