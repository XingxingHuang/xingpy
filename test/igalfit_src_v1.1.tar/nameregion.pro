function nameregion,state

;get the names of existing regions
oROIs=state.oROIModel->get(/all,count=nreg)
if nreg gt 0 then begin
   names=strarr(nreg)
   for i=0,nreg-1 do begin
      oROIs(i)->getproperty,name=name
      names(i)=name
   endfor
endif


thisname='Region '+strcompress(string(nreg+1,f='(I7)'),/rem)


return,thisname

end
