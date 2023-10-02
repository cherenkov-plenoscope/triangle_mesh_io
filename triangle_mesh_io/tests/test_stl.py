import triangle_mesh_io as tmi
import pkg_resources
import os
import tempfile


STL_ASCII_PATH = pkg_resources.resource_filename(
    package_or_requirement="triangle_mesh_io",
    resource_name=os.path.join(
        "tests", "resources", "gridfinity_cup_modules_x1-y1-z5.stl"
    ),
)


STL_BINARY_PATH = pkg_resources.resource_filename(
    package_or_requirement="triangle_mesh_io",
    resource_name=os.path.join("tests", "resources", "utah_teapot.stl"),
)


def test_diff():
    with open(STL_ASCII_PATH, "rt") as f:
        a = tmi.stl.loads(f.read(), mode="ascii")

    assert not tmi.stl.diff(a=a, b=a)
    b = a.copy()
    b["normal.x"][1337] += 2e-6
    assert tmi.stl.diff(a=a, b=b, eps=1e-6)
    assert not tmi.stl.diff(a=a, b=b, eps=1e-3)


def test_minimal():
    with tempfile.TemporaryDirectory(prefix="triangle_mesh_io_") as tmp:
        cube_path = os.path.join(tmp, "cube.stl")

        cube = tmi.stl.minimal()

        with open(cube_path, "wt") as f:
            f.write(tmi.stl.dumps(cube, mode="ascii"))

        with open(cube_path, "rt") as f:
            cube_back = tmi.stl.loads(f.read(), mode="ascii")

        diff = tmi.stl.diff(cube, cube_back)

        if diff:
            print(diff)
        assert len(diff) == 0


def _test_stl(original_path, original_mode):
    if original_mode == "binary":
        ori_mode = "binary"
        ori_fmode = "b"
        alt_mode = "ascii"
        alt_fmode = "t"
    elif original_mode == "ascii":
        ori_mode = "ascii"
        ori_fmode = "t"
        alt_mode = "binary"
        alt_fmode = "b"
    else:
        raise KeyError("original_mode must be either 'binary' or  'ascii'.")

    with open(original_path, "r" + ori_fmode) as f:
        s_ori = tmi.stl.loads(f.read(), mode=ori_mode)

    with tempfile.TemporaryDirectory(prefix="triangle_mesh_io_") as tmpdir:
        tmp_ori_path = os.path.join(tmpdir, "pot.original-format.stl")
        tmp_alt_path = os.path.join(tmpdir, "pot.alternative-format.stl")

        with open(tmp_ori_path, "w" + ori_fmode) as f:
            f.write(tmi.stl.dumps(s_ori, mode=ori_mode))

        with open(tmp_ori_path, "r" + ori_fmode) as f:
            s_ori_back = tmi.stl.loads(f.read(), mode=ori_mode)

        diff = tmi.stl.diff(a=s_ori, b=s_ori_back, eps=1e-6)
        if diff:
            print(diff)
        assert len(diff) == 0

        with open(tmp_alt_path, "w" + alt_fmode) as f:
            f.write(tmi.stl.dumps(s_ori_back, mode=alt_mode))

        with open(tmp_alt_path, "r" + alt_fmode) as f:
            s_alt_back = tmi.stl.loads(f.read(), mode=alt_mode)

        diff = tmi.stl.diff(a=s_ori, b=s_alt_back, eps=1e-6)
        if diff:
            print(diff)
        assert len(diff) == 0


def test_stl():
    _test_stl(original_path=STL_ASCII_PATH, original_mode="ascii")
    _test_stl(original_path=STL_BINARY_PATH, original_mode="binary")
