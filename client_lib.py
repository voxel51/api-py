import requests
import pprint


class Voxel51API:
    def __init__(self):
        self.url = 'http://localhost:4000/v1'
        self.token = ''

    # SIGN-UP AND AUTHENTICATION

    def getHomePage(self):
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

    def getDataPage(self):
        endpoint = self.url + '/data'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def listDataFiles(self):
        endpoint = self.url + '/data/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def getDataSpecs(self, fileID):
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def addDataFiles(self, files, groupName='Not Applicable'):
        endpoint = self.url + '/data'
        header = {'Authorization': 'Bearer ' + self.token}
        input_files = []
        for file in files:
            input_files.add('files', (file, open(file, 'rb')))
        print(input_files)
        res = requests.post(endpoint, headers=header, files=input_files)
        self.print_rsp(res)
        return res

    def deleteSingleFile(self, fileID):
        endpoint = self.url + '/data/' + fileID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def downloadSingleFile(self, fileID):
        endpoint = self.url + '/data/' + fileID + '/download'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def getDataSetNames(self, groupName):
        endpoint = self.url + '/data/group/' + groupName
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def deleteDataSet(self, groupName):
        endpoint = self.url + '/data/group/' + groupName
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def downloadDataSet(self, groupName):
        endpoint = self.url + '/data/group/' + groupName + '/download'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # TASK FUNCTIONS

    def tasksPage(self):
        endpoint = self.url + '/task'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def createTask(self, file, params):
        pass

    def getCurrentTasks(self):
        endpoint = self.url + '/task/list'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def runTask(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/run'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def pauseTask(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/pause'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def stopTask(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/stop'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def changeTaskStatus(self, taskID, status):
        if status != 'stop' or status != 'pause' or status != 'run':
            return 'IncorrectStatusError'

        endpoint = self.url + '/task/' + taskID + '/' + status
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.put(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def deleteTask(self, taskID):
        endpoint = self.url + '/task/' + taskID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.delete(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def getTaskStatus(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/status'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def getTaskDetails(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/specs'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def getTaskOutput(self, taskID):
        endpoint = self.url + '/task/' + taskID + '/output'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # PROCESS/DOC FUNCTIONS

    def docsPage(self):
        endpoint = self.url + '/process'
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    def getMethodDetails(self, methodID):
        endpoint = self.url + '/process/' + methodID
        header = {'Authorization': 'Bearer ' + self.token}
        res = requests.get(endpoint, headers=header)
        self.print_rsp(res)
        return res

    # UTILITY FUNCTIONS

    def print_rsp(self, res):
        pprint.pprintrint(res.url)
        pprint.pprintrint(res.status_code)
        pprint.pprintrint(res.json())
