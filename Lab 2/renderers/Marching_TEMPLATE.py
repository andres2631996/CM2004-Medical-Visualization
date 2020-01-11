__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk
from vtk.util.numpy_support import vtk_to_numpy

import sys
import numpy as np

from .cube_proxys import idx_to_coord_table, triangle_table



class MarchingRenderer:
    def __init__(self, source):
        source.Update()
        data = source.GetOutput()

        # here our marching cube algorithm is called
        poly_data = self.march_cubes(data)

        # mapper
        pol_map = vtk.vtkPolyDataMapper()
        pol_map.SetInputData(poly_data)

        surAct = vtk.vtkActor()
        surAct.SetMapper(pol_map)

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0., 0., 0.)
        self.renderer.AddActor(surAct)

        # 14 create an interactor
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera()

    def march_cubes(self, vtk_volume):
        volume =  self.vtkimg_to_numpy(vtk_volume)  # 1) convert the vtk_volume into a numpy array

        # 2) here, the numpy array is downsamped to make it quicker to process
        volume = volume[::5, ::5, ::5] 
        dimx, dimy, dimz = volume.shape # 3) get the dimensions of the numpy array

        iso_level =   140  # 4) set the iso-level, i.e. the threshold for the
                        #    volume, e.g. to 140 
        vtk_points = vtk.vtkPoints()   # 5) create a vtkPoints-structure like in the previous exercise 
        
        #vtk_points.InsertNextPoint(1.,0.,0.) # point Id: 0
        #vtk_points.InsertNextPoint(0.,0.,0.) # point Id: 1
        #vtk_points.InsertNextPoint(0.,1.,0.) # point Id: 2
        #vtk_points.InsertNextPoint(2.,1.,0.) # point Id: 3
        #vtk_points.InsertNextPoint(1.,1.,0.) # point Id: 4
        #vtk_points.InsertNextPoint(1.,2.,0.) # point Id: 5
        
        
        vtk_triangles = vtk.vtkCellArray() # 6) also create a cell structure as in exercise 2
        point_counter = 0
        vtk_poly_data = vtk.vtkPolyData() # 7) vtkPolyData, also known from exercise 2

        # 8) loop over all 3 dimensions (x, y, z) of the volume. Since we will access
        #    each index together with its next index, we only loop until dimx-1,
        #    dimy-1 and dimz-1.
        for x in range(dimx-1):
            for y in range(dimy-1):
                for z in range(dimz-1):
                    
                    # 9) extract a 2x2x2 subcube of the volume at the current (x, y, z)
                    subcube = volume[x:x+2,y:y+2,z:z+2]
            
            
                    # 10) get the index for the triangle_table, we imported from
                    #     cube_proxys.py. This index is returned by calling the member
                    #     function check_iso_level with the 2x2x2 subcube and the
                    #     iso_level.
                    
                    ind = self.check_iso_level(subcube,iso_level)

                    # 11) get the edge-indices (see figure 1) from the triangle_table
                    #     by using the previously calculated index, i.e.
                    #     triangle_table[idx]
                    
                    edge_ind = triangle_table[ind]

                    # 12) convert the list og edge-indices from the last step into a
                    #     list of coordinates by looking up idx_to_coord_table[idx] for
                    #     each element in the list. Store the result in a variable
                    #     called triangle_local
                    triangle_local = []
                    
                    for edge in edge_ind:
                        
                        coord = idx_to_coord_table[edge]
                        triangle_local.append(coord)

                    # 13) set the current origin to the current (x, y, z) plus 1
                    origin = [x+1, y+1, z+1]

                    # 14) for each point in triangle_local, and for each coordinate of
                    #     the points and the origin, calculate:
                    #           point = origin + triangle_point * 0.5
                    #     and store the results in a list, called triangle_global.
                    
                    triangle_global = []
                    
                    for point in triangle_local:
                        p = []
                        for i in range(len(origin)):
                            p.append(origin[i] + point[i] * 0.5)
                        
                        triangle_global.append(p)

                    # 15) append each point in triangle_global to vtk_points by valling
                    for point in triangle_global:
                        vtk_points.InsertNextPoint(point[0], point[1], point[2])

                    # 16) get a list of vtkTriangles by calling 
                    triangle_list = self.coords_to_vtktriangles(triangle_global, point_counter)

                    # 17) append every triangle from step 16) to vtk_triangles by using
                    for triangle in triangle_list:
                        
                        vtk_triangles.InsertNextCell(triangle)

                    # 18) increment the point counter by the number od triangle-points
                    point_counter += len(triangle_global)

        # 19) (Outside of the three x-, y-, z-loops): set the vtk_points and
        #     the vtk_triangles of ploy_data like we did in exercise 2
        
        vtk_poly_data.SetPoints(vtk_points)
        vtk_poly_data.SetPolys(vtk_triangles)

        return vtk_poly_data

    def vtkimg_to_numpy(self, vtkimg):
        dims = vtkimg.GetDimensions()
        sc = vtkimg.GetPointData().GetScalars()
        a = vtk_to_numpy(sc)
        a = a.reshape(*dims, order='F')

        return a

    def check_iso_level(self, vol_cube, iso_level):
        """
        get table index from 2x2x2 volume cube
        """
        table_idx = 0

        if vol_cube[0, 0, 0] < iso_level:
            table_idx |= 1
        if vol_cube[0, 1, 0] < iso_level:
            table_idx |= 2
        if vol_cube[1, 1, 0] < iso_level:
            table_idx |= 4
        if vol_cube[1, 0, 0] < iso_level:
            table_idx |= 8
        if vol_cube[0, 0, 1] < iso_level:
            table_idx |= 16
        if vol_cube[0, 1, 1] < iso_level:
            table_idx |= 32
        if vol_cube[1, 1, 1] < iso_level:
            table_idx |= 64
        if vol_cube[1, 0, 1] < iso_level:
            table_idx |= 128

        return table_idx

    def coords_to_vtktriangles(self, coords, point_counter):
        assert len(coords) % 3 == 0
      
        triang_list = list()

        for i in range(0, len(coords), 3):
            triangle = vtk.vtkTriangle()
            
            for j in range(3):
                triangle.GetPointIds().SetId(j, i + j + point_counter)
            triang_list.append(triangle)

        return triang_list


