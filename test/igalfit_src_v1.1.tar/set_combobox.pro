pro set_combobox,wid,setval

widget_control,wid,get_value=values
g=(where(values eq setval))(0)
if g ne -1 then widget_control,wid,combobox_index=g

end
