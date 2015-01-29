#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import numarray as num

def clearnan(a):
	""" Modulo que limpia de "nan" un array a."""
	b = list(a)
	delpos = []
	cl = 0
	while "nan" in b:
		delpos.append(b.index("nan") + cl)
		b.remove("nan")
		cl += 1
	return num.array(b), delpos
	
def cleardel(a,delpos):
	""" Modulo que limpia las posiciones "delpos" de un array a."""
	b = list(a)
	cl = 0
	for pos in delpos:
		b.pop(pos - cl)
		cl += 1
	return num.array(b)
