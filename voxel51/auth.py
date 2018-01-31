#!usr/bin/env python
'''
Voxel51 API Python client library authentication functions for programmatic
access to the API's functions.

Copyright 2017-2018, Voxel51, LLC
voxel51.com

David Hodgson, david@voxel51.com
'''

import os
LIB = os.path.dirname(os.__file__) + '/api-token.json'
# Grabs the modules install location


def load_token():
    '''Searches for API authentication token.
    Searches for the API token by checking if the VOXEL51_API_TOKEN
    environment variable is set; if not, it searches for a
    $LIB/.api-token.json file. Returns error if neither exist

    Args:
        None

    Returns:
        API token from environment variable or file
    '''
    token = os.environ.get('VOXEL51_API_TOKEN')
    if (token is None):
        return -1

    else:
        with open(LIB, 'rb') as f:
            token = f.read()
            if (token.length == 0):
                return -2

            else:
                return token


def activate_token(token):
    '''Copies input token to $LIB/.api-token.json.

    Args:
        token (str): API token to store in $LIB/.api-token.json

    Returns:
        None
    '''

    try:
        with open(LIB, 'w') as f:
            f.write(token)

    except IOError:
        return -1


def deactivate_token():
    '''Deletes the stored token from $LIB/.api-token.json.

    Args:
        None

    Returns:
        None
    '''

    try:
        os.remove(LIB)

    except IOError:
        return -1


print(LIB)
