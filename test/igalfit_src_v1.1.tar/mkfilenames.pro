pro mkfilenames,state


;prepare output directory
psep=path_sep()

dir=(*state).prefs.tempdir
l=strlen(dir)
last=(strmid(dir,l-1,1) eq psep)?psep:''
if (file_search(dir,/test_dir))(0)+psep ne dir then begin
   dir=''
   (*state).prefs.tempdir=dir
endif

if file_exist((*state).setfile.sci) then begin
   scifile=(reverse(strsplit((*state).setfile.sci,psep,/ext)))(0)
   (*state).usefile.sci=dir+scifile
endif else (*state).usefile.sci='none'

if file_exist((*state).setfile.unc) then begin
   uncfile=(reverse(strsplit((*state).setfile.unc,psep,/ext)))(0)
   (*state).usefile.unc=dir+uncfile
endif else (*state).usefile.unc='none'

if file_exist((*state).setfile.psf) then begin
;   psffile=(reverse(strsplit((*state).setfile.psf,psep,/ext)))(0)
   (*state).usefile.psf=(*state).setfile.psf;dir+psffile
endif else (*state).usefile.psf='none'

;(*state).usefile.psf=(*state).setfile.psf



end
