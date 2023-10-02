import triangle_mesh_io as tmi
import tempfile
import os


def test_minimal():
    with tempfile.TemporaryDirectory(prefix="triangle_mesh_io_") as tmp:
        cube_path = os.path.join(tmp, "cube.off")

        cube = tmi.off.minimal()

        with open(cube_path, "wt") as f:
            f.write(tmi.off.dumps(cube))

        with open(cube_path, "rt") as f:
            cube_back = tmi.off.loads(f.read())

        diff = tmi.off.diff(cube, cube_back)

        if diff:
            print(diff)
        assert len(diff) == 0
