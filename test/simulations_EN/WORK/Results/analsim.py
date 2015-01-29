#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

# TITLE: Programa para el análisis de las simulaciones de los errores.
# CREATED: 20070509 clsj
#

import scipy
import pylab as g
import matplotlib.cm as cmap
import sexcat
import numarray as num
import linreg
import MC
MC = MC.MC()

class analsim:
	
	def __init__(self):
		pass

# ======== Modulos auxiliares =========

	def clear(self,a):
		""" Modulo que limpia de "-9" un array."""
		b = list(a)
		delpos = []
		cl = 0
		while -9 in b:
			delpos.append(b.index(-9) + cl)
			b.remove(-9)
			cl += 1
		return num.array(b), delpos
	
	def cleardel(self,a,delpos):
		""" Modulo que limpia las posiciones "delpos" de un array."""
		b = list(a)
		cl = 0
		for pos in delpos:
			b.pop(pos - cl)
			cl += 1
		return num.array(b)
		
	def tensor2(self, nbinx, nbiny):
		T = []
		for k in range(0,nbiny):
			hk = []
			for j in range(0,nbinx):
				hk.append([])
			T.append(hk)
		return T
		
	def cuartil(self,x):
		x.sort()
		if len(x)%2 == 1:
			aux1 = x[0:len(x)/2+1]
			aux2 = x[len(x)/2:]
		else:
			aux1 = x[0:len(x)/2]
			aux2 = x[len(x)/2:]
		Q1 = scipy.median(aux1)
		Q3 = scipy.median(aux2)
		return abs((Q3-Q1)/1.35)
		
	def minmax(self, x):
		biny = len(x)
		try:
			binx = len(x[0])
		except: 
			print "x ha de ser bidimensional."
			return (0.,0.)
		y = []
		for j in range(biny):
			for i in range(binx):
				y.append(x[j][i])
		y.sort()
		y.reverse()
		maxx = y[0]
		if -99 in y:
			minx = y[y.index(-99) - 1]
		else:
			minx = y[-1]
		return minx, maxx
		
	def limdec(self,x, pmin):
		#Para buscar la posición del límite de detección
		detec = num.zeros(len(x[0]),type="Float32")
		for i in range(len(x)):
			for j in range(len(x[0])):
				if x[i][j] != -99.0: detec[j] += x[i][j]
		pos = 0
		while detec[pos] >= pmin:
			pos += 1
		return pos
		
#========== Moludos del ajuste ============
		
	def residuals(self, p, y, x):
		C,m = p
		#err = y - C*num.exp(m*x)
		err = y - C*(x)**m
		return err
		
	def funcfit(self, x, y):
		x = num.array(x)
		y = num.array(y)
		p0 = [0,0.5]
		fitresul = scipy.optimize.leastsq(self.residuals, p0, args = (y,x))
		return fitresul[0]
		
	def chisq(self, p, y, x):
		C,m = p
		chi = sum((y - C*num.exp(m*(x-15)))**2 / C*num.exp(m*(x-15)))
		return chi
	
	def bestfit(self, pos1, pos2, pos3, rangox, smap):
		err = []
		pos3 = min(pos2,pos3)
		for pos5 in range(pos3,pos2+1):
			#cs3,cs4 = self.expfit(rangox[pos1:pos5], smap[pos1:pos5])
			cs3,cs4 = scipy.polyfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]),1)
			err.append(self.chisq([cs3,cs4], smap[pos1:pos5], rangox[pos1:pos5]))
			#err.append(scipy.average(self.residuals([cs3,cs4], smap[pos1:pos5], rangox[pos1:pos5])**2))
			#print pos5, cs3,cs4, err[pos5-pos1-4]
		#print "====="
		pos5 = err.index(min(err)) + pos3
		return pos5, cs3, cs4
		
		return
	
		pos5 = pos1 + 10
		#while (rangox[pos5] < magcut):
		#	pos5 += 1
		cs4,cs3 = scipy.polyfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]),1)
		#cs3,cs4 = self.expfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]))
		while (num.exp(cs3) * num.exp(cs4*(rangox[pos5-1] - 15)) < max(smap[pos5:pos2])):
		#while (cs3 * num.exp(cs4*(rangox[pos5-1] - 15)) < max(smap[pos5:pos2])):	
			cs4,cs3 = scipy.polyfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]),1)
			#cs3,cs4 = self.expfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]))
			pos5 += 1
			if pos5 == pos2: break
	
	
	
