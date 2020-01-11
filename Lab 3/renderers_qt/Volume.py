__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import os
import sys

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VolumeRender:
    def __init__(self, filename, frame):
        # step 1: load the data
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(filename)

        castFilter = vtk.vtkImageCast()
        castFilter.SetInputConnection(reader.GetOutputPort())
        castFilter.Update()

        vtk_volume = castFilter.GetOutput()

        # step 2: transfer function, colot luts
        funColor = vtk.vtkColorTransferFunction()
        
        # matlab parula stye lut
        maxval = 512
        step = maxval/8

        funColor.AddRGBPoint(0*step, .2422, .1504, .6603)
        funColor.AddRGBPoint(1*step, .2810, .3228, .9578)
        funColor.AddRGBPoint(2*step, .1786, .5289, .9682)
        funColor.AddRGBPoint(3*step, .0689, .6948, .8394)
        funColor.AddRGBPoint(4*step, .2161, .7843, .5923)
        funColor.AddRGBPoint(5*step, .6720, .7793, .2227)
        funColor.AddRGBPoint(6*step, .9970, .7659, .2199)
        funColor.AddRGBPoint(7*step, .9769, .9839, .0805)

        funAlpha = vtk.vtkPiecewiseFunction() # opacity
        funAlpha.AddPoint(0, 0.)
        funAlpha.AddPoint(256, .01)
        
        # step 3: set the volume properties
        volProp = vtk.vtkVolumeProperty()
        volProp.SetColor(0, funColor)
        volProp.SetScalarOpacity(0, funAlpha)
        volProp.SetInterpolationTypeToLinear()

        # step 4: setup the volume mapper
        volMap = vtk.vtkGPUVolumeRayCastMapper()
        volMap.SetInputData(vtk_volume)
        
        # step 5: setup the actor
        volAct = vtk.vtkVolume()
        volAct.SetMapper(volMap)
        volAct.SetProperty(volProp)

        # step 6: setup the camera and the renderer
        self.renderer = vtk.vtkRenderer()

        camera = self.renderer.MakeCamera()
        camera.SetViewUp(0., 0., -.1)
        camera.SetPosition(-500, 100, 100)

        self.renderer.SetBackground(0., 0., 0.) # so to black
        self.renderer.SetActiveCamera(camera)
        self.renderer.AddActor(volAct)

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




