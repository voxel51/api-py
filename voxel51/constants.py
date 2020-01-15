'''
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

import os

try:
    from importlib.metadata import metadata  # Python 3.8
except ModuleNotFoundError:
    from importlib_metadata import metadata  # Python < 3.8


_META = metadata("voxel51-api-py")
NAME = _META["name"]
VERSION = _META["version"]
DESCRIPTION = _META["description"]
AUTHOR = _META["author"]
CONTACT = _META["contact"]
URL = _META["url"]
LICENSE = _META["license"]
VERSION_LONG = "%s v%s, %s" % (NAME, VERSION, AUTHOR)
