/*
 * $Id: _biggles.c,v 1.19 2007/04/19 15:51:46 mrnolta Exp $ 
 *
 * Copyright (C) 2001 Mike Nolta <mrnolta@users.sourceforge.net>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with this program; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA  02111-1307, USA.
 *
 */

#include <Python.h>
#include <math.h>
#include <numpy/arrayobject.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define PyArray_1D(v,i)\
	(*((double *)((v)->data+(i)*(v)->strides[0])))

#define PyArray_1D_ptr(v,i)\
	((double *)((v)->data+(i)*(v)->strides[0]))

#define PyArray_2D(m,i,j)\
	(*((double *)((m)->data+(i)*(m)->strides[0]+(j)*(m)->strides[1])))

/*
 *  I wish min/max(z) worked.
 */

#define BGL_MIN(a,b) (((a) < (b)) ? (a) : (b))
#define BGL_MAX(a,b) (((a) > (b)) ? (a) : (b))

static PyObject *
biggles_range( PyObject *self, PyObject *args )
{
	PyObject *input;
	PyArrayObject *x;
	int i, n;
	double *dp, min, max;

	if ( !PyArg_ParseTuple(args, "O", &input) )
		return NULL;

	x = (PyArrayObject *)
		PyArray_ContiguousFromObject( input, PyArray_DOUBLE, 0, 0 );
	if ( x == NULL )
		return NULL;

	n = PyArray_Size( input );
	dp = (double *) x->data;

	min = max = dp[0];
	for ( i = 1; i < n; i++ )
	{
		min = BGL_MIN( min, dp[i] );
		max = BGL_MAX( max, dp[i] );
	}
	
	Py_DECREF(x);
	return Py_BuildValue( "dd", min, max );
}

/******************************************************************************
 *  contour.py
 *
 *  The problem is, given a 2D matrix, draw isocontours. This is
 *  basically an exercise in interpolation, considering the matrix
 *  to be the values of a function sampled on a regular grid.
 *
 *  So it boils down to how best to interpolate a 2D function over
 *  a rectangular area given only the values at the corners.
 *
 *  The simplest solution would be a plane, but 4 points aren't
 *  necessarily coplanar. And the next simplest smooth function,
 *  a quadratic, is underdetermined. The "solution" seems to be
 *  to add a fifth point, the average of the four corner points.
 *
 *
 *    z[i,j+1] = p1 o-----------o p2 = z[i+1,j+1]
 *                  | +       + |
 *                  |   +   +   |
 *                  |     o <---+--- p4 = average(p0,p1,p2,p3)
 *                  |   +   +   |
 *                  | +       + |
 *      z[i,j] = p0 o-----------o p3 = z[i+1,j]
 *
 *
 *  This breaks the square up into four simplicies (triangles),
 *  each of which defines a plane. The algorithm is then simply
 *  figure out whether the simplex intersects the desired plane
 *  and ifso add a line segment to the render list.
 *
 *  Downside is that the output is a bunch of tiny unconnected line
 *  segments, which bloats postscript files and slows down rendering.
 *  Have to connect the dots at some point.
 *
 */
 
#define MAX_SEGS 4

static int
_find_zero( double p[3], double q[3], double zero[2] )
{
	double a;

	if ( p[2] == 0. )
	{
		zero[0] = p[0];
		zero[1] = p[1];
		return 1;
	}
	else if ( p[2]*q[2] < 0. )
	{
		a = p[2]/(p[2] - q[2]);
		zero[0] = p[0] + a*(q[0] - p[0]);
		zero[1] = p[1] + a*(q[1] - p[1]);
		return 1;
	}

	return 0;
}

static int
_pixel_interpolate( PyArrayObject *x, PyArrayObject *y, PyArrayObject *z,
	double z0, int i, int j, double segs[MAX_SEGS][4] )
{
	int k, l, ii, jj, kk;
	double p[5][3], zeros[3][2];
	int nz, ns;

	for ( l = 0; l < 3; l++ )
		p[4][l] = 0.;

	for ( k = 0; k < 4; k++ )
	{
		ii = i + (k/2 % 2);
		jj = j + ((k+1)/2 % 2);

		p[k][0] = PyArray_1D(x,ii);
		p[k][1] = PyArray_1D(y,jj);
		p[k][2] = PyArray_2D(z,ii,jj) - z0;

		for ( l = 0; l < 3; l++ )
			p[4][l] += 0.25 * p[k][l];
	}

	ns = 0;

	for ( k = 0; k < 4; k++ )
	{
		kk = (k + 1) % 4;

		nz = 0;
		nz += _find_zero( p[4], p[k], zeros[nz] );
		nz += _find_zero( p[k], p[kk], zeros[nz] );
		nz += _find_zero( p[kk], p[4], zeros[nz] );

		if ( nz == 2 )
		{
			segs[ns][0] = zeros[0][0];
			segs[ns][1] = zeros[0][1];
			segs[ns][2] = zeros[1][0];
			segs[ns][3] = zeros[1][1];
			ns++;
		}
	}

	return ns;
}

