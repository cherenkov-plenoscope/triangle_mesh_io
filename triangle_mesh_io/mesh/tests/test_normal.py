import triangle_mesh_io as tmi
import numpy as np


def in_margin(a, b, eps):
    return abs(b - a) < eps


def in_range(start, x, stop):
    return start <= x and x <= stop


def test_graph_make_face_edges():
    theta = tmi.mesh.normal.angle_between_rad([0, 0, 1], [0, 0, 1])
    assert in_margin(theta, 0.0, 1e-9)

    theta = tmi.mesh.normal.angle_between_rad([0, 0, 1], [0, 1, 0])
    assert in_margin(theta, np.deg2rad(90), 1e-9)

    theta = tmi.mesh.normal.angle_between_rad([0, 0, 1], [0, 0, -1])
    assert in_margin(theta, np.deg2rad(180), 1e-9)


def test_estimate_vertex_normal_based_on_neighbors():
    """
    micro mesh with five vertices and three faces

    2---------3-------4
    |       / |      /
    |  1  /   |  2 /
    |   /     |  /
    | /   0   |/
    0---------1
    """
    d2r = np.deg2rad
    vertex_normal_smooth_eps = d2r(5.0)

    vertices = [
        [0, 0, 0],  # 0
        [0, 1, 0],  # 1
        [1, 0, 1e-2],  # 2
        [1, 1, 0],  # 3
        [1, 1, 2],  # 4
    ]

    faces = [[0, 1, 3], [2, 0, 3], [1, 3, 4]]

    face_normals = tmi.mesh.normal.make_face_normals_from_vertices_and_faces(
        vertices=vertices,
        faces=faces,
    )

    vertices_to_faces = tmi.mesh.graph.list_faces_sharing_same_vertex(
        vertices=vertices,
        faces=faces,
    )

    faces_vn = []
    vertex_normals = []
    for face_idx in range(len(faces)):
        face_vn = [-1, -1, -1]
        for vdim in range(3):
            vn = tmi.mesh.normal.estimate_vertex_normal_based_on_neighbors(
                vertex_idx=faces[face_idx][vdim],
                face_idx=face_idx,
                face_normals=face_normals,
                vertices_to_faces=vertices_to_faces,
                vertex_normal_smooth_eps=vertex_normal_smooth_eps,
            )
            face_vn[vdim] = len(vertex_normals)
            vertex_normals.append(vn)
        faces_vn.append(face_vn)

    def n(face_idx, vdim):
        return vertex_normals[faces_vn[face_idx][vdim]]

    _theta = tmi.mesh.normal.angle_between_rad

    unit_mz = [0, 0, -1]
    unit_my = [0, -1, 0]
    # face 0
    assert in_range(d2r(0.1), _theta(n(0, 0), unit_mz), d2r(1.0))
    assert in_margin(_theta(n(0, 1), unit_mz), 0.0, d2r(1e-9))
    assert in_range(d2r(0.1), _theta(n(0, 2), unit_mz), d2r(1.0))

    # face 1
    assert in_range(d2r(0.1), _theta(n(1, 0), unit_mz), d2r(1.0))
    assert in_range(d2r(0.1), _theta(n(1, 1), unit_mz), d2r(1.0))
    assert in_range(d2r(0.1), _theta(n(1, 2), unit_mz), d2r(1.0))

    # face 2
    assert in_margin(_theta(n(2, 0), unit_my), 0.0, d2r(1e-6))
    assert in_margin(_theta(n(2, 1), unit_my), 0.0, d2r(1e-6))
    assert in_margin(_theta(n(2, 2), unit_my), 0.0, d2r(1e-6))
