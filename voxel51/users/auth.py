'''
Authentication module for the Voxel51 Platform API.

| Copyright 2017-2020, Voxel51, Inc.
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


TOKEN_ENV_VAR = "VOXEL51_API_TOKEN"
PRIVATE_KEY_ENV_VAR = "VOXEL51_API_PRIVATE_KEY"
BASE_API_URL_ENV_VAR = "VOXEL51_API_BASE_URL"

TOKEN_PATH = os.path.join(
    os.path.expanduser("~"), ".voxel51", "api-token.json")

DEFAULT_BASE_API_URL = "https://api.voxel51.com"
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
    '''Gets the path to the active API token, if any.

    If the ``VOXEL51_API_TOKEN`` environment variable is set, that path is
    used. Otherwise, ``~/.voxel51/api-token.json`` is used.

    Note that if the ``VOXEL51_API_PRIVATE_KEY`` environment variable is set,
    this function will always return None, since that environment variable
    always takes precedence over other methods for locating the active token.

    Returns:
        the path to the active token, or None if no token was found
    '''
    private_key = os.environ.get(PRIVATE_KEY_ENV_VAR, None)
    if private_key:
        return None

    token_path = os.environ.get(TOKEN_ENV_VAR, None)
    if token_path is not None:
        if not os.path.isfile(token_path):
            raise TokenError(
                "No file found at '%s=%s'" % (TOKEN_ENV_VAR, token_path))
    elif os.path.isfile(TOKEN_PATH):
        token_path = TOKEN_PATH

    return token_path


def load_token(token_path=None):
    '''Loads the active API token.

    The following strategy is used to locate the active API token (in order of
    precedence):

        (1) Use the provided ``token_path``
        (2) Use the ``VOXEL51_API_PRIVATE_KEY`` and ``VOXEL51_API_BASE_URL``
            environment variables
        (3) Use the ``VOXEL51_API_TOKEN`` environment variable
        (4) Load the active token from ``~/.voxel51/api-token.json``

    Args:
        token_path (str, optional): the path to a :class:`Token` JSON file.
            If no path is provided, the active token is loaded using the
            strategy described above

    Returns:
        a :class:`Token` instance

    Raises:
        :class:`TokenError` if no valid token was found
    '''
    # Load token from provided path
    if token_path is not None:
        return _load_token_from_path(token_path)

    # Load token from environment variables, if possible
    private_key = os.environ.get(PRIVATE_KEY_ENV_VAR, None)
    if private_key:
        base_api_url = os.environ.get(BASE_API_URL_ENV_VAR, None)
        return Token.from_private_key(private_key, base_api_url=base_api_url)

    # Try to load token from path
    token_path = get_active_token_path()
    if token_path is not None:
        return _load_token_from_path(token_path)

    raise TokenError("No API token found")


def _load_token_from_path(token_path):
    if not os.path.isfile(token_path):
        raise TokenError("No file found at '%s'" % token_path)

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
        private_key (str): the private key of the token
    '''

    def __init__(self, token_dict):
        '''Creates a token object with the given contents

        Args:
            token_dict (dict): a JSON dictionary defining an API token
        '''
        access_token = token_dict["access_token"]
        self.base_api_url = self._parse_base_api_url(access_token)
        self.creation_date = access_token.get("created_at", None)
        self.id = access_token.get("token_id", None)
        self.private_key = access_token["private_key"]
        self._token_dict = token_dict

    def __str__(self):
        return voxu.json_to_str(self._token_dict)

    def get_header(self):
        '''Returns a header dictionary for authenticating requests with
        this token.

        Returns:
            a header dictionary
        '''
        return {"Authorization": "Bearer " + self.private_key}

    @classmethod
    def from_json(cls, path):
        '''Loads a Token from JSON.

        Args:
            path (str): the path to a Token JSON file

        Returns:
            a Token instance
        '''
        return cls(voxu.read_json(path))

    @classmethod
    def from_dict(cls, token_dict):
        '''Loads a Token from a JSON dictionary.

        Args:
            token_dict (dict): a JSON dictionary defining the Token

        Returns:
            a Token instance
        '''
        return cls(token_dict)

    @classmethod
    def from_str(cls, token_str):
        '''Loads a Token from a JSON string.

        Args:
            token_str (str): a string representation of the Token

        Returns:
            a Token instance
        '''
        return cls(voxu.load_json(token_str))

    @classmethod
    def from_private_key(cls, private_key, base_api_url=None):
        '''Builds a Token from its private key.

        Args:
            private_key (str): the private key of the token
            base_api_url (str, optional): the base URL of the API for the
                token. If none, the default platform API is assumed

        Returns:
            a Token instance
        '''
        return cls({
            "access_token": {
                "private_key": private_key,
                "base_api_url": base_api_url or DEFAULT_BASE_API_URL,
            }
        })

    @staticmethod
    def _parse_base_api_url(access_token):
        base_api_url = access_token.get("base_api_url", None)
        if base_api_url is None:
            base_api_url = DEFAULT_BASE_API_URL
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
