#!/usr/bin/env python
'''
Installs the voxel51-api-py package.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
from setuptools import setup, find_packages


setup(
    name="voxel51-api-py",
    version="0.1.0",
    description="Python client library for the Voxel51 Platform",
    author="Voxel51, Inc.",
    contact="info@voxel51.com",
    url="https://github.com/voxel51/api-py",
    license="BSD-4-Clause",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    scripts=["voxel51/cli/voxel51"],
    install_requires=[
        "argcomplete",
        "future",
        "python-dateutil>=2.7.0",
        "requests",
        "requests-toolbelt",
        "six",
        "tabulate",
        "tzlocal",
        'futures; python_version<"3"',
        'importlib_metadata; python_version<"3.8"',
    ],
    extras_require={
        "dev": [
            "m2r",
            "pycodestyle",
            "pylint",
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    },
    python_requires=">=2.7",
)
