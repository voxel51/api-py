#!usr/bin/env python
'''
Voxel51 API Python client library for programmatic access to the
API's functions.

Copyright 2017-2018, Voxel51, LLC
voxel51.com

David Hodgson, david@voxel51.com
'''

import requests
import pprint
import json


class API:
    """Python client library for Voxel51 API"""

    # TODO Refactor to work with environment variable then look for hidden file
    def __init__(self):
        """Constructor of the API class."""

        self.url = 'http://localhost:4000/v1'
        """str: Base url to access API."""
        self.token = ''
        """str: Stores JSON web token for authentication"""

    # SIGN-UP AND AUTHENTICATION

    def get_home_page(self):
        """Returns hypermedia detailing basic steps to access the API.

        Returns:
            HTTP response with hypermedia. Error status is bad request.
        """

        endpoint = 'http://localhost:4000'
        res = requests.get(endpoint)
        self.print_rsp(res)
        return res

    # TODO Remove before production deployment
    def signup(self, username, password):
        """Creates a new client with username:password.
        If the passed username is already in use, the sign-up will not be
        successful. The username:password combination is used to get a valid
        authentication token.

        Args:
            username (str): Unique username for new client
            password (str): Password associated with username

        Returns:
            HTTP response with success; 4xx response if error
        """

        data = {
            'username': username,
            'password': password,
        }
        endpoint = 'http://localhost:4000/v1/sign-up'
        res = requests.post(endpoint, data=data)
        self.print_rsp(res)
        return res

    # TODO Remove before production deployment
    def authenticate(self, username, password):
        """Retrieves valid JSON web token if valid username:password supplied.
        Provides a valid authentication token if a valid username:password
        combination is attached to the HTTP request. Stores a valid token
        to the class token attribute.

        Args:
            username (str): Unique client username
            password (str): Password associated with username

        Returns:
            HTTP response with authentication token; 4xx response if error
        """

        endpoint = 'http://localhost:4000/v1/authenticate'
        res = requests.post(endpoint, auth=(username, password))
        self.print_rsp(res)
        self.token = res.json()['access_token']
        return res

    # DATA FUNCTIONS

    def get_data_page(self):
        """Returns hypermedia on available data route functions.

        Returns:
            HTTP response with hypermedia on available methods.
        """

        endpoint = self.url + '/data'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def list_data_files(self):
        """Returns a list of any data files present under client ID.
        If no files are present, returns a 404 response.

        Returns:
            HTTP response with files; 4xx response if error
        """

        endpoint = self.url + '/data/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_data_specs(self, fileID):
        """Returns details on the specified file if exists.

        Returns:
            HTTP response with file details; 4xx response if error.
        """

        fileID = str(fileID)
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def add_data_files(self, files, groupName='Not Applicable'):
        """Posts new file(s) to the server and assigns unique ID to each file.

        Args:
            files (str): Array of file paths
            groupName (str): Optional data set/group identifier

        Returns:
            HTTP response with uploaded files; 4xx or 5xx response if error
        """

        endpoint = self.url + '/data/upload'
        header = {'Authorization': 'Bearer ' + self.token}
        data = {'groupName': groupName}
        input_files = []
        for file in files:
            print(file)
            input_files.append(('files', open(file, 'rb')))
        try:
            print(input_files)
            res = requests.post(
                endpoint,
                headers=header,
                files=input_files,
                data=data)

            self.print_rsp(res)
        finally:
            for file in input_files:
                # [0] contains files key; [1] contains actual file
                file[1].close()
            return res

    def delete_file(self, fileID):
        """Deletes specified file from database if exists.

        Args:
            fileID (str, int): Unique file identifying number.

        Returns:
            HTTP response with Success 204; 4xx response if error
        """

        fileID = str(fileID)
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        pprint.pprint(res)
        return res

    def download_file(self, fileID):
        """Downloads specified file to the /data/downloads folder.

        Args:
            fileID (str, int): Unique file identifying number.

        Returns:
            HTTP response with downloaded file information
        """

        fileID = str(fileID)
        endpoint = self.url + '/data/' + fileID + '/download'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_data_set(self, groupName):
        """Returns information on specified data set if exists.
        Returns a 404 response if no set by the specified name exists.

        Args:
            groupName (str): Unique data set identifying name.

        Returns:
            HTTP response with files in data set; 4xx response if error
        """

        endpoint = self.url + '/data/group/' + groupName
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def delete_data_set(self, groupName):
        """Deletes all files from specified data set if exists.

        Args:
            groupName (str): Unique data set identifying name.

        Returns:
            HTTP response Success 204; 4xx or 5xx response if error
        """

        endpoint = self.url + '/data/group/' + groupName
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        pprint.pprint(res)
        return res

    def download_data_set(self, groupName):
        """Downloads all files in data set to /data/downloads/ folder.

        Args:
            groupName (str): Unique data set identifying name.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/data/group/' + groupName + '/download'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # TASK FUNCTIONS

    def tasks_page(self):
        """Returns hypermedia on available task functions.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/task'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def create_task(self, filename):
        """Creates a new task for an ETA backend pipeline.
        Requires a valid JSON file specifying parameters and key fields
        to be uploaded with it.

        Args:
            filename (str): Absolute path and filename to JSON parameter file.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        endpoint = self.url + '/task'
        header = {'Authorization': 'Bearer ' + self.token}
        f = open(filename, 'rb')
        g = json.load(f)
        f.close()
        f = open(filename, 'rb')
        files = []
        files.append(('file', f))
        res = requests.post(endpoint, headers=header, files=files, data=g)
        self.print_rsp(res)
        f.close()
        return res

    def get_current_tasks(self):
        """Returns all existing tasks related to the client ID.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/task/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def run_task(self, taskID):
        """Modifies the task status to run if paused or stopped.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/run'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def pause_task(self, taskID):
        """Modifies the task status to pause if currently running.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/pause'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def stop_task(self, taskID):
        """Modifes the task status to stop if paused or running.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/stop'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def delete_task(self, taskID):
        """Deletes a task if and only if it is currently stopped.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 201; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        pprint.pprint(res)
        return res

    def get_task_status(self, taskID):
        """Returns current status of specified task.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/status'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_details(self, taskID):
        """Returns details on specified task.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/specs'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_output(self, taskID):
        """Returns output if the specified task is complete.

        Args:
            taskID (str, int): Unique task identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/output'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # PROCESS/DOC FUNCTIONS

    def docs_page(self):
        """Returns hypermedia on documentation of available ETA methods.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/process'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def list_methods(self):
        """Returns a list of all available ETA backend methods.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        endpoint = self.url + '/process/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_method_details(self, methodID):
        """Returns details on the specified ETA backend method if it exists.

        Args:
            methodID (str, int): Unique ETA method identifying number.

        Returns:
            HTTP response Success 200; 4xx response if error
        """

        methodID = str(methodID)
        endpoint = self.url + '/process/' + methodID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # UTILITY FUNCTIONS

    # TODO Remove before production deployment
    def print_rsp(self, res):
        """Utility function to pretty print the response from requests.

        Args:
            res: HTTP response object

        Returns:
            None
        """

        pprint.pprint(res.url)
        pprint.pprint(res.status_code)
        pprint.pprint(res.json())

    # TODO Remove before production deployment
    def save_token(self):
        """Utility function to write and save API token to file for future use.

        Returns:
            None
        """

        f = open('.api-token.txt', 'w')
        f.write(self.token)
        f.close()

    # TODO Remove before production deployment
    def load_token(self):
        """Utility function to load written API token from saved file.

        Returns:
            None
        """

        f = open('.api-token.txt', 'rb')
        self.token = f.readline()
        f.close()
