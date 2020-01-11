__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk
import sys

def my_callback(obj, event):
    
    # Callback to be evaluated every time interaction happens
    
    global plane
    obj.GetPlane(plane)
    print(obj, event)
    
    
    
class MyCallback:
    def __init__(self,pl):
        self.plane = pl
    
    def __call__(self, obj, event):
        obj.GetPlane(self.plane)
        print(obj, event)
        
        

if __name__ == '__main__':
    # 1 get data path from the first argument
    filename = sys.argv[1] # '../data/head_self_t1.nii.gz' 
    
    # Set up plane object
    global plane
    plane = vtk.vtkPlane()
    
    # 2 set up the source
    reader_src = vtk.vtkNIFTIImageReader()
    reader_src.SetFileName(filename)

    # 3 set up the volume mapper
    vol_map = vtk.vtkGPUVolumeRayCastMapper()
    vol_map.SetInputConnection(reader_src.GetOutputPort())
    vol_map.AddClippingPlane(plane)

    # 4 transfer functions for color and opacity
    funColor = vtk.vtkColorTransferFunction()
    funColor.AddRGBPoint(0, 0., 0., 0.)
    funColor.AddRGBPoint(256, 1., 1., 1.)

    # 5 assign also an alpha (opacity) gradient to the values
    funAlpha = vtk.vtkPiecewiseFunction()
    funAlpha.AddPoint(0, 0.)
    funAlpha.AddPoint(256, .1)
    
    # 6 set up the volume properties
    volProp = vtk.vtkVolumeProperty()
    volProp.SetColor(0, funColor)
    volProp.SetScalarOpacity(0, funAlpha)
    volProp.SetInterpolationTypeToLinear()

    # 7 set up the actor
    volAct = vtk.vtkVolume()
    volAct.SetMapper(vol_map)
    volAct.SetProperty(volProp)

    # 8 set up the camera and the renderer
    renderer = vtk.vtkRenderer()

    camera = vtk.vtkCamera()
    camera.SetViewUp(0., 1., 0.)
    camera.SetPosition(-500, 100, 100)
    camera.SetFocalPoint(100, 100, 100)

    # 9 set the color of the renderers background to black (0., 0., 0.)
    renderer.SetBackground(0., 0., 0.)

    # 10 set the renderers canera as active
    renderer.SetActiveCamera(camera)

    # 11 add the volume actor to the renderer
    renderer.AddActor(volAct)

    # 12 create a render window
    ren_win = vtk.vtkRenderWindow()

    # 13 add renderer to the render window
    ren_win.AddRenderer(renderer)

    # 14 create an interactor
    iren = vtk.vtkRenderWindowInteractor()
    
    # Callable instance for plane widget
    callback_instance = MyCallback(plane)
    
    
    # Insert plane widget
    plane_widget = vtk.vtkImplicitPlaneWidget()
    plane_widget.DrawPlaneOff()
    plane_widget.SetInteractor(iren)
    plane_widget.PlaceWidget()
    plane_widget.AddObserver("InteractionEvent", callback_instance)
    
    # 15 connect interactor to the render window
    iren.SetRenderWindow(ren_win)

    # 16 start displaying the render window
    ren_win.Render()

    # 17 make the window interactive
    iren.Start()

