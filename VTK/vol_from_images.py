import vtk
from vmtk import vmtkscripts
from vmtk import pypes

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#    Script function: Creates a volume image from      #
#      a stack of dicom files                          #
#                                                      #
#    Prerequisites: VMTK and VTK must be installed     #
#                                                      #
########################################################

# Input file format

image_type = 'dicom'

# path to files

path = 'E:\\SoFIA3\\test_conversion\\SOF008'  # Enter path to dicom files

# read in images

myArguments = 'vmtkimagereader -f dicom -d %s --pipe vmtkimageviewer' % path

myPype = pypes.PypeRun(myArguments)
