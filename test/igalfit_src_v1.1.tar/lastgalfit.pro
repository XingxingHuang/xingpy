pro lastgalfit,lastgf

ndec=2             ;number of decimal places
root='galfit'      ;root name of galfit files
suffix=strjoin(replicate('[0123456789]',ndec),'')


;find the files
files=file_search(root+'.'+suffix,count=nfile)

;get the last 2 chars:
suf=fix(strmid(files,strlen(root)+1,ndec))
mx=max(suf,id)

lastgf=files(id)


end
