import numpy as np
import io


def init():
    """
    Returns an empty dict-structure for a Wavefront.
    """
    return {
        "v": [],
        "vn": [],
        "mtl": {},
    }


def dumps(obj):
    # COUNTING STARTS AT ONE
    s = io.StringIO()
    s.write("# vertices\n")
    for v in obj["v"]:
        s.write("v {:f} {:f} {:f}\n".format(v[0], v[1], v[2]))
    s.write("# vertex-normals\n")
    for vn in obj["vn"]:
        s.write("vn {:f} {:f} {:f}\n".format(vn[0], vn[1], vn[2]))
    s.write("# faces\n")

    for mtl in obj["mtl"]:
        s.write("usemtl {:s}\n".format(mtl))
        for f in obj["mtl"][mtl]:
            s.write(
                "f {:d}//{:d} {:d}//{:d} {:d}//{:d}\n".format(
                    1 + f["v"][0],
                    1 + f["vn"][0],
                    1 + f["v"][1],
                    1 + f["vn"][1],
                    1 + f["v"][2],
                    1 + f["vn"][2],
                )
            )
    s.seek(0)
    return s.read()


def _vector_from_line(key, line):
    tokens = str.split(line, " ")
    assert len(tokens) >= 4
    assert tokens[0] == key
    return [float(tokens[1]), float(tokens[2]), float(tokens[3])]


def _indices_from_slash_block(slash_block):
    tokens = str.split(slash_block, "/")
    assert len(tokens) == 3
    return int(tokens[0]) - 1, int(tokens[2]) - 1


def _face_from_line(line):
    tokens = str.split(line, " ")
    assert len(tokens) >= 4
    assert tokens[0] == "f"
    v1, vn1 = _indices_from_slash_block(tokens[1])
    v2, vn2 = _indices_from_slash_block(tokens[2])
    v3, vn3 = _indices_from_slash_block(tokens[3])
    return {"v": [v1, v2, v3], "vn": [vn1, vn2, vn3]}


def loads(s):
    ss = io.StringIO()
    ss.write(s)
    ss.seek(0)
    obj = init()

    mtl_is_open = False
    mtlkey = None
    mtl = []

    while True:
        line = ss.readline()
        if not line:
            if mtl_is_open:
                obj["mtl"][mtlkey] = mtl
            break
        if str.startswith(line, "#"):
            continue
        if str.strip(line) == "\n":
            continue

        if str.startswith(line, "v "):
            obj["v"].append(_vector_from_line("v", line))

        if str.startswith(line, "vn "):
            obj["vn"].append(_vector_from_line("vn", line))

        if str.startswith(line, "usemtl "):
            if mtl_is_open:
                obj["mtl"][mtlkey] = mtl
            else:
                mtl_is_open = True

            mtlkey = str.split(line, " ")[1]
            mtlkey = str.strip(mtlkey, "\n")
            mtl = []

        if str.startswith(line, "f "):
            if mtl_is_open:
                mtl.append(_face_from_line(line))
            else:
                raise AssertionError("Expected usemtl before first face 'f'.")
    return obj


def _angle_between_rad(a, b, eps=1e-9):
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    ab_aa_bb = np.dot(a, b) / (na * nb)
    if ab_aa_bb > 1.0 + eps:
        raise RuntimeError("Not expected. Bad vectors. Bad Numeric?")
    if ab_aa_bb > 1.0:
        ab_aa_bb = 1.0
    return np.arccos(ab_aa_bb)


def diff(a, b, v_eps=1e-6, vn_eps_rad=1e-6):
    diffs = []

    if len(a["v"]) != len(b["v"]):
        diffs.append("len(v)", len(a["v"]), len(b["v"]))
    else:
        for i in range(len(a["v"])):
            av = np.array(a["v"][i])
            bv = np.array(b["v"][i])
            delta_norm = np.linalg.norm(av - bv)
            if delta_norm > v_eps:
                diffs.append(
                    (
                        "v[{:d}]: norm diff. {:e}".format(i, delta_norm),
                        av,
                        bv,
                    )
                )
    if len(a["vn"]) != len(b["vn"]):
        diffs.append("len(vn)", len(a["vn"]), len(b["vn"]))
    else:
        for i in range(len(a["vn"])):
            avn = np.array(a["vn"][i])
            bvn = np.array(b["vn"][i])
            delta_rad = _angle_between_rad(avn, bvn, eps=1e-3 * vn_eps_rad)
            if delta_rad > vn_eps_rad:
                diffs.append(
                    (
                        "vn[{:d}]: angle diff. {:e}rad".format(i, delta_rad),
                        avn,
                        bvn,
                    )
                )
            delta_norm = np.linalg.norm(avn - bvn)
            if delta_norm > v_eps:
                diffs.append(
                    (
                        "vn[{:d}]: norm diff. {:e}".format(i, delta_norm),
                        avn,
                        bvn,
                    )
                )
    for amtlkey in a["mtl"]:
        if amtlkey not in b["mtl"]:
            diffs.append(("mtl", amtlkey, None))

    for bmtlkey in b["mtl"]:
        if bmtlkey not in a["mtl"]:
            diffs.append(("mtl", None, bmtlkey))
        else:
            amtl = a["mtl"][bmtlkey]
            bmtl = b["mtl"][bmtlkey]
            if len(amtl) != len(bmtl):
                diffs.append(
                    (
                        "len(mtl[{:s}])".format(bmtlkey),
                        len(amtl),
                        len(bmtl),
                    )
                )
            else:
                for fi in range(len(amtl)):
                    aface = amtl[fi]
                    bface = bmtl[fi]

                    for key in ["v", "vn"]:
                        for dim in [0, 1, 2]:
                            if aface[key][dim] != bface[key][dim]:
                                diffs.append(
                                    (
                                        'mtl["{:s}"][{:d}][{:s}][{:d}]'.format(
                                            bmtlkey, fi, key, dim
                                        ),
                                        aface[key][dim],
                                        bface[key][dim],
                                    )
                                )
    return diffs
