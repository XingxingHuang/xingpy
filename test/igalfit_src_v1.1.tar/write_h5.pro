pro write_h5,file,data,name,COMMENT=comment

fileid=h5f_create(file)
datatype=h5t_idl_create(data)
dataspace=h5s_create_simple(1)
dataset=h5d_create(fileid,name,datatype,dataspace)
;if keyword_set(COMMENT) then h5g_set_comment,fileid,name,comment

h5d_write,dataset,data
h5f_close,fileid

end
