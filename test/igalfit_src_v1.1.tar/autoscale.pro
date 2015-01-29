pro autoscale,state,LOSIG=losig,HISIG=hisig,SIGMA=sigma
if not keyword_set(LOSIG) then losig=(*state).prefs.losig
if not keyword_set(HISIG) then hisig=(*state).prefs.hisig
if not keyword_set(SIGMA) then sigma=(*state).prefs.sigma

img=(*(*state).img)
g=where(img ne 0. and finite(img),n)
if n le 10 then begin
   t=dialog_message(['Unable to compute autoscale parameters.',$
                     'Too few finite, non-zero pixels!',$
                     'Using min-max.'],/error,/center)
   lo=min(img)
   hi=max(img)
   ave=(hi+lo)/2.
   sig=abs(hi-lo)/sqrt(12.)
endif else begin
   resistant_mean,img(g),sigma,ave
   sig=robust_sigma(img(g))
   lo=ave-losig*sig
   hi=ave+hisig*sig
endelse

(*state).lodisp=lo
(*state).hidisp=hi
(*state).sky.ave=ave
(*state).sky.sig=sig

end
