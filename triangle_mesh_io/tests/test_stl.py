import triangle_mesh_io as tmi
import pkg_resources
import os
import tempfile


UTAH_TEAPOT_PATH = pkg_resources.resource_filename(
    package_or_requirement="triangle_mesh_io",
    resource_name=os.path.join("tests", "resources", "utah_teapot.stl"),
)


def test_is_almost_equal():
    with open(UTAH_TEAPOT_PATH, "rb") as f:
        a = tmi.stl.loads(f.read(), mode="binary")

    assert tmi.stl.is_almost_equal(a=a, b=a)
    b = a.copy()
    b["normal.x"][1337] += 2e-6
    assert not tmi.stl.is_almost_equal(a=a, b=b, eps=1e-6)
    assert tmi.stl.is_almost_equal(a=a, b=b, eps=1e-3)


def test_read_stl():
    with open(UTAH_TEAPOT_PATH, "rb") as f:
        s_orig = tmi.stl.loads(f.read(), mode="binary")

    with tempfile.TemporaryDirectory(prefix="triangle_mesh_io_") as tmpdir:
        tmp_ascii_path = os.path.join(tmpdir, "pot.ascii.stl")
        tmp_binary_path = os.path.join(tmpdir, "pot.binary.stl")

        with open(tmp_ascii_path, "wt") as f:
            f.write(tmi.stl.dumps(s_orig, mode="ascii"))

        with open(tmp_ascii_path, "rt") as f:
            s_orig_to_ascii = tmi.stl.loads(f.read(), mode="ascii")

        assert tmi.stl.is_almost_equal(a=s_orig, b=s_orig_to_ascii, eps=1e-6)

        with open(tmp_binary_path, "wb") as f:
            f.write(tmi.stl.dumps(s_orig_to_ascii, mode="binary"))

        with open(tmp_binary_path, "rb") as f:
            s_orig_to_ascii_to_binary = tmi.stl.loads(f.read(), mode="binary")

        assert tmi.stl.is_almost_equal(
            a=s_orig, b=s_orig_to_ascii_to_binary, eps=1e-6
        )