# ======== Módulos de apoyo gráfico ===========

	def zeroplot(self,catalsim,catalg,field):
		datasim = sexcat.rcat(catalsim)
		print "Catálogo %s leido" %catalsim
		datag = sexcat.rcat(catalg)
		print "Catálogo %s leido" %catalg
		akr = []
		mag = []
		for i in range(len(datag["NUMBER"])):
			if "_G"+str(field)+"-" in datag["FULL_ID"][i]:
				mag.append(datag["MAG_APER2"][i])
				#akr.append(datag["KRON_RADIUS"][i]*num.sqrt(datag["A_WORLD"][i]*datag["B_WORLD"][i]))
				akr.append(datag["FLUX_RADIUS"][i])
		g.plot(datasim["MAG_APER_PSF"], datasim["FLUX_RADIUS_IMG"], "bo", markersize=1)
		g.plot(mag,akr,"ro", markersize = 3)
		g.xlabel("MAG_APER2")
		g.ylabel("FLUX_RADIUS")
		g.title("MAG vs RADIUS")
		return datasim["MAG_APER_PSF"], datasim["FLUX_RADIUS_IMG"], mag, akr
		#catname = catalsim.split(".cat")[0]
		#g.savefig("figures/"+catname, format="eps")
		#print "Imagen grabada en %s" %("figures/"+catname+".eps")
				
	def onedfit(self,demap,nsexmap,pdmap,pdsexmap,mmap,smap,vmap,rangox,stepx,mlim,nmin = 100, leym = "", title = "", mode = 0):
		#Definimos el array de magnitudes
		rangox = num.array(rangox[:-1]) + stepx/2.
		#gain = 5.3
		#errflux = 1.087/num.sqrt(gain * 10**(-0.4*(rangox - 22.5)))
		# Buscamos donde hay más de cien fuentes: será las estadísticas que nos creamos.
		pos1 = 0
		while (nsexmap[pos1] <= nmin) & (rangox[pos1] <= mlim):
			pos1 += 1
		pos2 = len(demap) - 1
		while (nsexmap[pos2] <= nmin) & (pos2 != pos1):
			pos2 -= 1
		pos3 = 0
		while (rangox[pos3] < mlim):
			pos3 += 1
		pos2 += 1
		#if magcut == 0:
		#	pos4 = 0
		#	while (0 > pdmap[pos4]) | (pdmap[pos4] > 0.5):
		#		pos4 += 1
		if pos2 - pos1 < 4:
			print "No hay datos suficientes"
			return
		if mode == 0:
			g.figure(1)
			g.clf()
			vmin, vmax = self.minmax([pdmap])
			if vmin == vmax: vmin = 0.; vmax = 1.
			step = (vmax - vmin)/10.
			g.plot(rangox,pdmap,"bo")	
			g.axhline(0.5, linewidth = 2)
			g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
			g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
			#g.axvline(rangox[pos4] - stepx/2., color = "k", linewidth = 1)
			g.xlim(min(rangox)-0.5,max(rangox)+0.5)
			g.ylim(vmin-step,vmax+step)
			g.title("Grafica de deteccion"+title)
			g.xlabel("Magnitud total simulacion")
			g.ylabel("Probabilidad de deteccion")
		elif (mode == 5) | (mode == 4):
			g.figure(1)
			g.clf()
			vmin, vmax = self.minmax([pdsexmap])
			if vmin == vmax: vmin = 0.; vmax = 1.
			step = (vmax - vmin)/10.
			g.plot(rangox,pdsexmap,"bo")	
			g.axhline(0.5, linewidth = 2)
			g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
			g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
			#g.axvline(rangox[pos4] - stepx/2., color = "k", linewidth = 1)
			g.xlim(min(rangox)-0.5,max(rangox)+0.5)
			g.ylim(vmin-step,vmax+step)
			g.title("Grafica de eficiencia"+title)
			g.xlabel(leym)
			g.ylabel("Funcion de eficiencia")
		g.figure(2)
		g.clf()
		vmin1, vmax = self.minmax([mmap+smap])
		vmin, vmax1 = self.minmax([mmap-smap])
		step = (vmax - vmin)/10.
		g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
		g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
		g.axhline(0., color = "k", linewidth = 2)
#		c1,c0 = scipy.polyfit(rangox[:pos], num.log(abs(mmap[0][:pos])),1)
#		g.plot(rangox[:pos+1], -num.exp(c0) * num.exp(c1*rangox[:pos+1]), "r-", linewidth = 2)
#		g.plot(rangox, -num.exp(c0) * num.exp(c1*rangox), "r-", linewidth = 2)
		g.bar(rangox,[0.]*len(rangox),0.,mmap,yerr=smap)
		g.plot(rangox,mmap,"bo")
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Grafica de diferencias"+title)
		g.xlabel(leym)
		g.ylabel("Mediana de las diferencias")
		g.figure(3)
		g.clf()
		vmin, vmax = self.minmax([smap])
		step = (vmax - vmin)/10.
		g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
		g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
