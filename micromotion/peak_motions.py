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
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=224.608840942383, 
    height=302.445007324219)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()



path = 'G:\IBIOE_WORK\Lab_FE_revision'

os.chdir(path)

#Change this to point to the folder where you .inp files are located (this script should be run from the same folder).
#
#This line searches the above directory and creates a tuple of filenames which
#have the .inp extension.
target_files = [f for f in os.listdir(path) if f.endswith('.odb')]
#
#
#This line calculates how many .inp files there are and turns that value into an
#int for use in the for loop below.
a=int(len(target_files)) 

if a==0:
    print('No .inp files found')
    exit

for i in range(0,a):
    jobfile = target_files[i]
    jobname = path+'\\'+jobfile.split('.')[0]
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=ON)
    session.viewports['Viewport: 1'].setValues(displayedObject=None)
    o1 = session.openOdb(name=jobfile)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=-1)
    odb = session.odbs[jobfile]
    step_names = o1.steps.keys()
    frame_id_20degs = int(o1.steps[step_names[0]].frames[-1].frameId)
    session.writeFieldReport(fileName=jobname+'.txt', append=ON, 
        sortItem='Element Label', odb=odb, step=0, frame=frame_id_20degs, 
        outputPosition=ELEMENT_NODAL, variable=(('COPEN', ELEMENT_NODAL), (
        'CSLIP1', ELEMENT_NODAL), ('CSLIP2', ELEMENT_NODAL), ))
   
