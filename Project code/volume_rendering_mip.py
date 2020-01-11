# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 19:45:14 2019

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





class VolumeRendering:
    
    def __init__(self, arrays, readers,lut_key,animation, steps, 
                 opacity_window, opacity_key,opacity_max,light_int, index):
        
        
        """
        Class for Volume rendering.
        
        Inputs: arrays, readers from .nii or .mhd files,
        an opacity window (list of min-max), an opacity key, an opacity maximum, 
        a given light intensity and an index specifying which dataset to work with:
            
            0: speed
            1: PC-MRA
            2: carotid segmentation
            3: auxiliary segmentation
            4: T1 without contrast
            5: T1 with contrast
        
        
        """
        
        self.arrays = arrays
        self.readers = readers
        self.mip_key = None
        self.lut_key = lut_key
        self.animation = None
        self.animation_steps = steps
        self.index = index
        self.opacity_window = opacity_window
        self.opacity_key = opacity_key
        self.opacity_max = opacity_max
        self.light_int = light_int
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera()
        
    def lut_definition(self):
        
        """
        Set lookup table. Possible inputs:
            
            'rainbow': rainbow LUT
            'rb': red-blue LUT
            'br': blue-red LUT
            'bw': grayscale LUT (black & white)
        
        """
        
        ctfun = vtk.vtkColorTransferFunction()
        ctfun.SetColorSpaceToRGB()
    
        
        if self.lut_key == 'rainbow':
            
            ctfun.AddRGBPoint(self.opacity_window[0], 1., 0., 0.)
            ctfun.AddRGBPoint(self.opacity_window[1]/6, 1. , 1., 0.)
            ctfun.AddRGBPoint(self.opacity_window[1]/3, 0. , 1., 0.)
            ctfun.AddRGBPoint(self.opacity_window[1]/2, 0. , 1., 1.)
            ctfun.AddRGBPoint(self.opacity_window[1]*2/3, 1., 0., 1.)
            ctfun.AddRGBPoint(self.opacity_window[1]*5/6, 0., 0., 1.)
            ctfun.AddRGBPoint(self.opacity_window[1], 1., 0., 0.)
            
        elif self.lut_key == 'bw':
            
            ctfun.AddRGBPoint(self.opacity_window[0], 0., 0., 0.)
            ctfun.AddRGBPoint(self.opacity_window[1], 1., 1., 1.)
            
        elif self.lut_key == 'br':
            
            ctfun.AddRGBPoint(self.opacity_window[0], 0., 0., 1.)
            ctfun.AddRGBPoint(self.opacity_window[1], 1., 0., 0.)
            
        elif self.lut_key == 'rb':
            
            ctfun.AddRGBPoint(self.opacity_window[0], 1., 0., 0.)
            ctfun.AddRGBPoint(self.opacity_window[1], 0., 0., 1.)
            
        else:
                    
            print('Wrong lookup table key. Type "rainbow", "bw", "rb" or "br"')
            
            
        return ctfun
    
    
    def opacity_definition(self):
        
        # Define opacity transfer function according to the inputs given to the class
        
        gtfun = vtk.vtkPiecewiseFunction()
        
        if self.opacity_window is None:
            
            # If no window range is defined, set the whole histogram range as window
            
            self.opacity_window = [np.ndarray.min(self.arrays[self.index].flatten()), 
                                   np.ndarray.max(self.arrays[self.index].flatten())]
        
        else:
            
            if len(self.opacity_window) != 2: 
                print('The opacity window must just have 2 values: minimum and maximum')
                
            else:
                if self.opacity_window[0] > self.opacity_window[1]:
                    # Invert the list given
                    
                    self.opacity_window.reverse()
                
                # Set opacity values outside the windows 
                #to totally transparent before and totally opaque after the window
                
                
                gtfun.AddSegment(0, 0.0, self.opacity_window[0]/256, 0.0)
                gtfun.AddSegment(self.opacity_window[1]/256, self.opacity_max, 256, self.opacity_max)
                
                
                if self.opacity_key == 'Linear' or self.opacity_key == 'linear':
                    
                    gtfun.AddSegment(self.opacity_window[0]/256, 0.0, self.opacity_window[1]/256, self.opacity_max)
                    
                elif self.opacity_key == 'Logarithmic' or self.opacity_key == 'logarithmic':
                    
                    increase = (self.opacity_window[1] - self.opacity_window[0])/(256*3)
                    
                    for i in range(2):
                        
                        gtfun.AddSegment(self.opacity_window[0]/256 + increase*i, 0.0,
                                         self.opacity_window[0]/256 + increase*(i+1), 
                                         self.opacity_max*np.log10(9/(self.opacity_window[1]/256-
                                                     (self.opacity_window[0]/256 + increase*(i+1)))))
                
                
                elif self.opacity_key == 'Exponential' or self.opacity_key == 'exponential':
                    
                    increase = (self.opacity_window[1] - self.opacity_window[0])/(256*3)
                    
                    for i in range(2):
                        
                        gtfun.AddSegment(self.opacity_window[0]/256 + increase*i, 0.0,
                                         self.opacity_window[0]/256 + increase*(i+1), 
                                         self.opacity_max*np.exp(self.opacity_window[0]/256 + increase*(i+1)-self.opacity_window[1]/256))
                        
                else:
                    
                    print('Wrong opacity key. Type "linear", "exponential" or "logarithmic"')
                        
                        
        return gtfun        
                
                
        
    def execute(self):
        
        vol_map = vtk.vtkGPUVolumeRayCastMapper()
        vol_map.SetInputConnection(self.readers[self.index].GetOutputPort())
        
        # Do usual Volume Rendering

        # Compute color transfer function with the given LUT
        
        ctfun = self.lut_definition()
        
        # Compute opacity transfer function
        
        gtfun = self.opacity_definition()
        
        
        # Set Volume Property
        vol_prop = vtk.vtkVolumeProperty()
        vol_prop.SetColor(0, ctfun)
        vol_prop.SetScalarOpacity(0, gtfun)
        vol_prop.SetInterpolationTypeToLinear()
    
    

        # Set Actors

        vol_act = vtk.vtkVolume()
        vol_act.SetMapper(vol_map)
        vol_act.SetProperty(vol_prop)
        
        radius = 500
        
        # Set camera
        cam = vtk.vtkCamera()
        cam.SetViewUp(0., 1., 0.)
        cam.SetPosition(radius, radius, radius)
        cam.SetFocalPoint(0., 0., 0.)
        
        
        # Set light in the renderer
        
        ren = vtk.vtkRenderer()
        ren.SetBackground(0. , 0. , 0.)
        ren.SetAmbient(self.light_int, self.light_int, self.light_int)
        
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        
        # Set the renderers camera as active
        ren.SetActiveCamera(cam)
        
