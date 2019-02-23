'''
Applications interface for the Voxel51 Vision Services API.

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

import json

import requests

from voxel51.api import API, APIError
import voxel51.apps.auth as voxa


class ApplicationAPI(API):
    '''Main class for managing an application session with the Voxel51 Vision
    Services API.

    Note that :class:`voxel51.apps.api.ApplicationAPI` is a subclass of
    :class:`voxel51.api.API`, which implies that, unless specifically
    overridden, applications can access all methods exposed for regular
    platform users. In order to use these user-specific methods, however, you
    must first activate a user via
    :func:`voxel51.apps.api.ApplicationAPI.with_user`.

    Attributes:
        base_url (string): the base URL of the API
        token (voxel51.apps.auth.ApplicationToken): the authentication token
            for this session
        keep_alive (bool): whether the request session should be kept alive
            between requests
        active_user (string): the currently active username, or None if no user
            is activated
    '''

    def __init__(self, token=None, keep_alive=False):
        '''Creates a new ApplicationAPI instance.

        Args:
            token (voxel51.apps.auth.ApplicationToken, optional): an optional
                :class:`ApplicationToken` to use. If no token is provided, the
                ``VOXEL51_APP_TOKEN`` environment variable is checked and, if
                set, the token is loaded from that path. Otherwise, the token
                is loaded from ``~/.voxel51/app-token.json``
            keep_alive (bool, optional): whether to keep the request session
                alive between requests. By default, this is False
        '''
        if token is None:
            token = voxa.load_application_token()
        super(ApplicationAPI, self).__init__(
            token=token, keep_alive=keep_alive)
        self.active_user = None

    def with_user(self, username):
        '''Activates the given user.

        When finished performing actions for the user, call :func:`exit_user`.

        Args:
            username: the name of a user
        '''
        self.active_user = username
        self._header = self.token.get_header(username=username)

    def exit_user(self):
        '''Exits active user mode, if necessary.'''
        self.active_user = None
        self._header = self.token.get_header()

    @classmethod
    def from_json(cls, token_path):
        '''Creates an :class:`ApplicationAPI` instance from the given
        :class:`ApplicationToken` JSON file.

        Args:
            token_path: the path to an
                :class:`voxel51.apps.auth.ApplicationToken` JSON file

        Returns:
            an :class:`ApplicationAPI` instance
        '''
        token = voxa.load_application_token(token_path=token_path)
        return cls(token=token)

    # USERS ###################################################################

    def create_user(self, username):
        '''Creates a new application user with the given username.

        Args:
            username: a username for the new user

        Raises:
            voxel51.api.APIError: if the request was unsuccessful
        '''
        endpoint = self.base_url + "/apps/users"
        data = {"username": username}
        res = self._requests.post(endpoint, headers=self._header, json=data)
        _validate_response(res)

    def list_users(self):
        '''Returns a list of all application users.

        Returns:
            a list of usernames of the application users

        Raises:
            voxel51.api.APIError: if the request was unsuccessful
        '''
        endpoint = self.base_url + "/apps/users/list"
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["users"]

    # STATEMENTS ##############################################################

    def list_statements(self):
        '''Not yet implemented for applications.'''
        raise NotImplementedError(
            "list_statements() is not yet implemented for applications")

    def get_statement_details(self, statement_id):
        '''Not yet implemented for applications.'''
        raise NotImplementedError(
            "get_statement_details() is not yet implemented for applications")


def _validate_response(res):
    if not res.ok:
        raise APIError.from_response(res)


def _parse_json_response(res):
    return json.loads(res.content)
