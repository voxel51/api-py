'''
Main interface for the Voxel51 Vision Services API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com
'''
import json
import os

import requests
import requests_toolbelt as rtb
import requests_toolbelt.downloadutils.stream as rtbs
import six

import voxel51.auth as voxa
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

    # JOBS FUNCTIONS ##########################################################

    def create_job(self, job_json):
        '''Creates a new job in the cloud.

        Args:
            job_json (dict, str): either a JSON dictionary or the path to a
                JSON file on disk describing the algorithm, data, and
                parameters of the job to run

        Returns:
            A 204 success HTTP response if the job creation was succseful. If
                an error occured, a 4xx error response is returned
        '''
        if isinstance(job_json, six.string_types):
            job_json = voxu.read_json(job_json)

        endpoint = self.url + "/job"
        return self._session.post(
            endpoint, headers=self._header, data=job_json)

    def get_job_list(self):
        '''Returns a list of all existing jobs in the cloud.

        Returns:
            HTTP response containing the list of jobs. If no jobs are found,
                a 4xx error response is returned
        '''
        endpoint = self.url + "/job/list"
        return self._session.get(endpoint, headers=self._header)

    def start_job(self, job_id):
        '''Starts the job with the given ID. The job must be an existing job
        that is currently paused or stopped.

        Args:
            job_id (str): the ID of some existing job

        Returns:
            A 201 success HTTP response if the start was succseful. If an
                error occurs or the job ID was invalid, a 4xx error response
                is returned
        '''
        endpoint = self.url + "/job/" + job_id + "/run"
        return self._session.put(endpoint, headers=self._header)

    def pause_job(self, job_id):
        '''Pauses the job with the given ID. The job must be an existing job
        that is currently running.

        Args:
            job_id (str): the ID of some existing job

        Returns:
            A 201 success HTTP response if the pause was succseful. If an
                error occurs or the job ID was invalid, a 4xx error response
                is returned
        '''
        endpoint = self.url + "/job/" + job_id + "/pause"
        return self._session.put(endpoint, headers=self._header)

    def stop_job(self, job_id):
        '''Stops the job with the given ID. The job must be an existing job
        that is currently running.

        Args:
            job_id (str): the ID of some existing job

        Returns:
            A 201 success HTTP response if the stop was succseful. If an
                error occurs or the job ID was invalid, a 4xx error response
                is returned
        '''
        endpoint = self.url + "/job/" + job_id + "/stop"
        return self._session.put(endpoint, headers=self._header)

    def delete_job(self, job_id):
        '''Deletes the job with the given ID. The job must be an existing job
        that is currently stopped.

        Args:
            job_id (str): the ID of some existing job

        Returns:
            A 201 success HTTP response if the deletion was succseful. If an
                error occurs or the job ID was invalid, a 4xx error response
                is returned
        '''
        endpoint = self.url + "/job/" + job_id
        return self._session.delete(endpoint, headers=self._header)

    def get_job_status(self, job_id):
        '''Gets the status of the job with the given ID.

        Args:
            job_id (str): the ID of some existing job

        Returns:
            HTTP response describing the job status. If an error occurs or
                the job ID was invalid, a 4xx error response is returned
        '''
        endpoint = self.url + "/job/" + job_id + "/status"
        return self._session.get(endpoint, headers=self._header)

    def get_job_specs(self, job_id):
        '''Gets specifications of the job with the given ID.

        Args:
            job_id (str): the ID of some existing job

        Returns:
            HTTP response describing the job specifications. If an error occurs
                or the job ID was invalid, a 4xx error response is returned
        '''
        endpoint = self.url + "/job/" + job_id + "/specs"
        return self._session.get(endpoint, headers=self._header)

    def download_job_output(self, job_id, path):
        '''Downloads the output of the job with the given ID to the given path.

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
