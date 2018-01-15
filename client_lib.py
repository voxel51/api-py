import requests
import pprint


class Voxel51API:
    def __init__(self):
        self.url = 'http://localhost:4000/v1'
        self.token = ''

    # SIGN-UP AND AUTHENTICATION

    def get_home_page(self):
        endpoint = 'http://localhost:4000'
        res = requests.get(endpoint)
        self.print_rsp(res)
        return res

    def signup(self, username, password):
        data = {
            'username': username,
            'password': password,
        }
        endpoint = 'http://localhost:4000/sign-up'
        res = requests.post(endpoint, data=data)
        self.print_rsp(res)
        return res

    def authenticate(self, username, password):
        endpoint = 'http://localhost:4000/authenticate'
        res = requests.post(endpoint, auth=(username, password))
        self.print_rsp(res)
        self.token = res.json()['access_token']
        return res

    # DATA FUNCTIONS

    def get_data_page(self):
        endpoint = self.url + '/data'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def list_data_files(self):
        endpoint = self.url + '/data/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_data_specs(self, fileID):
        fileID = str(fileID)
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # TODO returns an error for file.close() (str cannot be closed)
    def add_data_files(self, files, groupName='Not Applicable'):
        endpoint = self.url + '/data/upload'
        header = {'Authorization': 'Bearer ' + self.token}
        input_files = []
        for file in files:
            print(file)
            input_files.append(('files', open(file, 'rb')))
        try:
            print(input_files)
            res = requests.post(endpoint, headers=header, files=input_files)
            self.print_rsp(res)
        finally:
            for file in input_files:
                # [0] contains files key; [1] contains actual file
                file[1].close()
            return res

    # TODO Fix error on print res.json() for success
    def delete_file(self, fileID):
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def download_file(self, fileID):
        endpoint = self.url + '/data/' + fileID + '/download'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_data_set(self, groupName):
        endpoint = self.url + '/data/group/' + groupName
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def delete_data_set(self, groupName):
        endpoint = self.url + '/data/group/' + groupName
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def download_data_set(self, groupName):
        endpoint = self.url + '/data/group/' + groupName + '/download'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # TASK FUNCTIONS

    def tasks_page(self):
        endpoint = self.url + '/task'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def create_task(self, file, params):
        pass

    def get_current_tasks(self):
        endpoint = self.url + '/task/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def run_task(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/run'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def pause_task(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/pause'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def stop_task(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/stop'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def change_task_status(self, taskID, status):
        if status != 'stop' or status != 'pause' or status != 'run':
            return 'IncorrectStatusError'

        endpoint = self.url + '/task/' + taskID + '/' + status
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def delete_task(self, taskID):
        endpoint = self.url + '/task/' + taskID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_status(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/status'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_details(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/specs'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_output(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/output'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # PROCESS/DOC FUNCTIONS

    def docs_page(self):
        endpoint = self.url + '/process'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_method_details(self, methodID):
        endpoint = self.url + '/process/' + methodID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # UTILITY FUNCTIONS

    def print_rsp(self, res):
        pprint.pprint(res.url)
        pprint.pprint(res.status_code)
        pprint.pprint(res.json())
