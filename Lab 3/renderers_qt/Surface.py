__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import os
import sys

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class SurfaceRender:
    def __init__(self, filename, frame):
        # step 1: load the data (source)
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(filename)

        # step 2: (filter) 
        castFilter = vtk.vtkImageCast()
        castFilter.SetInputConnection(reader.GetOutputPort())
        castFilter.SetOutputScalarTypeToUnsignedShort()

        # step 3: marching cubes (mapper)
        contour = vtk.vtkMarchingCubes()
        contour.SetInputConnection(castFilter.GetOutputPort())
        contour.ComputeNormalsOn()
        contour.ComputeGradientsOn()
        contour.SetValue(0, 100)
        
        conMapper =vtk.vtkPolyDataMapper()
        conMapper.SetInputConnection(contour.GetOutputPort())
       
        # step 4: (actor)
        # surAct = vtk.vtkLODActor()
        surAct = vtk.vtkActor()
        # surAct.SetNumberOfCloudPoints(100000)
        surAct.SetMapper(conMapper)

        # step 5: setup the camera and the renderer
        self.renderer = vtk.vtkRenderer()

        camera = self.renderer.MakeCamera()
        camera.SetViewUp(0., 0., -.1)
        camera.SetPosition(-500, 100, 100)

        self.renderer.SetBackground(0., 0., 0.) # so to black
        self.renderer.SetActiveCamera(camera)
        self.renderer.AddActor(surAct) 

        # step 8: window interaction (camera movement etc)
        self.interactor = QVTKRenderWindowInteractor(frame)
        interStyle = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(interStyle)

        self.interactor.Initialize()


if __name__ == '__main__':
    filename = sys.argv[1] # get filename from the first argument

    # step 7: create the render window
    winRender = vtk.vtkRenderWindow()
    
    winInter.SetRenderWindow(winRender)

    winRender.Render()
    winRender.AddRenderer(renderer)

    # step 9: set window size and start
    winRender.SetSize(1280, 720)
    winInter.Start()




