import setuptools
import os


with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join("triangle_mesh_io", "version.py")) as f:
    txt = f.read()
    last_line = txt.splitlines()[-1]
    version_string = last_line.split()[-1]
    version = version_string.strip("\"'")

setuptools.setup(
    name="triangle_mesh_io",
    version=version,
    description="Load and dump triangle-meshes from and to OBJ, OFF, and STL.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/cherenkov-plenoscope/triangle_mesh_io",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    packages=[
        "triangle_mesh_io",
        "triangle_mesh_io.mesh",
    ],
    package_data={
        "triangle_mesh_io": [
            os.path.join("tests", "resources", "*"),
        ],
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: File Formats",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Multimedia :: Graphics :: Editors",
    ],
    entry_points={
        "console_scripts": [
            "triangle-mesh-io=triangle_mesh_io.apps.main:main",
        ]
    },
)
