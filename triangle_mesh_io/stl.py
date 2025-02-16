"""
Stereolithography File Format (STL)
-----------------------------------

See: https://en.wikipedia.org/wiki/STL_(file_format)

Only a list of triangles. Not faces of a mesh.
STL does not state anything about the relations of the facets.
"""

import io
import numpy as np


def _dtype():
    return [
        ("normal.x", np.float32),
        ("normal.y", np.float32),
        ("normal.z", np.float32),
        ("vertex-0.x", np.float32),
        ("vertex-0.y", np.float32),
        ("vertex-0.z", np.float32),
        ("vertex-1.x", np.float32),
        ("vertex-1.y", np.float32),
        ("vertex-1.z", np.float32),
        ("vertex-2.x", np.float32),
        ("vertex-2.y", np.float32),
        ("vertex-2.z", np.float32),
        ("attribute_byte_count", np.uint16),
    ]


def diff(a, b, eps=1e-6):
    diffs = []
    if len(a) != len(b):
        diffs.append(("len", len(a), len(b)))

    for i in range(len(a)):
        for key, _ in _dtype():
            if key == "attribute_byte_count":
                continue
            if np.abs(a[key][i] - b[key][i]) > eps:
                diffs.append(
                    (
                        "facet: {:d}, key: {:s}".format(i, key),
                        a[key][i],
                        b[key][i],
                    )
                )
    return diffs


def minimal():
    """
    Returns a minimal cube (1, 1, 1).
    """
    vertices = np.array(
        [
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
            [0.0, 0.0, 1.0],
        ]
    )
    INDEX_STARTS_AT_0 = -1
    faces = INDEX_STARTS_AT_0 + np.array(
        [
            [1, 2, 6],
            [6, 5, 1],
            [2, 3, 6],
            [6, 3, 7],
            [5, 6, 7],
            [7, 8, 5],
            [3, 7, 4],
            [7, 8, 4],
            [1, 4, 8],
            [8, 5, 1],
            [1, 2, 3],
            [3, 4, 1],
        ]
    )
    out = init(size=len(faces))
    for i in range(len(faces)):
        out["vertex-0.x"][i] = vertices[faces[i, 0], 0]
        out["vertex-0.y"][i] = vertices[faces[i, 0], 1]
        out["vertex-0.z"][i] = vertices[faces[i, 0], 2]
        out["vertex-1.x"][i] = vertices[faces[i, 1], 0]
        out["vertex-1.y"][i] = vertices[faces[i, 1], 1]
        out["vertex-1.z"][i] = vertices[faces[i, 1], 2]
        out["vertex-2.x"][i] = vertices[faces[i, 2], 0]
        out["vertex-2.y"][i] = vertices[faces[i, 2], 1]
        out["vertex-2.z"][i] = vertices[faces[i, 2], 2]

        e01 = vertices[faces[i, 0]] - vertices[faces[i, 1]]
        e12 = vertices[faces[i, 1]] - vertices[faces[i, 2]]
        n = np.cross(e01, e12)

        out["normal.x"][i] = n[0]
        out["normal.y"][i] = n[1]
        out["normal.z"][i] = n[2]

        out["attribute_byte_count"][i] = 0

    return out


def init(size=0):
    """
    Returns
    """
    return np.recarray(shape=size, dtype=_dtype())


def _num_bytes_per_triangle():
    return len(init(size=1).tobytes())


def loads(s, mode="ascii"):
    if mode == "ascii":
        return _loads_ascii(s=s)
    elif mode == "binary":
        return _loads_binary(s=s)
    else:
        raise KeyError("mode must be either 'ascii' or 'binary'.")


def dumps(stl, mode="ascii"):
    if mode == "ascii":
        return _dumps_ascii(stl=stl)
    elif mode == "binary":
        return _dumps_binary(stl=stl)
    else:
        raise KeyError("mode must be either 'ascii' or 'binary'.")


def _gather_lines_of_facet(ss):
    out = []
    while True:
        line = ss.readline()
        if not line:
            break
        if "\n" == line:
            continue
        out.append(str.strip(line))
        if "endfacet" in line:
            break
    return out


def _facet_from_facet_lines(flines):
    flines = [str.strip(ll) for ll in flines]
    assert "facet normal" in flines[0]
    normal = [float(n) for n in flines[0].split(" ")[2:]]
    assert len(normal) == 3
    assert "outer loop" in flines[1]
    v = []
    for i in range(3):
        vi = [float(n) for n in flines[i + 2].split(" ")[1:]]
        assert len(vi) == 3
        v.append(vi)
    return normal, v


