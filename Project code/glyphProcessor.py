# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 19:05:05 2019

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



#frame = 32
#sl = 15
#
#
#filenames = ['4DPC_M_FFE.mat' , '4DPC_vel_AP.mat' , '4DPC_vel_FH.mat'
#             , '4DPC_vel_RL.mat' , 'carotid_segm.mhd' , '20121204_seg_final_cleaned.mat' , 'T1.mhd' , 'T1_Gd.mhd']
#
#loading = data_loader(filenames)
#vtk_files, array_files, readers = loading.process()


class glyphProcessing:
    
    def __init__(self,files, arrays, frame,sl,shape):
        
        """
        Compute glyph visualization given data files, time frame, orientation,
        desired shape and slice
        
        
        """
        
        
        self.files = files
        self.arrays = arrays
        self.frame = frame
        self.shape = shape
        self.slice = sl
        
    
    
    def execute(self):
        
        # Load data
        
        ap = sio.loadmat(self.files[1][0:-4]).get('Data')
        fh = sio.loadmat(self.files[2][0:-4]).get('Data')
        rl = sio.loadmat(self.files[3][0:-4]).get('Data')
        
        for i in range(ap.shape[-1]):
        
            ap[:,:,:,i] = ap[:,:,:,i]* self.arrays[3]
            fh[:,:,:,i] = fh[:,:,:,i]* self.arrays[3]
            rl[:,:,:,i] = rl[:,:,:,i]* self.arrays[3]
        
        
        
        # Prepare data for orientation
    
        
        if self.slice > ap.shape[2]:
            self.slice = -1 # Assign last axial slice
        ap_static = ap[:,:,self.slice,self.frame]
        fh_static = fh[:,:,self.slice,self.frame]
        rl_static = rl[:,:,self.slice,self.frame]
        
        # Coordinates
#        coord_x, coord_y = np.meshgrid(np.arange(fh_static.shape[0]),np.arange(rl_static.shape[1]))
#            
#        # Coordinate matrix
#        coord = np.transpose(np.array([coord_x.flatten(),
#                coord_y.flatten()]))
        
        # Indexes for carotid arteries
        non_zero = np.where(ap_static != 0)
        non_zero = list(non_zero)        
        
        # Coordinates
        coord = np.array([non_zero[1],
                          non_zero[0]])
        #coord = np.transpose(coord)
        
        # Vector matrix
        orientations = np.array([ap_static[coord[1], coord[0]].flatten(),
                                 fh_static[coord[1], coord[0]].flatten(),
                                 rl_static[coord[1], coord[0]].flatten()])
    
        orientations = orientations/3
        
        # Color matrix
        colors = 255*(orientations + 1)/2
    
    
    
        # VTK Points, Vectors and Colors
        
        points = vtk.vtkPoints()
        color_def = vtk.vtkUnsignedCharArray()
        color_def.SetNumberOfComponents(3)
        color_def.SetNumberOfTuples(coord.shape[1])
        
        pointNormalsArray = vtk.vtkDoubleArray()
        pointNormalsArray.SetNumberOfComponents(3)
        pointNormalsArray.SetNumberOfTuples(coord.shape[1])
        
        for i in range(coord.shape[1]):
            points.InsertNextPoint(np.concatenate((coord[:,i], [self.slice])))
            color_def.InsertTuple3(i, colors[0,i], colors[1,i], colors[2,i])
            pointNormalsArray.SetTuple(i, list(orientations[:,i]))
        
            
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.GetPointData().SetScalars(color_def)
        polydata.GetPointData().SetNormals(pointNormalsArray)
        
        # Shapes
        if self.shape == 'arrow' or self.shape == 'Arrow':
            source = vtk.vtkArrowSource()
            source.SetShaftRadius(0.1)
        elif self.shape == 'cube' or self.shape == 'Cube':
            source = vtk.vtkCubeSource()
            source.SetXLength(0.5)
            source.SetYLength(0.5)
            source.SetZLength(0.5)
        elif self.shape == 'sphere' or self.shape == 'Sphere':
            source = vtk.vtkSphereSource()
            source.SetRadius(0.5)
        elif self.shape == 'cone' or self.shape == 'Cone':
            source = vtk.vtkConeSource()
            source.SetResolution(1)
        else:
            print('Wrong shape. Please introduce "arrow", "cylinder" or "cone"')
        
        source.Update()
        
        
        # VTK Glyph
        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(source.GetOutputPort())
        glyph.SetColorModeToColorByScalar()
        glyph.SetVectorModeToUseNormal()
        glyph.ScalingOff()
        glyph.Update()
        
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        #pos = actor.GetPosition()
        ren = vtk.vtkRenderer()
        ren.AddActor(actor) # Glyph actor
        
        slice_actor, center = self.sliceProcessor()
        actor.SetPosition(-center[0], -center[1], -center[2])
        
        ren.AddActor(slice_actor) # Slice actor
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
        final_array[:,30:-30,:,:] = reswap
        
        final = final_array[:,:,:, self.frame]
        
        img = nib.Nifti1Image(final,np.eye(4))
            
        img.header.get_xyzt_units()
        img.to_filename(desired_filename)  # Save as NiBabel file
        
        # Produce a valid VTK reader from a .nii image
        
        
        nii_reader = vtk.vtkNIFTIImageReader()
        nii_reader.SetFileName(desired_filename)
        nii_reader.Update()
        
        return nii_reader
    
    

    def sliceProcessor(self):
        
        """
        Get Multiplanar Reconstructions to show over the glyphs.
        Take as input the position of the glyph actor
        
        """
        
        # Slice data
        
        frame_reader = self.array2niiFrame('speed.nii.gz', 'speedFrame' + str(self.frame) + '.nii.gz')
        
        
        frame_reader.Update()

        (xMin, xMax, yMin, yMax, zMin, zMax) = frame_reader.GetExecutive().GetWholeExtent(
                                                    frame_reader.GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = frame_reader.GetOutput().GetSpacing()
        (x0, y0, z0) = frame_reader.GetOutput().GetOrigin()

        center = [xSpacing * 0.5 *xMax,
                       ySpacing * 0.5 * yMax,
                       zSpacing * 0.5 * zMax]
        

        # Matrices for axial, coronal, sagittal, oblique view orientations
        orie_mat = self._get_orie_mat(center)
        
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
        
        #actor.SetPosition(desired_position)
        
        return actor, center
        
            
    def _get_orie_mat(self, center):
        trans_mat = vtk.vtkMatrix4x4()

        trans_mat.DeepCopy((1, 0, 0, center[0],
                        0, 1, 0, center[1],
                        0, 0, 1, self.slice ,
                        0, 0, 0, 1))
        
    

        return trans_mat          
            
            



#glyph = glyphProcessing(filenames,array_files, frame, sl, 'arrow')
#_ = glyph.execute()