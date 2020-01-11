# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 16:43:40 2019

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
#from data_loading import data_loader


class SurfaceRendering:
    
    def __init__(self, arrays, readers, lut_key, animation, animation_steps, light_int, index):
        
        """
        Perform surface rendering on the given arrays and readers 
        (as long as they have some segmentation mask available).
        Allow for LUT choosing, animation, number of animation steps 
        and ambient light intensity
        
        Index:
            0: for speed
            1: for PC-MRA
        
        """
        
        self.arrays = arrays
        self.readers = readers
        self.lut_key = lut_key
        self.animation = None
        self.animation_steps = animation_steps
        self.index = index
        self.light_int = light_int
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera()
        
    def array2nii(self, array, desired_filename):
    
        """
        Convert array into .nii file
        Desired filename must be .nii.gz
        Return the .nii reader in VTK
        
        """
        
        img = nib.Nifti1Image(array,np.eye(4))
            
        img.header.get_xyzt_units()
        img.to_filename(desired_filename)  # Save as NiBabel file
        
        # Produce a valid VTK reader from a .nii image
        
        
        nii_reader = vtk.vtkNIFTIImageReader()
        nii_reader.SetFileName(desired_filename)
        nii_reader.Update()
        
        return nii_reader
    
        
    def extract_segmentations(self):
        
        """
        Extract segmentations on speed and PC-MRA images. 
        Save them as .nii readers
        
        """
        segm_speed = np.zeros(self.arrays[0].shape) # For speed
        segm_pcmra = self.arrays[3]*self.arrays[1] # For PC-MRA
        
        # Analyze speed throughout time
        for i in range(self.arrays[0].shape[-1]):
            segm_speed[:,:,:,i] = self.arrays[3][30:-30,:,:]*self.arrays[0][:,:,:,i]
        
        segmentation_arrays = [segm_speed, segm_pcmra]
        
        speed_segm_reader = self.array2nii(segm_speed,os.getcwd() + 'segm_speed.nii.gz')
        pcmra_segm_reader = self.array2nii(segm_pcmra,os.getcwd() + 'segm_pcmra.nii.gz')
        
        segmentation_readers = [speed_segm_reader, pcmra_segm_reader]
        
        return segmentation_arrays, segmentation_readers
    
    
    
    def lut_selection(self):
    
        """
        Allow user choose the LUT for visualization. Possible keys:
            
            'bw': black & white
            'rainbow': rainbow
            'rb': red-blue
            'br': blue-red
        
        
        """
        lut = vtk.vtkLookupTable()
        
        if self.lut_key == 'bw':
            
            lut.SetHueRange(0, 0)
            lut.SetSaturationRange(0, 0)
            lut.SetValueRange(0.2, 1.0)
            
        elif self.lut_key == 'rainbow':
            
            lut.SetHueRange(0, 1)
            lut.SetSaturationRange(1, 1)
            
        elif self.lut_key == 'rb':
            
            lut.SetHueRange(0.0, 0.667)
            
        elif self.lut_key == 'br':
            
            lut.SetHueRange(0.667, 0.0)
        
        else:
            print('Wrong key. Please type a proper key')
        
        return lut
    
    
    def execute(self):
        
        """
        Main pipeline to be executed for surface rendering
        
        
        """
        
        segm_arrays, segm_readers = self.extract_segmentations()
        
        source = segm_readers[self.index]
        
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
        poly_map.SetLookupTable(self.lut_selection())
        
        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(poly_map) 
        
        radius = 500
        # Camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(radius, radius, radius)
        cam.SetFocalPoint(0, 0, 0)
        
        renderer = vtk.vtkRenderer() 
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        
        renderer.SetBackground(0. , 0., 0.)
        renderer.SetActiveCamera(cam)
        #renderer.AddActor(actor)
        renderer.SetAmbient(self.light_int, self.light_int, self.light_int)
        
#        renWin = vtk.vtkRenderWindow()
#        renWin.AddRenderer(renderer)
#        
#        # Set stereo
#        renWin.GetStereoCapableWindow()
#        renWin.StereoCapableWindowOn()
#        renWin.SetStereoRender(1)
#        renWin.SetStereoTypeToAnaglyph()
#        
#        iren = vtk.vtkRenderWindowInteractor()
#        iren.SetRenderWindow(renWin)
#        
#        iren.Initialize()
#        
#        if self.animation is not None or self.animation != 'No' or self.animation != 'no' or self.animation != 'n':
#            
#            cb = vtkTimerCallback(self.animation_steps, iren, radius, cam)
#            
#            iren.AddObserver('TimerEvent', cb.execute)
#            cb.timerId = iren.CreateRepeatingTimer(500)
#        
#        # start the interaction and timer
#        renWin.Render()
#        iren.Start()
#        print('Completed Surface Rendering!')
        
        return renderer, actor, cam
        
        
    def MouseMoveCallback(self, obj, event):
        
        self.inter_style.OnMouseMove()
        
        
# Class for animations
class vtkTimerCallback():
    def __init__(self, steps, iren, rad, cam):
        self.timer_count = 0
        self.steps = steps
        self.iren = iren
        self.timerId = None
        self.radius = rad
        self.camera = cam
        

    def execute(self, obj, event):
        step = 0
        while step < self.steps:
            self.camera.SetPosition(self.radius*np.cos(2*np.pi*self.timer_count /(self.steps)),
                                      self.radius, self.radius*np.sin(2*np.pi*self.timer_count /(self.steps)))
            iren = obj
            iren.GetRenderWindow().Render()
            self.timer_count += 1
            step += 1
        if self.timerId:
            iren.DestroyTimer(self.timerId)
            
            
#filenames = ['4DPC_M_FFE.mat' , '4DPC_vel_AP.mat' , '4DPC_vel_FH.mat'
#             , '4DPC_vel_RL.mat' , 'carotid_segm.mhd' , '20121204_seg_final_cleaned.mat' , 'T1.mhd' , 'T1_Gd.mhd']
#loading = data_loader(filenames)
#vtk_files, array_files, readers = loading.process()
#
#
#steps = 500
#surface_renderer = SurfaceRendering(array_files, readers, 'rainbow','y',steps,1,1)
#_,_,_ = surface_renderer.execute()

