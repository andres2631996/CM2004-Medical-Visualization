__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk
import sys
import os


if __name__ == '__main__':
    # 1 get data path from the first argument given

    filename = sys.argv[1]
    
    
    
    
    # 2 set up the source
    
    reader_src = vtk.vtkNIFTIImageReader()
    reader_src.SetFileName(filename)
    #scalar_range = output.GetScalarRange()
    
    # 3 set up the volume mapper
    
    vol_map = vtk.vtkGPUVolumeRayCastMapper()
    vol_map.SetInputConnection(reader_src.GetOutputPort())

    # 4 transfer functions for color and opacity
    #   for now: map value 0   -> black: (0., 0., 0.) 
    #                      512 -> black: (1., 1., 1.) 
    
    ctfun = vtk.vtkColorTransferFunction()
    ctfun.SetColorSpaceToRGB()
    ctfun.AddRGBPoint(0, 0., 0., 0.)
    ctfun.AddRGBPoint(512, 1., 1., 1.)

    # 5 assign also an alpha (opacity) gradient to the values
    #   for now: map value 0   -> 0. 
    #                      256 -> .01
    
    gtfun = vtk.vtkPiecewiseFunction()
    gtfun.AddPoint(0, 0.0)
    gtfun.AddPoint(256, 0.01)
    
    # 6 set up the volume properties with linear interpolation
    
    vol_prop = vtk.vtkVolumeProperty()
    vol_prop.SetColor(0, ctfun)
    vol_prop.SetScalarOpacity(0, gtfun)
    vol_prop.SetInterpolationTypeToLinear()

    # 7 set up the actor and connect it to the mapper
    
    vol_act = vtk.vtkVolume()
    vol_act.SetMapper(vol_map) 
    vol_act.SetProperty(vol_prop)

    # 8 set up the camera and the renderer
    #   for now: up-vector:       (0., 1., 0.)
    #            camera position: (-500, 100, 100)
    #            focal point:     (100, 100, 100)
    
    cam = vtk.vtkCamera()
    cam.SetViewUp(0., 1., 0.)
    cam.SetPosition(-500, 100, 100)
    cam.SetFocalPoint(100, 100, 100)

    # 9 set the color of the renderers background to black (0., 0., 0.)
    ren = vtk.vtkRenderer()
    ren.SetBackground(0. , 0. , 0.)

    # 10 set the renderers camera as active
    ren.SetActiveCamera(cam)

    # 11 add the volume actor to the renderer
    ren.AddActor(vol_act)

    # 12 create a render window
    renWin = vtk.vtkRenderWindow()

    # 13 add renderer to the render window
    renWin.AddRenderer(ren)

    # 14 create an interactor
    inter = vtk.vtkRenderWindowInteractor()

    # 15 connect interactor to the render window
    inter.SetRenderWindow(renWin)

    # 16 start displaying the render window
    renWin.Render()
    
    # 17 make the window interactive (start the interactor)
    inter.Start()