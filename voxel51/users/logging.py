'''
Logging utilities for the Voxel51 Platform API.

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

import logging


def setup_logging(level=logging.INFO, format="%(message)s"):
    '''Sets up basic logging to stdout.

    Note that this method uses `logging.basicConfig`, so it does nothing if
    the root logger already has handlers configured. This is intentional so
    that applications using this library can configure logging as desired.

    Args:
        level (str): the logging level. The default is `logging.INFO`
        format (str): the logging format. The default is `"%(message)s"`
    '''
    logging.basicConfig(level=level, format=format)
