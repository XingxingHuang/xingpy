#
#  sexcat.py - Python module to read, write and manage SExtractor catalogs
#
#  Copyright (C) 2005 David Abreu
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Last changes 14/02/06: added text2cat function and bugs fixed

"""SExCaT module to read and write SExtractor catalogs.

It uses a dictionary with the names of the columns as the keys.

It needs "string" and "numarray" modules

05/09/05
davidabreu@users.sourceforge.net

David Abreu
"""

import string
from numpy import numarray  # by xx

try:
   import MySQLdb
except ImportError:
   print "MySQL functions are not available"

def conv(f):
   """conv(jj)-> Try to transform a string to float
                 If it fails, it returns the string"""
   try :
      num=float(f)
   except ValueError :
      num=jj
   return num

def readcat(filename,l=0) :
   """readcat(filename,l=0) -> Returns a dictionary with the names of the
   				columns as keys

      This function reads a SExtractor catalog
      Using l=1 it returns header lines in one var and data lines in other
   """	
	
   #reeading file by lines
   file=open(filename,'r')
   todo=file.readlines()
   file.close()
   
   head=[]; data=[]; headlines=[]; datalines=[]
   
   i=0
   for linea in todo :
      if string.lstrip(linea)[0:1]=="#" :
         headlines.append(linea)
         head.append(linea.split())	 
      else :
         datalines.append(linea)
         data.append(linea.split())
         j=0
         for val in data[i] :
            data[i][j]=conv(data[i][j])
            j+=1
         i+=1
   
   llaves=[linea[2] for linea in head]
   coments=[linea[3:] for linea in head]
   
   tabla={}
   
   i=0
   for llave in llaves :
      col=[]
      for jj in data :
         col.append(jj[i])
      tabla[llave]=col
      i+=1
   
   tabla['llaves']=llaves
   tabla['comentarios']=coments
      
   for cuidado in data :
      if len(llaves)!=len(cuidado) :
         print "--------------------------------------------------------"
         print "Warning: Some columns haven't got name or are empties!"
	 print "Check the result."
         print "--------------------------------------------------------"
         break
      
   if l:
      return tabla, headlines, datalines
   else:
      return tabla
   
def readhead(filename):
   """readhead(filename) -> list with the names of the columns of a SExtractor
   catalog.
   """
   #reading file by lines
   file=open(filename,'r')
   todo=file.readlines()
   file.close()

   head=[]
   
   for linea in todo :
      if string.lstrip(linea)[0:1]=="#" :
         head.append(linea.split())
	 
   llaves=[linea[2] for linea in head]
   
   return llaves

def existe(filename):
   """existe(filename)-> Try to open a file in reading mode in if it exists,
                         returns 1."""
   try:
      file=open(filename,'r')
      e=1
   except IOError:
      e=0
   return e

def writecat(data,filename,lineas=0,overwrite=0) :
   """writecat(data,filename) -> Write a catalog in a file.
      Columns are in the same order as "llaves" in the dictionary
      overwrite=1 -> overwrites the file.
   """
#cheking column length
   l=data.keys()
   try:
      l.remove('llaves')
      l.remove('comentarios')
   except ValueError:
      pass
      
   for i in range(len(l)-1):
      if len(data[l[i]])!=len(data[l[i+1]]):
         print "--------------------------------------------"
         print "Columns with different lenght."
	 print "The program will stop."
         print "--------------------------------------------"
         return
	 
#what type of catalog
   if data.has_key('llaves') and data.has_key('comentarios'):
      for i in data['comentarios']:
         if str(i) =='[]':
	    coment=0
	 else:
	    coment=1
      ordenado=1
   else:
      if data.has_key('llaves'):
         ordenado=1
         coment=0
      else:
         ordenado=0
         coment=0

#file exixst?
   if not(overwrite) and existe(filename):
      print '----------------------------------'
      print 'File "'+filename+'" exists.'
      print '----------------------------------'
      print 'The program will stop.'
      return
   
#openeing the file
   file=open(filename,'w')
   
   if ordenado:
      if coment:
#shorted and commented
         c=0
         for i in data['llaves']:
	    d=data['comentarios'][c]
	    if len(d) == 1:
	       d=str(d[0])
	    else:
	       d=str(d)
	    file.write('# '+str(c+1)+' '+i+'\t\t '+d+'\n')
            c+=1
	 utiles=data['llaves']
	 if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    for i in utiles:
	       file.write(str(data[i][j])+'\t')
	    file.write('\n')
