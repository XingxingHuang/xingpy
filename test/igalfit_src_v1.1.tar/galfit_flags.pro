function galfit_flags,flags,UNRECOGNIZED=unrecognized

;As of GALFIT 3.0.4, these are the possible output flags
gf=[{f:'1',m:'number of iterations reached.  Quit out early.'},$
    {f:'2',m:'Suspected numerical convergence error in current solution.'},$
    {f:'A-1',m:'No input data image found. Creating model only.'},$
    {f:'A-2',m:'PSF image not found.  No convolution performed.'},$
    {f:'A-3',m:'No CCD diffusion kernel found or applied.'},$
    {f:'A-4',m:'No bad pixel mask image found.'},$
    {f:'A-5',m:'No sigma image found.'},$
    {f:'A-6',m:'No constraint file found.'},$
    {f:'C-1',m:'Error parsing the constraint file.'},$
    {f:'C-2',m:'Trying to constrain a parameter that is being held fixed.'},$
    {f:'H-1',m:'Exposure time header keyword is missing.  '+$
     'Default to 1 second.'},$
    {f:'H-2',m:'Exposure time is zero seconds.  Default to 1 second.'},$
    {f:'H-3',m:'GAIN header information is missing.'},$
    {f:'H-4',m:'NCOMBINE header information is missing.'},$
    {f:'I-1',m:'Convolution PSF exceeds the convolution box.'},$
    {f:'I-2',m:'Fitting box exceeds image boundary.'},$
    {f:'I-3',m:'Some pixels have infinite ADUs; set to 0.'},$
    {f:'I-4',m:'Sigma image has zero or negative pixels; set to 1e10.'},$
    {f:'I-5',m:'Pixel mask is not same size as data image.'}]



nflag=n_elements(flags)
msgs=replicate('Unrecognized GALFIT flag.',nflag)
order=intarr(nflag)
unrecognized=0L
for i=0,nflag-1 do begin
   g=(where(gf.f eq flags(i),nn))(0)
   if nn ne 0 then begin
      msgs(i)=gf(g).m 
      order(i)=g
   endif else begin
      unrecogonized++
      order(i)=n_elements(gf)+1
   endelse
endfor
order=sort(order)
msgs=msgs(order)
flags=flags(order)


return,msgs
end
