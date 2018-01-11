from client_lib import Voxel51API
import os

api = Voxel51API()

print('The following example demonstrates a typical user-case\n')
print('Sign-up')
api.signup('testCaseUser', 'admin')
os.system('pause')

print('\nGet authentication token')
api.authenticate('testCaseUser', 'admin')
os.system('pause')

print('\nCheck data page for available methods')
api.getDataPage()

print('\nList all current data files on record')
api.listDataFiles()

print('\nAs no data files are present, we need to upload some')
file1 = './use-case-data/ex1.txt'
file2 = './use-case-data/ex2.mp4'
file3 = './use-case-data/ex4.jpeg'
multiple_files = [file1, file2, file3]

api.addDataFiles(multiple_files, 'testData')

print('\nNow check that the files exist')
