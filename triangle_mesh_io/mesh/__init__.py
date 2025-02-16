from . import cluster
from . import normal
from . import graph
from .. import obj as _obj
import numpy as np
import warnings
import copy


def init_from_vertices_and_faces(vertices, faces, vertex_eps=None):
    """
    Faces refering to near by vertices (w.r.t. vertex_eps distance) will use
    a single common vertex. Duplicate vertices will be removed.
    Tiny faces which degenerate in this process to have two or more identical
    vertices will be removed, too.
    Vertices are considered duplicates when they are colser than the distance
    'vertex_eps'.

    Parameters
    ----------
    vertices : array like, float, shape(num vertices, 3)
        The vertices of the mesh with their 3D cartesian coordinates.
    faces : array like, int, shape(num faces, 3)
        The faces referencing the vertices by index.
    vertex_eps : float (default: None)
        Vertices closer together than 'vertex_eps' will be considered
        duplicates. If 'None', vertex_eps will be guessed based on the cloud
        of vertices using approx. 1e-5 * a robust estimate for the standard
        deviation of the vertices.
    """
    vertices, faces = remove_artifacts_from_vertices_and_faces(
        vertices=vertices, faces=faces
    )

    faces = make_faces_use_commen_vertices(
        vertices=vertices, faces=faces, vertex_eps=vertex_eps
    )

    vertices, faces = remove_artifacts_from_vertices_and_faces(
        vertices=vertices, faces=faces
    )

    return vertices, faces


def remove_artifacts_from_vertices_and_faces(vertices, faces):
    faces = remove_faces_with_less_than_three_unique_vertices(faces=faces)
    vertices, faces = remove_vertices_which_are_not_used_by_faces(
        vertices=vertices, faces=faces
    )
    return vertices, faces


def make_faces_use_commen_vertices(vertices, faces, vertex_eps):
    if vertex_eps is None:
        vertex_eps = 1e-5 * cluster.guess_68_percent_containment_width_3d(
            xyz=vertices
        )

    clusters = cluster.find_clusters(x=vertices, eps=vertex_eps)

    replace = cluster.find_replacement_map(x=vertices, clusters=clusters)

    new_faces = -1 * np.ones(shape=faces.shape, dtype=int)
    for face_idx in range(faces.shape[0]):
        vertex_0_idx, vertex_1_idx, vertex_2_idx = faces[face_idx]
        new_faces[face_idx] = [
            replace[vertex_0_idx],
            replace[vertex_1_idx],
            replace[vertex_2_idx],
        ]

    return new_faces


def _init_obj_from_vertices_and_faces_only(
    vertices,
    faces,
    mtl="NAME_OF_MATERIAL",
    vertex_eps=None,
    vertex_normal_eps=0.0,
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

    vertices, faces = init_from_vertices_and_faces(
        vertices=vertices, faces=faces, vertex_eps=vertex_eps
    )

    face_normals = normal.make_face_normals_from_vertices_and_faces(
        vertices=vertices, faces=faces
    )

    vertices_to_faces = graph.list_faces_sharing_same_vertex(
        vertices=vertices, faces=faces
    )

    wavefront = _obj.init()
    wavefront["mtl"][mtl] = []

    for v in vertices:
        wavefront["v"].append(v)

    vn_count = 0
    for face_idx in range(faces.shape[0]):
        face = faces[face_idx]
        ff = {}
        ff["v"] = [face[0], face[1], face[2]]

        fvn = [-1, -1, -1]
        for vdim in range(3):
            if vertex_normal_eps > 0.0:
                vn = normal.estimate_vertex_normal_based_on_neighbors(
                    vertex_idx=face[vdim],
                    face_idx=face_idx,
                    face_normals=face_normals,
                    vertices_to_faces=vertices_to_faces,
                    vertex_normal_eps=vertex_normal_eps,
                )
            else:
                vn = face_normals[face_idx]

            omega = normal.angle_between_rad(vn, face_normals[face_idx])
            if omega > np.deg2rad(0.1):
                print(
                    "face ",
                    face_idx,
                    "vertex ",
                    vdim,
                    "dev ",
                    np.rad2deg(omega),
                    "deg.",
                )

            wavefront["vn"].append(vn)
            fvn[vdim] = vn_count
            vn_count += 1

        ff["vn"] = fvn
        wavefront["mtl"][mtl].append(ff)

    return wavefront


def remove_faces_with_less_than_three_unique_vertices(faces):
    """
    Removes faces which only have two or one unique vertices and thus do not
    have a surface in 3D-space.
    """
    out_faces = []

    for face_idx in range(faces.shape[0]):
        face = faces[face_idx]
        num_uniqie_vertices = len(set(face))
        if num_uniqie_vertices == 3:
            out_faces.append(face)
    return np.asarray(out_faces, dtype=int)


def remove_vertices_which_are_not_used_by_faces(vertices, faces):
    out_vertices = []
    out_faces = []
    vertex_use = {}

    for face_idx in range(faces.shape[0]):
        face = faces[face_idx]
        new_face = []
        for vertex_idx in face:
            if vertex_idx not in vertex_use:
                vertex_use[vertex_idx] = len(vertex_use)
                out_vertices.append(vertices[vertex_idx])
            new_face.append(vertex_use[vertex_idx])
        out_faces.append(new_face)
    return np.asarray(out_vertices, dtype=float), np.asarray(
        out_faces, dtype=int
    )
