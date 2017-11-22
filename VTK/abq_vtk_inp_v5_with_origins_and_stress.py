import os
import io
import csv
import re

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#    Script function: Using Stress data and model      #
#         geometry information this script builds a    #
#    vtk version of the model with stresses included   #
#                                                      #
#    Prerequisites: An .rpt file with stresses and     #
#   the corresponding Abaqus .inp format model file    #
#                                                      #
########################################################

# Find all Abaqus .odb files in the directory and put them in a list
path = 'F:\\Modelling_files\\SoFIA3\\test_conversion'
# path = raw_input('input path to .odb file: ')
target_files = [f for f in os.listdir(path) if f.endswith('edited.inp')]
a = int(len(target_files))

# Load up .csv file and creates a dictionary where patient name is the key
# and a tuple of the x, y, z coordinates is the value
custom_offsets_file = 'F:\\Modelling_files\\origin_offsets2.csv'
custom_offsets = open((custom_offsets_file), 'r')
lines = csv.reader(custom_offsets, delimiter='\t')
offset = {}

for l in lines:
    pat_id = l[0]
    delta_x = l[1]
    delta_y = l[2]
    delta_z = l[3]
    offset[pat_id] = delta_x, delta_y, delta_z


# Main loop

for i in range(0, a):
    jobfile = target_files[i]
    patient_ID = jobfile.split('.inp')[0]
    filename = path+'\\'+jobfile

    # THIS SECTION PLACES EACH LINE OF THE FILE CORRESPONDING TO THE NODAL
    # COORDINATES INTO A LIST:
    nodes = []
    elements = []
    with open(filename, 'r') as file:
        for lines in file:
            #this next line uses a regular expression to extract the line
            # featuring the current node only when it conforms to the following
            # pattern node id, x, y, z. note that \s* matches zero or more
            # whitespaces,\d matches digits, \d+\.\d+ matches floats. This
            # eliminates the program accidently picking up occurances of the
            # node later when connectivity is being described.
            nodal_lines=re.match(r'^\s*\d+,+\s+\d+\.\d+,+\s+\S+\s+\S+\s+$',lines)
            #could simplify this expression
            if nodal_lines:
                nodes.append(lines)
            # as with the nodes \s* matches zero or more whitespace values.
            element_lines = re.match(r'\s*\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+$',lines)
            if element_lines:
                elements.append(lines)
    file.close()

# The above code will give both nodal and element definitions from a .inp file.
# however, regional part labels are not preserved and so the .vtk file will be
# a single continuous mesh. - NEXT GOAL IS PRESERVE LABELS.

