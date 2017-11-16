import os

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#                                                      #
########################################################

# This line sets up the path to the folder with .inp files.
#
path = input('Location of .inp file directory: ')
#
# This line searches the above directory and creates a tuple of filenames which
# have the .inp extension.
target_files = [f for f in os.listdir(path) if f.endswith('.inp')]
#
# This line calculates how many .inp files there are and turns that value
# into an int for use in the for loop below.
a = int(len(target_files))
if a == 0:
    print('No .inp files found')
    exit

# Job submission code.
# Note: This code requires Abaqus 6.12-4 to be installed on the system.
for i in range(0, a):
    new_jobfile = target_files[i]
    new_jobname = new_jobfile.split('.')[0]
    jobcommand = 'abq6124 job=' + new_jobname + ' int cpus=2'
    os.system(jobcommand)
    print('Your Abaqus job has been submitted')
