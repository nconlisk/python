import os
import io

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#    Script function: Sequentially executes data       #
#      extraction and conversion scripts               #
#                                                      #
#    Prerequisites: Abaqus/CAE and ipython must be     #
#                   installed                          #
#                                                      #
########################################################

command_1 = 'abq6101 cae script=abq_rpt.py'
command_2 = 'ipython abq_vtk_inp_v5_with_origins_and_stress.py'


os.system(command_1)

os.system(command_2)
