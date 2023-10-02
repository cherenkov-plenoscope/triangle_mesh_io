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
        ("vertex-1.x", np.float32),
        ("vertex-1.y", np.float32),
        ("vertex-1.z", np.float32),
        ("vertex-2.x", np.float32),
        ("vertex-2.y", np.float32),
        ("vertex-2.z", np.float32),
        ("vertex-3.x", np.float32),
        ("vertex-3.y", np.float32),
        ("vertex-3.z", np.float32),
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


def init(size=0):
    """
    Returns
    """
    return np.core.records.recarray(shape=size, dtype=_dtype())


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

        out["vertex-1.x"][i] = v[0][0]
        out["vertex-1.y"][i] = v[0][1]
        out["vertex-1.z"][i] = v[0][2]

        out["vertex-2.x"][i] = v[1][0]
        out["vertex-2.y"][i] = v[1][1]
        out["vertex-2.z"][i] = v[1][2]

        out["vertex-3.x"][i] = v[2][0]
        out["vertex-3.y"][i] = v[2][1]
        out["vertex-3.z"][i] = v[2][2]

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
        ss.write(
            "        vertex {:e} {:e} {:e}\n".format(
                stl["vertex-3.x"][i],
                stl["vertex-3.y"][i],
                stl["vertex-3.z"][i],
            )
        )
        ss.write("    endloop\n")
        ss.write("endfacet\n")
    ss.write("endsolid \n")

    ss.seek(0)
    return ss.read()


def _loads_binary(s):
    ss = io.BytesIO()
    ss.write(s)
    ss.seek(0)
    _header = ss.read(80)
    num_triangles = np.frombuffer(ss.read(4), dtype=np.uint32)[0]
    return np.frombuffer(ss.read(50 * num_triangles), dtype=_dtype())


def _dumps_binary(stl):
    ss = io.BytesIO()

    ss.write(b" " * 80)
    num_triangles = len(stl)
    ss.write(np.uint32(num_triangles).tobytes())
    ss.write(stl.tobytes())

    ss.seek(0)
    return ss.read()
