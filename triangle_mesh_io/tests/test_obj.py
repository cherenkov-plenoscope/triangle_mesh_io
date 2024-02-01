import triangle_mesh_io as tmi
from importlib import resources as importlib_resources
import tempfile
import os


OBJ_PATH = os.path.join(
    importlib_resources.files("triangle_mesh_io"),
    "tests",
    "resources",
    "optical_mirror.obj",
)


def test_minimal():
    with tempfile.TemporaryDirectory(prefix="triangle_mesh_io_") as tmp:
        cube_path = os.path.join(tmp, "cube.obj")

        cube = tmi.obj.minimal()

        with open(cube_path, "wt") as f:
            f.write(tmi.obj.dumps(cube))

        with open(cube_path, "rt") as f:
            cube_back = tmi.obj.loads(f.read())

        diff = tmi.obj.diff(cube, cube_back)

        if diff:
            print(diff)
        assert len(diff) == 0


def test_oby_io():
    with tempfile.TemporaryDirectory(prefix="triangle_mesh_io_") as tmp:
        tmp_path = os.path.join(tmp, "my_thing.obj")

        with open(OBJ_PATH, "rt") as f:
            my_thing_obj = tmi.obj.loads(f.read())

        with open(tmp_path, "wt") as f:
            f.write(tmi.obj.dumps(my_thing_obj))

        with open(tmp_path, "rt") as f:
            my_thing_obj_back = tmi.obj.loads(f.read())

        diff = tmi.obj.diff(my_thing_obj, my_thing_obj_back)

        if diff:
            print(diff)
        assert len(diff) == 0
