from client_lib import Voxel51API
import os

api = Voxel51API()

print('The following example demonstrates a typical user-case\n')
print('Sign-up')
api.signup('testCaseUser', 'admin')
input('Press enter to continue...\n')

print('\nGet authentication token')
api.authenticate('testCaseUser', 'admin')
input('Press enter to continue...\n')

print('\nCheck data page for available methods')
api.get_data_page()
input('Press enter to continue...\n')

print('\nList all current data files on record')
api.list_data_files()
input('Press enter to continue...\n')

print('\nAs no data files are present, we need to upload some')
file1 = os.getcwd() + '/use-case-data/ex1.txt'
file2 = os.getcwd() + '/use-case-data/ex2.mp4'
file3 = os.getcwd() + '/use-case-data/ex3.jpeg'
multiple_files = [file1, file2, file3]

api.add_data_files(multiple_files, 'testData')
input('Press enter to continue...\n')

print('\nNow check that the files exist')
api.list_data_files()
input('Press enter to continue...\n')

print('\nTo see specifics on one file, do the following')
api.get_data_specs('1')
input('Press enter to continue...\n')

print('\nCheck to make sure all the data files are there')
api.list_data_files()

print('\nGet the details of just one file')
api.get_data_specs('1')
input('Press enter to continue...\n')

print('\nDeleting a file you do not want anymore')
api.delete_file('3')
input('Press enter to continue...\n')

print('\nGet remaining files by group name')
api.get_data_set('testData')
input('Press enter to continue...\n')
