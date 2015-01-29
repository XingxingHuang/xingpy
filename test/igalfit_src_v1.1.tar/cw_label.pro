function cw_label,base,label,_EXTRA=_extra
;if not keyword_set(VALUE) then value=''

r=widget_base(base,/row)
l=widget_label(r,value=label)
t=widget_label(r,_EXTRA=_extra)

return,t
end
