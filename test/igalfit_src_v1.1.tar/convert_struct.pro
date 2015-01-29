function convert_struct,data

tags=tag_names(data)                   ;get the tag names
ntag=n_elements(tags)                  ;# of tags
nel=n_elements(data.(0))               ;# of elements

val=strarr(ntag)
for i=0,ntag-1 do begin
   type=size(data.(i)(0),/type)
   case type of
      1: val(i)='0b'
      2: val(i)='0'
      3: val(i)='0L'
      4: val(i)='0.'
      5: val(i)='0d0'
      7: val(i)='" "'
      else: val(i)='0.0'
   endcase
endfor


arg=strjoin("'"+tags+"',"+val,',')     ;create the argument to create_struct
cmd="out=create_struct("+arg+")"       ;create a command to call create_struct
t=execute(cmd)                         ;call create_struct
out=replicate(out,nel)                 ;make it a vector of structs

for i=0,ntag-1 do out(*).(i)=data.(i)  ;essentially do the "transpose"

return,out
end
