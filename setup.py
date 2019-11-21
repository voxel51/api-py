#!/usr/bin/env python
'''
Installs the voxel51-api-py package.

| Copyright 2017-2019, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
from setuptools import setup, find_packages

import voxel51.constants as voxc


setup(
    name=voxc.NAME,
    version=voxc.VERSION,
    description=voxc.DESCRIPTION,
    author=voxc.AUTHOR,
    author_email=voxc.CONTACT,
    url=voxc.URL,
    license=voxc.LICENSE,
    packages=find_packages(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    scripts=["voxel51/cli/voxel51"],
)
