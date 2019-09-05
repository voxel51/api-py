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

from concurrent.futures import Future
from contextlib import contextmanager
from datetime import datetime
import os
import time

import mimetypes
import requests
from requests_futures.sessions import FuturesSession

import voxel51.users.auth as voxa
import voxel51.users.jobs as voxj
import voxel51.users.utils as voxu


_BASE_API_URL = "https://api.voxel51.com/v1"
_CHUNK_SIZE = 32 * 1024 * 1024  # in bytes


class APIError(Exception):
    '''Exception raised when an :class:`API` request fails.'''

    def __init__(self, message, code):
        '''Creates a new APIError object.

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
            message = voxu.load_json(res)["error"]["message"]
        except:
            message = '%s for URL: %s' % (res.reason, res.url)

        return cls(message, res.status_code)


class API(object):
    '''Main class for managing a session with the Voxel51 Platform API.

    Attributes:
        base_url (string): the base URL of the API
        token (voxel51.users.auth.Token): the authentication token for this
            session
        keep_alive (bool): whether the request session should be kept alive
            between requests
    '''

    def __init__(self, token=None, keep_alive=False):
        '''Starts a new API session.

        Args:
            token (voxel51.users.auth.Token, optional): a Token to use. If no
                token is provided, the ``VOXEL51_API_TOKEN`` environment
                variable is checked and, if set, the token is loaded from that
                path. Otherwise, the token is loaded from
                ``~/.voxel51/api-token.json``
            keep_alive (bool, optional): whether to keep the request session
                alive between requests. By default, this is False
        '''
        self.base_url = _BASE_API_URL
        self.token = token if token is not None else voxa.load_token()
        self.keep_alive = keep_alive
        self._header = self.token.get_header()
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

    @contextmanager
    def threads(self, num_threads):
        old_requests = self._requests
        try:
            self._requests = FuturesSession(max_workers=num_threads)
            with self._requests:
                yield
        finally:
            self._requests = old_requests

    @classmethod
    def from_json(cls, token_path):
        '''Creates an API instance from the given Token JSON file.

        Args:
            token_path: the path to a :class:`voxel51.users.auth.Token` JSON
                file

        Returns:
            an API instance
        '''
        token = voxa.load_token(token_path=token_path)
        return cls(token=token)

    # ANALYTICS ###############################################################

    def list_analytics(self, all_versions=False):
        '''Returns a list of all available analytics.

        Args:
            all_versions (bool, optional): whether to return all versions of
                each analytic or only the latest version. By default, this is
                False

        Returns:
            a list of dictionaries describing the available analytics

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/analytics/list"
        data = {"all_versions": all_versions}
        res = self._requests.get(endpoint, headers=self._header, json=data)
        self._validate_response(res)
        return self._parse_json_response(res)["analytics"]

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
        endpoint = self.base_url + "/analytics"
        res = self._requests.get(
            endpoint, headers=self._header, params=analytics_query.to_dict())
        self._validate_response(res)
        return self._parse_json_response(res)

    def get_analytic_doc(self, analytic_id):
        '''Gets documentation about the analytic with the given ID.

        Args:
            analytic_id (str): the analytic ID

        Returns:
            a dictionary containing the analytic documentation

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/analytics/" + analytic_id
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)

    def upload_analytic(self, doc_json_path):
        '''Uploads the analytic documentation JSON file that describes a new
        analytic to deploy.

        See `this page <https://voxel51.com/docs/api/#analytics-upload-analytic/>`_
        for a description of the JSON format to use.

        Args:
            doc_json_path (str): the path to the analytic JSON

        Returns:
            a dictionary containing metadata about the posted analytic

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/analytics"
        filename = os.path.basename(doc_json_path)
        mime_type = _get_mime_type(doc_json_path)
        with open(doc_json_path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            res = self._requests.post(
                endpoint, headers=self._header, files=files)
        self._validate_response(res)
        return self._parse_json_response(res)["analytic"]

    def upload_analytic_image(self, analytic_id, image_tar_path, image_type):
        '''Uploads the Docker image for an analytic.

        The Docker image must be uploaded as a `.tar`, `.tar.gz`, or `.tar.bz`.

        See `this page <https://voxel51.com/docs/api/#analytics-upload-docker-image/>`_
        for more information about building and deploying Docker images to the
        platform.

        Args:
            analytic_id (str): the analytic ID
            image_tar_path (str): the path to the image tarfile
            image_type (str): the image computation type, "cpu" or "gpu"

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/analytics/" + analytic_id + "/images"
        params = {"type": image_type.lower()}
        filename = os.path.basename(image_tar_path)
        mime_type = _get_mime_type(image_tar_path)
        with open(image_tar_path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            res = voxu.upload_files(
                self._requests, endpoint, files, headers=self._header,
                params=params)
        self._validate_response(res)

    def delete_analytic(self, analytic_id):
        '''Deletes the analytic with the given ID. Only analytics that you
        own can be deleted.

        Args:
            analytic_id (str): the analytic ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/analytics/" + analytic_id
        res = self._requests.delete(endpoint, headers=self._header)
        self._validate_response(res)

    # DATA ####################################################################

    def list_data(self):
        '''Returns a list of all uploaded data.

        Returns:
            a list of dictionaries describing the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data/list"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["data"]

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
        endpoint = self.base_url + "/data"
        res = self._requests.get(
            endpoint, headers=self._header, params=data_query.to_dict())
        self._validate_response(res)
        return self._parse_json_response(res)

    def upload_data(self, path, ttl=None):
        '''Uploads the given data.

        Args:
            path (str): the path to the data file
            ttl (datetime|str, optional): a TTL for the data. If none is
                provided, the default TTL is used. If a string is provided, it
                must be in ISO 8601 format: "YYYY-MM-DDThh:mm:ss.sssZ"

        Returns:
            a dictionary containing metadata about the uploaded data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data"
        filename = os.path.basename(path)
        mime_type = _get_mime_type(path)
        with open(path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            if ttl is not None:
                if isinstance(ttl, datetime):
                    ttl = ttl.isoformat()
                files["data_ttl"] = (None, str(ttl))
            res = voxu.upload_files(
                self._requests, endpoint, files, headers=self._header)

        self._validate_response(res)
        return self._parse_json_response(res)["data"]

    def post_data_as_url(
            self, url, filename, mime_type, size, encoding=None, ttl=None):
        '''Posts data via URL.

        The data is not accessed nor uploaded at this time. Instead, the
        provided URL and metadata are stored as a reference to the file.

        The URL must be accessible via an HTTP GET request.

        Args:
            url (str): a URL (typically a signed URL) that can be accessed
                publicly via an HTTP GET request
            filename (str): the filename of the data
            mime_type (str): the MIME type of the data
            size (int): the size of the data, in bytes
            encoding (str, optional): an optional encoding of the file
            ttl (datetime|str, optional): a TTL for the data. If none is
                provided, the default TTL is used. If a string is provided, it
                must be in ISO 8601 format: "YYYY-MM-DDThh:mm:ss.sssZ"

        Returns:
            a dictionary containing metadata about the posted data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data/url"
        data = {
            "signed_url": url,
            "filename": filename,
            "mimetype": mime_type,
            "size": size,
        }
        if encoding:
            data["encoding"] = encoding
        if ttl is not None:
            if isinstance(ttl, datetime):
                ttl = ttl.isoformat()
            data["data_ttl"] = ttl

        res = self._requests.post(endpoint, json=data, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["data"]

    def get_data_details(self, data_id):
        '''Gets details about the data with the given ID.

        Args:
            data_id (str): the data ID

        Returns:
            a dictionary containing metadata about the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data/" + data_id
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["data"]

    def download_data(self, data_id, output_path=None):
        '''Downloads the data with the given ID.

        Args:
            data_id (str): the data ID
            output_path (str, optional): the output path to write to. By
                default, the data is written to the current working directory
                with the same filename as the uploaded data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        if not output_path:
            output_path = self.get_data_details(data_id)["filename"]

        endpoint = self.base_url + "/data/" + data_id + "/download"
        self._stream_download(endpoint, output_path)

    def get_data_download_url(self, data_id):
        '''Gets a signed download URL for the data with the given ID.

        Args:
            data_id (str): the data ID

        Returns:
            url (str): a signed URL with read access to download the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data/" + data_id + "/download-url"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["url"]

    def update_data_ttl(self, data_id, days):
        '''Updates the expiration date of the data by the specified number of
        days.

        To decrease the lifespan of the data, provide a negative number. Note
        that if the expiration date of the data after modification is in the
        past, the data will be deleted.

        Args:
            data_id (str): the data ID
            days (float): the number of days by which to extend the lifespan
                of the data

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data/" + data_id + "/ttl"
        data = {"days": str(days)}
        res = self._requests.put(endpoint, headers=self._header, data=data)
        self._validate_response(res)

    def delete_data(self, data_id):
        '''Deletes the data with the given ID.

        Args:
            data_id (str): the data ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/data/" + data_id
        res = self._requests.delete(endpoint, headers=self._header)
        self._validate_response(res)

    # JOBS ####################################################################

    def list_jobs(self):
        '''Returns a list of all jobs.

        Returns:
            a list of dictionaries describing the jobs

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/list"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["jobs"]

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
        endpoint = self.base_url + "/jobs"
        res = self._requests.get(
            endpoint, headers=self._header, params=jobs_query.to_dict())
        self._validate_response(res)
        return self._parse_json_response(res)

    def upload_job_request(
            self, job_request, job_name, auto_start=False, ttl=None):
        '''Uploads a job request.

        Args:
            job_request (voxel51.users.jobs.JobRequest): a JobRequest instance
                describing the job
            job_name (str): a name for the job
            auto_start (bool, optional): whether to automatically start the job
                upon creation. By default, this is False
            ttl (datetime|str, optional): a TTL for the job output. If none
                is provided, the default TTL is used. If a string is provided,
                it must be in ISO 8601 format: "YYYY-MM-DDThh:mm:ss.sssZ"

        Returns:
            a dictionary containing metadata about the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs"
        files = {
            "file": ("job.json", str(job_request), "application/json"),
            "job_name": (None, job_name),
            "auto_start": (None, str(auto_start)),
        }
        if ttl is not None:
            if isinstance(ttl, datetime):
                ttl = ttl.isoformat()
            files["job_ttl"] = (None, str(ttl))
        res = self._requests.post(endpoint, files=files, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["job"]

    def get_job_details(self, job_id):
        '''Gets details about the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary containing metadata about the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["job"]

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
        endpoint = self.base_url + "/jobs/" + job_id + "/request"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return voxj.JobRequest.from_dict(self._parse_json_response(res))

    def start_job(self, job_id):
        '''Starts the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/start"
        res = self._requests.put(endpoint, headers=self._header)
        self._validate_response(res)

    def update_job_ttl(self, job_id, days):
        '''Updates the expiration date of the job by the specified number of
        days.

        To decrease the lifespan of the job, provide a negative number. Note
        that if the expiration date of the job after modification is in the
        past, the job will be deleted.

        Args:
            job_id (str): the job ID
            days (float): the number of days by which to extend the lifespan
                of the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/ttl"
        data = {"days": str(days)}
        res = self._requests.put(endpoint, headers=self._header, data=data)
        self._validate_response(res)

    def archive_job(self, job_id):
        '''Archives the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/archive"
        res = self._requests.put(endpoint, headers=self._header)
        self._validate_response(res)

    def unarchive_job(self, job_id):
        '''Unarchives the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/unarchive"
        res = self._requests.put(endpoint, headers=self._header)
        self._validate_response(res)

    def get_job_state(self, job_id):
        '''Gets the state of the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            the :class:`voxel51.users.jobs.JobState` of the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        return self.get_job_details(job_id)["state"]

    def is_job_complete(self, job_id):
        '''Determines whether the job with the given ID is complete.

        Args:
            job_id (str): the job ID

        Returns:
            True if the job is complete, and False otherwise

        Raises:
            :class:`voxel51.users.jobs.JobExecutionError` if the job failed
            :class:`APIError` if the underlying API request was unsuccessful
        '''
        job_state = self.get_job_state(job_id)
        if job_state == voxj.JobState.FAILED:
            raise voxj.JobExecutionError("Job '%s' failed" % job_id)

        return job_state == voxj.JobState.COMPLETE

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
        while not self.is_job_complete(job_id):
            time.sleep(sleep_time)
            if (time.time() - start_time) > max_wait_time:
                raise voxj.JobExecutionError("Maximum wait time exceeded")

    def get_job_status(self, job_id):
        '''Gets the status of the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary describing the status of the job

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/status"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)

    def download_job_output(self, job_id, output_path):
        '''Downloads the output of the job with the given ID.

        Args:
            job_id (str): the job ID
            output_path (str): the output path to write to

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/output"
        self._stream_download(endpoint, output_path)

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
        endpoint = self.base_url + "/jobs/" + job_id + "/output-url"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["url"]

    def download_job_logfile(self, job_id, output_path):
        '''Downloads the logfile for the job with the given ID.

        Note that logfiles can only be downloaded for jobs that run private
        analytics.

        Args:
            job_id (str): the job ID
            output_path (str): the path to write the logfile

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/log"
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
        endpoint = self.base_url + "/jobs/" + job_id + "/log-url"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["url"]

    def delete_job(self, job_id):
        '''Deletes the job with the given ID.

        Only available for jobs that have not been started.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id
        res = self._requests.delete(endpoint, headers=self._header)
        self._validate_response(res)

    def kill_job(self, job_id):
        '''Force kills the job with the given ID.

        Only available for jobs that are queued or scheduled.

        Args:
            job_id (str): the job ID

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/jobs/" + job_id + "/kill"
        res = self._requests.put(endpoint, headers=self._header)
        self._validate_response(res)

    # STATUS ##################################################################

    def get_platform_status(self):
        '''Gets the current status of the platform.

        Returns:
            a dictionary describing the current platform status

        Raises:
            :class:`APIError` if the request was unsuccessful
        '''
        endpoint = self.base_url + "/status/all"
        res = self._requests.get(endpoint, headers=self._header)
        self._validate_response(res)
        return self._parse_json_response(res)["statuses"]

    # PRIVATE METHODS #########################################################

    _error_type = APIError

    def _stream_download(self, url, output_path):
        voxu.ensure_basedir(output_path)
        with self._requests.get(url, headers=self._header, stream=True) as res:
            with open(output_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=_CHUNK_SIZE):
                    f.write(chunk)
            self._validate_response(res)

    @classmethod
    def _validate_response(cls, res):
        if isinstance(res, Future):
            # _FutureResponse will validate this response later, as needed
            return
        if not res.ok:
            raise cls._error_type.from_response(res)

    @classmethod
    def _parse_json_response(cls, res):
        if isinstance(res, Future):
            return _FutureResponse(res, validator=cls._validate_response)
        return voxu.load_json(res.content)


def _get_mime_type(path):
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


class _FutureResponse(Future):
    def __init__(self, future, validator):
        super(_FutureResponse, self).__init__()
        self.future = future
        self.validator = validator

    def result(self):
        res = self.future.result()
        self.validator(res)
        return voxu.load_json(res.content)

    def __getitem__(self, key):
        return _FutureItem(self, key)


class _FutureItem(Future):
    def __init__(self, future, key):
        super(_FutureItem, self).__init__()
        self.future = future
        self.key = key

    def result(self):
        return self.future.result()[self.key]

    def __getitem__(self, key):
        return _FutureItem(self, key)