#		cs2,cs1,cs0 = scipy.polyfit(rangox[pos1:pos2], smap[pos1:pos2],2)
#		g.plot(rangox[:pos+1], cs2*rangox[:pos+1]**2 + cs1*rangox[:pos+1] + cs0, "r-", linewidth = 2)
#		g.plot(rangox, cs2*rangox**2 + cs1*rangox + cs0, "r-", linewidth = 2)
		pos5 = list(rangox).index(max(rangox[pos1:pos2]))
		#pos5 = pos2
		#while (rangox[pos5] < magcut):
		#	pos5 += 1
		cs4,cs3 = scipy.polyfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]),1)
		#cs5,cs6 = self.expfit(rangox[pos1:pos5],smap[pos1:pos5])
		#cs5,cs6 = self.funcfit(rangox[pos1:pos5],smap[pos1:pos5])
		#while (num.exp(cs3) * num.exp(cs4*(rangox[pos5-1] - 15)) < scipy.median(smap[pos5:pos2])):
		#while (cs3 * num.exp(cs4*(rangox[pos5-1] - 15)) < max(smap[pos5:pos2])):	
		#	pos5 += 1
		#	cs4,cs3 = scipy.polyfit(rangox[pos1:pos5] - 15., num.log(smap[pos1:pos5]),1)
			#cs3,cs4 = self.expfit(rangox[pos1:pos5] - 15., smap[pos1:pos5])
		#	if pos5 == pos1+4: break
		#print pos1, pos2, pos3
		#pos5, cs4, cs3 = self.bestfit(pos1, pos2, pos3, rangox, smap)
		g.axvline(rangox[pos5] - stepx/2.,color = "k", linewidth = 1)
		#g.axhline(max(smap[pos5:pos2]), color = "k", linewidth = 2)
		g.plot(rangox[:pos2], num.exp(cs3) * num.exp(cs4*(rangox[:pos2] - 15)), "r", linewidth = 2)
		#g.plot(rangox[:pos2], cs5 * num.exp(cs6*(rangox[:pos2])), "k:", linewidth = 2)
		#A,C,m = self.expfit(rangox[pos1:pos5], smap[pos1:pos5])
		#print A, C, m
		#g.plot(rangox[:pos2], A * num.exp(m*rangox[:pos2] - n*rangox[:pos2]**2), "b", linewidth = 2)
		#g.plot(rangox[:pos2], A * (1 + rangox[:pos2])**m * num.exp(-n*rangox[:pos2]**2), "b", linewidth = 2)
		#g.plot(rangox[:pos2], A + C * num.exp(m*rangox[:pos2]), "b", linewidth = 2)
		#g.plot(rangox, errflux, "k:", linewidth = 2)
		g.plot(rangox,smap,"bo")
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Grafica de sigmas"+title)
		g.xlabel(leym)
		g.ylabel("Sigma de las diferencias")
		#print "Ajuste del mapa de sigmas: %f + %f*m + %f*m**2; %f * exp(%f*m)" %(cs0,cs1,cs2,num.exp(cs3),cs4)
		#print "Ajuste del mapa de sigmas: "+ str(num.exp(cs3)) +" * exp("+ str(cs4)+"*m)"
		#print "Ajuste del mapa de sigmas: "+ str(cs3) +" * exp("+ str(cs4)+"*m)"
		g.figure(4)
		g.clf()
		vmin, vmax = self.minmax([vmap])
		step = (vmax - vmin)/10.
		g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
		g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
#		ce2,ce1,ce0 = scipy.polyfit(rangox[pos1:pos2], vmap[pos1:pos2],2)
#		g.plot(rangox[:pos+1], ce2*rangox[:pos+1]**2 + ce1*rangox[:pos+1] + ce0, "r-", linewidth = 2)
#		g.plot(rangox, ce2*rangox**2 + ce1*rangox + ce0, "r-", linewidth = 2)
		#ce4,ce3 = scipy.polyfit(rangox[pos1:pos2], num.log(vmap[pos1:pos2]),1)
		#g.plot(rangox, num.exp(ce3) * num.exp(ce4*rangox), "r-", linewidth = 2)
		#g.plot(rangox, errflux, "k:", linewidth = 2)
		g.plot(rangox,vmap,"bo")
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Grafica de errores"+title)
		g.xlabel(leym)
		g.ylabel("Mendiana de los errores de SExtractor")
		#print "Ajuste del mapa de errores: %f + %f*m + %f*m**2; %f * exp(%f*m)" %(ce0,ce1,ce2,num.exp(ce3),ce4)
		#print "Ajuste del mapa de sigmas: "+ str(num.exp(ce3)) +" * exp("+ str(ce4)+"*m)"
		g.figure(5)
		g.clf()
		rmap = smap / vmap
		vmin, vmax = self.minmax([rmap])
		g.plot(rangox,rmap,"bo")
