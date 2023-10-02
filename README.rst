################
Triangle Mesh IO
################
|TestStatus| |PyPiStatus| |BlackStyle|


Supports ``.obj`` object-wavefront, ``.off`` object-file-format,  and ``.stl``
stereo-litographie (both binary and ascii).
This pyhton-package serializes meshes of triangles from a python-dict into
a string (``dumps()``) or deserializes meshes of triangles from a string
(``loads()``) into a pyhton-dict.


************
Installation
************

.. code-block:: bash

    pip install triangle_mesh_io


*********
Functions
*********

For each file-format, ``triangle_mesh_io`` provides four basic functions:


-  ``init()`` Initializes an empty python-dict to hold the meshes/triangles.

-  ``loads(s)`` Loads the meshes/triangles from a string into a python-dict.

-  ``dumps(o)`` Dumps the meshes/triangles from a python-dict into a string.

-  ``diff(a, b)`` Lists differences between two meshes ``a``, and ``b``.


However, ``triangle_mesh_io`` does not convert between mesh-formats.
The features of the formats are very different: ``obj >> off >> stl``.
Becasue of this, the conversion between formats is highly dependend on the
use and can not be generalized. Thus, the python-dicts for the individual
formats are not the same. Each represents its file-format.


*******
Formats
*******

+--------------------------+------------+------------+------------+
|                          |  ``.obj``  |  ``.off``  |  ``.stl``  |
+==========================+============+============+============+
| can subdivide a meshe    |Yes (usemtl)|No          |No          |
+--------------------------+------------+------------+------------+
| can have surface-normals |Yes (vn)    |No          |Depends     |
+--------------------------+------------+------------+------------+
| can define a mesh        |Yes         |Yes         |No          |
+--------------------------+------------+------------+------------+


Defining a mesh is about defining relations between triangles (a.k.a. faces).
Unfortunately ``stl`` is just a list of coordinates of triangles.
Thus in ``stl`` possible neighboring-relations between triangles must be
discoverd in an additional search based on their spatial positions.


While ``stl`` has a surface-normal in its format, it is unfortunately
effectively only ever used as a kind of checksum for the triangle which it is
related to.
Most programs will not accept surface-normals which differ from the computed
normal of the corresponding triangel.


In general: When surface-normals are important to you, because you e.g.
simulate optical surfaces such as lenses: Use ``obj``.
When you want to define meshes of triangles which can reference more than one
surface (which can subdivide a mesh): Use ``obj``.
In all other cases you can already reduce down to ``off`` and stick to ``off``
as long as you are forced to reduce further down to ``stl`` in a final
export of your work-flow.


.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/triangle_mesh_io/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/triangle_mesh_io/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/triangle_mesh_io
    :target: https://pypi.org/project/triangle_mesh_io

.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

