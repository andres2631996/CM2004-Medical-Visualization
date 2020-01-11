import vtk
import sys

if __name__ == '__main__':
    # obj_src = vtk.vtkCylinderSource()
    filename =  sys.argv[1]
    obj_src = vtk.vtkOBJReader()
    obj_src.SetFileName(filename)

    # filter
    triangle = vtk.vtkTriangleFilter()
    triangle.SetInputConnection(obj_src.GetOutputPort())
    filter_ = vtk.vtkLoopSubdivisionFilter()
    filter_.SetInputConnection(triangle.GetOutputPort())
    filter_.SetNumberOfSubdivisions(3)
   
    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(filter_.GetOutputPort())

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # renderer
    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    ren.SetBackground(.2, .2, .2)

    ren_win = vtk.vtkRenderWindow()
    ren_in = vtk.vtkRenderWindowInteractor()

    in_style = vtk.vtkInteractorStyleTrackballCamera()
    ren_in.SetInteractorStyle(in_style)

    ren_win.AddRenderer(ren)
    ren_in.SetRenderWindow(ren_win)

    # enable stereo here
    
    ren_win.GetStereoCapableWindow()
    ren_win.StereoCapableWindowOn()
    ren_win.SetStereoRender(1)
    ren_win.SetStereoTypeToAnaglyph()

    ren_win.Render()
    ren_in.Start()

