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
        """Returns hypermedia detailing basic steps to access the API.

        Returns:
            HTTP response with hypermedia. Error status is bad request.
        """

        endpoint = self.url
        res = requests.get(endpoint)
        return res

    def get_data_page(self):
        """Returns hypermedia on available data route functions.

        Returns:
            HTTP response with hypermedia on available algorithms.
        """

        endpoint = self.url + '/data'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def list_data_files(self):
        """Returns a list of any data files present under client ID.
        If no files are present, returns a 404 response.

        Returns:
            HTTP response with files; 4xx response if error
        """

        endpoint = self.url + '/data/list'
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def get_data_specs(self, file_id):
        """Returns details on the specified file if exists.

        Returns:
            HTTP response with file details; 4xx response if error.
        """

        file_id = str(file_id)
        endpoint = self.url + '/data/' + file_id
        header = self.header
        res = requests.get(endpoint, headers=header)
        return res

    def add_data_files(self, files, group_name=None):
        """Posts new file(s) to the server and assigns unique ID to each file.

        Args:
            files (str): Array of file paths
            group_name(str): Optional data set/group identifier

        Returns:
            HTTP response with uploaded files; 4xx or 5xx response if error
        """

        endpoint = self.url + '/data/upload'
        header = self.header
        data = {'groupName': group_name}
        input_files = []
        for file in files:
            input_files.append(('files', open(file, 'rb')))
        try:
            res = requests.post(
                endpoint,
                headers=header,
                files=input_files,
                data=data)

        except IOError:
            pass

        finally:
            for file in input_files:
                # [0] contains files key; [1] contains actual file
                file[1].close()
            return res

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
