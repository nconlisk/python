import os
import re

########################################################
#                                                      #
#                Author: Noel Conlisk                  #
#               Email: noecon@gmail.com                #
#                                                      #
########################################################

# USER INPUTS.
#
path = input('Location of file directory: ')
#
# The below code finds ansys mesh files to convert.
#
target_files = [f for f in os.listdir(path) if f.endswith('ansysmesh.txt')]
#
# This line calculates how many ansysmesh files there are and turns that value
# into an int for use in the for loop below.
#
a = int(len(target_files))
if a == 0:
    print('No mesh files found')
    exit
#
# THIS SECTION PLACES EACH LINE OF THE FILE CORRESPONDING TO THE NODAL
# COORDINATES INTO A LIST.
for i in range(0, a):
    nodes = []
    elements = []
    text_file = target_files[i]
    with open(path+"/"+text_file, 'r') as file:
        for lines in file:
            # this next line uses a regular expression to extract the line
            # featuring the current node only when it conforms to the following
            # pattern node id, x, y, z. This eliminates the program accidently
            # picking up occurances of the node later when connectivity is
            # being described.
            nodal_lines = re.match(r'^\S+\s+\S+\s+\S+\s+\S+\s+\S+$', lines)
            if nodal_lines:
                nodes.append(lines)
            else:
                elements.append(lines)
    file.close()

    # ABAQUS FORMAT INPUT PARAMETERS.
    # Note: These params may vary depending on desired mechanical behaviour.
    Header = """*Heading
    *Preprint, echo=NO, model=NO, history=NO, contact=NO
    **
    ** Model definition
    **
    """

    Footer = """** MATERIALS
    **
    *MATERIAL, NAME=WALL
    *ELASTIC
    3000000., 0.46
    *SHELL SECTION, MATERIAL=WALL, ELSET=EWALL
    0.0005, 5
    **
    *Surface, name=LUMEN, type=element
    EWALL, SPOS
    **
    **
    ** History data
    **
    *STEP, name=Step-1, nlgeom=YES
    *Static
    1., 1., 1e-05, 1.
    *BOUNDARY
    INLET, ENCASTRE
    OUTLET, ENCASTRE
    *DSLOAD
    LUMEN,P,16000
    **
    *NODE PRINT
    U,
    RF,
    *EL PRINT
    S,
    **
    ** OUTPUT FOR ABAQUS QA PURPOSES
    **
    *EL FILE
    S,
    *NODE FILE
    U, RF
    *END STEP
    """

    # Note: In the footer, SPOS can only be used with DCCAX2, for CPS3 need to
    # use S1, S2, S3, if switch to S3 element type can then use SPOS.

    lines = []

    lines.append(Header+"*NODE, NSET=NALL\n")

    for b in range(len(nodes)):
        current_node = nodes[b].split("n,")[1]
        lines.append(current_node)

    lines.append("*ELEMENT, TYPE=S3, ELSET=EWALL\n")

    for c in range(len(elements)):
        current_element = elements[c].split("e,")[1]
        new_element = str(c+1)+","+current_element
        lines.append(new_element)

    lines.append(Footer)

    output_name = text_file.split("_ansysmesh.txt")[0]

    abaqus_file = path + "/" + "%s" % output_name + "_abaqus_mesh.inp"

    # WRITE OUT NEW ABAQUS FORMAT INPUT FILE.
    with open(abaqus_file, "w") as text_file:
        for l in lines:
            text_file.write(l)
        text_file.close()