#		c2,c1,c0 = scipy.polyfit(rangox[:pos], rmap[:pos],2)
#		g.plot(rangox[:pos+1], c2*rangox[:pos+1]**2 + c1*rangox[:pos+1] + c0, "r-", linewidth = 2)
#		g.plot(rangox, c2*rangox**2 + c1*rangox + c0, "r-", linewidth = 2)
#		rmap = [(cs2*rangox[:pos+1]**2 + cs1*rangox[:pos+1] + cs0) / (ce2*rangox[:pos+1]**2 + ce1*rangox[:pos+1] + ce0)]
#		g.plot(rangox[:pos+1],rmap,"b-", linewidth = 2)
#		rmap = [(cs2*rangox**2 + cs1*rangox + cs0) / (ce2*rangox**2 + ce1*rangox + ce0)]
#		g.plot(rangox,rmap,"b-", linewidth = 2)
#		rmap = [(num.exp(cs3) * num.exp(cs4*rangox[:pos+1])) / (num.exp(ce3) * num.exp(ce4*rangox[:pos+1]))]
#		g.plot(rangox[:pos+1],rmap,"b:", linewidth = 2)
		#rmap = [(num.exp(cs3) * num.exp(cs4*rangox)) / (num.exp(ce3) * num.exp(ce4*rangox))]
		#g.plot(rangox,rmap,"b:", linewidth = 2)
		g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 2)
		g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 2)
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Grafica de relacion entre errores"+title)
		g.xlabel(leym)
		g.ylabel("Sigma / Error SExtractor")
		
	def twoplot(self,demap, nsexmap, pdmap, mmap, smap, vmap, xx, yy, leym, leyre, minmag, maxmag, minre, maxre):
		g.figure(1)
		g.clf()
		vmin, vmax = self.minmax(pdmap)
		if vmin == vmax: vmin = 0; vmax = 1.
		g.pcolor(xx,yy,pdmap,cmap = cmap.gray_r,vmin=vmin,vmax=vmax)
		g.xlim(minmag,maxmag)
		g.ylim(minre,maxre)
		g.colorbar()
		g.title("Mapa de deteccion")
		g.xlabel(leym)
		g.ylabel(leyre)
		g.figure(2)
		g.clf()
		vmin, vmax = self.minmax(mmap)
		g.pcolor(xx,yy,mmap,cmap = cmap.gray_r,vmin=vmin,vmax=0)	
		g.xlim(minmag,maxmag)
		g.ylim(minre,maxre)
		g.colorbar()
		g.title("Mapa de diferencias")
		g.xlabel(leym)
		g.ylabel(leyre)
		g.figure(3)
		g.clf()
		vmin, vmax = self.minmax(smap)
		g.pcolor(xx,yy,smap,cmap = cmap.gray_r,vmin=vmin,vmax=0.5)	
		g.xlim(minmag,maxmag)
		g.ylim(minre,maxre)
		g.colorbar()
		g.title("Mapa de sigmas")
		g.xlabel(leym)
		g.ylabel(leyre)
		g.figure(4)
		g.clf()
		vmin, vmax = self.minmax(vmap)
		g.pcolor(xx,yy,vmap,cmap = cmap.gray_r,vmin=vmin,vmax=vmax)	
		g.xlim(minmag,maxmag)
		g.ylim(minre,maxre)
		g.colorbar()
		g.title("Mapa de relacion de varianzas")
		g.xlabel(leym)
		g.ylabel(leyre)
		
	def catalplot(self, catal, campo, mmap, xx, yy, leym, leyre, minmag, maxmag, minre, maxre):
		data = sexcat.rcat(catal)
		re = []
		mag = []
		for i in range(len(data["NUMBER"])):
			if "G"+campo in data["FULL_ID"][i]:
				try:
					re.append(num.log10(data["KRON_RADIUS"][i]))
					mag.append(data["MAG_APER2"][i])
				except:
					pass
		g.figure(6)
		g.clf()
		vmin, vmax = self.minmax(mmap)
		g.pcolor(xx,yy,mmap,cmap = cmap.gray_r,vmin=vmin,vmax=vmax)
		g.plot(mag,re,"ro",markersize=3)
		g.xlim(minmag-3.0,maxmag+3.0)
		g.ylim(minre-0.1,maxre + 0.1)
		g.colorbar()
		g.title("Mapa de diferencias")
		g.xlabel(leym)
		g.ylabel(leyre)

	def allplot(self, smap, rangox, stepx, leym):
		rangox = num.array(rangox[:-1]) + stepx/2.
		g.figure(7)
		g.clf()
		for i in range(len(smap)):
			vmin, vmax = self.minmax([smap[i]])
			step = (vmax - vmin)/10.
			g.plot(rangox,smap[i],"o")
			g.xlim(min(rangox)-0.5,max(rangox)+0.5)
			g.ylim(vmin-step,vmax+step)
			g.title("Mapa de sigmas")
			g.xlabel(leym)
			g.ylabel("Sigma de las diferencias")
			
	def contplot(self,nsexmap,pdmap,mmap,smap,rangox,stepx, leym, title):
		rangox = num.array(rangox[:-1]) + stepx/2.
		g.figure(1)
		g.clf()
		vmin, vmax = self.minmax([pdmap])
		if vmin == vmax: vmin = 0.; vmax = 1.
		step = (vmax - vmin)/10.
		g.plot(rangox,pdmap,"bo")	
		g.axhline(0.5, linewidth = 2)
		#g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
		#g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
		#g.axvline(rangox[pos4] - stepx/2., color = "k", linewidth = 1)
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Mapa de deteccion"+title)
		g.xlabel("Magnitud total simulacion")
		g.ylabel("Probabilidad de deteccion")
		g.figure(2)
		g.clf()
		vmin1, vmax = self.minmax([mmap+smap])
		vmin, vmax1 = self.minmax([mmap-smap])
		step = (vmax - vmin)/10.
		#g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
		#g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
		g.axhline(0., color = "k", linewidth = 2)
		#g.bar(rangox,[0.]*len(rangox),0.,mmap,yerr=smap)
		g.plot(rangox,mmap,"bo")	
		pos1 = 0
		while (rangox[pos1] < 17):
			pos1 += 1
		corr = scipy.median(mmap[:pos1])
		g.axhline(corr, color = "b", linewidth = 1)
		print corr
		guess = mmap - pdmap*corr
		guessl = []
		rangoxl = []
		nobj = []
		for i in range(len(guess)):
			if guess[i] != -99:
				guessl.append(guess[i])
				rangoxl.append(rangox[i])
				nobj.append(nsexmap[i])
				#print rangox[i],guess[i]
		fmin = guessl.index(min(guessl))
		#fmin = len(guessl)-1
		#while (guessl[fmin] > 0):
		#	fmin -= 1
		fmin += 4
		pos2 = -1
		#while (nobj[pos2] > 10):
		#	pos2 += 1
		#print rangoxl[fmin:pos2], guessl[fmin:pos2]
		m,c = scipy.polyfit(rangoxl[fmin:pos2], guessl[fmin:pos2],1)
		g.axvline(rangoxl[fmin] - stepx/2., color = "r", linewidth = 1)
		g.axvline(rangoxl[pos2] - stepx/2., color = "r", linewidth = 1)
		g.plot(rangox,pdmap*corr,"r-")
		g.plot(rangox,guess,"ro")
		g.plot(rangox[pos1:], m*rangox[pos1:] + c, "k-", linewidth = 2)
		g.plot(num.array(rangoxl[fmin:]) - m*num.array(rangoxl[fmin:]) - c,[1.]*len(rangoxl[fmin:]),"ko")
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Mapa de diferencias"+title)
		g.xlabel(leym)
		g.ylabel("Mediana de las diferencias")
		#print fmin, pos2
		print m,c
		g.figure(3)
		g.clf()
		vmin, vmax = self.minmax([smap])
		step = (vmax - vmin)/10.
		pos2 = 0
		while (rangox[pos2] < 20.5):
			pos2 += 1
		g.axvline(rangox[pos2] - stepx/2., color = "r", linewidth = 1)
		g.axvline(rangox[pos1] - stepx/2., color = "r", linewidth = 1)
		g.plot(rangox,smap,"bo")
		
		
		g.plot(rangox[:pos2],smap[:pos2]/pdmap[:pos2],"ro")
		g.xlim(min(rangox)-0.5,max(rangox)+0.5)
		g.ylim(vmin-step,vmax+step)
		g.title("Mapa de sigmas"+title)
		g.xlabel(leym)
		g.ylabel("Sigma de las diferencias")
		
		
		
		
