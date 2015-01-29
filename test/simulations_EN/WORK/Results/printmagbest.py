import pylab as g
import numarray as num

f = open("coefmagbest.cat")
fl = f.readlines()
f.close()
data = [l.split() for l in fl]

mrange = num.arange(15,21,0.001)
print mrange
g.clf()
c = 1
for i in range(c+0,c+1):
	g.plot(mrange, float(data[i][3]) +  float(data[i][4])*mrange** float(data[i][5]), "b-")
	