static PyObject *
biggles_contour_segments( PyObject *self, PyObject *args )
{
	PyObject *ox, *oy, *oz, *list, *ref;
	PyArrayObject *x, *y, *z;
	double z0;
	double segs[MAX_SEGS][4];
	int i, j, k, ns;

	list = NULL;

	if ( !PyArg_ParseTuple(args, "OOOd", &ox, &oy, &oz, &z0) )
		return NULL;

	x = (PyArrayObject *)
		PyArray_ContiguousFromObject( ox, PyArray_DOUBLE, 1, 1 );
	y = (PyArrayObject *)
		PyArray_ContiguousFromObject( oy, PyArray_DOUBLE, 1, 1 );
	z = (PyArrayObject *)
		PyArray_ContiguousFromObject( oz, PyArray_DOUBLE, 2, 2 );

	if ( x == NULL || y == NULL || z == NULL )
		goto quit;

	if ( z->dimensions[0] != x->dimensions[0] ||
	     z->dimensions[1] != y->dimensions[0] )
	{
		PyErr_SetString( PyExc_ValueError,
			"array dimensions are not compatible" );
		goto quit;
	}

	list = PyList_New( 0 );
	if ( list == NULL )
		goto quit;

	for ( i = 0; i < z->dimensions[0]-1; i++ )
	for ( j = 0; j < z->dimensions[1]-1; j++ )
	{
		ns = _pixel_interpolate( x, y, z, z0, i, j, segs );
		for ( k = 0; k < ns; k++ )
		{
			ref = Py_BuildValue( "((dd)(dd))",
				segs[k][0], segs[k][1],
				segs[k][2], segs[k][3] );
			PyList_Append( list, ref );
			Py_DECREF(ref); /* ??? */
		}
	}

quit:
	Py_XDECREF(x);
	Py_XDECREF(y);
	Py_XDECREF(z);
	return list;
}

/******************************************************************************
 *  hammer.py
 */

static void
_lb2xyz( double l, double b,
	double *x, double *y, double *z )
{
	*x = cos(b)*cos(l);
	*y = cos(b)*sin(l);
	*z = sin(b);
}

static void
_xyz2lb( double x, double y, double z,
	double *l, double *b)
{
	*l = atan2( y, x );
	*b = asin( z/sqrt(x*x + y*y + z*z) );
}

static void
_x_rotate( double l, double b, double theta, double *ll, double *bb )
{
	double x, y, z, y2, z2;

	_lb2xyz( l, b, &x, &y, &z );
	y2 = cos(theta)*y - sin(theta)*z;
	z2 = cos(theta)*z + sin(theta)*y;
	_xyz2lb( x, y2, z2, ll, bb );
}

static void
_y_rotate( double l, double b, double theta, double *ll, double *bb )
{
	double x, y, z, x2, z2;

	_lb2xyz( l, b, &x, &y, &z );
	x2 = cos(theta)*x - sin(theta)*z;
	z2 = cos(theta)*z + sin(theta)*x;
	_xyz2lb( x2, y, z2, ll, bb );
}

static void
_z_rotate( double l, double b, double theta, double *ll, double *bb )
{
	*ll = atan2( sin(l+theta), cos(l+theta) );
	*bb = b;
}

static void
_lb_input( double l, double b, double l0, double b0, double rot,
	double *ll, double *bb )
{
	double p, q, r, s;

	_z_rotate( l, b, -l0, &p, &q );
	_y_rotate( p, q, -b0, &r, &s );
	_x_rotate( r, s, rot, ll, bb );
}

static void
_lb2uv( double l, double b, double *u, double *v )
{
	double q;
	q = sqrt( 1. + cos(b)*cos(0.5*l) );
	*u = cos(b)*sin(0.5*l)/q;
	*v = 0.5*sin(b)/q;
}

static PyObject *
biggles_hammer_call( PyObject *self, PyObject *args )
{
	double l, b, l0, b0, rot;
	double ll, bb, u, v;

	if ( !PyArg_ParseTuple(args, "ddddd", &l, &b, &l0, &b0, &rot) )
		return NULL;

	_lb_input( l, b, l0, b0, rot, &ll, &bb );
	_lb2uv( ll, bb, &u, &v );

	return Py_BuildValue( "dd", u, v );
}

