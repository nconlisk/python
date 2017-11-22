import csv
import re

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#    Script function: Return x, y, z coordinates       #
#      from a 3D mesh based on a .csv file containing  #
#      nodal IDs                                       #
#        Usage: for use with Abaqus input files        #
#                                                      #
########################################################

# USER INPUTS:
path = input('Location of .inp file directory: ')
node_list = open(input('enter name of .csv file to import: '), 'r')
text_file = input('enter name of .inp file to import: ')

# THIS SECTION READS THE CONTENTS OF THE .CSV FILE AND PLACES THEM IN A LIST:
lines = csv.reader(node_list)
nodes = []
for l in lines:
    nodes = l
node_list.close()

node_ID = []
for i in range(len(nodes)):
    current_node = nodes[i].lstrip(' ')
    node_ID.append(current_node)

# THIS SECTION PLACES EACH LINE OF THE FILE CORRESPONDING TO THE NODAL
# COORDINATES INTO A LIST:
parsed_lines = []
with open(text_file, 'r') as file:
    for lines in file:
        # this next line uses a regular expression to extract the line
        # featuring the current node only when it conforms to the following
        # pattern node id, x, y, z. This eliminates the program accidently
        # picking up occurances of the node when connectivity is described
        nodal_lines = re.match(r'^\s+\S+\s+\S+\s+\S+\s+\S+\s+$', lines)
        if nodal_lines:
            parsed_lines.append(lines)
file.close()

# THIS SECTION SELECTS ONLY THOSE NODES IN THE NODE LIST AND PLACES
# THEM IN A NEW LIST CALLED COORDS:
coords = []
for i in range(len(node_ID)):
    current_node = (str(node_ID[i])+',')
    for l in range(len(parsed_lines)):
        lines_space_removed = parsed_lines[l].lstrip(' ')
        if lines_space_removed.startswith(current_node):
            coords.append(parsed_lines[l])

# WRITES THE COORDS OUT TO A NEW TEXT FILE BASED ON THE .CSV FILE NAME:
output = node_list.name.split('.')[0]+'_coords.txt'
with open(output, 'w') as new_file:
    for lines in coords:
        new_file.write(lines)
    new_file.close()
