f = open("ccorr.txt")
data = f.readlines()
data1 = [l.split() for l in data]
f.close()
f = open("coefmagbestold.cat")
data = f.readlines()
data2 = [l.split() for l in data]
f.close()
s = ""
for j in data2:
	for i in data1:
		if (i[0] == j[0]) & (i[1] == j[1]) & (j[3] != "-99"):
			j[3] = str(float(j[3])-float(i[2]))
			break
	for k in j:
		s += k+" "
	s += "\n"
f = open("coefmagbest.cat","w")
f.write(s)
f.close()
