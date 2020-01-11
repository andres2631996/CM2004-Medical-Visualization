# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 15:46:01 2019

@author: andre
"""

import scipy.io as sio
import numpy as np
import SimpleITK as sitk
import vtk
import vtk.util.numpy_support 
import sys
import nibabel as nib
import os

#from data_loading import data_loader



class MultiPlanarReconstruction():
        
    """
    Get Multiplanar Reconstructions 
    
    """
    
    
    def __init__(self, files, arrays, readers, frame,sl,orient,index):
        
    
        """
        Compute glyph visualization given data files, time frame, orientation,
        desired shape and slice
        
        """
        
        self.files = files
        self.arrays = arrays
        self.readers = readers
        self.frame = frame
        self.orient = orient
        self.slice = sl
        self.index = index
        
        
    def array2niiFrame(self, file4d, desired_filename):

        """
        Convert speed array frame into .nii file
        Desired filename must be .nii.gz
        Return the .nii reader in VTK
        
        """
        
        img = sitk.ReadImage(file4d)

        array = sitk.GetArrayFromImage(img)
        final_array = np.zeros((array.shape[2], array.shape[2], array.shape[1], array.shape[0]))
        swap = np.swapaxes(array, 0, -1)
        final_swap = np.swapaxes(swap, 1, 2)
        reswap = np.swapaxes(final_swap, 0, 1)
        
        if self.index == 0:
            # For speed processing
            final_array[:,30:-30,:,:] = reswap
            final = final_array[:,:,:, self.frame]
        else:
            final = reswap
        
    
        img = nib.Nifti1Image(final,np.eye(4))
            
        img.header.get_xyzt_units()
        img.to_filename(desired_filename)  # Save as NiBabel file
        
        # Produce a valid VTK reader from a .nii image
        
        
        nii_reader = vtk.vtkNIFTIImageReader()
        nii_reader.SetFileName(desired_filename)
        nii_reader.Update()
        
        return nii_reader
    
    
    def execute(self):
        
        
        # Slice data
        if self.index == 0:
            frame_reader = self.array2niiFrame('speed.nii.gz', 'speedFrame' + str(self.frame) + '.nii.gz')
        else:
            frame_reader = self.readers[self.index]
        
        frame_reader.Update()

        (xMin, xMax, yMin, yMax, zMin, zMax) = frame_reader.GetExecutive().GetWholeExtent(
                                                    frame_reader.GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = frame_reader.GetOutput().GetSpacing()
        (x0, y0, z0) = frame_reader.GetOutput().GetOrigin()

        center = [x0 + xSpacing * 0.5 * (xMin + xMax),
                       y0 + ySpacing * 0.5 * (yMin + yMax),
                       y0 + zSpacing * 0.5 * (yMin + zMax)]
        
        extent = [xMin, xMax, yMin, yMax, zMin, zMax]
        spacing = [xSpacing, ySpacing, zSpacing]
        origin = [x0, y0, z0]
        
        # Matrices for axial, coronal, sagittal view orientations
        orie_mat = self._get_orie_mat(center, extent, spacing, origin)
        
        reslice = vtk.vtkImageReslice()
        reslice.SetInputConnection(frame_reader.GetOutputPort())
        reslice.SetOutputDimensionality(2)
        reslice.SetResliceAxes(orie_mat)
        reslice.SetInterpolationModeToLinear()

        # Create a greyscale lookup table
        table = vtk.vtkLookupTable()
        table.SetRange(0, 1000) # image intensity range
        table.SetValueRange(0.0, 1.0) # from black to white
        table.SetSaturationRange(0.0, 0.0) # no color saturation
        table.SetRampToLinear()
        table.Build()

        # Map the image through the lookup table
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(table)
        color.SetInputConnection(reslice.GetOutputPort())

        # Display the image
        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(color.GetOutputPort())
        actor.SetPosition(-center[0], -center[1], -center[2])
        
        ren = vtk.vtkRenderer()
        ren.AddActor(actor)
        
        ren.ResetCamera()
        
#        renwin = vtk.vtkRenderWindow()
#        renwin.AddRenderer(ren)
#        
#        # Set stereo
#        renwin.GetStereoCapableWindow()
#        renwin.StereoCapableWindowOn()
#        renwin.SetStereoRender(1)
#        renwin.SetStereoTypeToCrystalEyes()
#        
#        
#        iren = vtk.vtkRenderWindowInteractor()
#        iren.SetRenderWindow(renwin)
#        renwin.Render()
#        iren.Initialize()
#        iren.Start()
        
        return ren
        
            
    def _get_orie_mat(self, center, extent, spacing, origin):
        trans_mat = vtk.vtkMatrix4x4()
        

        if self.orient == 'axial' or self.orient == 'Axial':
            trans_mat.DeepCopy((1, 0, 0, center[0],
                            0, 1, 0, center[1],
                            0, 0, 1, origin[2] + spacing[2]*self.slice ,
                            0, 0, 0, 1))
            
        elif self.orient == 'coronal' or self.orient == 'Coronal':
            trans_mat.DeepCopy((1, 0, 0, origin[0] + spacing[0]*self.slice,
                              0, 0, 1, center[1],
                              0,-1, 0, center[2],
                              0, 0, 0, 1))
            
        elif self.orient == 'sagittal' or self.orient == 'Sagittal':
            trans_mat.DeepCopy((0, 0,-1, center[0],
                               1, 0, 0, origin[1] + spacing[1]*self.slice,
                               0,-1, 0, center[2],
                               0, 0, 0, 1))
        else:
            raise ValueError

        return trans_mat



#frame = 32
#sl = 0
#orient = 'axial'
#index = 1
#filenames = ['4DPC_M_FFE.mat' , '4DPC_vel_AP.mat' , '4DPC_vel_FH.mat'
#             , '4DPC_vel_RL.mat' , 'carotid_segm.mhd' , '20121204_seg_final_cleaned.mat' , 'T1.mhd' , 'T1_Gd.mhd']
#
#loading = data_loader(filenames)
#vtk_files, array_files, readers = loading.process()
#
#glyph = MultiPlanarReconstruction(filenames,array_files, readers, frame, sl, orient, index)
#_ = glyph.execute()     