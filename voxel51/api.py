#!usr/bin/env python
'''
Main Python interface for the Voxel51 Vision Services API.

Copyright 2017-2018, Voxel51, LLC
voxel51.com

David Hodgson, david@voxel51.com
Brian Moore, brian@voxel51.com
'''
import requests

from voxel51 import auth


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

    def get_home_page(self):
        '''Gets details on the basic steps to access the API.

        Returns:
            HTTP response with hypermedia on basic API details
        '''
        endpoint = self.url
        return requests.get(endpoint)

    def get_data_page(self):
        '''Gets details on the available data-related functions.

        Returns:
            HTTP response with hypermedia on available data functions
        '''
        endpoint = self.url + "/data"
        return requests.get(endpoint, headers=self._header)

    def list_data(self):
        '''Returns a list of all data uploaded to the cloud.

        Returns:
            HTTP response containing the data list. If no data is found,
                a 4xx response is returned
        '''
        endpoint = self.url + "/data/list"
        return requests.get(endpoint, headers=self._header)

    def get_data_info(self, data_id):
        '''Gets details about the uploaded data with the given ID.

        Args:
            data_id (str): the ID of some uploaded data

        Returns:
            HTTP response containing information about the data. If no data is
                found with the given ID, a 4xx response is returned
        '''
        endpoint = self.url + "/data/" + str(data_id)
        return requests.get(endpoint, headers=self._header)

    def upload_data(self, paths, group_name=None):
        '''Uploads data to the cloud.

        Args:
            paths (str): a list of file paths
            group_name(str): optional group name to assign to the data

        Returns:
            HTTP response describing the newly uploaded data. If an error
                occured, a 4xx or 5xx response is returned

        Raises:
            DataUploadError
        '''
        data =
        try:
            # Open files
            files = []
            for p in paths:
                files.append(("files", open(p, "rb")))

            # Upload data
            endpoint = self.url + "/data/upload"
            return requests.post(
                endpoint,
                headers=self._header,
                files=files,
                data={"groupName": group_name},
            )
        except IOError as e:
            raise DataUploadError("Failed to upload data:\n" + e.message)
        finally:
            # Close files
            for f, _ in files:
                f.close()

    def delete_file(self, file_id):
        """Deletes specified file from database if exists.

        Args:
            file_id (str, int): Unique file identifying number.

        Returns:
            HTTP response with Success 204; 4xx response if error
        """

        file_id = str(file_id)
        endpoint = self.url + '/data/' + file_id
        header = self.header
        res = requests.delete(endpoint, headers=header)
        return res

    def download_file(self, file_id):
        """Downloads specified file to the /data/downloads folder.

        Args:
            file_id (str, int): Unique file identifying number.

        Returns:
            HTTP response with downloaded file information
        """

        file_id = str(file_id)
        endpoint = self.url + '/data/' + file_id + '/download'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def get_data_set(self, group_name):
        """Returns information on specified data set if exists.
        Returns a 404 response if no set by the specified name exists.

        Args:
            group_name(str): Unique data set identifying name.

        Returns:
            HTTP response with files in data set; 4xx response if error
        """

        endpoint = self.url + '/data/group/' + group_name
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def delete_data_set(self, group_name):
        """Deletes all files from specified data set if exists.

        Args:
            group_name(str): Unique data set identifying name.

        Returns:
            HTTP response Success 204; 4xx or 5xx response if error
        """

        endpoint = self.url + '/data/group/' + group_name
        header = self.header
        res = requests.delete(endpoint, headers=header)
        return res

    def download_data_set(self, group_name):
        """Downloads all files in data set to /data/downloads/ folder.

        Args:
            group_name(str): Unique data set identifying name.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/data/group/' + group_name + '/download'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def jobs_page(self):
        """Returns hypermedia on available job functions.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/job'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def create_job(self, filename):
        """Creates a new job for an ETA backend pipeline.
        Requires a valid JSON file specifying parameters and key fields
        to be uploaded with it.

        Args:
            filename (str): Absolute path and filename to JSON parameter file.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        endpoint = self.url + '/job'
        header = self.header
        g = None
        files = []
        with open(filename, 'rb') as f:
            g = json.load(f)

        with open(filename, 'rb') as f:
            files.append(('file', f))

        res = requests.post(endpoint, headers=header, files=files, data=g)
        f.close()
        return res

    def get_current_jobs(self):
        """Returns all existing jobs related to the client ID.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/job/list'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def run_job(self, jobID):
        """Modifies the job status to run if paused or stopped.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID + '/run'
        header = self.header
        res = requests.put(endpoint, headers=header)
        return res

    def pause_job(self, jobID):
        """Modifies the job status to pause if currently running.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID + '/pause'
        header = self.header
        res = requests.put(endpoint, headers=header)
        return res

    def stop_job(self, jobID):
        """Modifes the job status to stop if paused or running.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID + '/stop'
        header = self.header
        res = requests.put(endpoint, headers=header)
        return res

    def delete_job(self, jobID):
        """Deletes a job if and only if it is currently stopped.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID
        header = self.header
        res = requests.delete(endpoint, headers=header)
        return res

    def get_job_status(self, jobID):
        """Returns current status of specified job.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID + '/status'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def get_job_details(self, jobID):
        """Returns details on specified job.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID + '/specs'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def get_job_output(self, jobID):
        """Returns output if the specified job is complete.

        Args:
            jobID (str, int): Unique job identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        jobID = str(jobID)
        endpoint = self.url + '/job/' + jobID + '/output'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def docs_page(self):
        """Returns hypermedia on documentation of available ETA algorithms.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/info'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def list_algorithms(self):
        """Returns a list of all available ETA backend algorithms.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/info/list'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def get_algorithm_details(self, algorithmID):
        """Returns details on the specified ETA backend algorithm if it exists.

        Args:
            algorithmID (str, int): Unique ETA algorithm identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        algorithmID = str(algorithmID)
        endpoint = self.url + '/info/' + algorithmID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        return res


class DataUploadError(Exception):
    pass
