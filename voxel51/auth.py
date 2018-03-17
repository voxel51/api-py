'''
Authentication library for the Voxel51 Vision Services API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com
'''
import logging
import os

import voxel51.utils as voxu


logger = logging.getLogger(__name__)


TOKEN_ENVIRON_VAR = "VOXEL51_API_TOKEN"
VOXEL51_DIR = os.path.join(os.path.expanduser("~"), ".voxel51")
TOKEN_PATH = os.path.join(VOXEL51_DIR, "api-token.json")
PRIVATE_KEY_FIELD = "private_key"


def activate_token(path):
    '''Activates the given token by copying it to ~/.voxel51/api-token.json.

    Subsequent voxel51.api.API() instances created will now use this token
    for authentication.

    Args:
        path (str): the path to an API token to store in $LIB/.api-token.json
    '''
    voxu.copy_file(path, TOKEN_PATH)
    logger.info("Token successfully activated")


def deactivate_token():
    '''Deactivates (deletes) the currently active token, if any.

    The active token is the token at ~/.voxel51/api-token.json
    '''
    try:
        os.remove(TOKEN_PATH)
        logger.info("Token '%s' successfully deactivated", TOKEN_PATH)
    except OSError:
        logger.info("No active token to deactivate")


def load_token():
    '''Loads the active API token.

    If the VOXEL51_API_TOKEN environment variable is set, this is the active
    token and will be loaded. Otherwise the token is loaded from
    ~/.voxel51/api-token.json.

    Returns:
        The active token, an instance of Token()

    Raises:
        TokenLoadError: if no valid token was found
    '''
    path = os.environ.get(TOKEN_ENVIRON_VAR) or TOKEN_PATH
    try:
        return Token.from_disk(path)
    except IOError:
        raise TokenLoadError("No token found at '%s'" % TOKEN_PATH)


class TokenLoadError(Exception):
    pass


class Token(object):
    '''A class encapsulating an API authentication token.'''

    def __init__(self, content):
        '''Creates a token object with the given contents

        Args:
            content (dict): a JSON dictionary defining an API token
        '''
        self._content = content

    def get_header(self):
        '''Returns a header dictionary for authenticating requests with
        this token.'''
        return {"Authorization": "Bearer " + self._content[PRIVATE_KEY_FIELD]}

    @classmethod
    def from_disk(cls, path):
        '''Loads a token from disk.

        Args:
            path (str): the path to a valid token JSON file

        Returns:
            An instance of Token()
        '''
        return cls(voxu.read_json(path))
