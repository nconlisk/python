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



#Test of getLabels command and getArea() command
#If this works should return an area close to 100mm2.

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=180, 
    height=190)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()


path = 'F:\IBIOE_WORK\JOR_material\JOR_frictional_tests'

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

#Initial values
params1 = ['-0.02', '-0.04', '-0.06','-0.08', '-0.10', '-0.15']
params2 = ['0.02', '0.04', '0.06','0.08', '0.10', '0.15']
params3 = ['COPEN', 'CSLIP1', 'CSLIP2']

for i in range(0,a):
    jobfile = target_files[i]
    jobname = path+'\\'+jobfile
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=ON)
    session.viewports['Viewport: 1'].setValues(displayedObject=None)
    o1 = session.openOdb(name=jobfile)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
            intervalType=USER_DEFINED, intervalValues=(-0.15, -0.10, -0.08, -0.06, -0.04, -0.02, 0, 
            0.02, 0.04, 0.06, 0.08, 0.10, 0.15, ))

    #LOOP FOR ALL 3 STEPS.
    step_names = o1.steps.keys()
    for i in step_names:
        current_step = i
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=current_step, frame=-1)

        #LOOP TO OUTPUT ALL VARIABLES (E.G. COPEN, CSLIP1, CSLIP2).
        for i in range (0,len(params3)):
            current_param = params3[i]
            session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel= current_param, outputPosition=ELEMENT_NODAL, )
            session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                variableLabel=current_param, outputPosition=ELEMENT_NODAL, )
            session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=CONTOURS_ON_UNDEF)
            
            for f in range(0,len(params1)):
                total_cortical_area = ()
                total_cancellous_area = ()
                param1 = float(params1[f])
                param2 = float(params2[f])
                leaf = dgo.LeafFromSurfaceVarRange(minimumRange=param1, maximumRange=param2, 
                    insideRange=ON)
                session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)

                #CODE TO GET ACTIVE ELEMENTS.
                active_nodes = session.viewports['Viewport: 1'].getActiveNodeLabels(useCut=True, 
                        printResults=False)
                active_elements = session.viewports['Viewport: 1'].getActiveElementLabels(useCut=True, 
                        printResults=False)

                #THE ABOVE CREATES A DICTIONARY WITH PART NAME AS THE KEY AND ELEMENTS/NODES AS THE VALUES
                
                part_names = active_nodes.keys() #This gives the part name by finding the keys on the above dictionaries.
                if 'CANCELLOUS' in part_names[0]:
                    cancellous = part_names[0]
                    cortical = part_names[1]
                else:
                    cancellous = part_names[1]
                    cortical = part_names[0]
                    


                #The below lines gives lists of active elements/nodes by part.
                cancellous_nodes = active_nodes[cancellous]
                cortical_nodes = active_nodes[cortical]
                cancellous_elements = active_elements[cancellous]
                cortical_elements = active_elements[cortical]

                #NEXT STEP IS TO FIND THE ELEMENT CONNECTIVITY AND THEN FROM THIS WHICH NODES MAKE
                #UP A GIVEN ELEMENT.

                cancellous_element_connectivity = {}
                cortical_element_connectivity = {}

                #CONNECTIVITY VALUES ARE THEN APPENDED TO A DICTIONARY WHERE ELEMENT IS THE KEY AND NODE IDS ARE THE VALUE
                #THIS DICTIONARY WILL NEED TO BE RESET EVERY PARAM LOOP WITH ACTIVE ELEMENTS.

                for i in cancellous_elements:
                    ele_index = i - 1
                    cancellous_connectivity = o1.rootAssembly.instances[cancellous].elements[ele_index].connectivity
                    cancellous_element_connectivity[str(i)] = cancellous_connectivity
                    

                for i in cortical_elements:
                    ele_index = i - 1
                    cortical_connectivity = o1.rootAssembly.instances[cortical].elements[ele_index].connectivity
                    cortical_element_connectivity[str(i)] = cortical_connectivity
                    

                #NEXT STEP IS TO FIND THE NODAL COORDINATES FOR ALL THE ACTIVE NODES THEN TEST WHICH NODES ARE IN WHICH ELEMENT
                #AFTER THAT JUST ASSIGN THE NODAL COORDINATES TO ONE OF THE THREE POINTS, CALCULATE THE ARE OF THE ELEMENT
                #FACE AND THEN TOTAL THE FACES PER PART AND THEN TOTAL BOTH PARTS. SANITY CHECK - DO THE NUMBER OF AREA ENTRIES MATCH
                #THE NUMBER OF ACTIVE ELEMENTS.


                #NODAL COORDS BY PART

                cancellous_nodal_coordinates = {}
                cortical_nodal_coordinates = {}

                for i in cancellous_nodes:
                    node_index = i - 1
                    cancellous_coords = o1.rootAssembly.instances[cancellous].nodes[node_index].coordinates
                    cancellous_nodal_coordinates[str(i)] = cancellous_coords

                for i in cortical_nodes:
                    node_index = i - 1
                    cortical_coords = o1.rootAssembly.instances[cortical].nodes[node_index].coordinates
                    cortical_nodal_coordinates[str(i)] = cortical_coords


                #NODES IN ELEMENT AND AREA CALCULATION BY PART


                #CAN WE MOVE NODAL COORDS SECTION ABOVE ELEMENTS AND THEN ADD THE BELOW LINES TO ELEMENTS SECTION.


                cancellous_area_list = []
                cortical_area_list = []

                for i in cancellous_element_connectivity:
                    current_element = cancellous_element_connectivity[i]
                    p = []
                    q = []
                    r = []
                    for l in current_element:
                        current_node = str(l)
                        if current_node in cancellous_nodal_coordinates.keys():
                            if p == []:
                                p = cancellous_nodal_coordinates[current_node]
                                
                            elif q == []:
                                q = cancellous_nodal_coordinates[current_node]
                                
                            elif r == []:
                                r = cancellous_nodal_coordinates[current_node]
                                
                        else:
                            continue

                    #PROBLEM WITH P,Q,R SOME NODES FROM THE ELEMENT CONNECTIVITY DONT SEEM TO HAVE COORDINATES. 

                    #Calculate area of a triangle based on length of each side.
                    if p != [] and q != [] and r != []:
                        side_A = (((float(p[0]) - float(q[0]))**2)+((float(p[1]) - float(q[1]))**2)+((float(p[2]) - float(q[2]))**2))**0.5
                        side_B = (((float(q[0]) - float(r[0]))**2)+((float(q[1]) - float(r[1]))**2)+((float(q[2]) - float(r[2]))**2))**0.5
                        side_C = (((float(r[0]) - float(p[0]))**2)+((float(r[1]) - float(p[1]))**2)+((float(r[2]) - float(p[2]))**2))**0.5

                        s = (side_A + side_B + side_C)/2.0

                        area = (s*(s - side_A)*(s - side_B)*(s - side_C))**0.5

                        cancellous_area_list.append(area) #create this file at the right level so it is refreshed for each odb file.
                    else:
                        continue

                    
                            

                #REPEAT ABOVE FOR CORTICAL BONE ELEMENTS
                for i in cortical_element_connectivity:
                    current_element = cortical_element_connectivity[i]
                    p = []
                    q = []
                    r = []
                    for l in current_element:
                        current_node = str(l)
                        if current_node in cortical_nodal_coordinates.keys():
                            if p == []:
                                p = cortical_nodal_coordinates[current_node]
                                
                            elif q == []:
                                q = cortical_nodal_coordinates[current_node]
                                
                            elif r == []:
                                r = cortical_nodal_coordinates[current_node]
                                
                        else:
                            continue

                    
                    #NEED TO ONLY START AREA CALCULATION IF P Q R ARE NOT NONE. ALSO DOUBLECHECK WHY ELEMENT NOT IN KEYS WOULD BE IN CORTICAL_ELEMENT_CONNECTIVITY

                    #MAKE SURE CONNECTIVITY IS FOR ACTIVE NODES AND ELEMENTS ONLY.

                    #Calculate area of a triangle based on length of each side.
                    if p != [] and q != [] and r != []:
                        side_A = (((float(p[0]) - float(q[0]))**2)+((float(p[1]) - float(q[1]))**2)+((float(p[2]) - float(q[2]))**2))**0.5
                        side_B = (((float(q[0]) - float(r[0]))**2)+((float(q[1]) - float(r[1]))**2)+((float(q[2]) - float(r[2]))**2))**0.5
                        side_C = (((float(r[0]) - float(p[0]))**2)+((float(r[1]) - float(p[1]))**2)+((float(r[2]) - float(p[2]))**2))**0.5

                        s = (side_A + side_B + side_C)/2.0

                        area = (s*(s - side_A)*(s - side_B)*(s - side_C))**0.5

                        cortical_area_list.append(area)
                    else:
                        continue

                total_cortical_area = sum(cortical_area_list)
                total_cancellous_area = sum(cancellous_area_list)
                total_area = total_cancellous_area + total_cortical_area
                
                current_job= jobfile.split('.')[0]
                cutoff = params2[f].replace('.','dot')
                area_file = path+'//'+current_job+'_area_file_'+current_param+'_step_'+current_step+'_cutoff_'+cutoff+'.txt'
                new_file1=open(area_file,'w')
                new_file1.write('total area is: '+str(total_area))
                


 
