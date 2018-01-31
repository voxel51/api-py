#!usr/bin/env python
'''
Voxel51 API Python client library utility functions for programmatic access
to the API's functions.

Copyright 2017-2018, Voxel51, LLC
voxel51.com

David Hodgson, david@voxel51.com
'''

from pprint import pprint


def print_rsp(res):
    '''Utility function to pretty print the response from HTTP requests

    Args:
        res: HTTP response object

    Returns:
        None
    '''

    pprint(res.url)
    pprint(res.status_code)
    pprint(res.json())
