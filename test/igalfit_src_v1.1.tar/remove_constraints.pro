pro remove_constraints,state,constraints
nrem=n_elements(constraints)


names=getregnames(state)

for i=0,nrem-1 do begin
   if constraints(i) ne '' then begin
      cc=strsplit(constraints(i),' ',/ext)
      name=cc(0)+' '+cc(1)
      pos=(where(name eq names,n))(0)
      if n ne 0 then begin
         oROI=(*state).oROIModel->Get(pos=pos)
         if obj_valid(oROI) then begin
            oROI->GetProperty,uval=prop
         
            g=(where(prop.cons.param eq cc(2)))(0)
            prop.cons(g).wid=-1L
            prop.cons(g).set=0b
            prop.cons(g).type='relative'
            prop.cons(g).lo=0.0
            prop.cons(g).hi=0.0
            
            oROI->SetProperty,uval=prop    
         endif
      endif

;      cc=strsplit(cons(0),'(-|/|_)',/regex,/extr,count=n)
;      if n eq 1 and isnumber(cc(0)) eq 1 then begin
;         ;basic constraint
;         oROI=(*state).oROIModel->Get(pos=(fix(cc(0))-1)>0)
;         if obj_valid(oROI) then begin
;            oROI->GetProperty,uval=prop
;         
;            g=(where(prop.cons.param eq cons(1)))(0)
;            prop.cons(g).wid=-1L
;            prop.cons(g).set=0b
;            prop.cons(g).type='relative'
;            prop.cons(g).lo=0.0
;            prop.cons(g).hi=0.0
;            
;            oROI->SetProperty,uval=prop    
;         endif
;      endif else begin
;         ;linking constraint
;         
;      endelse
   endif

endfor

constraints=''

end
