import requests
import pprint
import json


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
        endpoint = 'http://localhost:4000/v1/sign-up'
        res = requests.post(endpoint, data=data)
        self.print_rsp(res)
        return res

    def authenticate(self, username, password):
        endpoint = 'http://localhost:4000/v1/authenticate'
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

    def add_data_files(self, files, groupName='Not Applicable'):
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
        fileID = str(fileID)
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        pprint.pprint(res)
        return res

    def download_file(self, fileID):
        fileID = str(fileID)
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
        pprint.pprint(res)
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

    def create_task(self, filename):
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
        endpoint = self.url + '/task/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def run_task(self, taskID):
        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/run'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def pause_task(self, taskID):
        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/pause'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def stop_task(self, taskID):
        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/stop'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def delete_task(self, taskID):
        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        pprint.pprint(res)
        return res

    def get_task_status(self, taskID):
        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/status'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_details(self, taskID):
        taskID = str(taskID)
        endpoint = self.url + '/task/' + taskID + '/specs'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_task_output(self, taskID):
        taskID = str(taskID)
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

    def list_methods(self):
        endpoint = self.url + '/process/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def get_method_details(self, methodID):
        methodID = str(methodID)
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

    def save_token(self):
        f = open('.api-token.txt', 'w')
        f.write(self.token)
        f.close()

    def load_token(self):
        f = open('.api-token.txt', 'rb')
        self.token = f.readline()
        f.close()