# This is format to get rid of first column "nodes[0].split(',')[1:]"
# Similarly to get first column to use as ID "nodes[0].strip().split(',')[0]"

    with open(patient_ID + '_realigned.vtk', 'w') as outFile:
        # write vtk header
        outFile.write('# vtk DataFile Version 3.0')
        outFile.write('\nvtk output')
        outFile.write('\nASCII')
        outFile.write('\nDATASET UNSTRUCTURED_GRID')

        # write points

        numNodesTotal = len(nodes)

        outFile.write('\n\nPOINTS ' + str(numNodesTotal) + ' float\n')

        # Checks if the current patient id is in the dictionary and if so
        # retrives the correct offset values in each direction and converts
        # them to a float.

        current_pat_id = patient_ID.split('_')[0]

        if current_pat_id in offset:
            delta_x = float(offset[current_pat_id][0])
            delta_y = (float(offset[current_pat_id][1]))/10.
            # Divides by 10 to correct y offset.
            delta_z = float(offset[current_pat_id][2])

        # Extracts and reformats nodes applying above offsets.
        for i in range(len(nodes)):
            curNode = nodes[i]
            node_coords = curNode.split(',')[1:]
            for a in range(3):
                if a == 0:
                    # this block inverts sign of y coordinates
                    # and corrects translations from vascops export error.
                    current_value = float(node_coords[a])
                    new_coord = current_value + delta_x
                    fix_x_direction = new_coord*1
                    coords_new = str(fix_x_direction)
                    node_coords1 = '     '+coords_new+''
                    outFile.write(node_coords1)
                elif a == 1:
                    current_value = float(node_coords[a])
                    new_coord = current_value + delta_y
                    fix_y_direction = new_coord*-1
                    coords_new = str(fix_y_direction)
                    node_coords1 = '     '+coords_new+''
                    outFile.write(node_coords1)
                else:
                    current_value = float(node_coords[a])
                    new_coord = current_value + delta_z
                    fix_z_direction = new_coord*1
                    coords_new = str(fix_z_direction)
                    node_coords1 = '     '+coords_new+'\n'
                    outFile.write(node_coords1)

        # write cells

        numElementsTotal = len(elements)
        # eltype = len(elements[0])

        eltype = 8
        # COULD IMPROVE BY LETTING SCRIPT AUTOMATICALLY DETECT ELEMENT TYPE.

        if eltype == 4:
            # linear tet
            vtk_el_ID = 10

        elif eltype == 10:
            # quad tet
            vtk_el_ID = 24

        elif eltype == 8:
            # quad brick
            vtk_el_ID = 12

        param = eltype + 1

        outFile.write('\n\nCELLS ' + str(numElementsTotal) + ' ' + str(numElementsTotal * param)+'\n')

        for j in range(len(elements)):
            # following line removes whitespace in the string
            el_no_space = "".join(elements[j].split())
            # this line searches the string for possible integers
            el_list = [int(i) for i in el_no_space.split(',')]
            # this line takes all ints except for the first row
            # which is the element ID
            curElement = el_list[1:]
            # this line writes out the vtk element ID as the first row
            outFile.write(str(eltype)+' ')
            # this loop then writes out the connetivity as the remaining rows
            for i in range(eltype):
                el_number = curElement[i] - 1
                # minus 1 as node numbering from 0 in vtk and 1 in abaqus
                outFile.write(str(el_number)+' ')
            outFile.write('\n')

        # cell types

        outFile.write('\n\nCELL_TYPES ' + str(numElementsTotal))

        for i in range(numElementsTotal):
            cell_type = '\n' + str(vtk_el_ID)
            outFile.write(cell_type)

        # write cell data

        outFile.write('\n\nCELL_DATA ' + str(numElementsTotal))

        # write point data

        outFile.write('\n\nPOINT_DATA ' + str(numNodesTotal))

        # UPDATE BELOW SECTION TO IMPORT STRESS VALUES FROM MODIFIED RPT FILE
        # REPLACE PARAMS WITH REGEX TO FILTER RPT FILE TO JUST VALUES
        # THEN USE CSV READER TO IMPORT COLUMNS
        # ALSO ADJUST NODES TO VTK FORMAT

        # The next line sets up an empty dictionary for the
        # extracted stress values.
        stress_values = {}

        nodal_file = patient_ID + '_unique_nodal.rpt'
        with open(path + '\\' + nodal_file, 'r') as stresses_rpt:
            for lines in stresses_rpt:
                value_lines = re.match(r'^\s*\d+\s+\S+\s+$', lines)
                # issue is handling exponential numbers
            if value_lines:
                node = lines.split()[0]
                key = int(node) - 1
                # convert node numbering to vtk from abaqus
                value = lines.split()[1]
                stress_values.setdefault(key, [])
                stress_values[key].append(value)
            else:
                print('no values found')
        stresses_rpt.close()

        # Converting dict contents to VTK format and add point data header.

        print(patient_ID)

        size = len(stress_values)
        print(size)

        outFile.write('\nSCALARS MISES double')
        outFile.write('\nLOOKUP_TABLE default\n')
        for i in range(0, size):
            key_label = i
            print(key_label)
        if len(stress_values[key_label]) == 1:
            nodal_mises_stress = stress_values[key_label][0]
            outFile.write(str(nodal_mises_stress) + ' ')
        else:
            new_value1 = stress_values[key_label][0]
            new_value2 = stress_values[key_label][1]
            avg_stress = (float(new_value1) + float(new_value2))/2.0
            outFile.write(str(avg_stress) + ' ')

        # Need to modify the above to allow multiple values to be recognised
        # as belonging to a single point.
        # Can we just write out a list association as point data?

        outFile.close()
