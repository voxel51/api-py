'''
Applications interface for the Voxel51 Platform API.

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

import mimetypes
import os

from voxel51.users.api import API, APIError
import voxel51.apps.auth as voxa
import voxel51.users.utils as voxu


class ApplicationAPI(API):
    '''Main class for managing an application session with the Voxel51 Platform
    API.

    Note that :class:`ApplicationAPI` is a subclass of
    :class:`voxel51.users.api.API`, which implies that, unless specifically
    overridden, applications can access all methods exposed for regular
    platform users. In order to use these user-specific methods, however, you
    must first activate a user via :func:`ApplicationAPI.with_user`.

    Attributes:
        base_url (str): the base URL of the API
        token (voxel51.apps.auth.ApplicationToken): the authentication token
            for this session
        keep_alive (bool): whether the request session should be kept alive
            between requests
        active_user (str): the currently active username, or None if no user
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
            username (str): the name of a user
        '''
        self.active_user = username
        self._header = self.token.get_header(username=username)

    def exit_user(self):
        '''Exits active user mode, if necessary.'''
        self.active_user = None
        self._header = self.token.get_header()

    @classmethod
    def from_json(cls, token_path, **kwargs):
        '''Creates an :class:`ApplicationAPI` instance from the given
        :class:`ApplicationToken` JSON file.

        Args:
            token_path (str): the path to an
                :class:`voxel51.apps.auth.ApplicationToken` JSON file
            **kwargs (dict): optional keyword arguments for
                `ApplicationAPI(token=token, **kwargs)`

        Returns:
            an :class:`ApplicationAPI` instance
        '''
        token = voxa.load_application_token(token_path=token_path)
        return cls(token=token, **kwargs)

    #
    # ANALYTICS ###############################################################
    #
    # Note that all analytic methods override the inherited methods from API,
    # because analytic listing has different behavior for applications than it
    # does for individual platform users
    #

    def list_analytics(self, all_versions=False):
        '''Returns a list of all available analytics.

        By default, only the latest version of each analytic is returned.
        Pending analytics are always excluded from this list.

        Args:
            all_versions (bool, optional): whether to return all versions of
                each analytic or only the latest version. By default, this is
                False

        Returns:
            a list of dictionaries describing the available analytics

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "analytics", "list")
        data = {"all_versions": all_versions}
        res = self._requests.get(endpoint, headers=self._header, json=data)
        _validate_response(res)
        return _parse_json_response(res)["analytics"]

    def query_analytics(self, analytics_query):
        '''Performs a customized analytics query.

        Args:
            analytics_query (voxel51.users.query.AnalyticsQuery): an
                AnalyticsQuery instance defining the customized analytics query
                to perform

        Returns:
            a dictionary containing the query results and total number of
            records

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "analytics")
        res = self._requests.get(
            endpoint, headers=self._header, params=analytics_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)

    def get_analytic_details(self, analytic_id):
        '''Gets details about the analytic with the given ID.

        Args:
            analytic_id (str): the analytic ID

        Returns:
            a dictionary containing metadata about the analytic

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(
            self.base_url, "apps", "analytics", analytic_id)
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["analytic"]

    def get_analytic_doc(self, analytic_id):
        '''Gets documentation about the analytic with the given ID.

        Args:
            analytic_id (str): the analytic ID

        Returns:
            a dictionary containing the analytic documentation

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(
            self.base_url, "apps", "analytics", analytic_id, "doc")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)

    def upload_analytic(self, doc_json_path, analytic_type=None):
        '''Uploads the analytic documentation JSON file that describes a new
        analytic to deploy.

        See `this page <https://voxel51.com/docs/applications/#analytics-upload-analytic/>`_
        for a description of the JSON format to use.

        Args:
            doc_json_path (str): the path to the analytic JSON
            analytic_type (AnalyticType, optional): the type of analytic that
                you are uploading. If not specified, it is assumed that you
                are uploading a standard platform analytic

        Returns:
            a dictionary containing metadata about the posted analytic

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "analytics")
        filename = os.path.basename(doc_json_path)
        mime_type = _get_mime_type(doc_json_path)
        with open(doc_json_path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            if analytic_type:
                files["analytic_type"] = (None, str(analytic_type))
            res = self._requests.post(
                endpoint, headers=self._header, files=files)
        _validate_response(res)
        return _parse_json_response(res)["analytic"]

    def upload_analytic_image(self, analytic_id, image_tar_path, image_type):
        '''Uploads the Docker image for an analytic.

        The Docker image must be uploaded as a `.tar`, `.tar.gz`, or `.tar.bz`.

        See `this page <https://voxel51.com/docs/applications/#analytics-upload-docker-image/>`_
        for a description of the JSON format to use.

        Args:
            analytic_id (str): the analytic ID
            image_tar_path (str): the path to the image tarfile
            image_type (str): the image computation type, "cpu" or "gpu"

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(
            self.base_url, "apps", "analytics", analytic_id, "images")
        params = {"type": image_type}
        filename = os.path.basename(image_tar_path)
        mime_type = _get_mime_type(image_tar_path)
        with open(image_tar_path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            res = voxu.upload_files(
                self._requests, endpoint, files, headers=self._header,
                params=params)
        _validate_response(res)

    def delete_analytic(self, analytic_id):
        '''Deletes the analytic with the given ID. Only analytics that your
        application owns can be deleted.

        Args:
            analytic_id (str): the analytic ID

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(
            self.base_url, "apps", "analytics", analytic_id)
        res = self._requests.delete(endpoint, headers=self._header)
        _validate_response(res)

    # DATA ####################################################################

    def query_application_data(self, data_query):
        '''Performs a customized data query at the application level.

        Queries using this route return results for all
            users of the application.

        Args:
            data_query (voxel51.users.query.DataQuery): a DataQuery instance
                defining the customized data query to perform

        Returns:
            a dictionary containing the query results and total number of
            records

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "data")
        res = self._requests.get(
            endpoint, headers=self._header, params=data_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)

    # JOBS ####################################################################

    def query_application_jobs(self, jobs_query):
        '''Performs a customized jobs query at the application level.

        Queries using this route return results for all
            users of the application.

        Args:
            jobs_query (voxel51.users.query.JobsQuery): a JobsQuery instance
                defining the customized jobs query to perform

        Returns:
            a dictionary containing the query results and total number of
                records

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "jobs")
        res = self._requests.get(
            endpoint, headers=self._header, params=jobs_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)

    # USERS ###################################################################

    def create_user(self, username):
        '''Creates a new application user with the given username.

        Args:
            username (str): a username for the new user

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "users")
        data = {"username": username}
        res = self._requests.post(endpoint, headers=self._header, json=data)
        _validate_response(res)

    def list_users(self):
        '''Returns a list of all application users.

        Returns:
            a list of usernames of the application users

        Raises:
            :class:`ApplicationAPIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "users", "list")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["users"]

    # STATUS ##################################################################

    def get_platform_status(self):
        '''Gets the current status of the platform.

        Returns:
            a dictionary describing the current platform status

        Raises:
            :class:`ApplicationAPIError`: if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "apps", "status", "all")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["statuses"]


class ApplicationAPIError(APIError):
    '''Exception raised when an :class:`ApplicationAPI` request fails.'''
    pass


def _get_mime_type(path):
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


def _validate_response(res):
    if not res.ok:
        raise ApplicationAPIError.from_response(res)


def _parse_json_response(res):
    return voxu.load_json(res.content)