#sorted
      else:
         c=0
         for i in data['llaves']:
            file.write('# '+str(c+1)+' '+i+'\n')
            c+=1
         utiles=data['llaves']
         if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    for i in utiles:
	       file.write(str(data[i][j])+'\t')
	    file.write('\n')
   else:
#unsorted
      utiles=data.keys()
      c=0
      for i in utiles:
         file.write('# '+str(c+1)+' '+i+'\n')
         c+=1
      if lineas:
         jj=lineas
      else:
         jj=range(len(data[utiles[0]]))
      for j in jj:
	 for i in utiles:
	    file.write(str(data[i][j])+'\t')
	 file.write('\n')
      
   file.close()	    
   return 'Data in: "'+str(filename)+'"'

def ptabcat(data,lineas=0) :
   """ptabcat(data) -> Prints a catalog on the screen to use in html.
   
            Columns are in the same order as "llaves" in the dictionary
   """
#shecking columns lenght
   l=data.keys()
   try:
      l.remove('llaves')
      l.remove('comentarios')
   except ValueError:
      pass
      
   for i in range(len(l)-1):
      if len(data[l[i]])!=len(data[l[i+1]]):
         print "--------------------------------------------"
         print "Columns with different lenght."
	 print "The program will stop."
         print "--------------------------------------------"
         return
	 
#type of catalog
   if data.has_key('llaves') and data.has_key('comentarios'):
      for i in data['comentarios']:
         if str(i) =='[]':
	    coment=0
	 else:
	    coment=1
      ordenado=1
   else:
      if data.has_key('llaves'):
         ordenado=1
         coment=0
      else:
         ordenado=0
         coment=0
   
   if ordenado:
      if coment:
#sorted and commented
         c=0
         for i in data['llaves']:
	    d=data['comentarios'][c]
	    if len(d) == 1:
	       d=str(d[0])
	    else:
	       d=str(d)
	    print('# '+str(c+1)+' '+i+'\t\t '+d+'<br>')
            c+=1
	 utiles=data['llaves']
	 print "<TABLE border=0>"
	 if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
            print "<TR>"
	    for i in utiles:
	       print("<TD>"+str(data[i][j])+"</TD>")
	    print "</TR>"
#sorted
      else:
         c=0
         for i in data['llaves']:
            print('# '+str(c+1)+' '+i+'<br>')
            c+=1
         utiles=data['llaves']
	 print "<TABLE border=0>"
         if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    print "<TR>"
	    for i in utiles:
	       print("<TD>"+str(data[i][j])+"</TD>")
	    print "</TR>"
   else:
#unsorted
      utiles=data.keys()
      c=0
      for i in utiles:
         print('# '+str(c+1)+' '+i+'<br>')
         c+=1
      print "<TABLE border=0>"
      if lineas:
         jj=lineas
      else:
	 jj=range(len(data[utiles[0]]))
      for j in jj:
         print "<TR>"
	 for i in utiles:
	    print("<TD>"+str(data[i][j])+"</TD>")
	 print "</TR>"
      	    
   return
      
def pcat(data,lineas=0) :
   """pcat(data) -> Prints a catalog on the screen.
   
            Columns are in the same order as "llaves" in the dictionary
	    "lineas" has the indexes of the lines to print.
   """
#cheking column lenght
   l=data.keys()
   try:
      l.remove('llaves')
      l.remove('comentarios')
   except ValueError:
      pass
      
   for i in range(len(l)-1):
      if len(data[l[i]])!=len(data[l[i+1]]):
         print "--------------------------------------------"
         print "Columns with different lenght."
	 print "The program will stop."
         print "--------------------------------------------"
         return
	 
#type of the catalog
   if data.has_key('llaves') and data.has_key('comentarios'):
      for i in data['comentarios']:
         if str(i) =='[]':
	    coment=0
	 else:
	    coment=1
      ordenado=1
   else:
      if data.has_key('llaves'):
         ordenado=1
         coment=0
      else:
         ordenado=0
         coment=0
   
   if ordenado:
      if coment:

#sorted and commented
         c=0
         for i in data['llaves']:
	    d=data['comentarios'][c]
	    if len(d) == 1:
	       d=str(d[0])
	    else:
	       d=str(d)
	    print('# '+str(c+1)+' '+i+'\t\t '+d)
            c+=1
	 utiles=data['llaves']
	 if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
            p=""
	    for i in utiles:
	       p=p+str(data[i][j])+"\t"
	    print p
