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
from sys import version_info

if version_info >= (3,8):
    from importlib.metadata import metadata
else:
    from importlib_metadata import metadata

#
# IMPORTANT: this module can't import other modules from this package!
#

# Package metadata
PACKAGE_METADATA = metadata("voxel51-api-py")
NAME = PACKAGE_METADATA["name"]
VERSION = PACKAGE_METADATA["version"]
DESCRIPTION = PACKAGE_METADATA["description"]
AUTHOR = PACKAGE_METADATA["author"]
CONTACT = PACKAGE_METADATA["contact"]
URL = PACKAGE_METADATA["url"]
LICENSE = PACKAGE_METADATA["license"]
VERSION_LONG = "%s v%s, %s" % (NAME, VERSION, AUTHOR)
