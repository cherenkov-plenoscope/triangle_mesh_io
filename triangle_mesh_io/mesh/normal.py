import numpy as np
import copy
import warnings


def make_normal_from_face(a, b, c):
    a = np.asarray(a)
    b = np.asarray(b)
    c = np.asarray(c)
    a_to_b = b - a
    a_to_c = c - a
    n = np.cross(a_to_b, a_to_c)
    norm = np.linalg.norm(n)
    if norm <= 1e-9:
        raise RuntimeError
    n = n / norm
    return n


def make_face_normals_from_vertices_and_faces(vertices, faces):
    normals = []
    for idx, f in enumerate(faces):
        a = vertices[f[0]]
        b = vertices[f[1]]
        c = vertices[f[2]]
        try:
            n = make_normal_from_face(a=a, b=b, c=c)
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


def angle_between_rad(a, b):
    NUMERIC_DOT_TOLLERANCE = 1.0 + 1e-9
    _a = np.asarray(a)
    _b = np.asarray(b)
    an = _a / np.linalg.norm(_a)
    bn = _b / np.linalg.norm(_b)
    assert len(an) == 3
    assert len(bn) == 3
    theta = np.dot(an, bn)
    if theta < NUMERIC_DOT_TOLLERANCE:
        if theta > 1.0:
            theta = 1.0
    return np.arccos(theta)


def estimate_vertex_normal_based_on_neighbors(
    vertex_idx,
    face_idx,
    face_normals,
    vertices_to_faces,
    vertex_normal_smooth_eps,
):
    neighbor_faces = vertices_to_faces[vertex_idx]
    face_normal = copy.copy(face_normals[face_idx])

    normals = [face_normal]
    for nface_idx in neighbor_faces:
        if nface_idx != face_idx:
            nface_normal = copy.copy(face_normals[nface_idx])
            nface_normal = nface_normal / np.linalg.norm(nface_normal)
            theta = angle_between_rad(face_normal, nface_normal)

            if theta <= vertex_normal_smooth_eps:
                normals.append(nface_normal)

    normals = np.asarray(normals)

    vertex_normal = np.average(normals, axis=0)
    vertex_normal = vertex_normal / np.linalg.norm(vertex_normal)

    return vertex_normal
