'''
Authentication module for the Voxel51 Platform API.

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
import os

import voxel51.users.utils as voxu


logger = logging.getLogger(__name__)


TOKEN_ENVIRON_VAR = "VOXEL51_API_TOKEN"
TOKEN_PATH = os.path.join(
    os.path.expanduser("~"), ".voxel51", "api-token.json")

HELP_URL = "https://voxel51.com/docs/api/?python#authentication"


def activate_token(path):
    '''Activates the token by copying it to ``~/.voxel51/api-token.json``.

    Subsequent API instances created will now use this token for
    authentication.

    Args:
        path (str): the path to a :class:`Token` JSON file
    '''
    voxu.copy_file(path, TOKEN_PATH)
    logger.info("API token successfully activated")


def deactivate_token():
    '''Deactivates (deletes) the currently active token, if any.

    The active token is the token at ``~/.voxel51/api-token.json``.
    '''
    try:
        os.remove(TOKEN_PATH)
        logger.info("API token '%s' successfully deactivated", TOKEN_PATH)
    except OSError:
        logger.info("No API token to deactivate")


def get_active_token_path():
    '''Gets the path to the active API token.

    If the ``VOXEL51_API_TOKEN`` environment variable is set, that path is
    used. Otherwise, ``~/.voxel51/api-token.json`` is used.

    Returns:
        the path to the active token

    Raises:
        :class:`TokenError` if no token was found
    '''
    token_path = os.environ.get(TOKEN_ENVIRON_VAR, None)
    if token_path is not None:
        if not os.path.isfile(token_path):
            raise TokenError(
                "No API token found at '%s=%s'" %
                (TOKEN_ENVIRON_VAR, token_path))
    elif os.path.isfile(TOKEN_PATH):
        token_path = TOKEN_PATH
    else:
        raise TokenError("No API token found")

    return token_path


def load_token(token_path=None):
    '''Loads the active API token.

    Args:
        token_path (str, optional): the path to a :class:`Token` JSON file.
            If no path is provided, the ``VOXEL51_API_TOKEN`` environment
            variable is checked and, if set, the token is loaded from that
            path. Otherwise, it is loaded from ``~/.voxel51/api-token.json``

    Returns:
        a :class:`Token` instance

    Raises:
        :class:`TokenError` if no valid token was found
    '''
    if token_path is None:
        token_path = get_active_token_path()
    elif not os.path.isfile(token_path):
        raise TokenError("No API token found at '%s'" % token_path)

    try:
        return Token.from_json(token_path)
    except IOError:
        raise TokenError("File '%s' is not a valid API token" % token_path)


class Token(object):
    '''A class encapsulating an API authentication token.

    Attributes:
        base_api_url (str): the base URL of the API for the token
        creation_date (str): the creation date of the token
        id (str): the ID of the token
    '''

    def __init__(self, token_dict):
        '''Creates a token object with the given contents

        Args:
            token_dict (dict): a JSON dictionary defining an API token
        '''
        access_token = token_dict["access_token"]
        self.base_api_url = self._parse_base_api_url(access_token)
        self.creation_date = access_token["created_at"]
        self.id = access_token["token_id"]
        self._private_key = access_token["private_key"]
        self._token_dict = token_dict

    def __str__(self):
        return voxu.json_to_str(self._token_dict)

    def get_header(self):
        '''Returns a header dictionary for authenticating requests with
        this token.

        Returns:
            a header dictionary
        '''
        return {"Authorization": "Bearer " + self._private_key}

    @classmethod
    def from_json(cls, path):
        '''Loads a Token from JSON.

        Args:
            path (str): the path to a Token JSON file

        Returns:
            a Token instance
        '''
        return cls(voxu.read_json(path))

    @staticmethod
    def _parse_base_api_url(access_token):
        base_api_url = access_token.get("base_api_url", None)
        if base_api_url is None:
            base_api_url = "https://api.voxel51.com"
            logger.warning(
                "No base API URL found in token; defaulting to '%s'. To "
                "resolve this message, download a new API token from the "
                "Platform", base_api_url)

        return base_api_url


class TokenError(Exception):
    '''Exception raised when a problem with a :class:`Token` is encountered.'''

    def __init__(self, message):
        '''Creates a TokenError instance.

        Args:
            message (str): the error message
        '''
        super(TokenError, self).__init__(
            "%s. See %s for more information about activating an API token."
            % (message, HELP_URL))
