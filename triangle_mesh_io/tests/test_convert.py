import triangle_mesh_io as tmi


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
