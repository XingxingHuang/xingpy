function type_error,keyword
  t=dialog_message(['The '+keyword+' is the wrong datatype!',$
                    'Unable to proceed.'],/error,/center)
  return,0b
end
