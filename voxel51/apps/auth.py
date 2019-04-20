'''
Application authentication module for the Voxel51 Platform API.

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

from voxel51.auth import Token, TokenLoadError
import voxel51.utils as voxu


logger = logging.getLogger(__name__)


TOKEN_ENVIRON_VAR = "VOXEL51_APP_TOKEN"
KEY_HEADER = "x-voxel51-application"
USER_HEADER = "x-voxel51-application-user"
TOKEN_PATH = os.path.join(
    os.path.expanduser("~"), ".voxel51", "app-token.json")


def activate_application_token(path):
    '''Activates the application token by copying it to
    ``~/.voxel51/app-token.json``.

    Subsequent API instances created will now use this token for
    authentication.

    Args:
        path (str): the path to an :class:`ApplicationToken` JSON file
    '''
    voxu.copy_file(path, TOKEN_PATH)
    logger.info("ApplicationToken successfully activated")


def deactivate_application_token():
    '''Deactivates (deletes) the currently active application token, if any.

    The active application token is at ``~/.voxel51/app-token.json``.
    '''
    try:
        os.remove(TOKEN_PATH)
        logger.info(
            "ApplicationToken '%s' successfully deactivated", TOKEN_PATH)
    except OSError:
        logger.info("No token to deactivate")


def load_application_token(token_path=None):
    '''Loads the active application token.

    Args:
        token_path: an optional path to an :class:`ApplicationToken` JSON file.
            If no path is provided, the ``VOXEL51_APP_TOKEN`` environment
            variable is checked and, if set, the token is loaded from that
            path. Otherwise, the token is loaded from
            ``~/.voxel51/app-token.json``

    Returns:
        an :class:`ApplicationToken` instance

    Raises:
        voxel51.auth.TokenLoadError: if no valid token was found
    '''
    path = token_path or os.environ.get(TOKEN_ENVIRON_VAR) or TOKEN_PATH
    try:
        return ApplicationToken.from_json(path)
    except IOError:
        raise TokenLoadError("No application token found")


class ApplicationToken(Token):
    '''A class encapsulating an application's API authentication token.'''

    def get_header(self, username=None):
        '''Returns a header dictionary for authenticating requests with
        this application token.

        Args:
            username: an optional username for which the requests are being
                performed. By default, no username is included

        Returns:
            a header dictionary
        '''
        header = {KEY_HEADER: self._private_key}
        if username:
            header[USER_HEADER] = username
        return header
