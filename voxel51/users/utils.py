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
import six
# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

import json
import logging
import os
import shutil
import sys

from requests_toolbelt.multipart.encoder import MultipartEncoder


logger = logging.getLogger(__name__)


def urljoin(*args):
    '''Combines the URL parts into a single URL.

    Args:
        *args: a list of URL parts

    Returns:
        the full URL
    '''
    return "/".join([a.strip("/") for a in args])


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
        return json.loads(str_or_bytes.decode())


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
    with open(path, "wb") as f:
        f.write(_to_bytes(json_to_str(obj)))


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
    #
    # NOTE: this is limited to 8K chunk size. If this becomes an issue,
    # monkey-patching data.read to ignore the given chunk size is an option
    #
    data = MultipartEncoder(files)

    headers = headers.copy()
    headers["Content-Type"] = data.content_type
    return requests.post(url, headers=headers, data=data, **kwargs)


def query_yes_no(question, default=None):
    '''Asks a yes/no question via the command-line and returns the answer.

    This function is case insensitive and partial matches are allowed.

    Args:
        question: the question to ask
        default: the default answer, which can be "yes", "no", or None (a
            response is required). The default is None

    Returns:
        True/False whether the user replied "yes" or "no"

    Raises:
        ValueError: if the default value was invalid
    '''
    valid = {"y": True, "ye": True, "yes": True, "n": False, "no": False}

    if default:
        default = default.lower()
        try:
            prompt = " [Y/n] " if valid[default] else " [y/N] "
        except KeyError:
            raise ValueError("Invalid default value '%s'" % default)
    else:
        prompt = " [y/n] "

    while True:
        sys.stdout.write(question + prompt)
        choice = six.moves.input().lower()
        if default and not choice:
            return valid[default]
        if choice in valid:
            return valid[choice]
        print("Please respond with 'y[es]' or 'n[o]'")


def to_human_time_str(num_seconds, decimals=1, max_unit=None):
    '''Converts the given number of seconds to a human-readable time string.

    The supported units are ["ns", "us", "ms", "second", "minute", "hour",
    "day", "week", "month", "year"].

    Examples:
        0.001 => "1ms"
        60 => "1 minute"
        65 => "1.1 minutes"
        60123123 => "1.9 years"

    Args:
        num_seconds: the number of seconds
        decimals: the desired number of decimal points to show in the string.
            The default is 1
        max_unit: an optional max unit, e.g., "hour", beyond which to stop
            converting to larger units, e.g., "day". By default, no maximum
            unit is used

    Returns:
        a human-readable time string like "1.5 minutes" or "20.1 days"
    '''
    if num_seconds == 0:
        return "0 seconds"

    units = [
        "ns", "us", "ms", " second", " minute", " hour", " day", " week",
        " month", " year"]
    conversions = [1000, 1000, 1000, 60, 60, 24, 7, 52 / 12, 12, float("inf")]
    pluralizable = [
        False, False, False, True, True, True, True, True, True, True]

    if max_unit and not any(u.strip() == max_unit for u in units):
        logger.warning("Unsupported max_unit = %s; ignoring", max_unit)
        max_unit = None

    num = 1e9 * num_seconds  # start with smallest unit
    for unit, conv, plural in zip(units, conversions, pluralizable):
        if abs(num) < conv:
            break
        if max_unit and unit.strip() == max_unit:
            break
        num /= conv

    # Convert to string with the desired number of decimals, UNLESS those
    # decimals are zeros, in which case they are removed
    str_fmt = "%." + str(decimals) + "f"
    num_only_str = (str_fmt % num).rstrip("0").rstrip(".")

    # Add units
    num_str = num_only_str + unit
    if plural and num_only_str != "1":
        num_str += "s"  # handle pluralization

    return num_str


def to_human_decimal_str(num, decimals=1, max_unit=None):
    '''Returns a human-readable string represntation of the given decimal
    (base-10) number.

    Supported units are ["", "K", "M", "B", "T"].

    Examples:
        65 => "65"
        123456 => "123.5K"
        1e7 => "10M"

    Args:
        num: a number
        decimals: the desired number of digits after the decimal point to show.
            The default is 1
        max_unit: an optional max unit, e.g., "M", beyond which to stop
            converting to larger units, e.g., "B". By default, no maximum unit
            is used

    Returns:
        a human-readable decimal string
    '''
    units = ["", "K", "M", "B", "T"]
    if max_unit is not None and max_unit not in units:
        logger.warning("Unsupported max_unit = %s; ignoring", max_unit)
        max_unit = None

    for unit in units:
        if abs(num) < 1000:
            break
        if max_unit is not None and unit == max_unit:
            break
        num /= 1000

    str_fmt = "%." + str(decimals) + "f"
    return (str_fmt % num).rstrip("0").rstrip(".") + unit


def to_human_bytes_str(num_bytes, decimals=1, max_unit=None):
    '''Returns a human-readable string represntation of the given number of
    bytes.

    Supported units are ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"].

    Examples:
        123 => "123B"
        123000 => "120.1KB"
        1024 ** 4 => "1TB"

    Args:
        num_bytes: a number of bytes
        decimals: the desired number of digits after the decimal point to show.
            The default is 1
        max_unit: an optional max unit, e.g., "TB", beyond which to stop
            converting to larger units, e.g., "PB". By default, no maximum
            unit is used

    Returns:
        a human-readable bytes string
    '''
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    if max_unit is not None and max_unit not in units:
        logger.warning("Unsupported max_unit = %s; ignoring", max_unit)
        max_unit = None

    for unit in units:
        if abs(num_bytes) < 1024:
            break
        if max_unit is not None and unit == max_unit:
            break
        num_bytes /= 1024

    str_fmt = "%." + str(decimals) + "f"
    return (str_fmt % num_bytes).rstrip("0").rstrip(".") + unit


def to_human_bits_str(num_bits, decimals=1, max_unit=None):
    '''Returns a human-readable string represntation of the given number of
    bits.

    Supported units are ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"].

    Examples:
        123 => "123b"
        123000 => "120.1Kb"
        1024 ** 4 => "1Tb"

    Args:
        num_bits: a number of bits
        decimals: the desired number of digits after the decimal point to show.
            The default is 1
        max_unit: an optional max unit, e.g., "Tb", beyond which to stop
            converting to larger units, e.g., "Pb". By default, no maximum
            unit is used

    Returns:
        a human-readable bits string
    '''
    units = ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"]
    if max_unit is not None and max_unit not in units:
        logger.warning("Unsupported max_unit = %s; ignoring", max_unit)
        max_unit = None

    for unit in units:
        if abs(num_bits) < 1024:
            break
        if max_unit is not None and unit == max_unit:
            break
        num_bits /= 1024

    str_fmt = "%." + str(decimals) + "f"
    return (str_fmt % num_bits).rstrip("0").rstrip(".") + unit


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
    if isinstance(v, dict):
        return {ki: _recurse(vi) for ki, vi in iteritems(v)}
    if isinstance(v, Serializable):
        return v.to_dict()
    return v


def _to_bytes(val, encoding="utf-8"):
    bytes_str = (
        val.encode(encoding) if isinstance(val, six.text_type) else val)
    if not isinstance(bytes_str, six.binary_type):
        raise TypeError("Failed to convert %r to bytes" % bytes_str)

    return bytes_str
