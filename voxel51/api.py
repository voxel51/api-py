'''
Main interface for the Voxel51 Vision Services API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com
'''
import json
import os

import mimetypes
import requests
import requests_toolbelt.downloadutils.stream as rtbs

import voxel51.auth as voxa
import voxel51.jobs as voxj
import voxel51.utils as voxu


BASE_API_URL = "https://api.voxel51.com/v1"
VERIFY_REQUESTS = False  # @todo remove once SSL certificate is signed


class API(object):
    '''Main class for managing a session with the Voxel51 Vision Services API.

    Examples:
        ```python
        from voxel51.api import API

        # Start an API session
        api = API()

        # Get the list of algorithms exposed by the API
        algo_list = api.get_algorithm_list()
        ```

    Attributes:
        url (string): the base URL of the API
        token (voxel51.auth.Token): the authentication token for this session
    '''

    def __init__(self):
        '''Starts a new API session.'''
        self.url = BASE_API_URL
        self.token = voxa.load_token()
        self._header = self.token.get_header()
        self._session = requests.Session()

    # ALGORITHM FUNCTIONS #####################################################

    def list_algorithms(self):
        '''Returns a list of all available algorithms.

        Returns:
            a list of dicts describing the available algorithms

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/algo/list"
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)["algorithms"]

    def get_algorithm_doc(self, algo_id):
        '''Gets documentation about the algorithm with the given ID.

        Args:
            algo_id (str): the algorithm ID

        Returns:
            a dictionary containing the algorithm documentation

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/algo/" + algo_id
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
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
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
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
                files=files, headers=self._header, verify=VERIFY_REQUESTS)

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
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)["data"]

    def download_data(self, data_id, output_path):
        '''Downloads the data with the given ID.

        Args:
            data_id (str): the data ID
            output_path (str): the output path to write to

        Raises:
            APIError if the request was unsuccessful
        '''
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
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)

    # DATASET FUNCTIONS #######################################################

    def list_datasets(self):
        '''Returns a list of all datasets in cloud storage.

        Returns:
            a list of dataset IDs

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/dataset/list"
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)["datasets"]

    def create_dataset(self, dataset_name):
        '''Creates a new dataset in the cloud with the given name.

        Args:
            dataset_name (str): a name for the dataset

        Returns:
            a dictionary containing metadata about the dataset

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/dataset"
        files = {"dataset_name": (None, dataset_name)}
        res = self._session.post(endpoint,
            headers=self._header, files=files, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)

    def add_data_to_dataset(self, data_id, dataset_id):
        '''Adds the data with the given ID to the dataset with the given ID.

        Args:
            data_id (str): the ID of the data to add to the dataset
            dataset_id (str): the dataset ID

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/dataset/" + dataset_id
        files = {"data_id": (None, data_id)}
        res = self._session.put(endpoint,
            headers=self._header, files=files, verify=VERIFY_REQUESTS)
        _validate_response(res)

    def remove_data_from_dataset(
            self, data_id, dataset_id, delete_files=False):
        '''Removes the data with the given ID from the dataset with the given
        ID.

        Args:
            data_id (str): the ID of the data to remove from the dataset
            dataset_id (str): the dataset ID
            delete_files (bool): whether to delete the underlying data file
                from cloud storage. By default, this is False

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/dataset/" + dataset_id
        files = {
            "data_id": (None, data_id),
            "delete_files": (None, str(delete_files)),
        }
        res = self._session.delete(endpoint,
            headers=self._header, files=files, verify=VERIFY_REQUESTS)
        _validate_response(res)

    def get_dataset_details(self, dataset_id):
        '''Gets details about the dataset with the given ID.

        Args:
            dataset_id (str): the dataset ID

        Returns:
            a dictionary containing metadata about the dataset

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/dataset/" + dataset_id
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)["dataset"]

    def download_dataset(self, dataset_id, output_path):
        '''Downloads the dataset with the given ID as a zip file.

        Args:
            dataset_id (str): the dataset ID
            output_path (str): the output path to write to

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/dataset/" + dataset_id + "/download"
        self._stream_download(endpoint, output_path)

    def delete_dataset(self, dataset_id, delete_files=False):
        '''Deletes the dataset with the given ID.

        Args:
            dataset_id (str): the dataset ID
            delete_files (bool): whether to delete the underlying data files
                from cloud storage. By default, this is False

        Raises:
            APIError if the request was unsuccessful
        '''
        self.remove_data_from_dataset(
            dataset_id, None, delete_files=delete_files)

    # JOBS FUNCTIONS ##########################################################

    def list_jobs(self):
        '''Returns a list of all jobs in the cloud.

        Returns:
            a list of job IDs

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/job/list"
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
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
        endpoint = self.url + "/job"
        files = {
            "file": ("job.json", str(job_request), "application/json"),
            "job_name": (None, job_name),
            "auto_start": (None, str(auto_start)),
        }
        res = self._session.post(endpoint,
            files=files, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)

    def get_job_details(self, job_id):
        '''Gets details about the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary containing metadata about the job

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/job/" + job_id
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
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
        endpoint = self.url + "/job/" + job_id + "/request"
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return voxj.JobRequest.from_dict(_parse_json_response(res))

    def start_job(self, job_id):
        '''Starts the job with the given ID.

        Args:
            job_id (str): the job ID

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/job/" + job_id + "/start"
        res = self._session.put(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)

    def get_job_status(self, job_id):
        '''Gets the status of the job with the given ID.

        Args:
            job_id (str): the job ID

        Returns:
            a dictionary describing the status of the job

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/job/" + job_id + "/status"
        res = self._session.get(
            endpoint, headers=self._header, verify=VERIFY_REQUESTS)
        _validate_response(res)
        return _parse_json_response(res)

    def download_job_output(self, job_id, output_path):
        '''Downloads the output of the job with the given ID.

        Args:
            job_id (str): the job ID
            output_path (str): the output path to write to

        Raises:
            APIError if the request was unsuccessful
        '''
        endpoint = self.url + "/job/" + job_id + "/output"
        self._stream_download(endpoint, output_path)

    # PRIVATE FUNCTIONS #######################################################

        Args:
            job_id (str): the ID of some existing job
            path (str): the path to write to

        Returns:
            HTTP response containing information about the downloaded job
                output. If an error occurs or the ID was invalid, a 4xx error
                response is returned
        '''
        endpoint = self.url + "/job/" + job_id + "/output"
        self._stream_download(endpoint, path)

    # INFO FUNCTIONS ##########################################################

    def get_algorithm_list(self):
        '''Returns a list of all available vision algorithms.

        Returns:
            HTTP response containing the algorithms list. If an error occurs,
                a 4xx error response is returned
        '''
        # @todo rename this route "/docs/list"?
        endpoint = self.url + "/info/list"
        return self._session.get(endpoint, headers=self._header)

    def get_algorithm_info(self, algo_id):
        '''Gets information about the vision algorithm with the given ID.

        Args:
            algo_id (str): the ID of some vision algorithm

        Returns:
            HTTP response containing information about the algorithm. If no
                data is found with the given ID, a 4xx error response is
                returned
        '''
        # @todo rename this route "/docs/:algoId"?
        endpoint = self.url + "/info/" + algo_id
        return self._session.get(endpoint, headers=self._header)

    # PRIVATE FUNCTIONS #######################################################

    def _stream_download(self, url, path):
        res = self._session.get(url, headers=self._header, stream=True)
        voxu.ensure_basedir(path)
        with open(path, "wb") as f:
            rtbs.stream_response_to_file(res, path=f)
        return res
