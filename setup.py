#!/usr/bin/env python
'''
Installs the voxel51-api-py package.

| Copyright 2017-2019, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
from setuptools import setup, find_packages

import voxel51.constants as voxc


setup_requires = [
    "future",
]

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
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires="~2.7, >=3",
)