static PyObject *
biggles_hammer_call_vec( PyObject *self, PyObject *args )
{
	PyObject *ol, *ob, *ret;
	PyArrayObject *l, *b, *u, *v;
	double l0, b0, rot;
	double ll, bb;
	int i, n;

	ret = NULL;

	if ( !PyArg_ParseTuple(args, "OOddd", &ol, &ob, &l0, &b0, &rot) )
		return NULL;

	l = (PyArrayObject *)
		PyArray_ContiguousFromObject( ol, PyArray_DOUBLE, 1, 1 );
	b = (PyArrayObject *)
		PyArray_ContiguousFromObject( ob, PyArray_DOUBLE, 1, 1 );

	if ( l == NULL || b == NULL )
		goto quit0;

	n = BGL_MIN( l->dimensions[0], b->dimensions[0] );

	u = (PyArrayObject *) PyArray_FromDims( 1, &n, PyArray_DOUBLE );
	v = (PyArrayObject *) PyArray_FromDims( 1, &n, PyArray_DOUBLE );

	if ( u == NULL || v == NULL )
		goto quit1;

	for ( i = 0; i < n; i++ )
	{
		_lb_input( PyArray_1D(l,i), PyArray_1D(b,i),
			l0, b0, rot, &ll, &bb );
		_lb2uv( ll, bb, PyArray_1D_ptr(u,i), PyArray_1D_ptr(v,i) );
	}

	ret = Py_BuildValue( "OO", u, v );

quit1:
	Py_XDECREF(u);
	Py_XDECREF(v);
quit0:
	Py_XDECREF(l);
	Py_XDECREF(b);
	return ret;
}

static void
_lb_geodesic( int div,
	double l0, double b0,
	double l1, double b1,
	double l[], double b[] )
{
	double lr0, br0, lr1, br1;
	double db;
	int i;

	_z_rotate( l1, b1, -l0, &lr0, &br0 );
	_y_rotate( lr0, br0, -b0+M_PI/2, &lr1, &br1 );

	l[0] = l0;
	b[0] = b0;

	db = (br1 - M_PI/2)/div;

	for ( i = 1; i < div; i++ )
	{
		_y_rotate( lr1, M_PI/2 + i*db, -M_PI/2+b0, &lr0, &br0 );
		_z_rotate( lr0, br0, l0, l+i, b+i );
	}

	l[div] = l1;
	b[div] = b1;
}

static PyObject *
biggles_hammer_geodesic_fill( PyObject *self, PyObject *args )
{
	PyObject *ol, *ob, *ref;
	PyArrayObject *l, *b, *l2, *b2;
	int i, n, div, dims[1];

	ref = NULL;

	if ( !PyArg_ParseTuple(args, "OOi", &ol, &ob, &div) )
		return NULL;

	l = (PyArrayObject *)
		PyArray_ContiguousFromObject( ol, PyArray_DOUBLE, 1, 1 );
	b = (PyArrayObject *)
		PyArray_ContiguousFromObject( ob, PyArray_DOUBLE, 1, 1 );

	if ( l == NULL || b == NULL )
	{	
		Py_XDECREF(l);
		Py_XDECREF(b);
		return NULL;
	}

	n = l->dimensions[0];
	dims[0] = (n-1)*div + 1;

	l2 = (PyArrayObject *) PyArray_FromDims( 1, dims, PyArray_DOUBLE );
	b2 = (PyArrayObject *) PyArray_FromDims( 1, dims, PyArray_DOUBLE );

	if ( l2 == NULL || b2 == NULL )
		goto quit;

	for ( i = 0; i < n-1; i++ )
		_lb_geodesic( div,
			PyArray_1D(l,i), PyArray_1D(b,i),
			PyArray_1D(l,i+1), PyArray_1D(b,i+1),
			((double *)l2->data) + i*div,
			((double *)b2->data) + i*div );


	ref = Py_BuildValue( "OO", l2, b2 );
quit:
	Py_DECREF(l);
	Py_DECREF(b);
	Py_XDECREF(l2);
	Py_XDECREF(b2);
	return ref;
}

static PyObject *
biggles_hammer_connect( PyObject *self, PyObject *args )
{
	double l1, b1, l2, b2;
	double l0, b0, rot;
	double ll1, bb1, ll2, bb2;
	int connect;

	if ( !PyArg_ParseTuple(args, "ddddddd",
			&l1, &b1, &l2, &b2, &l0, &b0, &rot) )
		return NULL;

	_lb_input( l1, b1, l0, b0, rot, &ll1, &bb1 );
	_lb_input( l2, b2, l0, b0, rot, &ll2, &bb2 );

	connect = sin(ll1)*sin(ll2) < 0.;

	return Py_BuildValue( "i", connect );
}

/******************************************************************************
 *  module init
 */

static PyMethodDef BigglesMethods[] = 
{
	/* general */
	{ "range", biggles_range, METH_VARARGS },

	/* contour.py */
	{ "contour_segments", biggles_contour_segments, METH_VARARGS },

	/* hammer.py */
	{ "hammer_call", biggles_hammer_call, METH_VARARGS },
	{ "hammer_call_vec", biggles_hammer_call_vec, METH_VARARGS },
	{ "hammer_connect", biggles_hammer_connect, METH_VARARGS },
	{ "hammer_geodesic_fill", biggles_hammer_geodesic_fill, METH_VARARGS },

	{ NULL, NULL }
};

void
init_biggles( void )
{
	Py_InitModule( "_biggles", BigglesMethods );
	import_array();
}
