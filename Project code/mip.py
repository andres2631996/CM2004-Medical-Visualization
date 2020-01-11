# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 17:56:29 2019

@author: andre
"""
# Import necessary libraries
import scipy.io as sio
import numpy as np
import SimpleITK as sitk
import vtk
import vtk.util.numpy_support 
import sys
import nibabel as nib
import os

from data_loading import data_loader

class MIP:
    
    def __init__(self,arrays,readers,orientation,light_int, index):
        
        """
        Complete Maximum Intensity Projection (MIP)
        
        Inputs: data arrays, data readers, orientation (axial, sagittal, coronal, oblique)
        animation, number of animation steps and index of desired dataset
        
        
            0: speed
            1: PC-MRA
            2: carotid segmentation
            3: auxiliary segmentation
            4: T1 without contrast
            5: T1 with contrast
        
        """
        
        self.arrays = arrays
        self.readers = readers
        self.orientation = orientation
        self.index = index
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera()
        self.light_int = light_int
        
    def execute(self):
     
        
        # Do Maximum Intensity Projection (MIP)
        
        # Compute Volume Center
        (xMin, xMax, yMin, yMax, zMin, zMax) = self.readers[self.index].GetExecutive().GetWholeExtent(self.readers[self.index].GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = self.readers[self.index].GetOutput().GetSpacing()
        (x0, y0, z0) = self.readers[self.index].GetOutput().GetOrigin()
        
        
        center = [x0 + xSpacing * 0.5 * (xMin + xMax),
          y0 + ySpacing * 0.5 * (yMin + yMax),
          z0 + zSpacing * 0.5 * (zMin + zMax)]
        
        # Matrices for axial, coronal, sagittal, oblique view orientations
        axial = vtk.vtkPlane()
        axial.SetOrigin(center[0],center[1],center[2])
        axial.SetNormal(0., 0., 1.)

        
        coronal = vtk.vtkPlane()
        coronal.SetOrigin(center[0],center[1],center[2])
        coronal.SetNormal(1., 0., 0.)

        
        sagittal = vtk.vtkPlane()
        sagittal.SetOrigin(center[0],center[1],center[2])
        sagittal.SetNormal(0., 1., 0.)

        
        
        
        reslice = vtk.vtkImageResliceMapper()
        reslice.SetInputConnection(self.readers[self.index].GetOutputPort())

        
        if self.orientation == 'axial' or self.orientation == 'Axial':
            reslice.SetSlicePlane(axial)
            
        elif self.orientation == 'coronal' or self.orientation == 'Coronal':
            reslice.SetSlicePlane(coronal)
            
        elif self.orientation == 'sagittal' or self.orientation == 'Sagittal':
            reslice.SetSlicePlane(sagittal)
        

        else:
            print('Wrong orientation. Please type "axial", "coronal" or "sagittal"')
            
        #reslice.SetInterpolationModeToLinear()
        reslice.SetSlabThickness(20)
        reslice.SetSlabTypeToMax()
        
        radius = 500
        
        # Set camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(radius, radius, radius)
        cam.SetFocalPoint(0., 0., 0.)
        
        imageSlice = vtk.vtkImageSlice()
        imageSlice.SetMapper(reslice);
        imageSlice.GetProperty().SetInterpolationTypeToNearest()
        
        light = vtk.vtkLight()
        light.SetIntensity(self.light_int)
        
        renderer = vtk.vtkRenderer()
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        renderer.AddViewProp(imageSlice)
        renderer.AddLight(light)
        renderer.ResetCamera()
        
        
#        window = vtk.vtkRenderWindow()
#        window.AddRenderer(renderer)
#        
#        # Set stereo
#        window.GetStereoCapableWindow()
#        window.StereoCapableWindowOn()
#        window.SetStereoRender(1)
#        window.SetStereoTypeToAnaglyph()
#        
#        iren = vtk.vtkRenderWindowInteractor()
#        iren.SetRenderWindow(window)
#
#        
#        renderer.Render()
#        iren.Start()
#        print('Completed MIP!')
        
        return renderer
        
        
    def MouseMoveCallback(self, obj, event):
    
        self.inter_style.OnMouseMove()    
            
            
        
#filenames = ['4DPC_M_FFE.mat' , '4DPC_vel_AP.mat' , '4DPC_vel_FH.mat'
#             , '4DPC_vel_RL.mat' , 'carotid_segm.mhd' , '20121204_seg_final_cleaned.mat' , 'T1.mhd' , 'T1_Gd.mhd']
#loading = data_loader(filenames)
#vtk_files, array_files, readers = loading.process()
#        
#mip = MIP(array_files, readers, 'coronal',1, 0)
#ren = mip.execute()
            
