'''
Utility functions for the Voxel51 Platform API.

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
from future.utils import iteritems
# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

import json
import logging
import os
import shutil

from requests_toolbelt.multipart.encoder import MultipartEncoder


logger = logging.getLogger(__name__)


def read_json(path):
    '''Reads JSON from file.

    Args:
        path (str): the input path

    Returns:
        a JSON list/dictionary
    '''
    with open(path, "rt") as f:
        return json.load(f)


def load_json(str_or_bytes):
    '''Loads JSON from string.

    Args:
        str_or_bytes (str): the input string or bytes

    Returns:
        a JSON list/dictionary
    '''
    try:
        return json.loads(str_or_bytes)
    except TypeError:
        # Must be a Python version for which json.loads() cannot handle bytes
        return json.loads(str_or_bytes.decode("utf-8"))


def json_to_str(obj):
    '''Generates a string representation of the JSON object.

    Args:
        obj: an object that can be directly dumped to a JSON file

    Returns:
        a string representation of the JSON object
    '''
    return json.dumps(obj, indent=4)


def write_json(obj, path):
    '''Writes JSON object to file, creating the output directory if necessary.

    Args:
        obj: an object that can be directly dumped to a JSON file
        path (str): the output path
    '''
    ensure_basedir(path)
    with open(path, "wt") as f:
        f.write(json_to_str(obj))


def copy_file(inpath, outpath):
    '''Copies the input file to the output location.

    The base output directory is created, if necessary.

    Args:
        inpath (str): the input file
        output (str): the output file location
    '''
    ensure_basedir(outpath)
    shutil.copy(inpath, outpath)


def ensure_basedir(path):
    '''Makes the base directory of the given path, if necessary.

    Args:
        path (str): a file path
    '''
    dirname = os.path.dirname(path)
    if dirname and not os.path.isdir(dirname):
        logger.info("Making directory '%s'", dirname)
        os.makedirs(dirname)


class Serializable(object):
    '''Base class for objects that can be represented in JSON format.'''

    def __str__(self):
        return self.to_str()

    def to_dict(self):
        '''Generates a JSON dictionary representation of the object.

        Returns:
            a JSON dictionary representation of the object
        '''
        return {
            v: _recurse(getattr(self, k))
            for k, v in iteritems(self._attributes())
        }

    def to_str(self):
        '''Generates a string representation of the object.

        Returns:
            a string representation of the object
        '''
        return json_to_str(self.to_dict())

    def to_json(self, path):
        '''Write the object to disk in JSON format.

        Args:
            path (str): the output JSON file path. The base output directory
                is created, if necessary
        '''
        write_json(self.to_dict(), path)

    @classmethod
    def from_dict(cls, d):
        '''Constructs a Serializable object from a JSON representation of it.
        Subclasses must implement this method.

        Args:
            d (dict): a JSON dictionary representation of a Serializable
                subclass

        Returns:
            an instance of the Serializable subclass
        '''
        raise NotImplementedError("subclass must implement from_dict()")

    @classmethod
    def from_str(cls, s):
        '''Constructs a Serializable object from a string representation of it.

        Args:
            s (str): a string representation of a Serializable subclass

        Returns:
            an instance of the Serializable subclass
        '''
        return cls.from_dict(load_json(s))

    @classmethod
    def from_json(cls, path):
        '''Constructs a Serializable object from a JSON file.

        Args:
            path (str): the path to a JSON file

        Returns:
            an instance of the Serializable subclass
        '''
        return cls.from_dict(read_json(path))

    def _attributes(self):
        '''Returns a dictionary describing the class attributes to be
        serialized.

        Subclasses can override this method, but, by default, all attributes
        in vars(self) are returned, minus private attributes (those starting
        with "_").

        Returns:
            a dictionary mapping attribute names to field names (as they
            should appear in the JSON file)
        '''
        return {a: a for a in vars(self) if not a.startswith("_")}


def _recurse(v):
    if isinstance(v, list):
        return [_recurse(vi) for vi in v]
    elif isinstance(v, dict):
        return {ki: _recurse(vi) for ki, vi in iteritems(v)}
    elif isinstance(v, Serializable):
        return v.to_dict()
    return v


def upload_files(requests, url, files, headers, **kwargs):
    '''Upload one or more files of any size using a streaming upload.

    This is intended as an alternative to using ``requests`` directly for files
    larger than 2GB.

    Args:
        requests (requests|requests.Session): an existing session to use, or
            the ``requests`` module
        url (str): the request endpoint
        files (dict): files to upload, in the same format as the ``files``
            argument to ``requests``
        headers (dict): headers to include
        kwargs: any other arguments to pass to ``requests``

    Returns:
        a ``requests.Response``
    '''
    # note: this is limited to 8K chunk size. If this becomes an issue,
    # monkey-patching data.read to ignore the given chunk size is an option.
    data = MultipartEncoder(files)
    # add the necessary content-type without modifying the original headers
    headers = headers.copy()
    headers["Content-Type"] = data.content_type
    return requests.post(url, headers=headers, data=data, **kwargs)
