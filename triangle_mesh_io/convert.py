import numpy as np
import io
from . import obj as _obj
from . import off as _off
from . import stl as _stl


def off2obj(off, mtl="NAME_OF_MATERIAL"):
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
    return init_obj_from_vertices_and_faces_only(
        vertices=off["v"], faces=off["f"], mtl=mtl
    )


def init_obj_from_vertices_and_faces_only(
    vertices, faces, mtl="NAME_OF_MATERIAL"
):
    """
    Returns a wavefron-dictionary.
    Vertext-normals 'vn' are created based on the faces surface-normals.
    The wavefront has only one material 'mtl' named 'mtl'.

    Parameters
    ----------
    vertices : list/array of vertices
        The 3D-vertices of the mesh.
    faces : list/array of faces
        The faces (triangles) which reference 3 vertices each.
    mtl : str
        The name of the only material in the output wavefront.
    """
    all_vns = _make_normals_from_faces(vertices=vertices, faces=faces)
    unique_vns, unique_vn_map = _group_normals(all_vns)

    wavefront = _obj.init()
    wavefront["mtl"][mtl] = []

    for v in vertices:
        wavefront["v"].append(v)

    for vn in unique_vns:
        wavefront["vn"].append(vn)

    for i in range(len(faces)):
        face = faces[i]
        ff = {}
        fv = [face[0], face[1], face[2]]

        ff["v"] = fv
        unique_vn_i = unique_vn_map[i]
        fvn = [unique_vn_i, unique_vn_i, unique_vn_i]

        ff["vn"] = fvn
        wavefront["mtl"][mtl].append(ff)

    return wavefront


def _make_normal_from_face(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    a_to_b = b - a
    a_to_c = c - a
    n = np.cross(a_to_b, a_to_c)
    n = n / np.linalg.norm(n)
    return n


def _make_normals_from_faces(vertices, faces):
    normals = []
    for f in faces:
        a = vertices[f[0]]
        b = vertices[f[1]]
        c = vertices[f[2]]
        n = _make_normal_from_face(a=a, b=b, c=c)
        normals.append(n)
    return normals


def _group_normals(normals):
    """
    Identify equal normals so that those can be shared by faces.
    This reduces storage space in obj-files and accelerates raytracing.
    """
    nset = set()
    unique_normals = []
    unique_map = []
    unique_i = -1
    for i in range(len(normals)):
        normal = normals[i]
        ntuple = (normal[0], normal[1], normal[2])
        if ntuple not in nset:
            nset.add(ntuple)
            unique_i += 1
            unique_normals.append(normal)
        unique_map.append(unique_i)

    return unique_normals, unique_map
