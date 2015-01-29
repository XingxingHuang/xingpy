f = open("groth-k--v20.cat","r")
file = f.readlines()
f.close()

head = [l for l in file if l[0] == "#"]
data = [l for l in file if l[0] != "#"]

s = ""
for i in head:
	s += i
for i in data:
	if "Ks_G10" in i.split()[-1]:
		pass
	else:
		s += i
f = open("groth-k--v21.cat","w")
f.write(s)
f.close()
	