def _loads_ascii(s):
    ss = io.StringIO()
    ss.write(s)
    ss.seek(0)

    firstline = ss.readline()
    assert firstline.startswith("solid ")

    facets = []

    while True:
        line = ss.readline()
        if not line:
            break
        if "facet normal" in line:
            fll = [line]
            fll += _gather_lines_of_facet(ss)
            n, v = _facet_from_facet_lines(flines=fll)

            facets.append((n, v))

        elif "endsolid" in line:
            break
        else:
            pass

    out = init(len(facets))
    for i in range(len(facets)):
        n, v = facets[i]
        out["normal.x"][i] = n[0]
        out["normal.y"][i] = n[1]
        out["normal.z"][i] = n[2]

        out["vertex-0.x"][i] = v[0][0]
        out["vertex-0.y"][i] = v[0][1]
        out["vertex-0.z"][i] = v[0][2]

        out["vertex-1.x"][i] = v[1][0]
        out["vertex-1.y"][i] = v[1][1]
        out["vertex-1.z"][i] = v[1][2]

        out["vertex-2.x"][i] = v[2][0]
        out["vertex-2.y"][i] = v[2][1]
        out["vertex-2.z"][i] = v[2][2]

    return out


def _dumps_ascii(stl):
    ss = io.StringIO()
    ss.write("solid \n")

    for i in range(len(stl)):
        ss.write(
            "facet normal {:e} {:e} {:e}\n".format(
                stl["normal.x"][i],
                stl["normal.y"][i],
                stl["normal.z"][i],
            )
        )
        ss.write("    outer loop\n")
        ss.write(
            "        vertex {:e} {:e} {:e}\n".format(
                stl["vertex-0.x"][i],
                stl["vertex-0.y"][i],
                stl["vertex-0.z"][i],
            )
        )
        ss.write(
            "        vertex {:e} {:e} {:e}\n".format(
                stl["vertex-1.x"][i],
                stl["vertex-1.y"][i],
                stl["vertex-1.z"][i],
            )
        )
        ss.write(
            "        vertex {:e} {:e} {:e}\n".format(
                stl["vertex-2.x"][i],
                stl["vertex-2.y"][i],
                stl["vertex-2.z"][i],
            )
        )
        ss.write("    endloop\n")
        ss.write("endfacet\n")
    ss.write("endsolid \n")

    ss.seek(0)
    return ss.read()


def _loads_binary(s):
    NUM_BYTES_PER_TRIANGLE = _num_bytes_per_triangle()
    ss = io.BytesIO()
    ss.write(s)
    ss.seek(0)
    _header = ss.read(80)
    num_triangles = np.frombuffer(ss.read(4), dtype=np.uint32)[0]
    return np.frombuffer(
        ss.read(NUM_BYTES_PER_TRIANGLE * num_triangles), dtype=_dtype()
    )


def _dumps_binary(stl):
    ss = io.BytesIO()

    ss.write(b" " * 80)
    num_triangles = len(stl)
    ss.write(np.uint32(num_triangles).tobytes())
    ss.write(stl.tobytes())

    ss.seek(0)
    return ss.read()


def to_vertices_and_faces(stl):
    num_faces = stl.shape[0]
    num_vertices = 3 * num_faces
    faces = np.zeros(shape=(num_faces, 3), dtype=int)
    vertices = np.zeros(shape=(num_vertices, 3), dtype=float)

    vi = 0
    for fi in range(num_faces):
        sface = stl[fi]
        v0 = [sface["vertex-0.x"], sface["vertex-0.y"], sface["vertex-0.z"]]
        v1 = [sface["vertex-1.x"], sface["vertex-1.y"], sface["vertex-1.z"]]
        v2 = [sface["vertex-2.x"], sface["vertex-2.y"], sface["vertex-2.z"]]

        vi0 = vi
        vertices[vi] = v0
        vi += 1

        vi1 = vi
        vertices[vi] = v1
        vi += 1

        vi2 = vi
        vertices[vi] = v2
        vi += 1

        faces[fi] = [vi0, vi1, vi2]

    assert vi == num_vertices
    assert fi + 1 == num_faces

    return vertices, faces
