import triangle_mesh_io as tmi


def test_graph_make_face_edges():
    face = [1, 2, 3]
    e0, e1, e2 = tmi.mesh.graph.make_face_edges(face=face)
    assert e0 == (1, 2)
    assert e1 == (2, 3)
    assert e2 == (3, 1)


def test_list_faces_sharing_same_vertex():
    minimal = tmi.off.minimal()
    vertices, faces = tmi.off.to_vertices_and_faces(off=minimal)
    fsv = tmi.mesh.graph.list_faces_sharing_same_vertex(
        vertices=vertices, faces=faces
    )
    assert len(fsv) == len(vertices)

    for vertex_idx in range(len(fsv)):
        for share_face_idx in fsv[vertex_idx]:
            assert vertex_idx in faces[share_face_idx]

        for face_idx in range(len(faces)):
            if face_idx not in fsv[vertex_idx]:
                assert vertex_idx not in faces[face_idx]


def test_find_edges_sharing_faces():
    minimal = tmi.off.minimal()
    vertices, faces = tmi.off.to_vertices_and_faces(off=minimal)
    edges = tmi.mesh.graph.find_edges_sharing_faces(faces=faces)

    for edge in edges:
        for face_idx in edges[edge]:
            assert edge[0] in faces[face_idx]
            assert edge[1] in faces[face_idx]

        for face_idx in range(len(faces)):
            if face_idx not in edges[edge]:
                assert not (
                    edge[0] in faces[face_idx] and edge[1] in faces[face_idx]
                )


def test_edges_have_same_vertices_independent_of_direction():
    _edges_have_same_vertices = (
        tmi.mesh.graph.edges_have_same_vertices_independent_of_direction
    )

    assert _edges_have_same_vertices((0, 1), (0, 1))
    assert _edges_have_same_vertices((0, 1), (1, 0))
    assert not _edges_have_same_vertices((0, 0), (1, 0))
    assert not _edges_have_same_vertices((1, 1), (1, 0))
    assert not _edges_have_same_vertices((0, 1), (0, 0))
    assert not _edges_have_same_vertices((0, 1), (1, 1))


def test_faces_share_edge_independent_of_direction():
    _faces_share_edge = (
        tmi.mesh.graph.faces_share_edge_independent_of_direction
    )

    s, a, b = _faces_share_edge([0, 1, 2], [0, 1, 4])
    assert s
    assert a == 0
    assert b == 0

    s, a, b = _faces_share_edge([0, 1, 2], [1, 0, 4])
    assert s
    assert a == 0
    assert b == 0

    s, a, b = _faces_share_edge([0, 1, 2], [4, 0, 1])
    assert s
    assert a == 0
    assert b == 1

    s, a, b = _faces_share_edge([0, 1, 2], [4, 1, 0])
    assert s
    assert a == 0
    assert b == 1

    s, a, b = _faces_share_edge([0, 1, 2], [3, 4, 5])
    assert not s
    assert a == -1
    assert b == -1


def test_find_faces_sharing_at_least_one_edge():
    minimal = tmi.off.minimal()
    vertices, faces = tmi.off.to_vertices_and_faces(off=minimal)
    shares = tmi.mesh.graph.find_faces_sharing_at_least_one_edge(faces=faces)

    for face_idx in shares:
        for neighbor_face_idx in shares[face_idx]:
            assert tmi.mesh.graph.faces_share_edge_independent_of_direction(
                face_a=faces[face_idx],
                face_b=faces[neighbor_face_idx],
            )

        for foreign_face_idx in range(len(faces)):
            if (
                foreign_face_idx not in shares[face_idx]
                and foreign_face_idx != face_idx
            ):
                do_share, _, _ = (
                    tmi.mesh.graph.faces_share_edge_independent_of_direction(
                        face_a=faces[face_idx],
                        face_b=faces[foreign_face_idx],
                    )
                )
                assert not do_share
