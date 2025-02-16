import numpy as np
import io


def init():
    """
    Returns an empty object-wavefront-dict.
    """
    return {
        "v": [],
        "vn": [],
        "mtl": {},
    }


def minimal():
    """
    Returns a minimal cube (1, 1, 1) with six sub-meshes. Each
    face of the cube is one individual mesh.
    """
    obj_str = (
        "# vertices\n"
        "v 1.0 0.0 0.0\n"
        "v 1.0 1.0 0.0\n"
        "v 0.0 1.0 0.0\n"
        "v 0.0 0.0 0.0\n"
        "v 1.0 0.0 1.0\n"
        "v 1.0 1.0 1.0\n"
        "v 0.0 1.0 1.0\n"
        "v 0.0 0.0 1.0\n"
        "# vertex normals\n"
        "vn 1.0 0.0 0.0\n"
        "vn 0.0 1.0 0.0\n"
        "vn 0.0 0.0 1.0\n"
        "vn -1.0 0.0 0.0\n"
        "vn 0.0 -1.0 0.0\n"
        "vn 0.0 0.0 -1.0\n"
        "# faces\n"
        "usemtl pos-x\n"
        "f 1//1 2//1 6//1\n"
        "f 6//1 5//1 1//1\n"
        "usemtl pos-y\n"
        "f 2//2 3//2 6//2\n"
        "f 6//2 3//2 7//2\n"
        "usemtl pos-z\n"
        "f 5//3 6//3 7//3\n"
        "f 7//3 8//3 5//3\n"
        "usemtl neg-x\n"
        "f 3//4 7//4 4//4\n"
        "f 7//4 8//4 4//4\n"
        "usemtl neg-y\n"
        "f 1//5 4//5 8//5\n"
        "f 8//5 5//5 1//5\n"
        "usemtl neg-z\n"
        "f 1//6 2//6 3//6\n"
        "f 3//6 4//6 1//6\n"
    )
    return loads(obj_str)


def dumps(obj):
    """
    Serializes a wavefront-object-dict into a string.

    Parameters
    ----------
    obj : dict (object-wavefront-dict)
        The object-wavefront to be serialized.
    """

    IN_OBJ_INDEX_STARTS_WITH_1 = 1

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
                    IN_OBJ_INDEX_STARTS_WITH_1 + f["v"][0],
                    IN_OBJ_INDEX_STARTS_WITH_1 + f["vn"][0],
                    IN_OBJ_INDEX_STARTS_WITH_1 + f["v"][1],
                    IN_OBJ_INDEX_STARTS_WITH_1 + f["vn"][1],
                    IN_OBJ_INDEX_STARTS_WITH_1 + f["v"][2],
                    IN_OBJ_INDEX_STARTS_WITH_1 + f["vn"][2],
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
    IN_OBJ_INDEX_STARTS_WITH_1 = 1
    return (
        int(tokens[0]) - IN_OBJ_INDEX_STARTS_WITH_1,
        int(tokens[2]) - IN_OBJ_INDEX_STARTS_WITH_1,
    )


def _face_from_line(line):
    tokens = str.split(line, " ")
    assert len(tokens) >= 4
    assert tokens[0] == "f"
    v1, vn1 = _indices_from_slash_block(tokens[1])
    v2, vn2 = _indices_from_slash_block(tokens[2])
    v3, vn3 = _indices_from_slash_block(tokens[3])
    return {"v": [v1, v2, v3], "vn": [vn1, vn2, vn3]}


def loads(s):
    """
    Deserializes a wavefront-object-dict from a string 's'.

    Parameters
    ----------
    s : str
        A string with the payload of an '.obj'-file.
    """
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
    """
    Lists the differences between the wavefront-objects 'a' and 'b'.

    Parameters
    ----------
    a : dict (wavefront-object)
        The first wavefront-object.
    b : dict (wavefront-object)
        The second wavefront-object.
    v_eps : float
        Vertex 'v' differences up to a distance of 'v_eps' will be ignored.
    vn_eps_rad : float
        Vertex-normal 'vn' differences up to angles of 'vn_eps_rad' will be
        ignored. In radians.
    """
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


def to_vertices_and_faces(obj, mtlkeys=None):
    """
    Returns vertices and faces of certain materials in mtlkeys.

    Parameters
    ----------
    obj : object-wavefront dictionary
        The object.
    mtlkeys : list of str (default: None)
        List of mtl keys to be put into the returned faces.
        When mtlkeys is None (default), all materials will be used.
    """
    if mtlkeys is None:
        mtlkeys = list(obj["mtl"].keys())

    num_faces = 0
    for mtlkey in mtlkeys:
        num_faces += len(obj["mtl"][mtlkey])

    vertices = np.array(obj["v"], dtype=float)
    faces = np.zeros(shape=(num_faces, 3), dtype=int)

    face_idx = 0
    for mtlkey in mtlkeys:
        for ff in obj["mtl"][mtlkey]:
            faces[face_idx] = ff["v"]
            face_idx += 1

    return vertices, faces
