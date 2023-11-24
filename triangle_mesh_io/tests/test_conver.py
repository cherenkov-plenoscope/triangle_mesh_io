import triangle_mesh_io as tmi


def test_convert_off2obj():
    off_cube = tmi.off.minimal()
    obj_cube = tmi.convert.off2obj(off=off_cube, mtl="abc")

    assert len(off_cube["f"]) == sum(
        [len(obj_cube["mtl"][mkey]) for mkey in obj_cube["mtl"]]
    )