# ========== Modulos principales ============
		
	def mag(self,fichin, minmag, difmag = 1., magi = 0, magf = 3, plot = 0):
		if magi == 0: magi = "MAG_MODEL"
		elif magi == 1: magi = "MAG_APER_MODEL"
		elif magi == 2: magi = "MAG_APER_IMG"
		elif magi == 3: magi = "MAG_APER_PSF"
		if magf == 0: magf = "MAG_MODEL"
		elif magf == 1: magf = "MAG_APER_MODEL"
		elif magf == 2: magf = "MAG_APER_IMG"
		elif magf == 3: magf = "MAG_APER_PSF"
		data = sexcat.rcat(fichin)
		msex, delpos = self.clear(data[magf])
		mini = self.cleardel(data[magi], delpos)
		minifit = []
		msexfit = []
		maxmagt = max(mini)
		if difmag > maxmagt - minmag:
			difmag = maxmagt - minmag
		for pos in range(len(mini)):
			if minmag <= mini[pos] < minmag+difmag:
				minifit.append(mini[pos])
				msexfit.append(msex[pos])
			print pos
		minifit = num.array(minifit)
		msexfit = num.array(msexfit)
		mdiff = minifit - msexfit
		#m,b,me,be,chi = linreg.linregresion(minifit,minifit - msexfit, prin = "no")
		#corr = float("%2.5f" %(m*(minmag + difmag / 2.) + b))
		if len(mdiff) == 0:
			print "No hay datos para calcular la desviación."
			corr = 0
		else:
			corr = scipy.median(minifit - msexfit)
		if plot == 1:
			g.figure(1)
			g.clf()
			g.plot(mini,msex,".")
			g.plot([min(mini) -1,max(mini)+1],[min(mini) -1,max(mini)+1],"r-", linewidth = 2)
			g.xlabel(magi)
			g.ylabel(magf)
			g.figure(2)
			g.clf()
			g.plot(mini,mini - msex,".")
			g.axhline(0, linewidth = 2)
			g.xlabel(magi)
			g.ylabel(magi + " - " + magf)
			g.figure(3)
			g.clf()
			g.plot(minifit,minifit - msexfit,".")
			g.axhline(corr, color = "k", linewidth = 2)
			g.xlabel(magi)
			g.ylabel(magi + " - " + magf)
		return corr
		
	def bidimap(self,fichin, minmag, maxmag, nbinmag, minre, maxre, nbinre, nmin = 100, mlim = 0.5, mode = 0, mode1 = 0, mode2 = 5):
		""" Modulo de python que obtiene los mapas bidimensionales de interés de las simulaciones de errores.
		
			mode = Espacio en el que mostramos las gráfica:
				0 : MAG_MODEL, RE_MODEL
				1 : MAG_APER_MODEL, KRON_MODEL
				2 : MAG_BEST_MODEL, KRON_MODEL
				3 : MAG_APER_IMG, KRON_IMG
				4 : MAG_BEST_IMG, KRON_IMG
				5 : MAG_APER_PSF, KRON_IMG
				6 : MAG_APER_PSF, RE_MODEL
				7 : MAG_MODEL, KRON_IMG
				"""
		#Definimos el modo de estudio.
		if mode == 0:
			mag = "MAG_MODEL"
			kron = ""
			re = "RE_MODEL"
			re2 = ""
			leym = "Magnitud total simulacion"
			leyre = "log(re) simulacion"
		elif mode == 1:
			mag = "MAG_APER_MODEL"
			kron = ""
			#kron = "KRON_MODEL"
			#re = "A_IMAGE_MODEL"
			re = "FLUX_RADIUS_MODEL"
			#re2 = "B_IMAGE_MODEL"
			leym = "Magnitud apertura (simulacion)"
			leyre = "log(FLUX_RADIUS) simulacion"
		elif mode == 2:
			mag = "MAG_BEST_MODEL"
			kron = ""
			#kron = "KRON_MODEL"
			#re = "A_IMAGE_MODEL"
			re = "FLUX_RADIUS_MODEL"
			#re2 = "B_IMAGE_MODEL"
			leym = "Magnitud best (simulacion)"
			leyre = "log(FLUX_RADIUS) simulacion"	
		elif mode == 3:
			mag = "MAG_APER_IMG"
			#kron = "KRON_IMG"
			kron = ""
			#re = "A_IMAGE_IMG"
			re = "FLUX_RADIUS_IMG"
			#re2 = "B_IMAGE_IMG"
			leym = "Magnitud apertura (imagen)"
			leyre = "log(FLUX_RADIUS) imagen"
		elif mode == 4:
			mag = "MAG_BEST_IMG"
			#kron = "KRON_IMG"
			kron = ""
			#re = "A_IMAGE_IMG"
			re = "FLUX_RADIUS_IMG"
			#re2 = "B_IMAGE_IMG"
			leym = "Magnitud best (imagen)"
			leyre = "log(FLUX_RADIUS) imagen"
		elif mode == 5:
			mag = "MAG_APER_PSF"
			#kron = "KRON_IMG"
			kron = ""
			#re = "A_IMAGE_IMG"
			re = "FLUX_RADIUS_IMG"
			#re2 = "B_IMAGE_IMG"
			leym = "Magnitud apertura (PSF)"
			leyre = "log(FLUX_RADIUS) IMG"
			#leyre = "log(kr*sqrt(AB)) PSF"
		elif mode == 6:
			mag = "MAG_APER_PSF"
			#kron = "KRON_IMG"
			kron = ""
			#re = "A_IMAGE_IMG"
			re = "RE_MODEL"
			#re2 = "B_IMAGE_IMG"
			leym = "Magnitud apertura (PSF)"
			leyre = "log(re) simulacion"
			#leyre = "log(kr*sqrt(AB)) PSF"
		elif mode == 7:
			mag = "MAG_MODEL"
			#kron = "KRON_IMG"
			kron = ""
			#re = "A_IMAGE_IMG"
			re = "FLUX_RADIUS_IMG"
			#re2 = "B_IMAGE_IMG"
			leym = "Magnitud total simulacion"
			leyre = "log(FLUX_RADIUS) IMG"
			#leyre = "log(kr*sqrt(AB)) PSF"
		else:
			print "La variable mode ha de ser 0,1,2,3,4 ,5, 6 o 7"
			return [],[],[],[],[],[],[]
			
		if mode1 == 0:
			mag1 = "MAG_MODEL"
		elif mode1 == 1:
			mag1 = "MAG_APER_MODEL"
		elif mode1 == 2:
			mag1 = "MAG_BEST_MODEL"
		elif mode1 == 3:
			mag1 = "MAG_APER_IMG"
		elif mode1 == 4:
			mag1 = "MAG_BEST_IMG"
		else:
			print "La variable mode1 ha de ser 0,1 o 2."
			return [],[],[],[],[],[],[]
		
		if mode2 == 3:
			mag2 = "MAG_APER_IMG"
			magerr2 = "MAGERR_APER_IMG"
		elif mode2 == 4:
			mag2 = "MAG_BEST_IMG"
			magerr2 = "MAGERR_BEST_IMG"
		elif mode2 == 5:
			mag2 = "MAG_APER_PSF"
			magerr2 = "MAGERR_APER_PSF"
		else:
			print "La variable mode ha de ser 3,4 o 5."
			return [],[],[],[],[],[],[]
			
		# Definimos los tensores necesarios para el análisis
		nmap = num.zeros((nbinre,nbinmag),type="Float32")
		nsexmap = num.zeros((nbinre,nbinmag),type="Int")
		demap = num.zeros((nbinre,nbinmag),type="Int")
		magmap = self.tensor2(nbinmag,nbinre)
		sigmap = self.tensor2(nbinmag,nbinre)
		
		# Leemos el fichero con los datos
		print "Leyendo el catálogo..."
		data = sexcat.rcat(fichin)
		print "Catálogo leido."
		
		# Definiciones varias
		stepx = (maxmag - minmag)/float(nbinmag)
		rangox = num.arange(minmag,maxmag+stepx,stepx)
		
		# Los radios están en el espacio de logaritmos		
		#maxre = scipy.log10(maxre)
		#minre = scipy.log10(minre)
		maxre = maxre
		minre = minre
		stepy = (maxre - minre)/float(nbinre)
		rangoy = num.arange(minre,maxre+stepy,stepy)
		maxresim = maxre
		minresim = minre
		#maxresim = maxre
		#minresim = minre
		stepysim = (maxre - minre)/float(nbinre)
		rangoysim = num.arange(minre,maxre+stepy,stepy)
		#maxresim = scipy.log10(max(data["RE_MODEL"]) + 0.1)
		#minresim = scipy.log10(min(data["RE_MODEL"]) - 0.1)
		#stepysim = (maxresim - minresim)/float(nbinre)
		#rangoysim = num.arange(minresim,maxresim+stepysim,stepysim)
		#maxre = scipy.log10(max(data[re]) + 0.1)
		#minre = scipy.log10(min(self.clear(data[re])[0]) - 0.1)
		#stepy = (maxre - minre)/float(nbinre)
		#rangoy = num.arange(minre,maxre+stepy,stepy)
		# Llenamos la matrices de detección, diferencias y errores.
		status = 0
		print "Obteniendo los datos del catálogo..."
		if kron == "":
			datare = data[re]
		else:
			#datare = num.sqrt(data[re]*data[re2])*data[kron]
			datare = data[re]
		for pos in range(len(data["NUMBER"])):
			#if (minmag <= data["MAG_MODEL"][pos] < maxmag) & (minresim <= scipy.log10(data["RE_MODEL"][pos]) < maxresim):
			if (minmag <= data["MAG_MODEL"][pos] < maxmag) & (minresim <= data["RE_MODEL"][pos] < maxresim):
				nx = int((data["MAG_MODEL"][pos] - minmag)/stepx)
				#ny = int((scipy.log10(data["RE_MODEL"][pos]) - minresim)/stepysim)
				ny = int((data["RE_MODEL"][pos] - minresim)/stepysim)
				nmap[ny][nx] += 1
				demap[ny][nx] += data["DETECTION"][pos]
			#if (data["DETECTION"][pos] == 1) & (minmag <= data[mag][pos] < maxmag) & (minre <= scipy.log10(datare[pos]) < maxre):
			if (data["DETECTION"][pos] == 1) & (minmag <= data[mag][pos] < maxmag) & (minre <= datare[pos] < maxre):
				nx = int((data[mag][pos] - minmag)/stepx)
				#ny = int((scipy.log10(datare[pos]) - minre)/stepy)
				ny = int((datare[pos] - minre)/stepy)
				nsexmap[ny][nx] += 1
				magmap[ny][nx].append(data[mag1][pos] - data[mag2][pos])
				sigmap[ny][nx].append(data[magerr2][pos])
			# Ponemos aquí una linea de status, para saber por donde va :-D
			if 100.*pos/len(data["NUMBER"]) >= status:
				print "\tCompletado el %i por ciento." %(status)
				status += 10
		print "Determinando los mapas de sucesos..."
		pdmap = demap / nmap
		pdsexmap = nsexmap / nmap
		# Limpiamos los nans y ponemos -99.
		for j in range(nbinre):
			for i in range(nbinmag):
				if str(pdmap[j][i]) == "nan": pdmap[j][i] = -99.
				if str(pdsexmap[j][i]) == "nan": pdsexmap[j][i] = -99.
		# Determinamos los mapas de medianas y sigmas.
		mmap = num.zeros((nbinre,nbinmag),type="Float32")
		smap = num.zeros((nbinre,nbinmag),type="Float32")
		vmap = num.zeros((nbinre,nbinmag),type="Float32")
		for j in range(0,nbinre):
			for i in range(0,nbinmag):
				if len(magmap[j][i]) != 0:
					mmap[j][i] = scipy.median(magmap[j][i])
					smap[j][i] = self.cuartil(magmap[j][i])
					vmap[j][i] = scipy.median(sigmap[j][i])
				else:
					mmap[j][i] = -99
					smap[j][i] = -99
					vmap[j][i] = -99
		print "Graficas de los mapas de sucesos..."			
		# Dibujamos los mapitas.
		xx = []
		for i in range(len(rangoy)):
			xx.append(rangox)
		yy = []
		for pos in range(len(rangoy)):
			yyaux = []
			for i in range(len(rangox)):
				yyaux.append(rangoy[pos])
			yy.append(yyaux)
		yysim = []
		for pos in range(len(rangoysim)):
			yyaux = []
			for i in range(len(rangox)):
				yyaux.append(rangoysim[pos])
			yysim.append(yyaux)
		xx = num.array(xx); yy = num.array(yy); yysim = num.array(yysim); mmap = num.array(mmap); smap = num.array(smap); vmap = num.array(vmap)
		
		# Salvamos los resultados en un fichero
		s = ""
		for matriz in [nmap, nsexmap, pdmap, pdsexmap, mmap, smap, vmap, xx, yy]:
			s += "["
			for elemento in matriz:
				s += str(list(elemento))+","
			s = s[:-1] + "]\n"
		s += "[" + str(list(rangox)) + "]\n[[" + str(stepx) + "]]\n[" + str(list(rangoy)) + "]\n"
		fichout = "resul_" + fichin.split(".")[0] + "_minmag" + str(minmag)+"_maxmag"+ str(maxmag) + "_nmag" + str(nbinmag) + "_minre" + str(minre) + "_maxre" + str(maxre) + "_nre" + str(nbinre) + "_mode"+ str(mode) + "_mode1" + str(mode1) + "_mode2" +str(mode2) +".txt"	
		f = open(fichout,"w")
		f.write(s)
		f.close()

		# Hacemos las gráficas		
		#self.readresul(fichout, nmin, mlim, de1 = "yes", de2 = "yes", de3 = "no")

		return nmap, nsexmap, pdmap, mmap, smap, vmap, magmap, sigmap, rangox

