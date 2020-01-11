__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk


class VolumeRenderer:
    def __init__(self, source):
        # filter
        volOut = vtk.vtkOutlineFilter()
        volOut.SetInputConnection(source.GetOutputPort())

        outMap = vtk.vtkPolyDataMapper()
        outMap.SetInputConnection(volOut.GetOutputPort())

        outAct = vtk.vtkActor()
        outAct.SetMapper(outMap)

        # step 1: set up the volume mapper
        volMap = vtk.vtkGPUVolumeRayCastMapper()
        volMap.SetInputConnection(source.GetOutputPort())

        # step 2: transfer functions for color and opacity
        funColor = vtk.vtkColorTransferFunction()
        
        maxval = 512
        lut = self._get_lut()
        step = maxval/len(lut)

        # assign one color point for each grayscale step
        for idx, color in enumerate(lut):
            funColor.AddRGBPoint(idx*step, *color)

        # assign also an alpha (opacity) gradient to the values
        funAlpha = vtk.vtkPiecewiseFunction()
        funAlpha.AddPoint(0, 0.)
        funAlpha.AddPoint(256, .01)
        
        # step 3: set up the volume properties
        volProp = vtk.vtkVolumeProperty()
        volProp.SetColor(0, funColor)
        volProp.SetScalarOpacity(0, funAlpha)
        volProp.SetInterpolationTypeToLinear()

        # step 4: setup the actor
        volAct = vtk.vtkVolume()
        volAct.SetMapper(volMap)
        volAct.SetProperty(volProp)

        # step 5: setup the camera and the renderer
        self.renderer = vtk.vtkRenderer()

        camera = self.renderer.MakeCamera()
        camera.SetViewUp(0., 1., 0.)
        camera.SetPosition(-500, 100, 100)
        camera.SetFocalPoint(0, 100, 100)

        self.renderer.SetBackground(0., 0., 0.) # so to black
        self.renderer.SetActiveCamera(camera)
        self.renderer.AddActor(volAct)
        self.renderer.AddActor(outAct)

        # step 6: window interaction (camera movement etc)
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera()


    def _get_lut(self):
        # matlab parula stye lut
        lut = [(.2422, .1504, .6603),
               (.2810, .3228, .9578),
               (.1786, .5289, .9682),
               (.0689, .6948, .8394),
               (.2161, .7843, .5923),
               (.6720, .7793, .2227),
               (.9970, .7659, .2199),
               (.9769, .9839, .0805)]

        return lut
