__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk


class surface_renderer:
    def __init__(self, source):
        
        out_source = source.GetOutputPort()
        obj = source.GetOutput()
        
        
        # Marching Cubes
        march = vtk.vtkMarchingCubes()
        march.ComputeNormalsOn()
        march.ComputeGradientsOn()
        march.SetValue(0,100)
        march.SetInputData(obj)
        
        # Filter
        cast_filter = vtk.vtkImageCast()
        cast_filter.SetOutputScalarTypeToUnsignedShort()
        cast_filter.SetInputConnection(out_source)
        cast_filter.Update()
        
        
        
        # Mapper
        poly_map = vtk.vtkPolyDataMapper()
        poly_map.SetInputConnection(march.GetOutputPort())
        
        
        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(poly_map) 
        
        
        # Camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(-500, 100, 100)
        cam.SetFocalPoint(100, 100, 100)
    
        self.renderer = vtk.vtkRenderer() # ...; NOTE: type must be vtk.vtkRenderer 
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera() # ...; NOTE: type must be vtk.vtkInteractorStyle
        
        self.renderer.SetBackground(0. , 0., 0.)
        self.renderer.SetActiveCamera(cam)
        self.renderer.AddActor(actor)
        
        
        # Interactor style
        
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)


    def MouseMoveCallback(self, obj, event):
        
        self.inter_style.OnMouseMove()


class triangle_renderer:
    def __init__(self):
        
        points = vtk.vtkPoints()
        points.InsertNextPoint(3.,0.,0.) # point Id: 0
        points.InsertNextPoint(0.,0.,0.) # point Id: 1
        points.InsertNextPoint(0.,3.,0.) # point Id: 2
        points.InsertNextPoint(4.,2.,0.) # point Id: 3
        points.InsertNextPoint(2.,2.,0.) # point Id: 4
        points.InsertNextPoint(2.,4.,0.) # point Id: 5
        
        triangle1 = vtk.vtkTriangle()
        triangle1.GetPointIds().SetId(0,0)
        triangle1.GetPointIds().SetId(1,1)
        triangle1.GetPointIds().SetId(2,2)
        
        triangle2 = vtk.vtkTriangle()
        triangle2.GetPointIds().SetId(0,3)
        triangle2.GetPointIds().SetId(1,4)
        triangle2.GetPointIds().SetId(2,5)
        
        triangles = vtk.vtkCellArray()
        triangles.InsertNextCell(triangle1)
        triangles.InsertNextCell(triangle2)
        
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetPolys(triangles)
        
        
        
        
        # Mapper
        poly_map = vtk.vtkPolyDataMapper()
        poly_map.SetInputData(poly_data)
        
        
        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(poly_map) 
        
        
        # Camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(5, 5, 5)
        cam.SetFocalPoint(0, 0, 0)
    
        self.renderer = vtk.vtkRenderer() # ...; NOTE: type must be vtk.vtkRenderer 
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera() # ...; NOTE: type must be vtk.vtkInteractorStyle
        
        self.renderer.SetBackground(0. , 0., 0.)
        self.renderer.SetActiveCamera(cam)
        self.renderer.AddActor(actor)
        
        
        # Interactor style
        
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)


    def MouseMoveCallback(self, obj, event):
        
        self.inter_style.OnMouseMove()