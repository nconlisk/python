import os
import io
import csv

from abaqus import *
from abaqusConstants import *

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#    Script function: Stress data extraction script    #
#                                                      #
#    Prerequisites: Must be called through Abaqus/CAE  #
#                                                      #
########################################################

# TO CALL FROM CMD TYPE abq6101 cae noGUI=abq_rpt.py.

# Find all .odb files in the directory and put them in a list
path = 'E:\\SoFIA3\\test_conversion\\'
# path = raw_input('input path to .odb file: ')
target_files = [f for f in os.listdir(path) if f.endswith('.odb')]
a = int(len(target_files))


# Main loop

for i in range(0, a):
    jobfile = target_files[i]
    patient_ID = jobfile.split('.odb')[0]
    filename = path+'\\'+jobfile
    # create odb object from odb file.
    o1 = session.openOdb(name=filename)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    # frame = o1.steps[ 'Step-1' ].frames[-1]
    frame = len(o1.steps['Step-1'].frames) - 1
    # the - 1 is becaue odb file starts from 0 and results from 1, so if 4
    # increments len would return 5 (where increments are 0 - 4),
    # as we want the last increment or 4 in the example we simply subtract 1
    # from the total size.

    # Section to generate .rpt file of nodal stresses.
    report_name = path + '\\' + patient_ID + '_unique_nodal.rpt'

    odb = session.odbs[filename]
    nf = NumberFormat(numDigits=6, precision=0, format=AUTOMATIC)
    session.fieldReportOptions.setValues(numberFormat=nf, printTotal=OFF, printMinMax=OFF)
    session.writeFieldReport(fileName=report_name, append=ON, sortItem='Node Label', odb=odb, step=0, frame=frame, outputPosition=NODAL, variable=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), ))

    o1.close()
sys.exit()
