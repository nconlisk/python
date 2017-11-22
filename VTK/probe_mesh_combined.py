"""Probe image with mesh. Use VTK 5.10 which comes with Anaconda: Created by Arjan Geers, Modified by Noel Conlisk"""
import os
import vtk


def read_image(path):
    """Read VTK ImageData"""
    filename, extension = os.path.splitext(path)
    if extension == '.vtk':
        reader = vtk.vtkStructuredPointsReader()
    elif extension == '.vti':
        reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(path)
    reader.Update()
    return reader.GetOutput()


def read_mesh(path):
    """Read VTK-file"""
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(path)
    reader.Update()
    return reader.GetOutput()


def probe(image, mesh):
    """Sample image with mesh"""
    prober = vtk.vtkProbeFilter()
    prober.SetInput(mesh)
    prober.SetSource(image)
    prober.Update()
    return prober.GetOutput()


def write_mesh(mesh, path):
    """Write VTK UnstructuredGrid. Depending on the file extension either
    legacy VTK format or VTK XML format will be used."""
    filename, extension = os.path.splitext(path)
    if extension == '.vtk':
        writer = vtk.vtkUnstructuredGridWriter()
    elif extension == '.vtu':
        writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInput(mesh)
    writer.SetFileName(path)
    writer.Write()


image = read_image('SOF086_pet_data.vtk')
mesh = read_mesh('SOF086_2_3_edited_realigned.vtk')
output = probe(image, mesh)
write_mesh(output, 'SOF086_pet_values.vtu')
