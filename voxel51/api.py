'''
Main interface for the Voxel51 Vision Services API.

| Copyright 2017-2018, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
'''
import json
import os
import time

import mimetypes
import requests

import voxel51.auth as voxa
import voxel51.jobs as voxj
import voxel51.utils as voxu


BASE_API_URL = "https://api.voxel51.com/v1"
CHUNK_SIZE = 32 * 1024 * 1024  # in bytes


class API(object):
    '''Main class for managing a session with the Voxel51 Vision Services API.

    Attributes:
        url (string): the base URL of the API
        token (voxel51.auth.Token): the authentication token for this session
    '''

    def __init__(self, token_path=None):
        '''Starts a new API session.

        Args:
            token_path: an optional path to a valid Token JSON file. If no path
                is provided as an argument, the ``VOXEL51_API_TOKEN``
                environment variable is checked and, if set, the token is
                loaded from that path. Otherwise, the token is loaded from
                ``~/.voxel51/api-token.json``
        '''
        self.url = BASE_API_URL
        self.token = voxa.load_token(token_path=token_path)
        self._header = self.token.get_header()
        self._session = requests.Session()

    # ANALYTICS FUNCTIONS #####################################################

    def list_analytics(self):
        '''Returns a list of all available analytics.

        Returns:
            a list of dicts describing the available analytics

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/analytics/list"
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["analytics"]

    def query_analytics(self, analytics_query):
        '''Performs a customized analytics query.

        Args:
            analytics_query (voxel51.query.AnalyticsQuery): an AnalyticsQuery
                instance defining the customized analytics query to perform

        Returns:
            a list of dicts containing the query results

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/analytics"
        res = self._session.get(
            endpoint, headers=self._header, params=analytics_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)["analytics"]

    def get_analytic_doc(self, analytic_id):
        '''Gets documentation about the analytic with the given ID.

        Args:
            analytic_id (str): the analytic ID

        Returns:
            a dictionary containing the analytic documentation

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/analytics/" + analytic_id
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)

    # DATA FUNCTIONS ##########################################################

    def list_data(self):
        '''Returns a list of all data uploaded to cloud storage.

        Returns:
            a list of data IDs

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/data/list"
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def query_data(self, data_query):
        '''Performs a customized data query.

        Args:
            data_query (voxel51.query.DataQuery): a DataQuery instance defining
                the customized data query to perform

        Returns:
            a list of dicts containing the query results

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/data"
        res = self._session.get(
            endpoint, headers=self._header, params=data_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def upload_data(self, path):
        '''Uploads data to cloud storage.

        Args:
            path (str): the path to the data file

        Returns:
            a dictionary containing metadata about the uploaded data

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/data"
        filename = os.path.basename(path)
        mime_type = _get_mime_type(path)
        with open(path, "rb") as df:
            files = {"file": (filename, df, mime_type)}
            res = self._session.post(endpoint,
                files=files, headers=self._header)

        _validate_response(res)
        return _parse_json_response(res)["data"]

    def get_data_details(self, data_id):
        '''Gets details about the data with the given ID.

        Args:
            data_id (str): the data ID

        Returns:
            a dictionary containing metadata about the data

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/data/" + data_id
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def download_data(self, data_id, output_path=None):
        '''Downloads the data with the given ID.

        Args:
            data_id (str): the data ID
            output_path (str, optional): the output path to write to. By
                default, the data is written to the current working directory
                with the same filename as the data in cloud storage

        Raises:
            APIError if the request was unsuccessful
        '''
        if not output_path:
            output_path = self.get_data_details(data_id)["filename"]

        endpoint = self.url + "/data/" + data_id + "/download"
        self._stream_download(endpoint, output_path)

    def delete_data(self, data_id):
        '''Deletes the data with the given ID from the cloud.

        Args:
            data_id (str): the data ID

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/data/" + data_id
        res = self._session.delete(
            endpoint, headers=self._header)
        _validate_response(res)

    # JOBS FUNCTIONS ##########################################################

    def list_jobs(self):
        '''Returns a list of all jobs in the cloud.

        Returns:
            a list of job IDs

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs/list"
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["jobs"]

    def query_jobs(self, jobs_query):
        '''Performs a customized jobs query.

        Args:
            jobs_query (voxel51.query.JobsQuery): a JobsQuery instance defining
                the customized jobs query to perform

        Returns:
            a list of dicts containing the query results

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs"
        res = self._session.get(
            endpoint, headers=self._header, params=jobs_query.to_dict())
        _validate_response(res)
        return _parse_json_response(res)["jobs"]

    def upload_job_request(self, job_request, job_name, auto_start=False):
        '''Uploads a job request to the cloud.

        Args:
            job_request (voxel51.jobs.JobRequest): a JobRequest instance
                describing the job
            job_name (str): a name for the job
            auto_start (bool): whether to automatically start the job upon
                creation. By default, this is False

        Returns:
            a dictionary containing metadata about the job

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs"
        files = {
            "file": ("job.json", str(job_request), "application/json"),
            "job_name": (None, job_name),
            "auto_start": (None, str(auto_start)),
        }
        res = self._session.post(endpoint,
            files=files, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["job"]

    def get_job_details(self, job_id):
        '''Gets details about the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary containing metadata about the job

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs/" + job_id
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)["job"]

    def get_job_request(self, job_id):
        '''Gets the job request for the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a voxel51.jobs.JobRequest instance describing the job

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs/" + job_id + "/request"
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return voxj.JobRequest.from_dict(_parse_json_response(res))

    def start_job(self, job_id):
        '''Starts the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs/" + job_id + "/start"
        res = self._session.put(
            endpoint, headers=self._header)
        _validate_response(res)

    def get_job_state(self, job_id):
        '''Gets the state of the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            the state of the job, which is a value in the JobState enum

        Raises:
            APIError if the request was unsuccessful
        '''
        return self.get_job_details(job_id)["state"]

    def is_job_complete(self, job_id):
        '''Determines whether the job with the given ID is complete.

        Args:
            job_id (str): the job ID

        Returns:
            True if the job is complete, and False otherwise

        Raises:
            JobExecutionError if the job failed
            APIError if the underlying API request was unsuccessful
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
            JobExecutionError if the job failed or the maximum wait time was
                exceeded
            APIError if an underlying API request was unsuccessful
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
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs/" + job_id + "/status"
        res = self._session.get(
            endpoint, headers=self._header)
        _validate_response(res)
        return _parse_json_response(res)

    def download_job_output(self, job_id, output_path="output.zip"):
        '''Downloads the output of the job with the given ID.

        Args:
            job_id (str): the job ID
            output_path (str, optional): the output path to write to. The
                default is 'output.zip'

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/jobs/" + job_id + "/output"
        self._stream_download(endpoint, output_path)

    # PRIVATE FUNCTIONS #######################################################

    def _stream_download(self, url, output_path):
        res = self._session.get(
            url, headers=self._header, stream=True)
        voxu.ensure_basedir(output_path)
        with open(output_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)

        _validate_response(res)


class APIError(Exception):
    '''Exception raised when an API request fails.'''

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
            an instance of APIError

        Raises:
            ValueError: if the given response is not an error response
            HTTPError: if the error was caused by the HTTP connection, not
                the API itself
        '''
        if res.ok:
            raise ValueError("Response is not an error")

        try:
            message = _parse_json_response(res)["error"]["message"]
        except ValueError:
            res.raise_for_status()

        return cls(message, res.status_code)


def _get_mime_type(path):
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


def _validate_response(res):
    if not res.ok:
        raise APIError.from_response(res)


def _parse_json_response(res):
    return json.loads(res.content)
