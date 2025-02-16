from . import mesh as _mesh
from . import obj as _obj
from . import off as _off
from . import stl as _stl
import numpy as np


def stl_to_obj(
    stl,
    mtl="NAME_OF_MATERIAL",
    vertex_eps=None,
    vertex_normal_eps=0.0,
    vertex_normal_smooth_eps=np.deg2rad(2.5),
):
    """
    Returns a wavefron-dictionary from an Stereolithography triangle list.

    Parameters
    ----------
    stl : numpy.recarray with dtype=triangle_medh_io.stl._dtype()
        Contains the faces and their vertices defined in the Stereolithography
        triangle list.
    mtl : str
        The key given to the material in the output wavefront.
    """
    vertices, faces = _stl.to_vertices_and_faces(stl=stl)
    return _mesh.init_from_vertices_and_faces_with_vertex_normals(
        vertices=vertices,
        faces=faces,
        mtl=mtl,
        vertex_eps=vertex_eps,
        vertex_normal_eps=vertex_normal_eps,
        vertex_normal_smooth_eps=vertex_normal_smooth_eps,
    )


def off_to_obj(
    off,
    mtl="NAME_OF_MATERIAL",
    vertex_eps=None,
    vertex_normal_eps=0.0,
    vertex_normal_smooth_eps=np.deg2rad(2.5),
):
    """
    Returns a wavefron-dictionary from an Object-File-Format-dictionary.

    Parameters
    ----------
    off : dict
        Contains the vertices 'v' and the faces 'f' present in the
        Object-File-Format.
    mtl : str
        The key given to the material in the output wavefront.
    """

    vertices, faces = _off.to_vertices_and_faces(off=off)
    return _mesh.init_from_vertices_and_faces_with_vertex_normals(
        vertices=vertices,
        faces=faces,
        mtl=mtl,
        vertex_eps=vertex_eps,
        vertex_normal_eps=vertex_normal_eps,
        vertex_normal_smooth_eps=vertex_normal_smooth_eps,
    )
