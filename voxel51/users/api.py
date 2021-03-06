'''
Main interface for the Voxel51 Platform API.

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

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import time

import dateutil.parser
import mimetypes
import requests

import voxel51.users.auth as voxa
import voxel51.users.jobs as voxj
import voxel51.users.query as voxq
import voxel51.users.utils as voxu


_CHUNK_SIZE = 32 * 1024 * 1024  # in bytes


class AnalyticType(object):
    '''Enum describing the possible types of analytics.'''

    PLATFORM = "PLATFORM"
    IMAGE_TO_VIDEO = "IMAGE_TO_VIDEO"


class AnalyticImageType(object):
    '''Enum describing the possible types of analytic images.'''

    CPU = "CPU"
    GPU = "GPU"


class API(object):
    '''Main class for managing a session with the Voxel51 Platform API.

    Using this API requires a valid API token. The following strategy is used
    to locate your active API token (in order of precedence):

        (1) Use the :class:`voxel51.users.auth.Token` provided when
            constructing the :class:`API` instance
        (2) Use the ``VOXEL51_API_PRIVATE_KEY`` and ``VOXEL51_API_BASE_URL``
            environment variables
        (3) Use the ``VOXEL51_API_TOKEN`` environment variable
        (4) Load the active token from ``~/.voxel51/api-token.json``

    Attributes:
        base_url (string): the base URL of the API
        token (voxel51.users.auth.Token): the authentication token for this
            session
        keep_alive (bool): whether the request session should be kept alive
            between requests
    '''

    def __init__(self, token=None, keep_alive=False):
        '''Creates an API instance.

        Args:
            token (voxel51.users.auth.Token, optional): a
                :class:`voxel51.users.auth.Token` to use. If no token is
                provided, the strategy described above is used to locate the
                active token
            keep_alive (bool, optional): whether to keep the request session
                alive between requests. By default, this is False
        '''
        if token is None:
            token = voxa.load_token()

        self.base_url = voxu.urljoin(token.base_api_url, "v1")
        self.token = token
        self.keep_alive = keep_alive
        self._header = token.get_header()
        self._requests = requests.Session() if keep_alive else requests

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        '''Closes the HTTP session. Only needs to be called when
        `keep_alive=True` is passed to the constructor.
        '''
        if self.keep_alive:
            self._requests.close()

    @classmethod
    def from_json(cls, token_path, **kwargs):
        '''Creates an API instance from the given Token JSON file.

        Args:
            token_path (str): the path to a :class:`voxel51.users.auth.Token`
                JSON file
            **kwargs (dict): optional keyword arguments for
                `API(token=token, **kwargs)`

        Returns:
            an :class:`API` instance
        '''
        token = voxa.load_token(token_path=token_path)
        return cls(token=token, **kwargs)

    @staticmethod
    def thread_map(callback, iterable, max_workers=None):
        '''Applies the callback function to each item in the iterable using a
        pool of parallel worker threads.

        Args:
            callback (function): the function to call on each list item
            iterable (iterable): an iterable of arguments to pass to the
                callback
            max_workers (int, optional): the number of worker threads to use.
                The default is `None`, which uses a handful of threads for each
                CPU on your machine. See the documentation for the
                `concurrent.futures.ThreadPoolExecutor` method for more details

        Returns:
            a list of values returned by `callback`, in the same order as the
            input `iterable`
        '''
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(callback, iterable))

    # ANALYTICS ###############################################################

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
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "analytics", "list")
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
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "analytics")
        res = self._requests.get(
            endpoint, headers=self._header, json=analytics_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)

    def get_analytic_id(self, name, version=None):
        '''Gets the ID of the analytic with the given name (and optional
        version).

        Args:
            name (str): the analytic name
            version (str, optional): the analytic version. By default, the
                latest version of the analytic is returned

        Returns:
            the ID of the analytic

        Raises:
            ValueError if the specified analytic was not found
        '''
        analytics_query = voxq.AnalyticsQuery()
        analytics_query.add_fields(["id", "name", "version"])
        analytics_query.add_search("name", name)

        if version is not None:
            analytics_query.add_search("version", version)
            analytics_query.set_all_versions(True)

        analytics = self.query_analytics(analytics_query)["analytics"]

        # Queries match substrings, so we must enforce exact matching manually
        analytics = [
            a for a in analytics
            if a["name"] == name and (
                version is None or a["version"] == version)]

        if not analytics:
            pretty_name = _render_pretty_analytic_name(name, version=version)
            raise ValueError("Analytic '%s' not found" % pretty_name)

        return analytics[0]["id"]

    def get_analytic_details(self, analytic_id):
        '''Gets details about the analytic with the given ID.

        Args:
            analytic_id (str): the analytic ID

        Returns:
            a dictionary containing metadata about the analytic

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "analytics", analytic_id)
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
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "analytics", analytic_id, "doc")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)

    def upload_analytic(self, doc_json_path, analytic_type=None):
        '''Uploads the analytic documentation JSON file that describes a new
        analytic to deploy.

        See `this page <https://voxel51.com/docs/api/#analytics-upload-analytic/>`_
        for a description of the JSON format to use.

        Args:
            doc_json_path (str): the path to the analytic JSON
            analytic_type (AnalyticType, optional): the type of analytic that
                you are uploading. If not specified, it is assumed that you
                are uploading a standard platform analytic

        Returns:
            a dictionary containing metadata about the posted analytic

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "analytics")
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

        See `this page <https://voxel51.com/docs/api/#analytics-upload-docker-image/>`_
        for more information about building and deploying Docker images to the
        platform.

        Args:
            analytic_id (str): the analytic ID
            image_tar_path (str): the path to the image tarfile
            image_type (AnalyticImageType): the type of analytic image

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(
            self.base_url, "analytics", analytic_id, "images")
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
        '''Deletes the analytic with the given ID. Only analytics that you
        own can be deleted.

        Args:
            analytic_id (str): the analytic ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "analytics", analytic_id)
        res = self._requests.delete(endpoint, headers=self._header)
        _validate_response(res)

    def batch_get_analytic_details(self, analytic_ids):
        '''Gets details about the analytics with the given IDs.

        Args:
            analytic_ids (list): the analytic IDs

        Returns:
            a dictionary mapping analytic IDs to response dictionaries. The
            ``success`` field of each response will be set to ``True`` on
            success or ``False`` on failure, and the ``response`` field will
            contain the analytic details in the same format as returned by
            :func:`get_analytic_details`

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("analytics", "details", analytic_ids)

    # DATA ####################################################################

    def list_data(self):
        '''Returns a list of all uploaded data.

        Returns:
            a list of dictionaries describing the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data", "list")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def query_data(self, data_query):
        '''Performs a customized data query.

        Args:
            data_query (voxel51.users.query.DataQuery): a DataQuery instance
                defining the customized data query to perform

        Returns:
            a dictionary containing the query results and total number of
            records

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data")
        res = self._requests.get(
            endpoint, headers=self._header, json=data_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)

    def upload_data(self, path, ttl=None):
        '''Uploads the given data.

        Args:
            path (str): the path to the data file
            ttl (datetime|str, optional): a TTL for the data. If none is
                provided, the default TTL is used. If a string is provided, it
                must be in ISO 8601 format, e.g., "YYYY-MM-DDThh:mm:ss.sssZ".
                If a non-UTC timezone is included in the datetime or string, it
                will be respected

        Returns:
            a dictionary containing metadata about the uploaded data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data")
        filename = os.path.basename(path)
        mime_type = _get_mime_type(path)
        with open(path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            if ttl is not None:
                files["data_ttl"] = (None, _parse_datetime(ttl))
            res = voxu.upload_files(
                self._requests, endpoint, files, headers=self._header)

        _validate_response(res)
        return _parse_json_response(res)["data"]

    def post_data_as_url(
            self, url, filename, mime_type, size, expiration_date,
            encoding=None):
        '''Posts data via URL.

        The data is not accessed nor uploaded at this time. Instead, the
        provided URL and metadata are stored as a reference to the file.

        The URL must be accessible via an HTTP GET request.

        The URL (typically a signed URL) should be accessible until the
        expiration date that you specify. Note that the expiration date of data
        posted via this route cannot be updated later.

        Args:
            url (str): a URL (typically a signed URL) that can be accessed
                publicly via an HTTP GET request
            filename (str): the filename of the data
            mime_type (str): the MIME type of the data
            size (int): the size of the data, in bytes
            expiration_date (datetime|str): the expiration date for the URL you
                provided. If a string is provided, it must be in ISO 8601
                format, e.g., "YYYY-MM-DDThh:mm:ss.sssZ". If a non-UTC timezone
                is included in the datetime or string, it will be respected
            encoding (str, optional): an optional encoding of the file

        Returns:
            a dictionary containing metadata about the posted data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data", "url")
        data = {
            "signed_url": url,
            "filename": filename,
            "mimetype": mime_type,
            "size": size,
            "data_ttl": _parse_datetime(expiration_date),
        }
        if encoding:
            data["encoding"] = encoding

        res = self._requests.post(endpoint, json=data, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def get_data_details(self, data_id):
        '''Gets details about the data with the given ID.

        Args:
            data_id (str): the data ID

        Returns:
            a dictionary containing metadata about the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data", data_id)
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def download_data(self, data_id, output_path=None):
        '''Downloads the data with the given ID.

        Args:
            data_id (str): the data ID
            output_path (str, optional): the output path to write to. By
                default, the data is written to the current working directory
                with the same filename as the uploaded data

        Returns:
            the path to the downloaded data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        if not output_path:
            output_path = self.get_data_details(data_id)["name"]

        endpoint = voxu.urljoin(self.base_url, "data", data_id, "download")
        self._stream_download(endpoint, output_path)
        return output_path

    def get_data_download_url(self, data_id):
        '''Gets a signed download URL for the data with the given ID.

        Args:
            data_id (str): the data ID

        Returns:
            url (str): a signed URL with read access to download the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data", data_id, "download-url")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["url"]

    def update_data_ttl(self, data_id, days=None, expiration_date=None):
        '''Updates the expiration date of the data.

        Note that if the expiration date of the data after modification is in
        the past, the data will be deleted.

        Exactly one keyword argument must be provided.

        Args:
            data_id (str): the data ID
            days (float, optional): the number of days by which to extend the
                lifespan of the data. To decrease the lifespan of the data,
                provide a negative number
            expiration_date (datetime|str, optional): a new TTL for the data.
                If a string is provided, it must be in ISO 8601 format, e.g.,
                "YYYY-MM-DDThh:mm:ss.sssZ". If a non-UTC timezone is included
                in the datetime or string, it will be respected

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data", data_id, "ttl")

        data = {}
        if days is not None:
            data["days"] = str(days)
        if expiration_date is not None:
            data["expiration_date"] = _parse_datetime(expiration_date)
        if len(data) != 1:
            raise APIError(
                "Either `days` or `expiration_date` must be provided", 400)

        res = self._requests.put(endpoint, headers=self._header, data=data)
        _validate_response(res)

    def delete_data(self, data_id):
        '''Deletes the data with the given ID.

        Args:
            data_id (str): the data ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "data", data_id)
        res = self._requests.delete(endpoint, headers=self._header)
        _validate_response(res)

    def batch_get_data_details(self, data_ids):
        '''Gets details about the data with the given IDs.

        Args:
            data_ids (list): the data IDs

        Returns:
            a dictionary mapping data IDs to response dictionaries. The
            ``success`` field of each response will be set to ``True`` on
            success or ``False`` on failure, and the ``response`` field will
            contain the data details in the same format as returned by
            :func:`get_data_details`

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("data", "details", data_ids)

    def batch_update_data_ttl(self, data_ids, days=None, expiration_date=None):
        '''Updates the expiration dates of the data with the given IDs.

        Note that if the expiration date of the data after modification is in
        the past, the data will be deleted.

        Exactly one keyword argument must be provided.

        Args:
            data_ids (list): the data IDs
            days (float, optional): the number of days by which to extend the
                lifespan of the data. To decrease the lifespan of the data,
                provide a negative number
            expiration_date (datetime|str, optional): a new expiration date for
                the data. If a string is provided, it must be in ISO 8601
                format, e.g., "YYYY-MM-DDThh:mm:ss.sssZ". If a non-UTC timezone
                is included in the datetime or string, it will be respected

        Returns:
            a dictionary mapping data IDs to dictionaries indicating whether
            the data was successfully processed. The ``success`` field will be
            set to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        data = {}
        if days is not None:
            data["days"] = str(days)
        if expiration_date is not None:
            data["expiration_date"] = _parse_datetime(expiration_date)
        if len(data) != 1:
            raise APIError(
                "Either `days` or `expiration_date` must be provided", 400)
        return self._batch_request("data", "ttl", data_ids, data)

    def batch_delete_data(self, data_ids):
        '''Deletes the data with the given IDs.

        Args:
            data_ids (list): the data IDs

        Returns:
            a dictionary mapping data IDs to dictionaries indicating whether
            the data was successfully processed. The ``success`` field will be
            set to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("data", "delete", data_ids)

    # JOBS ####################################################################

    def list_jobs(self):
        '''Returns a list of all unarchived jobs.

        Returns:
            a list of dictionaries describing the jobs

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", "list")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["jobs"]

    def query_jobs(self, jobs_query):
        '''Performs a customized jobs query.

        Args:
            jobs_query (voxel51.users.query.JobsQuery): a JobsQuery instance
                defining the customized jobs query to perform

        Returns:
            a dictionary containing the query results and total number of
                records

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs")
        res = self._requests.get(
            endpoint, headers=self._header, json=jobs_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)

    def upload_job_request(
            self, job_request, job_name, auto_start=False, ttl=None):
        '''Uploads a job request.

        Args:
            job_request (voxel51.users.jobs.JobRequest): a JobRequest instance
                describing the job
            job_name (str): a name for the job
            auto_start (bool, optional): whether to automatically start the job
                upon creation. By default, this is False
            ttl (datetime|str, optional): a TTL for the job output. If none is
                provided, the default TTL is used. If a string is provided, it
                must be in ISO 8601 format, e.g., "YYYY-MM-DDThh:mm:ss.sssZ".
                If a non-UTC timezone is included in the datetime or string, it
                will be respected

        Returns:
            a dictionary containing metadata about the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs")
        files = {
            "file": ("job.json", str(job_request), "application/json"),
            "job_name": (None, job_name),
            "auto_start": (None, str(auto_start)),
        }
        if ttl is not None:
            files["job_ttl"] = (None, _parse_datetime(ttl))
        res = self._requests.post(endpoint, files=files, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["job"]

    def get_job_details(self, job_id):
        '''Gets details about the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary containing metadata about the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id)
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["job"]

    def get_job_request(self, job_id):
        '''Gets the job request for the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a :class:`voxel51.users.jobs.JobRequest` instance describing the
            job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "request")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return voxj.JobRequest.from_dict(_parse_json_response(res))

    def start_job(self, job_id):
        '''Starts the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "start")
        res = self._requests.put(endpoint, headers=self._header)
        _validate_response(res)

    def update_job_ttl(self, job_id, days=None, expiration_date=None):
        '''Updates the expiration date of the job.

        Note that if the expiration date of the job after modification is in
        the past, the job output will be deleted.

        Exactly one keyword argument must be provided.

        Args:
            job_id (str): the job ID
            days (float, optional): the number of days by which to extend the
                lifespan of the job. To decrease the lifespan of the job,
                provide a negative number
            expiration_date (datetime|str, optional): a new TTL for the job.
                If a string is provided, it must be in ISO 8601 format, e.g.,
                "YYYY-MM-DDThh:mm:ss.sssZ". If a non-UTC timezone is included
                in the datetime or string, it will be respected

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "ttl")

        data = {}
        if days is not None:
            data["days"] = str(days)
        if expiration_date is not None:
            data["expiration_date"] = _parse_datetime(expiration_date)
        if len(data) != 1:
            raise APIError(
                "Either `days` or `expiration_date` must be provided", 400)

        res = self._requests.put(endpoint, headers=self._header, data=data)
        _validate_response(res)

    def archive_job(self, job_id):
        '''Archives the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "archive")
        res = self._requests.put(endpoint, headers=self._header)
        _validate_response(res)

    def unarchive_job(self, job_id):
        '''Unarchives the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "unarchive")
        res = self._requests.put(endpoint, headers=self._header)
        _validate_response(res)

    def get_job_state(self, job_id=None, job=None):
        '''Gets the state of the job.

        Exactly one keyword argument should be provided.

        Args:
            job_id (str, optional): the job ID
            job (dict, optional): the metadata dictionary for the job, as
                returned by :func:`get_job_details` or :func:`query_jobs`

        Returns:
            the :class:`voxel51.users.jobs.JobState` of the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        if job_id is not None:
            state = self.get_job_details(job_id)["state"]
        elif job is not None:
            state = job["state"]
        else:
            raise APIError("Either `job_id` or `job` must be provided", 400)

        return state

    def is_job_complete(self, job_id=None, job=None):
        '''Determines whether the job is complete.

        Exactly one keyword argument should be provided.

        Args:
            job_id (str, optional): the job ID
            job (dict, optional): the metadata dictionary for the job, as
                returned by :func:`get_job_details` or :func:`query_jobs`

        Returns:
            True if the job is complete, and False otherwise

        Raises:
            :class:`voxel51.users.jobs.JobExecutionError` if the job failed
            :class:`APIError` if the request was unsuccessful
        '''
        state = self.get_job_state(job_id=job_id, job=job)
        if state == voxj.JobState.FAILED:
            raise voxj.JobExecutionError("Job '%s' failed" % job_id)

        return state == voxj.JobState.COMPLETE

    def wait_until_job_completes(
            self, job_id, sleep_time=5, max_wait_time=600):
        '''Block execution until the job with the given ID is complete.

        Args:
            job_id (str): the job ID
            sleep_time (float, optional): the number of seconds to wait
                between job state checks. The default is 5
            max_wait_time (float, optional): the maximum number of seconds to
                wait for the job to complete. The default is 600

        Raises:
            :class:`voxel51.users.jobs.JobExecutionError` if the job failed
            :class:`APIError` if an underlying API request was unsuccessful
        '''
        start_time = time.time()
        while not self.is_job_complete(job_id=job_id):
            time.sleep(sleep_time)
            if (time.time() - start_time) > max_wait_time:
                raise voxj.JobExecutionError("Maximum wait time exceeded")

    def is_job_expired(self, job_id=None, job=None):
        '''Determines whether the job is expired.

        Exactly one keyword argument should be provided.

        Args:
            job_id (str, optional): the job ID
            job (dict, optional): the metadata dictionary for the job, as
                returned by :func:`get_job_details` or :func:`query_jobs`

        Returns:
            True if the job is expired, and False otherwise

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        if job_id is not None:
            return self.get_job_details(job_id)["expired"]

        if job is None:
            raise APIError("Either `job_id` or `job` must be provided", 400)

        # Note that we could just return `job.expired` here, but we are
        # computing this value dynamically from `job.expiration_date` in case
        # the job metadata was generated awhile ago...
        expiration = dateutil.parser.parse(job["expiration_date"])
        now = datetime.utcnow()
        return now >= expiration.replace(tzinfo=None)

    def get_job_status(self, job_id):
        '''Gets the status of the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary describing the status of the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "status")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)

    def download_job_output(self, job_id, output_path=None):
        '''Downloads the output of the job with the given ID.

        Args:
            job_id (str): the job ID
            output_path (str, optional): the output path to write to. By
                default, the file is written to the current working directory
                with the recommend output filename for the job

        Returns:
            the path to the downloaded job output

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        if not output_path:
            output_path = self.get_job_details(job_id)["output_filename"]

        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "output")
        self._stream_download(endpoint, output_path)
        return output_path

    def get_job_output_download_url(self, job_id):
        '''Gets a signed download URL for the output of the job with the given
        ID.

        Args:
            job_id (str): the job ID

        Returns:
            url (str): a signed URL with read access to download the job output

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "output-url")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["url"]

    def download_job_logfile(self, job_id, output_path=None):
        '''Downloads the logfile for the job with the given ID.

        Note that logfiles can only be downloaded for jobs that run private
        analytics.

        Args:
            job_id (str): the job ID
            output_path (str, optional): the path to write the logfile. If
                not provided, the logfile is returned as a string

        Returns:
            the logfile as a string, if `output_path` is None; otherwise None

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "log")
        if output_path is None:
            res = self._requests.get(endpoint, headers=self._header)
            _validate_response(res)
            return res.content.decode()

        self._stream_download(endpoint, output_path)

    def get_job_logfile_download_url(self, job_id):
        '''Gets a signed download URL for the logfile of the job with the given
        ID.

        Note that logfiles can only be downloaded for jobs that run private
        analytics.

        Args:
            job_id (str): the job ID

        Returns:
            url (str): a signed URL with read access to download the job
            logfile

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "log-url")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["url"]

    def delete_job(self, job_id):
        '''Deletes the job with the given ID.

        Note that only jobs that have not been started can be deleted.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id)
        res = self._requests.delete(endpoint, headers=self._header)
        _validate_response(res)

    def kill_job(self, job_id):
        '''Force kills the job with the given ID.

        Note that only jobs that are queued or scheduled can be killed.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "jobs", job_id, "kill")
        res = self._requests.put(endpoint, headers=self._header)
        _validate_response(res)

    def batch_get_job_details(self, job_ids):
        '''Gets details about the jobs with the given IDs.

        Args:
            job_ids (list): the job IDs

        Returns:
            a dictionary mapping job IDs to response dictionaries. The
            ``success`` field of each response will be set to ``True`` on
            success or ``False`` on failure, and the ``response`` field will
            contain the job details in the same format as returned by
            :func:`get_job_details`

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("jobs", "details", job_ids)

    def batch_start_jobs(self, job_ids):
        '''Starts the jobs with the given IDs.

        Args:
            job_ids (list): the job IDs

        Returns:
            a dictionary mapping job IDs to dictionaries indicating whether the
            job was successfully processed. The ``success`` field will be set
            to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("jobs", "start", job_ids)

    def batch_archive_jobs(self, job_ids):
        '''Archives the jobs with the given IDs.

        Args:
            job_ids (list): the job IDs

        Returns:
            a dictionary mapping job IDs to dictionaries indicating whether the
            job was successfully processed. The ``success`` field will be set
            to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("jobs", "archive", job_ids)

    def batch_unarchive_jobs(self, job_ids):
        '''Unarchives the jobs with the given IDs.

        Args:
            job_ids (list): the job IDs

        Returns:
            a dictionary mapping job IDs to dictionaries indicating whether the
            job was successfully processed. The ``success`` field will be set
            to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("jobs", "unarchive", job_ids)

    def batch_update_jobs_ttl(self, job_ids, days=None, expiration_date=None):
        '''Updates the expiration dates of the jobs with the given IDs.

        Note that if the expiration date of a job after modification is in
        the past, the job output will be deleted.

        Exactly one keyword argument must be provided.

        Args:
            job_ids (list): the job IDs
            days (float, optional): the number of days by which to extend the
                lifespan of each job. To decrease the lifespan of the jobs,
                provide a negative number
            expiration_date (datetime|str, optional): a new expiration date for
                each job. If a string is provided, it must be in ISO 8601
                format, e.g., "YYYY-MM-DDThh:mm:ss.sssZ". If a non-UTC timezone
                is included in the datetime or string, it will be respected

        Returns:
            a dictionary mapping job IDs to dictionaries indicating whether the
            job was successfully processed. The ``success`` field will be set
            to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        data = {}
        if days is not None:
            data["days"] = str(days)
        if expiration_date is not None:
            data["expiration_date"] = _parse_datetime(expiration_date)
        if len(data) != 1:
            raise APIError(
                "Either `days` or `expiration_date` must be provided", 400)
        return self._batch_request("jobs", "ttl", job_ids, data)

    def batch_delete_jobs(self, job_ids):
        '''Deletes the jobs with the given IDs.

        Note that only jobs that have not been started can be deleted.

        Args:
            job_ids (list): the job IDs

        Returns:
            a dictionary mapping job IDs to dictionaries indicating whether the
            job was successfully processed. The ``success`` field will be set
            to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("jobs", "delete", job_ids)

    def batch_kill_jobs(self, job_ids):
        '''Force kills the jobs with the given IDs.

        Note that only jobs that are queued or scheduled can be killed.

        Args:
            job_ids (list): the job IDs

        Returns:
            a dictionary mapping job IDs to dictionaries indicating whether the
            job was successfully processed. The ``success`` field will be set
            to ``True`` on success or ``False`` on failure

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self._batch_request("jobs", "kill", job_ids)

    # STATUS ##################################################################

    def get_platform_status(self):
        '''Gets the current status of the platform.

        Returns:
            a dictionary describing the current platform status

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = voxu.urljoin(self.base_url, "status", "all")
        res = self._requests.get(endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["statuses"]

    # PRIVATE METHODS #########################################################

    def _batch_request(self, type, action, ids, params=None):
        endpoint = voxu.urljoin(self.base_url, type, "batch")
        body = {}
        if params is not None:
            body.update(**params)

        body.update(action=action, ids=list(ids))
        res = self._requests.post(endpoint, headers=self._header, json=body)
        _validate_response(res)
        statuses = _parse_json_response(res)["responses"]
        return statuses

    def _stream_download(self, url, output_path):
        voxu.ensure_basedir(output_path)
        with self._requests.get(url, headers=self._header, stream=True) as res:
            _validate_response(res)
            with open(output_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=_CHUNK_SIZE):
                    f.write(chunk)


class APIError(Exception):
    '''Exception raised when an :class:`API` request fails.'''

    def __init__(self, message, code):
        '''Creates an APIError instance.

        Args:
            message (str): the error message
            code (int): the error code
        '''
        super(APIError, self).__init__("%d: %s" % (code, message))

    @classmethod
    def from_response(cls, res):
        '''Constructs an APIError from a requests reponse.

        Args:
            res (requests.Response): a requests response

        Returns:
            an APIError instance

        Raises:
            ValueError if the given response is not an error response
        '''
        if res.ok:
            raise ValueError("Response is not an error")

        try:
            message = _parse_json_response(res)["error"]["message"]
        except:
            message = '%s for URL: %s' % (res.reason, res.url)

        return cls(message, res.status_code)


def _render_pretty_analytic_name(name, version=None):
    return "%s v%s" % (name, version) if version else name


def _parse_datetime(datetime_or_str):
    if isinstance(datetime_or_str, datetime):
        return datetime_or_str.isoformat()

    return str(datetime_or_str)


def _get_mime_type(path):
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


def _validate_response(res):
    if not res.ok:
        raise APIError.from_response(res)


def _parse_json_response(res):
    return voxu.load_json(res.content)
