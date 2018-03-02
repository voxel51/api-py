#!/usr/bin/env python
'''
Install Voxel51 API Python client library.

Copyright 2018, Voxel51, LLC
voxel51.com
'''
from setuptools import setup, find_packages


setup(
    name="voxel51-api-python",
    version="1.0",
    description='Python client library for the Voxel51 Vision Services API',
    author="Voxel51, LLC",
    author_email="support@voxel51.com",
    url="https://github.com/voxel51/api-python",
    license="BSD 4-clause",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["requests", "requests-toolbelt", "six"],
)
