import triangle_mesh_io as tmi
from importlib import resources as importlib_resources
import os
import numpy as np
import tempfile


def test_convert_off_to_obj():
    off_cube = tmi.off.minimal()
    obj_cube = tmi.convert.off_to_obj(off=off_cube, mtl="abc")

    assert len(off_cube["f"]) == sum(
        [len(obj_cube["mtl"][mkey]) for mkey in obj_cube["mtl"]]
    )


def test_convert_stl_to_obj():
    stl_cube = tmi.stl.minimal()
    obj_cube = tmi.convert.stl_to_obj(
        stl=stl_cube,
        mtl="abc",
    )

    assert len(stl_cube) == sum(
        [len(obj_cube["mtl"][mkey]) for mkey in obj_cube["mtl"]]
    )


RESOURCE_PATH = os.path.join(
    importlib_resources.files("triangle_mesh_io"), "tests", "resources"
)


def test_full_cahin():
    NAME = "openucci-rim-disk"

    with open(os.path.join(RESOURCE_PATH, NAME + ".off"), "rt") as f:
        off = tmi.off.loads(f.read())

    obj = tmi.convert.off_to_obj(
        off=off,
        mtl="rim",
        vertex_eps=None,
        vertex_normal_eps=np.deg2rad(1e-3),
        vertex_normal_smooth_eps=np.deg2rad(10.0),
    )

    with open(os.path.join(RESOURCE_PATH, NAME + ".obj"), "wt") as f:
        f.write(tmi.obj.dumps(obj))
