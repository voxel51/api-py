from client_lib import Voxel51API
import os
import sqlite3


# seed a complete task for final function calls
con = sqlite3.connect('../database.sqlite')

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

print('\nDownload remaining files by group name')
api.download_data_set('testData')
input('Press enter to continue...\n')

print('\nSee what methods are available for tasks')
api.tasks_page()
input('Press enter to continue...\n')

file4 = os.getcwd() + '/use-case-data/params.json'
print('\nCreate a new task using one of the files')
api.create_task(file4)
input('Press enter to continue...\n')

print('\nSee if you have any current tasks')
api.get_current_tasks()
input('Press enter to continue...\n')

print('\nTry to pause the running task')
api.pause_task(1)
input('Press enter to continue...\n')

print('\nRun the task again')
api.run_task(1)
input('Press enter to continue...\n')

print('\nStop the task')
api.stop_task(1)
input('Press enter to continue...\n')

# change the isComplete status to true
seed = "UPDATE Tasks SET isComplete = 'true' WHERE Tasks.name = 'testCase'"
with con:
    cur = con.cursor()
    cur.execute(seed)

con.close()

print('\nRemind ourselves of the task details')
api.get_task_details(1)
input('Press enter to continue...\n')

print('\nGet the output from the completed task')
api.get_task_output(1)
input('Press enter to continue...\n')