#sorted
      else:
         c=0
         for i in data['llaves']:
            print('# '+str(c+1)+' '+i)
            c+=1
         utiles=data['llaves']
         if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    p=""
	    for i in utiles:
	       p=p+str(data[i][j])+"\t"
	    print p
   else:
#unsorted
      utiles=data.keys()
      c=0
      for i in utiles:
         print('# '+str(c+1)+' '+i)
         c+=1
      if lineas:
         jj=lineas
      else:
	 jj=range(len(data[utiles[0]]))
      for j in jj:
         p=""
	 for i in utiles:
	    p=p+str(data[i][j])+"\t"
         print p
      	    
   return

def phtmlcat(data,lineas=0) :
   """phtmlcat(data) -> Prints a catalog on the screen inside an html table.
   
            Columns are in the same order as "llaves" in the dictionary
	    "lineas" has the indexes of the lines to print.
   """
#shecking column length
   l=data.keys()
   try:
      l.remove('llaves')
      l.remove('comentarios')
   except ValueError:
      pass
      
   for i in range(len(l)-1):
      if len(data[l[i]])!=len(data[l[i+1]]):
         print "--------------------------------------------"
         print "Columns with different lenght."
	 print "The program will stop."
         print "--------------------------------------------"
         return
	 
#type of the catalog
   if data.has_key('llaves') and data.has_key('comentarios'):
      for i in data['comentarios']:
         if str(i) =='[]':
	    coment=0
	 else:
	    coment=1
      ordenado=1
   else:
      if data.has_key('llaves'):
         ordenado=1
         coment=0
      else:
         ordenado=0
         coment=0
   
   if ordenado:
      if coment:

#sorted and commented
         c=0
         for i in data['llaves']:
	    d=data['comentarios'][c]
	    if len(d) == 1:
	       d=str(d[0])
	    else:
	       d=str(d)
	    print('# '+str(c+1)+' '+i+'\t\t '+d)
            c+=1
	 utiles=data['llaves']
	 if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    print "<TR>"
	    for i in utiles:
	       print("<TD>"+str(data[i][j])+"</TD>")
	    print "</TR>"
#sorted
      else:
         c=0
	 print "<table border=1>"
	 print "<tr>"
         for i in data['llaves']:
            print('<td>'+i+'</td>')
            c+=1
         utiles=data['llaves']
         if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    print "<TR>"
	    for i in utiles:
	       print("<TD>"+str(data[i][j])+"</TD>")
	    print "</TR>"
	 print "</table>"
   else:
#unsorted
      utiles=data.keys()
      c=0
      for i in utiles:
         print('# '+str(c+1)+' '+i)
         c+=1
      if lineas:
         jj=lineas
      else:
	 jj=range(len(data[utiles[0]]))
      for j in jj:
         p=""
	 for i in utiles:
	    p=p+str(data[i][j])+"\t"
         print p
      	    
   return

def writelatexcat(data,filename,lineas=0,overwrite=0) :
   """writelatexcat(data,filename) -> Write a catalog in a latex table.
   
            Columns are in the same order as "llaves" in the dictionary
	    "lineas" has the indexes of the lines to print.
            overwrite=1 -> overwrites the file.
   """
#checking column lenght
   l=data.keys()
   try:
      l.remove('llaves')
      l.remove('comentarios')
   except ValueError:
      pass
      
   for i in range(len(l)-1):
      if len(data[l[i]])!=len(data[l[i+1]]):
         print "--------------------------------------------"
         print "Columns with different lenght."
	 print "The program will stop."
         print "--------------------------------------------"
         return
	 
#type of the catalog
   if data.has_key('llaves') and data.has_key('comentarios'):
      for i in data['comentarios']:
         if str(i) =='[]':
	    coment=0
	 else:
	    coment=1
      ordenado=1
   else:
      if data.has_key('llaves'):
         ordenado=1
         coment=0
      else:
         ordenado=0
         coment=0

#file exixst?
   if not(overwrite) and existe(filename):
      print '----------------------------------'
      print 'File "'+filename+'" exists.'
      print '----------------------------------'
      print 'The program will stop.'
      return
   
#opening the file
   file=open(filename,'w')
   
   if ordenado:
      if coment:
#sorted and commented
         c=0
         for i in data['llaves']:
	    d=data['comentarios'][c]
	    if len(d) == 1:
	       d=str(d[0])
	    else:
	       d=str(d)
	    file.write('# '+str(c+1)+' '+i+'\t\t '+d+'\n')
            c+=1
	 utiles=data['llaves']
	 if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    for i in utiles:
	       file.write(str(data[i][j])+'\t')
	    file.write('\n')