#========== Modulos para hacer las gráficas y los análisis a partir de un fichero =====

	def str2list(self,s):
		lista = []
		aux = s.split("],")
	 	for i in aux:
			aux2 = i.split(",")
			listaux = []
			for j in aux2:
				if ("[" in j) & ("]" in j):
					listaux.append(float(j.split("[")[-1].split("]")[0]))
				elif "[" in j:
					listaux.append(float(j.split("[")[-1]))
				elif "]" in j:
					listaux.append(float(j.split("]")[0]))
				else:
					listaux.append(float(j))
			lista.append(listaux)
		return num.array(lista)
			
	def readresul(self, fichin, nmin = 100, mlim = 20.5, de1 = "no", de2 = "no", de3 = "no", de4 = "no"):
		# Obtenemos cosas del nombre del ficrero de entrada.
		data = fichin.split("_")
		mode = int(data[-3].split("mode")[1])
		if mode == 0:
			leym = "Magnitud simulacion"
			leyre = "log(re) simulacion"
		elif mode == 1:
			leym = "Magnitud apertura (simulacion)"
			leyre = "log(FLUX_RADIUS) simulacion"
		elif mode == 2:
			leym = "Magnitud best (simulacion)"
			leyre = "log(FLUX_RADIUS) simulacion"
		elif mode == 3:
			leym = "Magnitud apertura (imagen)"
			leyre = "log(FLUX_RADIUS) imagen"
		elif mode == 4:
			leym = "Magnitud best (imagen)"
			leyre = "log(FLUX_RADIUS) imagen"
		elif mode == 5:
			leym = "Magnitud apertura (PSF)"
			leyre = "log(FLUX_RADIUS) imagen"
		elif mode == 6:
			leym = "Magnitud apertura (PSF)"
			leyre = "log(re)"
		elif mode == 7:
			leym = "Magnitud simulacion"
			leyre = "log(FLUX_RADIUS) imagen"
		minmag = float(data[-9].split("minmag")[1])
		maxmag = float(data[-8].split("maxmag")[1])
		nbinmag = float(data[-7].split("nmag")[1])
		minre = float(data[-6].split("minre")[1])
		maxre = float(data[-5].split("maxre")[1])
		nbinre = float(data[-4].split("nre")[1])
		# Leemos el fichero y obtenemos los arrays de datos
		f = open(fichin,"r")
		lines = f.readlines()
		f.close()
		data = [l.split("\n")[0] for l in lines]
		nmap = self.str2list(data[0])
		nsexmap = self.str2list(data[1])
		pdmap = self.str2list(data[2])
		pdsexmap = self.str2list(data[3])
		mmap = self.str2list(data[4])
		smap = self.str2list(data[5])
		vmap = self.str2list(data[6])
		xx = self.str2list(data[7])
		yy = self.str2list(data[8])
		rangox = self.str2list(data[9])[0]
		stepx = self.str2list(data[10])[0][0]
		rangoy = self.str2list(data[11])[0]
		demap = pdmap * nmap		
		# Ya tengo todo lo que necesito, así que ahora solo hay de dibujar :-D
		if nbinre > 1:
			if (de1 == "yes") | (de1 == "si"):
				self.twoplot(demap, nsexmap, pdmap, mmap, smap, vmap, xx, yy, leym, leyre, minmag, maxmag, minre, maxre)
				raw_input("Espera...")
				#if "groth_wi" in fichin:
					#campo = str(int(fichin.split("groth_wi")[1][0:2]))
					#self.catalplot("groth-k--v11.cat", campo, mmap, xx, yy, leym, leyre, minmag, maxmag,  num.log10(minre),  num.log10(maxre))
			if (de2 == "yes") | (de2 == "si"):
				for pos in range(len(pdmap)):
					title = "\nlog(r) = [" + "%2.3f" %rangoy[pos] + ":" + "%2.3f" %rangoy[pos+1] + "]"
					self.onedfit(demap[pos], nsexmap[pos], pdmap[pos], pdsexmap[pos], mmap[pos], smap[pos], vmap[pos], rangox, stepx, mlim, nmin, leym, title, mode)
					raw_input("Espera...")
			if (de3 == "yes") | (de3 == "si"):
				self.allplot(smap, rangox, stepx, leym)
			if (de4 == "yes") | (de4 == "si"):
				for pos in range(len(pdmap)):
					title = "\nlog(r) = [" + "%2.3f" %rangoy[pos] + ":" + "%2.3f" %rangoy[pos+1] + "]"
					self.contplot(nsexmap[pos],pdmap[pos],mmap[pos],smap[pos],rangox,stepx,leym, title)
					raw_input("Espera...")
					#return
		else:
			#try:
			self.onedfit(demap[0],nsexmap[0],pdmap[0], pdsexmap[0], mmap[0], smap[0], vmap[0], rangox, stepx, mlim, nmin, leym, "", mode)
			#except:
			#	print "Fallo en las gráficas..."
		return nmap, nsexmap, pdmap, pdsexmap, mmap, smap, vmap, rangox
			
			
