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
