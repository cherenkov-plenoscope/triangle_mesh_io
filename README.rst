################
Triangle Mesh IO
################
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|



Supports ``.obj`` object wavefront, ``.off`` object file format,  and ``.stl``
stereo litographie (both binary and ascii).
This pyhton package serializes meshes of triangles from a python dict into
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

For each file-format, ``triangle_mesh_io`` provides five basic functions:


- ``m = loads(s)`` Loads the meshes/triangles from a string into a python dict.

- ``s = dumps(m)`` Dumps the meshes/triangles from a python dict into a string.

- ``l = diff(m1, m2)`` Lists differences ``l`` between two meshes ``m1``, and ``m2``.

- ``m = init()`` Initializes an empty python dict to hold the meshes/triangles.

- ``m = minimal()`` Initializes a cube (1,1,1) as a minimal example of a populated dict.


*******
Example
*******

.. code-block:: python

    import triangle_mesh_io as tmi

    m = tmi.obj.minimal()
    print(m)


.. code-block::

    {'v': [[1.0, 0.0, 0.0],
      [1.0, 1.0, 0.0],
      [0.0, 1.0, 0.0],
      [0.0, 0.0, 0.0],
      [1.0, 0.0, 1.0],
      [1.0, 1.0, 1.0],
      [0.0, 1.0, 1.0],
      [0.0, 0.0, 1.0]],
     'vn': [[1.0, 0.0, 0.0],
      [0.0, 1.0, 0.0],
      [0.0, 0.0, 1.0],
      [-1.0, 0.0, 0.0],
      [0.0, -1.0, 0.0],
      [0.0, 0.0, -1.0]],
     'mtl': {'pos-x': [{'v': [0, 1, 5], 'vn': [0, 0, 0]},
       {'v': [5, 4, 0], 'vn': [0, 0, 0]}],
      'pos-y': [{'v': [1, 2, 5], 'vn': [1, 1, 1]},
       {'v': [5, 2, 6], 'vn': [1, 1, 1]}],
      'pos-z': [{'v': [4, 5, 6], 'vn': [2, 2, 2]},
       {'v': [6, 7, 4], 'vn': [2, 2, 2]}],
      'neg-x': [{'v': [2, 6, 3], 'vn': [3, 3, 3]},
       {'v': [6, 7, 3], 'vn': [3, 3, 3]}],
      'neg-y': [{'v': [0, 3, 7], 'vn': [4, 4, 4]},
       {'v': [7, 4, 0], 'vn': [4, 4, 4]}],
      'neg-z': [{'v': [0, 1, 2], 'vn': [5, 5, 5]},
       {'v': [2, 3, 0], 'vn': [5, 5, 5]}]}}


.. code-block:: python

       s = tmi.obj.dumps(m)
       print(s)


.. code-block::

    # vertices
    v 1.000000 0.000000 0.000000
    v 1.000000 1.000000 0.000000
    v 0.000000 1.000000 0.000000
    v 0.000000 0.000000 0.000000
    v 1.000000 0.000000 1.000000
    v 1.000000 1.000000 1.000000
    v 0.000000 1.000000 1.000000
    v 0.000000 0.000000 1.000000
    # vertex-normals
    vn 1.000000 0.000000 0.000000
    vn 0.000000 1.000000 0.000000
    vn 0.000000 0.000000 1.000000
    vn -1.000000 0.000000 0.000000
    vn 0.000000 -1.000000 0.000000
    vn 0.000000 0.000000 -1.000000
    # faces
    usemtl pos-x
    f 1//1 2//1 6//1
    f 6//1 5//1 1//1
    usemtl pos-y
    f 2//2 3//2 6//2
    f 6//2 3//2 7//2
    usemtl pos-z
    f 5//3 6//3 7//3
    f 7//3 8//3 5//3
    usemtl neg-x
    f 3//4 7//4 4//4
    f 7//4 8//4 4//4
    usemtl neg-y
    f 1//5 4//5 8//5
    f 8//5 5//5 1//5
    usemtl neg-z
    f 1//6 2//6 3//6
    f 3//6 4//6 1//6


.. code-block:: python

       m_back = tmi.obj.loads(s)
       assert len(tmi.obj.diff(m, m_back)) == 0


*******
Formats
*******

``triangle_mesh_io`` has only limited features to convert between mesh formats.
The formats are very different and the amount of information is roughly:
``obj >> off >> stl``.
Thus the python dicts for the individual
formats are not the same. Each dict-format follows its corresponding
file format.


+--------------------------+------------+------------+------------+
|                          |  ``.obj``  |  ``.off``  |  ``.stl``  |
+==========================+============+============+============+
| can subdivide a mesh     |Yes (usemtl)|No          |No          |
+--------------------------+------------+------------+------------+
| can have surface-normals |Yes (vn)    |No          |Depends     |
+--------------------------+------------+------------+------------+
| can define a mesh        |Yes         |Yes         |No          |
+--------------------------+------------+------------+------------+


Defining a mesh is about defining relations between triangles (a.k.a. faces).
Unfortunately ``stl`` is just a list of coordinates of triangles.
Thus in ``stl``, possible neighboring-relations between triangles must be
discoverd in an additional search based on the triangles positions.


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

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
