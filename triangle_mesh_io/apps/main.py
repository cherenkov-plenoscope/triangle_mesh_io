import triangle_mesh_io
import argparse
import os
import sys
import numpy as np

RC_GOOD = 0
RC_BAD = 17


def read_any_mesh(path):
    try:
        with open(path, "rt") as f:
            stl = triangle_mesh_io.stl.loads(f.read(), mode="t")
        return triangle_mesh_io.stl.to_vertices_and_faces(stl=stl)
    except:
        pass

    try:
        with open(path, "rb") as f:
            stl = triangle_mesh_io.stl.loads(f.read(), mode="b")
        return triangle_mesh_io.stl.to_vertices_and_faces(stl=stl)
    except:
        pass

    try:
        with open(path, "rt") as f:
            off = triangle_mesh_io.off.loads(f.read())
        return triangle_mesh_io.off.to_vertices_and_faces(off=off)
    except:
        pass

    try:
        with open(path, "rt") as f:
            obj = triangle_mesh_io.obj.loads(f.read())
        return triangle_mesh_io.obj.to_vertices_and_faces(obj=obj)
    except:
        pass

    assert False, "Expected either STL, OFF, or OBJ file."


def main():
    parser = argparse.ArgumentParser(
        prog="triangle-mesh-io",
        description="Convert, repair and add vertex-normals to triangle meshes.",
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Print the version."
    )

    commands = parser.add_subparsers(help="Commands", dest="command")

    # init
    # ----
    to_obj_cmd = commands.add_parser(
        "to-obj",
        help=(
            "Convert an STL or OFF mesh to an OBJ mesh with vertex-normals."
        ),
    )
    to_obj_cmd.add_argument(
        "in_path",
        default=None,
        metavar="IN_PATH",
        type=str,
        help=("Path of the input mesh (STL, OFF, or OBJ)."),
    )
    to_obj_cmd.add_argument(
        "out_path",
        default=None,
        metavar="OUT_PATH",
        type=str,
        help=("Path of the output obj mesh."),
    )
    to_obj_cmd.add_argument(
        "--mtl",
        default="NAME_OF_MATERIAL",
        metavar="NAME_OF_MATERIAL",
        type=str,
        help=("Name of the obj material."),
    )
    to_obj_cmd.add_argument(
        "--vertex-epsilon",
        default=None,
        metavar="EPS",
        type=float,
        help=("Vertices closer than this are considerd the same."),
    )
    to_obj_cmd.add_argument(
        "--vertex-normal-epsilon-deg",
        default=1e-9,
        metavar="DEG",
        type=float,
        help=("Vertex normals closer than this are considerd the same."),
    )
    to_obj_cmd.add_argument(
        "--vertex-normal-smooth-epsilon-deg",
        default=2.5,
        metavar="DEG",
        type=float,
        help=("Vertex normals closer than this are considerd the same."),
    )

    args = parser.parse_args()

    if args.version:
        print(triangle_mesh_io.__version__)
        return RC_GOOD

    if args.command == "to-obj":
        vertices, faces = read_any_mesh(path=args.in_path)

        obj = triangle_mesh_io.mesh.init_from_vertices_and_faces_with_vertex_normals(
            vertices=vertices,
            faces=faces,
            mtl=args.mtl,
            vertex_eps=args.vertex_epsilon,
            vertex_normal_eps=np.deg2rad(args.vertex_normal_epsilon_deg),
            vertex_normal_smooth_eps=np.deg2rad(
                args.vertex_normal_smooth_epsilon_deg
            ),
        )
        with open(args.out_path, "wt") as f:
            f.write(triangle_mesh_io.obj.dumps(obj=obj))

    else:
        print("Unknown command.")
        parser.print_help()
        return RC_BAD


if __name__ == "__main__":
    sys.exit(main())