#        # Add the volume actor to the renderer
#        ren.AddActor(vol_act)
#        
#        # Create a render window
#        renWin = vtk.vtkRenderWindow()
#        
#        # Add renderer to the render window
#        renWin.AddRenderer(ren)
#        
#        # Set stereo
#        renWin.GetStereoCapableWindow()
#        renWin.StereoCapableWindowOn()
#        renWin.SetStereoRender(1)
#        renWin.SetStereoTypeToAnaglyph()
#        
#        # Create an interactor
#        inter = vtk.vtkRenderWindowInteractor()
#        
#        # Connect interactor to the render window
#        inter.SetRenderWindow(renWin)
#        
#        
#        inter.Initialize()
#        
#        if self.animation is not None or self.animation != 'No' or self.animation != 'no' or self.animation != 'n':
#            
#            cb = vtkTimerCallback(self.animation_steps, inter, radius, cam)
#            
#            inter.AddObserver('TimerEvent', cb.execute)
#            cb.timerId = inter.CreateRepeatingTimer(500)
#        
#        
#        # Start displaying the render window
#        renWin.Render()
#        
#        # Make the window interactive (start the interactor)
#        inter.Start()

        #print('Completed Volume Rendering!')
        
        
        return ren, vol_act, cam
        
        
        
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
## Initialize Volume Rendering
#
#ind = 0
#window = [np.ndarray.min(array_files[ind].flatten()), np.ndarray.max(array_files[ind].flatten())]
#exe = VolumeRendering(array_files,readers, 'bw', 'Yes', 500, window,'logarithmic',0.05, 1, ind)
#_,_,_ = exe.execute()
