import numpy as np
import sklearn.cluster
import warnings
import io
import copy
from . import obj as _obj
from . import off as _off
from . import stl as _stl


def stl2obj(
    stl, mtl="NAME_OF_MATERIAL", vertex_eps=None, vertex_normal_eps=0.0
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
    vertices, faces = _stl._to_vertices_and_faces(stl=stl)
    return _init_obj_from_vertices_and_faces_only(
        vertices=vertices,
        faces=faces,
        mtl=mtl,
        vertex_eps=vertex_eps,
        vertex_normal_eps=vertex_normal_eps,
    )


def off2obj(
    off, mtl="NAME_OF_MATERIAL", vertex_eps=None, vertex_normal_eps=0.0
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

    vertices, faces = _off._to_vertices_and_faces(off=off)
    return _init_obj_from_vertices_and_faces_only(
        vertices=vertices,
        faces=faces,
        mtl=mtl,
        vertex_eps=vertex_eps,
        vertex_normal_eps=vertex_normal_eps,
    )


def _prepare_mesh_from_vertices_and_faces(vertices, faces, vertex_eps=None):
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
    faces = _make_faces_use_commen_vertices(
        vertices=vertices, faces=faces, vertex_eps=vertex_eps
    )
    faces = _remove_degenerate_faces(faces=faces)
    vertices, faces = _remove_unused_vertices(vertices=vertices, faces=faces)
    return vertices, faces


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

    vertices, faces = _prepare_mesh_from_vertices_and_faces(
        vertices=vertices, faces=faces, vertex_eps=vertex_eps
    )

    face_normals = _make_face_normals_from_vertices_and_faces(
        vertices=vertices, faces=faces
    )

    vertices_to_faces = _list_faces_sharing_same_vertex(
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
                vn = _estimate_vertex_normal_based_on_neighbors(
                    vertex_idx=face[vdim],
                    face_idx=face_idx,
                    face_normals=face_normals,
                    vertices_to_faces=vertices_to_faces,
                    vertex_normal_eps=vertex_normal_eps,
                )
            else:
                vn = face_normals[face_idx]

            omega = _angle_between_rad(vn, face_normals[face_idx])
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


def _find_clusters(x, eps):
    clustering = sklearn.cluster.DBSCAN(eps=eps).fit(x)

    NOISE = -1

    clusters = {}
    for vertex_i, cluster_i in enumerate(clustering.labels_):
        if cluster_i == NOISE:
            continue

        if cluster_i not in clusters:
            clusters[int(cluster_i)] = [int(vertex_i)]
        else:
            clusters[int(cluster_i)].append(int(vertex_i))

    for cluster_i in clusters:
        clusters[cluster_i] = sorted(clusters[cluster_i])

    return clusters


def _find_replacement_map(vertices, clusters):
    rm = {}
    for cluster_i in clusters:
        first_vertx = clusters[cluster_i][0]
        rm[first_vertx] = first_vertx
        for vertex in clusters[cluster_i][1:]:
            rm[vertex] = first_vertx

    out = -1 * np.ones(shape=vertices.shape[0], dtype=int)
    for vi in range(vertices.shape[0]):
        if vi in rm:
            out[vi] = rm[vi]
        else:
            out[vi] = vi

    return out


def _guess_std_1d(x):
    return np.quantile(x, 0.84) - np.quantile(x, 0.16)


def _guess_std_3d(xyz):
    dx = _guess_std_1d(xyz[:, 0])
    dy = _guess_std_1d(xyz[:, 1])
    dz = _guess_std_1d(xyz[:, 2])
    return np.median([dx, dy, dz])


def _make_faces_use_commen_vertices(vertices, faces, vertex_eps):
    if vertex_eps is None:
        vertex_eps = 1e-5 * _guess_std_3d(xyz=vertices)

    clusters = _find_clusters(x=vertices, eps=vertex_eps)

    replace = _find_replacement_map(vertices=vertices, clusters=clusters)

    nfaces = -1 * np.ones(shape=faces.shape, dtype=int)
    for fi in range(faces.shape[0]):
        iv0, iv1, iv2 = faces[fi]
        nfaces[fi] = [replace[iv0], replace[iv1], replace[iv2]]

    return nfaces


def _remove_degenerate_faces(faces):
    out = []
    for fi in range(faces.shape[0]):
        face = faces[fi]
        num_uniqie_vertices = len(set(face))
        if num_uniqie_vertices == 3:
            out.append(face)

    return np.asarray(out, dtype=int)


def _remove_unused_vertices(vertices, faces):
    nvertices = []
    nfaces = []
    vertex_use = {}

    for fi in range(faces.shape[0]):
        face = faces[fi]
        nface = []
        for vi in face:
            if vi not in vertex_use:
                vertex_use[vi] = len(vertex_use)
                nvertices.append(vertices[vi])
            nface.append(vertex_use[vi])
        nfaces.append(nface)
    return np.asarray(nvertices, dtype=float), np.asarray(nfaces, dtype=int)


def _make_normal_from_face(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    a_to_b = b - a
    a_to_c = c - a
    n = np.cross(a_to_b, a_to_c)
    norm = np.linalg.norm(n)
    if norm <= 1e-9:
        raise RuntimeError
    n = n / norm
    return n


def _make_face_normals_from_vertices_and_faces(vertices, faces):
    normals = []
    for idx, f in enumerate(faces):
        a = vertices[f[0]]
        b = vertices[f[1]]
        c = vertices[f[2]]
        try:
            n = _make_normal_from_face(a=a, b=b, c=c)
            normals.append(n)
        except RuntimeError:
            message = f"face #{idx:d}: a "
            message += str(a)
            message += ", b "
            message += str(b)
            message += ", c "
            message += str(c)
            message += " can not be normalized."
            warnings.warn(message=message, category=RuntimeWarning)

            normals.append([0, 0, 1])
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


def _list_faces_sharing_same_vertex(vertices, faces):
    vcon = [[] for i in range(len(vertices))]
    for face_idx, face in enumerate(faces):
        for vertex_idx in face:
            vcon[vertex_idx].append(face_idx)
    return vcon


def _find_edges_sharing_faces(faces):
    edges = {}
    for fi, face in enumerate(faces):
        sface = sorted(face)
        e0 = (sface[0], sface[1])
        e1 = (sface[1], sface[2])
        e2 = (sface[0], sface[2])
        if e0 not in edges:
            edges[e0] = [fi]
        else:
            edges[e0].append(fi)

        if e1 not in edges:
            edges[e1] = [fi]
        else:
            edges[e1].append(fi)

        if e2 not in edges:
            edges[e2] = [fi]
        else:
            edges[e2].append(fi)

    return edges


def _find_faces_sharing_at_least_one_edge(faces):
    edges = _find_edges_sharing_faces(faces)
    tfaces = {}

    for edge in edges:
        sfaces = edges[edge]
        for sface in sfaces:
            if sface not in tfaces:
                tfaces[sface] = set(sfaces)
            else:
                tfaces[sface].update(set(sfaces))

    # remove face itself
    for i in tfaces:
        tfaces[i].remove(i)

    for i in tfaces:
        tfaces[i] = list(tfaces[i])

    return tfaces


def _angle_between_rad(a, b):
    _a = np.asarray(a)
    _b = np.asarray(b)
    an = _a / np.linalg.norm(_a)
    bn = _b / np.linalg.norm(_b)
    assert len(an) == 3
    assert len(bn) == 3
    return np.arccos(np.dot(an, bn))


def _estimate_vertex_normal_based_on_neighbors(
    vertex_idx, face_idx, face_normals, vertices_to_faces, vertex_normal_eps
):
    neighbor_faces = vertices_to_faces[vertex_idx]
    face_normal = copy.copy(face_normals[face_idx])

    normals = [face_normal]
    for nface_idx in neighbor_faces:
        if nface_idx != face_idx:
            nface_normal = copy.copy(face_normals[nface_idx])
            nface_normal = nface_normal / np.linalg.norm(nface_normal)
            theta = _angle_between_rad(face_normal, nface_normal)

            if theta <= vertex_normal_eps:
                normals.append(nface_normal)

    normals = np.asarray(normals)

    vertex_normal = np.average(normals, axis=0)
    vertex_normal = vertex_normal / np.linalg.norm(vertex_normal)

    return vertex_normal
