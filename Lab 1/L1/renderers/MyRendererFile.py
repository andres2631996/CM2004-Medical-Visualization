__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk


class myRenderer:
    def __init__(self, source):
        out_source = source.GetOutputPort()
        
        # Mapper
        vol_map = vtk.vtkGPUVolumeRayCastMapper()
        vol_map.SetInputConnection(out_source)
        
        # Color Transfer Function
        ctfun = vtk.vtkColorTransferFunction()
        ctfun.SetColorSpaceToRGB()
        ctfun.AddRGBPoint(0, 0., 0., 0.)
        ctfun.AddRGBPoint(512, 1., 1., 1.)
        
        # Opacity Tranfer Function
        gtfun = vtk.vtkPiecewiseFunction()
        gtfun.AddPoint(0, 0.0)
        gtfun.AddPoint(256, 0.01)
        
        # Volume property
        vol_prop = vtk.vtkVolumeProperty()
        vol_prop.SetColor(0, ctfun)
        vol_prop.SetScalarOpacity(0, gtfun)
        vol_prop.SetInterpolationTypeToLinear()
        
        # Actor
        vol_act = vtk.vtkVolume()
        vol_act.SetMapper(vol_map) 
        vol_act.SetProperty(vol_prop)
        
        
        # Camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(-500, 100, 100)
        cam.SetFocalPoint(100, 100, 100)

        self.renderer = vtk.vtkRenderer() # ...; NOTE: type must be vtk.vtkRenderer 
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera() # ...; NOTE: type must be vtk.vtkInteractorStyle
        
        self.renderer.SetBackground(0. , 0., 0.)
        self.renderer.SetActiveCamera(cam)
        self.renderer.AddActor(vol_act)
        
        
        # Interactor style
        
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)


    def MouseMoveCallback(self, obj, event):
        
        self.inter_style.OnMouseMove()
    
    
    
class myNewRenderer:
    def __init__(self, source):
        out_source = source.GetOutputPort()
        
        # Mapper
        vol_map = vtk.vtkGPUVolumeRayCastMapper()
        vol_map.SetInputConnection(out_source)
        
        # Color Transfer Function
        ctfun = vtk.vtkColorTransferFunction()
        ctfun.SetColorSpaceToRGB()
        ctfun.AddRGBPoint(0, 0., 0., 0.)
        ctfun.AddRGBPoint(512, 1., 0., 1.)
        
        # Opacity Tranfer Function
        gtfun = vtk.vtkPiecewiseFunction()
        gtfun.AddPoint(0, 0.0)
        gtfun.AddPoint(256, 0.05)
        
        # Volume property
        vol_prop = vtk.vtkVolumeProperty()
        vol_prop.SetColor(0, ctfun)
        vol_prop.SetScalarOpacity(0, gtfun)
        vol_prop.SetInterpolationTypeToLinear()
        
        # Actor
        vol_act = vtk.vtkVolume()
        vol_act.SetMapper(vol_map) 
        vol_act.SetProperty(vol_prop)
        
        
        # Camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(-500, 200, 300)
        cam.SetFocalPoint(250, 100, 250)

        self.renderer = vtk.vtkRenderer() # ...; NOTE: type must be vtk.vtkRenderer 
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera() # ...; NOTE: type must be vtk.vtkInteractorStyle
        
        self.renderer.SetBackground(0. , 0., 0.)
        self.renderer.SetActiveCamera(cam)
        self.renderer.AddActor(vol_act)
        
        
        # Interactor style
        
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)


    def MouseMoveCallback(self, obj, event):
        
        self.inter_style.OnMouseMove()
    
    
