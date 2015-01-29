function writefile_error,file
t=dialog_message(['Unable to open the '+file+' for writing!',$
                     !error_state.msg,$
                     !error_state.sys_msg],/err,/cent,$
                    title='Writing File Error')
return,0b
end