#sorted
      else:
         #header latex tabular
	 file.write('\\'+'begin{tabular}{|')
         for i in data['llaves']:
            file.write('c|')
         file.write('}\n')
	 file.write('\hline \n')
	 c=1
	 for i in data['llaves']:
	    file.write(str(i))
	    if c < len(data['llaves']): file.write('&')
	    c+=1
	 file.write('\\\ \n')
	 file.write('\hline \n')
	 file.write('\hline \n')
	 
         utiles=data['llaves']
         if lineas:
	    jj=lineas
	 else:
	    jj=range(len(data[utiles[0]]))
	 for j in jj:
	    c=1
	    for i in utiles:
	       file.write(str(data[i][j]))
	       if c < len(utiles): file.write('&')
	       c+=1
	    file.write('\\\ \n')
	    file.write('\hline \n')
         file.write('\end{tabular}')
   else:
#unsorted
      utiles=data.keys()
      c=0
      for i in utiles:
         file.write('# '+str(c+1)+' '+i+'\n')
         c+=1
      if lineas:
         jj=lineas
      else:
         jj=range(len(data[utiles[0]]))
      for j in jj:
	 for i in utiles:
	    file.write(str(data[i][j])+'\t')
	 file.write('\n')
      
   file.close()	    
   return 'Data in: "'+str(filename)+'"'
      
def addcol(cat,name,data,com=0,s=0) :
    """addcol(cat,name,data,com=0,s=0) -> Adds a column to a catalog
    
      cat=var with a catalog read by readcat or rcat.
      name=column name.
      data=data of the column->same number of elementes as the other columns.
      com=comments
      s=1 columm will be overwrited."""
      
    if not(s):
        try:
            cat['llaves'].index(name)
	    print "Column exists, program will stop."
	    return cat
        except ValueError:
	    pass

    cat[str(name)]=data
    cat['llaves'].append(name)
    if not com:
        cat['comentarios'].append(' ')
	return cat
    else:
        cat['comentarios'].append(com)
        return cat
	
def delcol(cat,name):
   """delcol(cat,name) -> Delete a column of a catalog.
      cat=var with a catalog read by readcat or rcat.
      name=column name."""
   
   try:
      i=cat['llaves'].index(name)
   except ValueError:
      print 'Column "'+str(name)+'" does\'nt exist'
      return cat
   
   del cat[name]
   cat['llaves'].remove(name)
   try:
      del cat['comentarios'][i]
   except ValueError:
      pass
      
   return cat
   
def foi(s):
   """foi(s)-> Search a "." in a string."""
   try:
      s.index('.')
      f=1
   except ValueError:
      f=0
   return f
         
def convf(f,fs=0):
   """convf(f)-> Try to transform a string to float
                 If it fails, it returns the string.
		  fs=1 returns the format."""
   try :
      num=float(f)
      format='f'
   except ValueError:
      num=f
      format='s'
   if fs:
      return num,format
   else:
      return num
         
def convi(i,fs=0):
   """convi(i)-> Try to transform a string to integer
                 If it fails, it returns the string.
		  fs=1 returns the format"""
   try :
      num=int(i)
      format='i'
   except ValueError:
      num=i
      format='s'
   if fs:
      return num,format
   else:
      return num
   
def rcat(filename,f=0) :
   """rcat(filename) -> Returns a dictionary with the names of the
   		columns as keys and the columns are numarrays

      This function reads a SExtractor catalog
      Using f=1 it returns a list with column formats."""	
	
   #reading by lines
   file=open(filename,'r')
   todo=file.readlines()
   file.close()
   
   head=[]; data=[]; headlines=[]; datalines=[]; fl=[]
   i=0
   for linea in todo:
      if string.lstrip(linea)[0:1]=="#" :
         headlines.append(linea)
         head.append(linea.split())
	 fl.append('s')	 
      else:
         datalines.append(linea)
         data.append(linea.split())
         j=0
         for val in data[i]:
	    if foi(data[i][j]):
	       data[i][j],fl[j]=convf(data[i][j],fs=1)
	    else:
	       data[i][j],fl[j]=convi(data[i][j],fs=1)
            j+=1
         i+=1
   
   llaves=[linea[2] for linea in head]
   coments=[linea[3:] for linea in head]
   
   tabla={}

   i=0
   for llave in llaves :
      col=[]
      for jj in data :
         col.append(jj[i])
      if fl[i]=='s':
         tabla[llave]=col
      else:
         try:
	    tabla[llave]=numarray.asarray(col)
         except:
	    tabla[llave]=col
      i+=1
   
   tabla['llaves']=llaves
   tabla['comentarios']=coments
      
   for cuidado in data :
      if len(llaves)!=len(cuidado) :
         print "--------------------------------------------------------"
         print "Warning: Some columns haven't got name or are empties!"
	 print "Check the result."
         print "--------------------------------------------------------"
         break
   if f:
      return tabla, fl
   else:
      return tabla   

