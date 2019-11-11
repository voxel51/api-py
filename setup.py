#!/usr/bin/env python
'''
Installs the Python client library for the Voxel51 Platform API.

Copyright 2017-2019, Voxel51, Inc.
voxel51.com
'''
from setuptools import setup, find_packages


setup(
    name="voxel51-api-python",
    version="0.1.0",
    description="Python client library for the Voxel51 Platform API",
    author="Voxel51, Inc.",
    author_email="support@voxel51.com",
    url="https://github.com/voxel51/api-python",
    license="BSD 4-clause",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "requests>=2.18.4",
    ],
    scripts=["voxel51/cli/voxel51"],
)
