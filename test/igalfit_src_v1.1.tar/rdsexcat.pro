function rdsexcat,file,other,ALLFLOAT=allfloat,SILENT=silent,CONVERT=convert
if n_params() lt 1 then begin
print,'data = rdsexcat(file,[other,/ALLFLOAT,/SILENT,/CONVERT])'
print,'       data will be a structure'
print,'       other will be a structure'
print,'             with tags "unit, name, desc"'
return,-1
endif

;hardcoded settings (could make these defined iteratively)
nhdr=200                        ;maximum number of SEx header rows
fmt='(A2000)'                   ;format for length of a given row


;read the data
readfmt,file,fmt,hdr,SILENT=silent,numline=nhdr     

g=where(strmid(hdr,0,1) eq '#',nhdr,complement=b,ncomplement=nb)
if g(0) eq -1 then begin    ;test if the SEx cat is of the "ASCII_HEAD" type
   message,'The SEx catalog '+file+' does not have an supported header.',/cont
   message,'Please verify that the catalog type is set to ASCII_HEAD.',/cont
   message,'Exitting.',/cont
endif
if nb eq 0 then return,-1
data=strtrim(hdr(b))
hdr=strtrim(hdr(g))

;parse the header with logic
;NUMBER, PARAMETER NAME, DESCRIPTION, UNIT
num=strarr(nhdr)
name=strarr(nhdr)
desc=strarr(nhdr)
unit=strarr(nhdr)
for i=0,nhdr-1 do begin
   t=strsplit(hdr(i),' ',/ext)
   nt=n_elements(t)
   num(i)=t(1)
   name(i)=t(2)
   last=strmid(t(nt-1),strlen(t(nt-1))-1,1)
   if strlen(hdr(i)) gt  50 then begin
      if last eq ']' then begin
         desc(i)=strjoin(t(3:nt-2),' ')
         unit(i)=t(nt-1)
      endif else begin
         desc(i)=strjoin(t(3:nt-1),' ')
         unit(i)=''
      endelse
   endif 
endfor

;---------------parse the header with hardcoding format-----------------
;-------------Hopefully SEx won't change it's output format-------------
;num=strcompress(strmid(hdr,2,3),/rem)
;name=strcompress(strmid(hdr,6,15),/rem)
;desc=strmid(hdr,22,47)
;unit=strcompress(strmid(hdr,70,30),/rem)
;-----------------------------------------------------------------------

;set the defaults for read_ascii.pro
version=1.0                       
datastart=n_elements(num)         
delimiter=32b
missingvalue=!values.f_nan
commentsymbol=''
fieldcount=max(float(num))


if keyword_set(ALLFLOAT) then fieldtypes=replicate(4L,fieldcount) else begin   
;if you don't use ALLFLOAT, it will test if the first line
;contains a '.'
   sdata=strsplit(data(0),' ',/extract)
   ncol=n_elements(sdata)
   fieldtypes=replicate(4L,ncol)
   for i=0,ncol-1 do begin
      q=strpos(sdata(i),'.')
      if q(0) eq -1 then fieldtypes(i)=3L
   endfor
endelse


;Check for "multiples" (generally associated with multiple apertures
;or multiple sizes)
name2=[''] & num2=[0,long(num)]
name2=[''] & num2=[long(num),max(long(num))+1]
desc2=[''] & unit2=['']
for i=0,n_elements(num)-1 do begin
   del=num2(i+1)-num2(i)
   if del eq 1 then begin
      desc2=[desc2,desc(i)]
      unit2=[unit2,unit(i)]
      name2=[name2,name(i)]
   endif else begin
      sub=strcompress(string((indgen(del)+1),f='(I6)'),/rem) 
                                ;the (I6) is the max # of multiples
                                ;SEx allows (just a guess, but
                                ;let's hope they have less than a million.
      
      desc2=[desc2,strarr(del)+desc(i)]
      unit2=[unit2,strarr(del)+unit(i)]
      name2=[name2,name(i)+sub]
   endelse
endfor
fieldnames=name2(1:n_elements(name2)-1)
unit2=unit2(1:n_elements(name2)-1)
desc2=desc2(1:n_elements(name2)-1)


fieldlocations=strsplit(data(0),' ')
fieldgroups=lindgen(fieldcount)



template={version:version,$
          datastart:datastart,$
          delimiter:delimiter,$
          missingvalue:missingvalue,$
          commentsymbol:commentsymbol,$
          fieldcount:fieldcount,$
          fieldtypes:fieldtypes,$
          fieldnames:fieldnames,$
          fieldlocations:fieldlocations,$
          fieldgroups:fieldgroups}

other={desc:desc2,unit:unit2,name:fieldnames}


data=read_ascii(file,template=template)
if keyword_set(CONVERT) then data=convert_struct(data)


return,data
end
