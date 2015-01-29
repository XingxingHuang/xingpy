revised



http://sexcat.sourceforge.net

SExCaT: python module to read and write SExtractor catalogs.

It uses a dictionary with the names of the columns as the keys.

It needs "string" and "numarray" modules

05/09/05
davidabreu@users.sourceforge.net

David Abreu

--------------------------------------------------------------------------------

Instalation:
------------

Copy the file "sexcat.py" into your working directory or in $PYTHONPATH

Use:
----

To read SExtractor catalogs
All the columns must have a name

Examples:
---------

import sexcat
data=sexcat.rcat("file.cat")
print data["llaves"] # List with all the column names
print data["X_IMAGE"] # Content of the column with name "X_IMAGE"

For more examples or suggestions, you can write me to
"davidabreu@users.sourceforge.net"

Good luck!
