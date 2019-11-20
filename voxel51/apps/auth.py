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

from voxel51.users.auth import Token, TokenError
import voxel51.users.utils as voxu


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


def get_active_application_token_path():
    '''Gets the path to the active application token.

    If the ``VOXEL51_APP_TOKEN`` environment variable is set, that path is
    used. Otherwise, ``~/.voxel51/app-token.json`` is used.

    Returns:
        the path to the active application token

    Raises:
        :class:`ApplicationTokenError` if no application token was found
    '''
    token_path = os.environ.get(TOKEN_ENVIRON_VAR, None)
    if token_path is not None:
        if not os.path.isfile(token_path):
            raise ApplicationTokenError(
                "No application token found at '%s=%s'" %
                (TOKEN_ENVIRON_VAR, token_path))
    elif os.path.isfile(TOKEN_PATH):
        token_path = TOKEN_PATH
    else:
        raise ApplicationTokenError("No application token found")

    return token_path


def load_application_token(token_path=None):
    '''Loads the active application token.

    Args:
        token_path (str, optional): the path to an :class:`ApplicationToken`
            JSON file. If no path is provided, the ``VOXEL51_APP_TOKEN``
            environment variable is checked and, if set, the token is loaded
            from that path. Otherwise, it is loaded from
            ``~/.voxel51/app-token.json``

    Returns:
        an :class:`ApplicationToken` instance

    Raises:
        :class:`ApplicationTokenError` if no valid application token was found
    '''
    if token_path is None:
        token_path = get_active_application_token_path()
    elif not os.path.isfile(token_path):
        raise ApplicationTokenError(
            "No application token found at '%s'" % token_path)

    try:
        return ApplicationToken.from_json(token_path)
    except IOError:
        raise ApplicationTokenError(
            "File '%s' is not a valid application token" % token_path)


class ApplicationToken(Token):
    '''A class encapsulating an application's API authentication token.'''

    def get_header(self, username=None):
        '''Returns a header dictionary for authenticating requests with
        this application token.

        Args:
            username (str, optional): a username for which the requests are
                being performed. By default, no username is included

        Returns:
            a header dictionary
        '''
        header = {KEY_HEADER: self._private_key}
        if username:
            header[USER_HEADER] = username
        return header


class ApplicationTokenError(TokenError):
    '''Exception raised when a problem with an :class:`ApplicationToken` is
    encountered.
    '''
    pass
