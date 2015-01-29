function getregnames,state,NREG=nreg
oROIs=(*state).oROIModel->Get(/all,count=nreg)
if nreg gt 0 then begin
   names=strarr(nreg)
   for i=0,nreg-1 do begin
      oROIs(i)->GetProperty,name=thisname
      names(i)=thisname
   endfor      
endif else names=['']
return,names
end
