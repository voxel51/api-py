#!usr/bin/env python
'''
Main Python interface for the Voxel51 Vision Services API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com

David Hodgson, david@voxel51.com
Brian Moore, brian@voxel51.com
'''
import os

import requests
import requests_toolbelt as rtb
import requests_toolbelt.downloadutils.stream as rtbs
import six

from voxel51 import auth
from voxel51 import utils


# @todo move to https://api.voxel51.com/v1 for production
BASE_API_URL = "http://localhost:4000/v1"


class API(object):
    '''A class for managing a session with the Voxel51 Vision Services API.

    Attributes:
        url (string): the base URL of the API
        token (voxel51.auth.Token): the authentication token for this session
    '''

    def __init__(self):
        '''Starts a new API session.'''
        self.url = BASE_API_URL
        self.token = auth.load_token()
        self._header = self.token.get_header()
        self._session = requests.Session()

    def get_home_page(self):
        '''Gets details on the basic steps to access the API.

        Returns:
            HTTP response with a description of basic API functions
        '''
        endpoint = self.url
        return self._session.get(endpoint)

    # DATA FUNCTIONS ##########################################################

    def get_data_page(self):
        '''Gets details on the available data-related functions.

        Returns:
            HTTP response with a description of available data functions
        '''
        endpoint = self.url + "/data"
        return self._session.get(endpoint, headers=self._header)

    def get_data_list(self):
        '''Returns a list of all data uploaded to the cloud.

        Returns:
            HTTP response containing the data list. If no data is found,
                a 4xx error response is returned
        '''
        endpoint = self.url + "/data/list"
        return self._session.get(endpoint, headers=self._header)

    def get_data_info(self, data_id):
        '''Gets information about the uploaded data with the given ID.

        Args:
            data_id (str): the ID of some uploaded data

        Returns:
            HTTP response containing information about the data. If no data is
                found with the given ID, a 4xx error response is returned
        '''
        endpoint = self.url + "/data/" + data_id
        return self._session.get(endpoint, headers=self._header)

    def get_dataset_info(self, group_name):
        '''Gets information about the dataset with the given name.

        Args:
            group_name (str): the name of an uploaded dataset

        Returns:
            HTTP response containing information about the dataset. If no
                group is found with the given ID, a 4xx error reponse is
                returned
        '''
        endpoint = self.url + "/data/group/" + group_name
        return self._session.get(endpoint, headers=self._header)

    def upload_data(self, paths, group_name=None):
        '''Uploads data to the cloud.

        Args:
            paths (str, list): a filepath or list of filepaths
            group_name (str): optional group name to assign to the data

        Returns:
            HTTP response describing the newly uploaded data. If an error
                occured, a 4xx or 5xx error response is returned
        '''
        if isinstance(paths, six.string_types):
            paths = [paths]

        '''
        try:
            endpoint = self.url + "/data/upload"
            files = [("files", open(p, "rb")) for p in paths]
            data = {"groupName": group_name}
            return self._session.post(
                endpoint, headers=self._header, files=files, data=data)
        except IOError as e:
            raise DataUploadError("Failed to upload data:\n" + e.message)
        finally:
            for _, f in files:
                f.close()
        '''

        try:
            endpoint = self.url + "/data/upload"
            data = {os.path.basename(p): open(p, "rb") for p in paths}
            data["groupName"] = group_name
            encoder = rtb.MultipartEncoder(data)
            headers = self._header.copy()
            headers["Content-Type"] = encoder.content_type
            self._session.post(endpoint, data=encoder, headers=headers)
        finally:
            for f in files.values():
                f.close()

    def delete_data(self, data_id):
        '''Deletes the data with the given ID from the cloud.

        Args:
            data_id (str): the ID of some uploaded data

        Returns:
            A 204 success HTTP response if the deletion was successful. If an
                error occurs or the ID was invalid, a 4xx error response is
                returned
        '''
        endpoint = self.url + "/data/" + data_id
        return self._session.delete(endpoint, headers=self._header)

    def delete_dataset(self, group_name):
        '''Deletes the dataset with the given group name.

        Args:
            group_name (str): the name of an uploaded dataset

        Returns:
            A 204 success HTTP response if the deletion was succseful. If an
                error occurs or the group name was invalid, a 4xx or 5xx error
                response is returned
        '''
        endpoint = self.url + "/data/group/" + group_name
        return self._session.delete(endpoint, headers=self._header)

    def download_data(self, data_id, path):
        '''Downloads the data with the given ID to the given path.

        Args:
            data_id (str): the ID of some uploaded data
            path (str): the path to write to

        Returns:
            HTTP response containing information about the downloaded data. If
                an error occurs or the ID was invalid, a 4xx error response is
                returned
        '''
        endpoint = self.url + "/data/" + data_id + "/download"
        #return self._session.get(endpoint, headers=self._header)
        return self._download(endpoint, path)

    def download_dataset(self, group_name, path):
        '''Downloads the dataset with the given group name to the given path.

        Args:
            group_name (str): the name of an uploaded dataset
            path (str): the path to write to

        Returns:
            HTTP response containing information about the downloaded dataset.
                If an error occurs or the group name was invalid, a 4xx error
                response is returned
        '''
        endpoint = self.url + "/data/group/" + group_name + "/download"
        #return self._session.get(endpoint, headers=self._header)
        return self._download(endpoint, path)

    # JOBS FUNCTIONS ##########################################################

    def get_jobs_page(self):
        '''Gets details on the available job-related functions.

        Returns:
            HTTP response with a description of available job functions
        '''
        endpoint = self.url + "/job"
        return self._session.get(endpoint, headers=self._header)

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
            job_json = utils.read_json(job_json)

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

    # @todo allow user to customize download location
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
        #return self._session.get(endpoint, headers=self._header)
        self._download(endpoint, path)

    # INFO FUNCTIONS ##########################################################

    def get_docs_page(self):
        '''Gets details on the available algorithm documentation functions.

        Returns:
            HTTP response with a description of basic algorithm documentation
            functions
        '''
        # @todo rename this route "/docs"?
        endpoint = self.url + "/info"
        return self._session.get(endpoint, headers=self._header)

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

    def _download(self, url, path):
        res = self._session.get(url, headers=self._header, stream=True)
        utils.ensure_basedir(path)
        with open(path, "wb") as f:
            rtbs.stream_response_to_file(res, path=f)
        return res
