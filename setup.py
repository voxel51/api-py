#!/usr/bin/env python
'''
Installs the voxel51-api-py package.

| Copyright 2017-2019, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
from json import load
from os import path
from setuptools import setup, find_packages


install_requires = [
    "argcomplete",
    "future",
    "python-dateutil",
    "requests",
    "requests-toolbelt",
    "six",
    "tabulate",
    "tzlocal",
    'futures; python_version<"3"',
]

extras_require = {
    "dev": [
        "m2r",
        "pycodestyle",
        "pylint",
        "sphinx",
        "sphinxcontrib-napoleon",
    ]
}

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "voxel51", "version.json")) as json_file:
    about = load(json_file)

setup(
    name=about["name"],
    version=about["version"],
    description=about["description"],
    author=about["author"],
    author_email=about["contact"],
    url=about["url"],
    license=about["license"],
    packages=find_packages(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    scripts=["voxel51/cli/voxel51"],
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=2.7",
)
