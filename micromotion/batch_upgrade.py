import os
import io

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#        Usage: Run through Abaqus/CAE                 #
#               development environment                #
#                                                      #
########################################################


from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=180, 
    height=190)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()


path = 'G:\IBIOE_WORK\Lab_FE_revision'

os.chdir(path)

target_files = [f for f in os.listdir(path) if f.endswith('.odb')]

a=int(len(target_files)) 

if a==0:
    print('No .inp files found')
    exit

for i in range(0,a):
    new_jobfile = target_files[i]
    old_jobname = new_jobfile.split('.')[0]
    new_jobname = old_jobname+'_upgraded'
    jobcommand='abq6124 -upgrade -job '+new_jobname+' -odb '+old_jobname
    os.system(jobcommand)
    print('Your file has been upgraded')
