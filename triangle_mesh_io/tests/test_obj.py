import triangle_mesh_io as tmi
import pkg_resources
import tempfile
import os


OBJ_PATH = pkg_resources.resource_filename(
    package_or_requirement="triangle_mesh_io",
    resource_name=os.path.join("tests", "resources", "optical_mirror.obj"),
)


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
