import numpy as np


def make_face_edges(f):
    return ((f[0], f[1]), (f[1], f[2]), (f[2], f[0]))


def list_faces_sharing_same_vertex(vertices, faces):
    vcon = [[] for i in range(len(vertices))]
    for face_idx, face in enumerate(faces):
        for vertex_idx in face:
            vcon[vertex_idx].append(face_idx)
    return vcon


def find_edges_sharing_faces(faces):
    edges = {}
    for fi, face in enumerate(faces):
        sface = sorted(face)
        e0, e1, e2 = make_face_edges(sface)
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


def find_faces_sharing_at_least_one_edge(faces):
    edges = find_edges_sharing_faces(faces)
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


def edges_have_same_vertices_independent_of_direction(edge_a, edge_b):
    sa = sorted(edge_a)
    sb = sorted(edge_b)
    return sa == sb


def make_second_face_with_same_winding_as_first(a, b):
    sa = set(a)
    sb = set(b)
    common_vertices = sa.intersection(sb)
    only_in_b_but_not_in_a = sb.difference(sa)
    assert len(common_vertices) == 2
    assert len(only_in_b_but_not_in_a) == 1
    ea = make_face_edges(a)
    eb = make_face_edges(b)

    for ia, ib in [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    ]:
        if edges_have_same_vertices_independent_of_direction(ea[ia], eb[ib]):
            break
    # print("a", ea[ia], "b", eb[ib])

    if ea[ia][0] == eb[ib][1] and ea[ia][1] == eb[ib][0]:
        # winding is the same, do not do anything
        return np.asarray(b)
    else:
        # winding needs to be turned around
        return np.flip(b)


class Flood:
    def __init__(self, faces, faces_sharing_at_least_one_edge):
        self.done = set()
        self.interface = set()
        self.todo = set(np.arange(len(faces)))

        self.faces = np.asarray(faces)
        self.nfaces = faces_sharing_at_least_one_edge

        self.wound_faces = faces.copy()
        self.num_meshes = 0
        self.faces_meshes = -1 * np.ones(shape=faces.shape[0], dtype=int)

    def seed_new_mesh(self):
        assert len(self.interface) == 0
        face_idx = self.todo.pop()
        self.wound_faces[face_idx] = self.faces[face_idx]
        self.faces_meshes[face_idx] = self.num_meshes
        self.done.add(face_idx)

        self.num_meshes += 1

        for neighbor_face_idx in self.nfaces[face_idx]:
            if neighbor_face_idx in self.todo:
                self.todo.remove(neighbor_face_idx)
                self.interface.add(neighbor_face_idx)

    def flood_mesh_along_the_interface(self):
        next_interface = set()
        while len(self.interface) > 0:
            face_idx = self.interface.pop()

            has_one_neighbor_face_in_state_done = False
            for neighbor_face_idx in self.nfaces[face_idx]:
                if neighbor_face_idx in self.done:
                    has_one_neighbor_face_in_state_done = True
                    break
            assert has_one_neighbor_face_in_state_done

            self.wound_faces[face_idx] = (
                make_second_face_with_same_winding_as_first(
                    a=self.wound_faces[neighbor_face_idx],
                    b=self.faces[face_idx],
                )
            )
            self.faces_meshes[face_idx] = self.num_meshes

            self.done.add(face_idx)

            for neighbor_face_idx in self.nfaces[face_idx]:
                if neighbor_face_idx in self.todo:
                    if neighbor_face_idx not in self.interface:
                        self.todo.remove(neighbor_face_idx)
                        next_interface.add(neighbor_face_idx)

        self.interface = next_interface

    def flood(self):
        self.seed_new_mesh()
        while not self.is_done():
            print("done", len(self.done), "interface", len(self.interface))
            if len(self.interface) > 0:
                self.flood_mesh_along_the_interface()
            else:
                self.seed_new_mesh()

    def is_done(self):
        return len(self.todo) == 0