def newcat(name, data, com=0):
   """newcat(name,data,com=0) -> new catalog using "data"
   
      name=name of the column.
      com=comments."""
      
   tabla={}
   tabla['llaves']=[str(name)]
   if com:
      tabla['comentarios']=[com]
   else:
      tabla['comentarios']=[' ']
   tabla[str(name)]=data
   
   return tabla

def sql2cat(headlines,datalines):
   """sql2cat(headlines,datalines) -> Returns a catalog using MySQL output
   
      headlines=tuple obtained from "describe cat" and "fetchall"
      datalines=tuple obtained from "select * from cat" and "fetchall"
      
      For more information see MySQLdb module."""

   data=[]
   for linea in datalines: data.append(list(linea))

   llaves=[linea[0] for linea in headlines]
   tipos=[linea[1] for linea in headlines]

   tabla={}

   i=0
   for llave in llaves:
      col=[]
      for jj in data:
         col.append(jj[i])
      if string.lstrip(tipos[i][0:7])=='varchar':
         tabla[llave]=col
      else:
         tabla[llave]=numarray.asarray(col)
      i+=1

   tabla['llaves']=llaves
   
   return tabla

def cat2sql(cat,sqlcursor,catname=0):
   """cat2sql(cat,sqlcursor,catname) -> Writes a MySQL table from a catalog.
   
      cat=filename of the catalog.
      sqlcursor=cursor for sql (see MySQLdb).
      catname=name of the table."""
      
   a,fa=rcat(cat,f=1)
   
   if catname: name=catname
   else: name=str(cat[0:string.find(cat,".cat")])

   #creating table
   ffa=[]
   for i in range(len(fa)):
      if fa[i]=="i": ffa.append("int")
      if fa[i]=="f": ffa.append("double")
      if fa[i]=="s":
         longitud=len(a[a["llaves"][i]][0])
         ffa.append("varchar("+str(longitud)+")") #variable length

   comando="create table "+str(name)+"("
   i=0
   for j in a["llaves"]:
      comando=comando+j+" "+ffa[i]+", "
      i+=1

   comando=comando[:-2]+");"
   sqlcursor.execute(comando)

   #insert into table
   utiles=a['llaves']
   jj=range(len(a[utiles[0]]))
   for j in jj:
      p=""
      for i in utiles:
         p=p+"'"+str(a[i][j])+"'"+", "
      p=p[:-2]
      sqlcursor.execute("insert into "+str(name)+" values ("+p+");")

   return

def text2cat(texto,f=0) :
# New function to transform text lines into a catalogue
#
   """text2cat(texto,f=0) -> Returns a catalogue from the result of readlines()
   			in a catalogue type file.
   
      f=1 returns also a list with formats of the columns"""	
	
   #reading lines
   todo=texto
   
   head=[]; data=[]; headlines=[]; datalines=[]; fl=[]
   i=0
   for linea in todo:
      if string.lstrip(linea)[0:1]=="#" :
         headlines.append(linea)
         head.append(linea.split())
	 fl.append('s')	 
      else:
         datalines.append(linea)
         data.append(linea.split())
         j=0
         for val in data[i]:
	    if foi(data[i][j]):
	       data[i][j],fl[j]=convf(data[i][j],fs=1)
	    else:
	       data[i][j],fl[j]=convi(data[i][j],fs=1)
            j+=1
         i+=1
   
   llaves=[linea[2] for linea in head]
   coments=[linea[3:] for linea in head]
   
   tabla={}

   i=0
   for llave in llaves :
      col=[]
      for jj in data :
         col.append(jj[i])
      if fl[i]=='s':
         tabla[llave]=col
      else:
         try:
	    tabla[llave]=numarray.asarray(col)#ltoarr(col,f)
         except:
	    tabla[llave]=col
      i+=1
   
   tabla['llaves']=llaves
   tabla['comentarios']=coments
      
   for cuidado in data :
      if len(llaves)!=len(cuidado) :
         print "--------------------------------------------------------"
         print "Warning: Some columns haven't got name or are empties!"
	 print "Check the result."
         print "--------------------------------------------------------"
         break
   if f:
      return tabla, fl
   else:
      return tabla
