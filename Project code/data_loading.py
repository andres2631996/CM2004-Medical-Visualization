# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 11:00:42 2019

@author: Usuario
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


# Generalize in one class for data importation

class data_loader:
    
    """
    Get 4D flow data, segmentation data and T1 (without/with contrast) data  
    
    """
    
    def __init__(self,filenames):
        self.filenames = filenames
        #speed_vtk, pcmra_vtk, carotid_segm_vtk, aux_segm_vtk, t1_without_vtk, t1_with_vtk = self.process()
        
        
        #self.arglen = len(sys.argv) 
        #self.key = sys.argv[1]
        
    def mat2nii(self,file,desired_filename):
        
        # Convert .mat into .nii file. The desired filename should include .nii.gz
        # Return the data array from the .mat file
        
        mat = sio.loadmat(file[0:-4]).get('Data')
        img = nib.Nifti1Image(mat,np.eye(4))
        
        img.header.get_xyzt_units()
        img.to_filename(os.path.join(desired_filename))  # Save as NiBabel file
        
        # Produce a valid VTK reader from a .nii image
        
        
        nii_reader = vtk.vtkNIFTIImageReader()
        nii_reader.SetFileName(desired_filename)
        nii_reader.Update()
        
        return mat, nii_reader
        
    
    def mhd_reader(self,file):
        
        # Import .mhd file
        
        itk_img = sitk.ReadImage(file)
        mhd = sitk.GetArrayFromImage(itk_img)
        #mhd_vtk = vtk.util.numpy_support.numpy_to_vtk(mhd.ravel())
        
        
        mhd_reader = vtk.vtkMetaImageReader()
        mhd_reader.SetFileName(file)
        mhd_reader.Update()
        
        return mhd, mhd_reader
    
    def speed_pcmra(self,ffe,ap,fh,rl):
        
        # Compute speed and PC-MRA info
        
        speed = np.sqrt(ap**2 + fh**2 + rl**2)
        tfs = np.arange(start = 0, stop = np.shape(speed)[3]).astype(int)
        pcmra = np.mean(fh[:,:,:,tfs]*ffe[:,:,:,tfs], axis = 3)
        
        speed_final = speed[30:-30,:,:,:]
        
        speed_norm = 256.0*(speed_final - np.ndarray.min(speed_final))/(np.ndarray.max(speed_final) - np.ndarray.min(speed_final))
        pcmra_norm = 256.0*(pcmra - np.ndarray.min(pcmra))/(np.ndarray.max(pcmra) - np.ndarray.min(pcmra))
        
        return speed_norm, pcmra_norm
    
    
    
    def process(self):
        
        #print('Introduce all files of interest: 4D flow + Segmentation + T1')
        
        # 4D flow processing
        
        ffe, _ = self.mat2nii(self.filenames[0],'ffe.nii.gz')
        ap, _ = self.mat2nii(self.filenames[1], 'ap.nii.gz')
        fh, _ = self.mat2nii(self.filenames[2], 'fh.nii.gz')
        rl, _ = self.mat2nii(self.filenames[3], 'rl.nii.gz')
        
        speed, pcmra = self.speed_pcmra(ffe,ap,fh,rl)
        
        # Normalize all data
        
        speed_vtk = vtk.util.numpy_support.numpy_to_vtk(speed.ravel())
        pcmra_vtk = vtk.util.numpy_support.numpy_to_vtk(pcmra.ravel())
        
        # .nii.gz files for speed and PC-MRA and readers
        
        speed_img = nib.Nifti1Image(speed,np.eye(4))
        
        speed_img.header.get_xyzt_units()
        speed_img.to_filename(os.path.join('speed.nii.gz'))  # Save as NiBabel file
        
        speed_reader = vtk.vtkNIFTIImageReader()
        speed_reader.SetFileName('speed.nii.gz')
        
        
        
        pcmra_img = nib.Nifti1Image(pcmra,np.eye(4))
        
        pcmra_img.header.get_xyzt_units()
        pcmra_img.to_filename(os.path.join('pcmra.nii.gz'))  # Save as NiBabel file
        
        pcmra_reader = vtk.vtkNIFTIImageReader()
        pcmra_reader.SetFileName('pcmra.nii.gz')
        
        # Segmentation processing
        
        carotid_segm, carotid_reader = self.mhd_reader(self.filenames[4])
        aux_segm, aux_reader = self.mat2nii(self.filenames[5], 'aux_segm.nii.gz')
        
        carotid_segm_vtk = vtk.util.numpy_support.numpy_to_vtk(carotid_segm.ravel())
        aux_segm_vtk = vtk.util.numpy_support.numpy_to_vtk(aux_segm.ravel())
        
        
        
        # T1 processing
        
        t1_without, t1_without_reader = self.mhd_reader(self.filenames[6])
        t1_with, t1_with_reader = self.mhd_reader(self.filenames[7])
        
        
        t1_with.reshape(t1_with.shape[1], t1_with.shape[2], t1_with.shape[0])
        
        t1_without_vtk = vtk.util.numpy_support.numpy_to_vtk(t1_without.ravel())
        t1_with_vtk = vtk.util.numpy_support.numpy_to_vtk(t1_with.ravel())
        
        print('Data importation complete!')
        
        array_files = [speed, pcmra, carotid_segm, aux_segm, t1_without, t1_with]
        
        vtk_files = [speed_vtk, pcmra_vtk, carotid_segm_vtk, aux_segm_vtk, t1_without_vtk, t1_with_vtk]
        
        readers = [speed_reader, pcmra_reader, carotid_reader, aux_reader, t1_without_reader, t1_with_reader]
        
        return vtk_files, array_files, readers
        
        
        
    
        




    