"""
Object-File-Format (OFF)
------------------------

See: https://en.wikipedia.org/wiki/OFF_(file_format)

A set of vertices and faces, but no vertex-normals.

OFFs do not have groups or materials like OBJs.
OFFs are indexed from zero, OBJs are indexed from one.
"""
import io
import numpy as np


def init():
    """
    Returns an empty dict-structure for an object.
    """
    return {"v": [], "f": []}


def diff(a, b, eps=1e-6):
    diffs = []
    if len(a["v"]) != len(b["v"]):
        diffs.append(("len(v)", len(a["v"]), len(b["v"])))
    else:
        for i in range(len(a["v"])):
            av = np.array(a["v"][i])
            bv = np.array(b["v"][i])
            delta = np.linalg.norm(av - bv)
            if delta > eps:
                diffs.append(
                    (
                        "v[{:d}]: delta > {:e}".format(i, eps),
                        a["v"][i],
                        b["v"][i],
                    )
                )
    if len(a["f"]) != len(b["f"]):
        diffs.append(("len(f)", len(a["f"]), len(b["f"])))
    else:
        for i in range(len(a["f"])):
            for dim in [0, 1, 2]:
                if a["f"][i][dim] != b["f"][i][dim]:
                    diffs.append(
                        (
                            "f[{:d}][{:d}]".format(i, dim),
                            a["f"][i][dim],
                            b["f"][i][dim],
                        )
                    )
    return diffs


def dumps(off, float_format="{:e}"):
    """
    Returns an off-string dumped from an off-dictionary.

    Parameters
    ----------
    off : off-dictionary
        Contains the vertices 'v' and faces 'f'.
    float_format : str
        The format-string for floats.
    """
    s = io.StringIO()
    s.write("OFF {:d} {:d} 0\n".format(len(off["v"]), len(off["f"])))
    v_format = float_format + " " + float_format + " " + float_format + "\n"

    for v in off["v"]:
        s.write(v_format.format(v[0], v[1], v[2]))

    for f in off["f"]:
        s.write("3 {:d} {:d} {:d}\n".format(f[0], f[1], f[2]))

    s.seek(0)
    return s.read()


def loads(s):
    """
    Returns an off-dictionary parsed from an off-string 's'.

    Parameters
    ----------
    s : off-str
        The string containing the object-file.
    """
    lines = str.splitlines(s)
    num_lines = len(lines)

    off = init()
    num_vertices = 0
    num_faces = 0
    num_edges = 0
    found_off = False

    for ln in range(len(lines)):
        line = lines[ln]
        sline = str.strip(line)

        if len(sline) == 0:
            continue

        if "#" == sline[0]:
            continue

        if sline[0:3] == "OFF":
            found_off = True
            off_line = str.replace(sline, "OFF", "")
            off_line = str.strip(off_line)
            off_tokens = str.split(off_line, " ")
            num_vertices = int(off_tokens[0])
            num_faces = int(off_tokens[1])
            num_edges = int(off_tokens[2])

        if found_off:
            break

    idx_vertex = 0
    while (ln + 1) < num_lines and idx_vertex < num_vertices:
        ln += 1
        line = lines[ln]
        sline = str.strip(line)

        if len(sline) == 0:
            continue

        if "#" == sline[0]:
            continue

        vertex_tokens = str.split(sline, " ")
        vertex = [float(token) for token in vertex_tokens]
        off["v"].append(vertex)
        idx_vertex += 1

    idx_face = 0
    while (ln + 1) < num_lines and idx_face < num_faces:
        ln += 1
        line = lines[ln]
        sline = str.strip(line)

        if len(sline) == 0:
            continue

        if "#" == sline[0]:
            continue

        face_tokens = str.split(sline, " ")
        num_vertices_in_face = int(face_tokens[0])
        assert num_vertices_in_face == 3
        face_tokens = face_tokens[1:4]
        face = [int(token) for token in face_tokens]
        off["f"].append(face)
        idx_face += 1

    return off
