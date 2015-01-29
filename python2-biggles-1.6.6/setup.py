#!/usr/bin/env python
#
# $Id: setup.py,v 1.34 2010/04/09 21:28:15 mrnolta Exp $
#
# Copyright (C) 2001-10 :
#
#	Berthold Hollmann <bhoel@starship.python.net>
#	Mike Nolta <mrnolta@users.sourceforge.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA  02111-1307, USA.
#

#
# distutils setup file for biggles originally contributed
# by Berthold Hollmann.
#

from distutils.core import setup, Extension
from distutils.command.install_data import install_data
from distutils.sysconfig import get_python_inc
import distutils.log
import sys, os, os.path

# include/library directories
# if None, setup will try to discover the correct value automatically
plot_h_dir  = None  # dir containing plot.h (from plotutils)
libplot_dir = None  # dir containing libplot.so (from plotutils)
libX11_dir  = None  # dir containing libX11.so

def search_for_file( name, dirs ):
	for dir in dirs:
		if not os.path.isdir( dir ):
			continue
		fn = os.path.join( dir, name )
		if os.path.exists(fn):
			return dir
	#print "%s not found" % name
	return None

def search_for_library( name, dirs ):
	extns = ['a','so','dylib']
	for extn in extns:
		dir = search_for_file( 'lib'+name+'.'+extn, dirs )
		if dir is not None:
			return dir
	#print "lib%s not found" % name
	return None

def dir_ends_in( dir, x ):
	# returns True is dir is of the form "/../../x"
	head,tail = os.path.split( dir )
	if tail == '':
		head,tail = os.path.split( head )
	if tail == x:
		return True
	return False

_biggles_module_inc_dirs = []
libplot_module_inc_dirs = []
libplot_module_lib_dirs = []

if sys.platform == "win32":

	libplot_module_libs = ["plot.dll"]

else:
	try:
		import numpy
		numpy_inc_dir = numpy.get_include()
		_biggles_module_inc_dirs.append( numpy_inc_dir )
		libplot_module_inc_dirs.append( numpy_inc_dir )
	except:
		print "numpy module not found; add /path/to/numpy to PYTHONPATH"

	candidate_dirs = [
		'/usr',
		'/usr/X11R6',
		sys.prefix,
	]

	if 'LD_LIBRARY_PATH' in os.environ:
		for dir in os.environ['LD_LIBRARY_PATH'].split(':'):
			head,tail = os.path.split( dir )
			if tail == '':
				head,tail = os.path.split( head )
			if tail == 'lib' or tail == 'lib64':
				candidate_dirs.append( head )

	candidate_dirs.append( '/usr/local' )

	candidate_lib_dirs = []
	for dir in candidate_dirs:
		candidate_lib_dirs.append( os.path.join(dir,'lib') )
		candidate_lib_dirs.append( os.path.join(dir,'lib64') )

	candidate_inc_dirs = []
	for dir in candidate_dirs:
		candidate_inc_dirs.append( os.path.join(dir,'include') )

	if plot_h_dir is None:
		plot_h_dir = search_for_file( 'plot.h', candidate_inc_dirs )
		print "found plot.h in %s" % plot_h_dir
	if libplot_dir is None:
		libplot_dir = search_for_library( 'plot', candidate_lib_dirs )
		print "found libplot in %s" % libplot_dir
	if libX11_dir is None:
		libX11_dir = search_for_library( 'X11', candidate_lib_dirs )
		print "found libX11 in %s" % libX11_dir

	if plot_h_dir is not None:
		libplot_module_inc_dirs.append( plot_h_dir )
	else:
		print 'unable to find plot.h; add "-I/path/to/plot.h"'

	if libplot_dir is not None:
		libplot_module_lib_dirs.append( libplot_dir )
	else:
		print 'unable to find libplot; add "-L/path/to/libplot"'

	if libX11_dir is not None:
		libplot_module_lib_dirs.append( libX11_dir )
	else:
		print 'unable to find plot.h; add "-L/path/to/libX11"'

	#_biggles_module_inc_dirs = [ numpy_inc_dir ]
	#libplot_module_inc_dirs = [ plot_h_dir, numpy_inc_dir ]
	#libplot_module_lib_dirs = [ libplot_dir, libX11_dir ]

	libplot_module_libs = ["plot","Xaw","Xmu","Xt","SM","ICE","Xext","X11"]

# own install_data class to allow installation of data file
# (config.ini) to biggles directory

class my_install_data( install_data ):

	def finalize_options( self ):
		self.set_undefined_options( "install", \
			( "install_lib", "install_dir" ), \
			( "root", "root" ), \
			( "force", "force" ), \
		)

long_description = """\
Biggles is a Python module for creating publication-quality 2D scientific
plots. It supports multiple output formats (postscript, x11, png, svg, gif),
understands simple TeX, and sports a high-level, elegant interface. It's
intended for technical users with sophisticated plotting needs.
"""

setup(
	# Distribution meta-data

	name		= "python2-biggles",
	version		= "1.6.6",
	author		= "Mike Nolta",
	author_email	= "mike@nolta.net",
	url		= "http://biggles.sourceforge.net/",
	license		= "GPL",
	description	= "scientific plotting module",
	long_description= long_description,

	# Description of the modules and packages in the distribution

	packages	= [ "biggles", "biggles.libplot" ],
	package_dir	= { "biggles" : "src" },

	ext_package	= "biggles",
	ext_modules	= [
		Extension( "_biggles",
			["src/_biggles.c"],
			include_dirs = _biggles_module_inc_dirs ),

		Extension( "libplot.libplot",
			["src/libplot/libplot.c"],
			include_dirs = libplot_module_inc_dirs,
			library_dirs = libplot_module_lib_dirs,
			libraries = libplot_module_libs ), 
	],

	cmdclass	= { "install_data" : my_install_data },
	data_files	= [ ("biggles", ["src/config.ini"]) ]
)

# vim: sts=8 sw=8 noexpandtab
