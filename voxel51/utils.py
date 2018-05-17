'''
Utility functions for the Voxel51 Vision Services API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com
'''
import json
import logging
import os
import shutil


logger = logging.getLogger(__name__)


def ensure_basedir(path):
    '''Makes the base directory of the given path, if necessary.

    Args:
        path (str): a file path
    '''
    dirname = os.path.dirname(path)
    if dirname and not os.path.isdir(dirname):
        logger.info("Making directory '%s'", dirname)
        os.makedirs(dirname)


def copy_file(inpath, outpath):
    '''Copies the input file to the output location.

    The base output directory is created, if necessary.

    Args:
        inpath (str): the input file
        output (str): the output file location
    '''
    ensure_basedir(outpath)
    shutil.copy(inpath, outpath)


def read_json(path):
    '''Reads JSON from file.

    Args:
        path (str): the input path

    Returns:
        a JSON list/dictionary
    '''
    with open(path, "rt") as f:
        return json.load(f)


def write_json(obj, path):
    '''Writes JSON object to file, creating the output directory if necessary.

    Args:
        obj: an object that can be directly dumped to a JSON file
        path (str): the output path
    '''
    ensure_basedir(path)
    with open(path, "wt") as f:
        f.write(json.dumps(obj, indent=4))


class Serializable(object):
    '''Base class for objects that can be serialized as JSON dictionaries.'''

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, d):
        '''Constructs a Serializable object from a JSON dictionary. Subclasses
        must implement this method.
        '''
        raise NotImplementedError("subclass must implement from_dict()")

    @classmethod
    def from_json(cls, path):
        '''Constructs a Serializable object from a JSON file.

        Subclasses may override this method, but, by default, this method
        simply reads the JSON and calls from_dict(), which subclasses must
        implement.
        '''
        return cls.from_dict(read_json(path))

    def to_dict(self):
        '''Serialzes the object into a JSON dictionary.

        Returns:
            a JSON serializable dictionary representation of this object.
        '''
        return {
            v: _recurse(getattr(self, k))
            for k, v in self._attributes().items()
        }

    def to_json(self, path):
        '''Serialzes the object to disk.

        Args:
            path (str): the output JSON file path. The base output directory
                is created, if necessary
        '''
        write_json(self.to_dict(), path)

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
        return {ki: _recurse(vi) for ki, vi in v.items()}
    elif isinstance(v, Serializable):
        return v.to_dict()
    return v
