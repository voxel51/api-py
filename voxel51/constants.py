'''
Package-wide constants.

IMPORTANT: this module can't import other modules from this package!

| Copyright 2017-2019, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=unused-wildcard-import
# pragma pylint: disable=wildcard-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import *
# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

import json
import os


# Paths and directories
VOXEL51_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_JSON_PATH = os.path.join(VOXEL51_DIR, "version.json")


# Version
with open(VERSION_JSON_PATH, "rt") as f:
    _VER = json.load(f)
NAME = _VER["name"]
VERSION = _VER["version"]
DESCRIPTION = _VER["description"]
AUTHOR = _VER["author"]
CONTACT = _VER["contact"]
URL = _VER["url"]
LICENSE = _VER["license"]