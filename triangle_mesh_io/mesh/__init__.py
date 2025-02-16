from . import cluster
from . import normal
from . import graph
from . import artifacts
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
    vertices, faces = artifacts.remove_artifacts_from_vertices_and_faces(
        vertices=vertices, faces=faces
    )

    if vertex_eps is None:
        vertex_eps = 1e-5 * cluster.guess_68_percent_containment_width_3d(
            xyz=vertices
        )
    faces = make_faces_use_commen_vertices(
        vertices=vertices, faces=faces, vertex_eps=vertex_eps
    )

    vertices, faces = artifacts.remove_artifacts_from_vertices_and_faces(
        vertices=vertices, faces=faces
    )

    try:
        faces_sharing_at_least_one_edge = (
            graph.find_faces_sharing_at_least_one_edge(faces=faces)
        )
        flood = graph.Flood(
            faces=faces,
            faces_sharing_at_least_one_edge=faces_sharing_at_least_one_edge,
        )
        flood.flood()
        faces = flood.wound_faces
    except Exception as err:
        print(err)
        print(
            "Failed to enforce consistent (same) winding direction of "
            "vertices for faces which are part of the same surface manifold."
        )

    return vertices, faces


def make_faces_use_commen_vertices(vertices, faces, vertex_eps):
    clusters = cluster.find_clusters(x=vertices, eps=vertex_eps)
    vertex_replacement_map = cluster.find_replacement_map(
        x=vertices, clusters=clusters
    )

    return apply_vertex_replacement_map_to_faces(
        faces=faces,
        vertex_replacement_map=vertex_replacement_map,
    )


def apply_vertex_replacement_map_to_faces(faces, vertex_replacement_map):
    new_faces = -1 * np.ones(shape=faces.shape, dtype=int)
    for face_idx in range(faces.shape[0]):
        vertex_0_idx, vertex_1_idx, vertex_2_idx = faces[face_idx]
        new_faces[face_idx] = [
            vertex_replacement_map[vertex_0_idx],
            vertex_replacement_map[vertex_1_idx],
            vertex_replacement_map[vertex_2_idx],
        ]
    return new_faces


def make_faces_use_commen_vertex_normals(obj, vertex_normal_eps):
    clusters = cluster.find_clusters(x=obj["vn"], eps=vertex_normal_eps)
    vn_map = cluster.find_replacement_map(x=obj["vn"], clusters=clusters)

    mtl = apply_vertex_normal_replacement_map_to_materials(
        materials=obj["mtl"],
        vertex_normal_replacement_map=vn_map,
    )
    out = {"v": copy.copy(obj["v"]), "vn": copy.copy(obj["vn"]), "mtl": mtl}
    return artifacts.remove_vertex_normals_which_are_not_used_by_faces(obj=out)


def apply_vertex_normal_replacement_map_to_materials(
    materials, vertex_normal_replacement_map
):
    new_materials = {}
    for mtl in materials:
        new_materials[mtl] = []

        for face_idx in range(len(materials[mtl])):
            old_face = materials[mtl][face_idx]
            old_vn_0_idx, old_vn_1_idx, old_vn_2_idx = old_face["vn"]

            new_face = {}
            new_face["v"] = old_face["v"]
            new_face["vn"] = [
                vertex_normal_replacement_map[old_vn_0_idx],
                vertex_normal_replacement_map[old_vn_1_idx],
                vertex_normal_replacement_map[old_vn_2_idx],
            ]
            new_materials[mtl].append(new_face)

    return new_materials


def _init_obj_from_vertices_and_faces_only(
    vertices,
    faces,
    mtl="NAME_OF_MATERIAL",
    vertex_eps=None,
    vertex_normal_eps=np.deg2rad(1e-9),
    vertex_normal_smooth_eps=np.deg2rad(2.5),
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
            if vertex_normal_smooth_eps > 0.0:
                vn = normal.estimate_vertex_normal_based_on_neighbors(
                    vertex_idx=face[vdim],
                    face_idx=face_idx,
                    face_normals=face_normals,
                    vertices_to_faces=vertices_to_faces,
                    vertex_normal_smooth_eps=vertex_normal_smooth_eps,
                )
            else:
                vn = face_normals[face_idx]

            wavefront["vn"].append(vn)
            fvn[vdim] = vn_count
            vn_count += 1

        ff["vn"] = fvn
        wavefront["mtl"][mtl].append(ff)

    try:
        wavefront = make_faces_use_commen_vertex_normals(
            obj=wavefront, vertex_normal_eps=vertex_normal_eps
        )
    except Exception as err:
        print(err)
        print(
            "Failed to enforce consistent (same) winding direction of "
            "vertices for faces which are part of the same surface manifold."
        )

    return wavefront
