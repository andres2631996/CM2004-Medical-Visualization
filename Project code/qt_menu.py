# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 11:22:16 2019

@author: andre
"""

# Main file from where to implement the Qt menu


import vtk
import sys
import scipy.io as sio
import numpy as np
import SimpleITK as sitk
import vtk.util.numpy_support 
import nibabel as nib
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog
from PyQt5 import Qt

from random import random


from data_loading import data_loader
from surface_rendering import SurfaceRendering, vtkTimerCallback
from volume_rendering_mip import VolumeRendering
from surface_volume_rendering import SurfaceAndVolumeRendering
from mip import MIP
from glyphProcessor import glyphProcessing
from mpr import MultiPlanarReconstruction

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        global vtk_files
        global array_files
        global readers
        
        
        vtk_files, array_files, readers = self.loader()  
        
        self.index = 1 # Default data index to be displayed (PC-MRA)
        self.orientation = 'axial' # Default orientation for MIP/MPR
        self.animation = 'No' # Default animation
        self.surface_lut = 'bw' # Default LUT for surface rendering
        self.volume_lut = 'bw' # Default LUT for volume rendering
        self.volume_transf = 'linear' # Default transfer function for volume rendering
        self.shape = 'arrow' # Default glyph shape
        
        self.setup_ui() 
        self.setup_vtk_renderer()
        
        # Connection of data combo box
        self.data_cb.currentIndexChanged.connect(self.onDataClicked)
        
        # Connection of modality combo box
        self.modality_cb.currentIndexChanged.connect(self.onRenderClicked)

        # Connection of orientation combo box
        self.orientation_cb.currentIndexChanged.connect(self.onOrientationClicked)
        
        # Connection of surface LUT combo box
        self.surfaceLUT_cb.currentIndexChanged.connect(self.onSurfaceLUTClicked)
        
        # Connection of volume LUT combo box
        self.volumeLUT_cb.currentIndexChanged.connect(self.onVolumeLUTClicked)
        
        # Connection of volume rendering transfer function combo box
        self.volumeOpacity_cb.currentIndexChanged.connect(self.onVolumeOpacityClicked)
        
        # Connection of glyph shape combo box
        self.glyph_cb.currentIndexChanged.connect(self.onShapeClicked)
        
        
        # Connection of light dial
        self.light_int = 1  # Default light intensity

        
        # Connection of animation speed dial
        self.animation_steps = 500  # Default animation steps (inverse of animation speed)

        
        # Connection of maximum opacity dial
        self.max_opacity = 0.05  # Default maximum opacity (volume rendering only)
        self.opacity_dial.valueChanged.connect(self.onOpacityDialMoved)
        
        # Connection of window minimum and maximum sliders
        
        self.window_minimum = np.amin(array_files[self.index].flatten()) # Window minimum value
        self.window_maximum = np.amax(array_files[self.index].flatten()) # Window maximum value
        
        self.window_minimum_slider.valueChanged.connect(self.onMinimumMoved)
        self.window_maximum_slider.valueChanged.connect(self.onMaximumMoved)
        #self.pushButton.clicked.connect(self.on_button_clicked)
        
        # Connection of frame slider
        self.frame_value = 0 # Default frame value for dynamic data
        self.frame_slider.valueChanged.connect(self.onFrameMoved)  
        
        # Connection of slice sliders for glyphs and MPR
        self.slice_glyph = int(array_files[0].shape[-2]//2) # Default Glyph Slice value
        self.sliceGlyphs_slider.valueChanged.connect(self.onSliceGlyphMoved)
        
        self.slice_MPR = 0 # Default MPR Slice value
        self.sliceMPR_slider.valueChanged.connect(self.onSliceMPRMoved)
        
        
        
    
    def onRenderClicked(self):
        
        # Display images when radiobuttons are checked
        
        
            
        if self.modality_cb.currentText() == 'MPR':
            
            # MPR
            mpr = MultiPlanarReconstruction(filenames,array_files, readers, self.frame_value, self.slice_MPR, self.orientation, self.index)
            self.ren = mpr.execute() 
            
            self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
            self.renWin = self.vtkWidget.GetRenderWindow()
            self.iren = self.renWin.GetInteractor()
            
            self.frame.setLayout(self.vl)
            
            # Set stereo
            self.renWin.GetStereoCapableWindow()
            self.renWin.StereoCapableWindowOn()
            self.renWin.SetStereoRender(1)
            self.renWin.SetStereoTypeToCrystalEyes()
        
    
            
            self.show()
            self.iren.Initialize()
            self.iren.Start()
            
    
            self.vtkWidget.Render()
        
        elif self.modality_cb.currentText() == 'MIP':
            
            # MIP
            
            mip_rendering = MIP(array_files, readers,self.orientation,self.light_int, self.index)
            self.ren = mip_rendering.execute()
            
            self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
            self.renWin = self.vtkWidget.GetRenderWindow()
            self.iren = self.renWin.GetInteractor()
            
            self.frame.setLayout(self.vl)
            
            # Set stereo
            self.renWin.GetStereoCapableWindow()
            self.renWin.StereoCapableWindowOn()
            self.renWin.SetStereoRender(1)
            self.renWin.SetStereoTypeToCrystalEyes()
        
    
            
            self.show()
            self.iren.Initialize()
            self.iren.Start()
            
    
            self.vtkWidget.Render()
            
            
        
        elif self.modality_cb.currentText() == 'Surface Rendering':
            
            
            # Surface rendering
            
            surface = SurfaceRendering(array_files, readers, self.surface_lut, self.animation, 10000, self.light_int,self.index)
            self.ren, self.actor, self.cam = surface.execute()
        
            self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
            self.renWin = self.vtkWidget.GetRenderWindow()
            self.iren = self.renWin.GetInteractor()
            
            self.ren.AddActor(self.actor)
            
            self.frame.setLayout(self.vl)
            
            # Set stereo
            self.renWin.GetStereoCapableWindow()
            self.renWin.StereoCapableWindowOn()
            self.renWin.SetStereoRender(1)
            self.renWin.SetStereoTypeToCrystalEyes()
            
        
            radius = 500
            
            #animation_steps = 100
            
            if self.animation == 'Yes':
                
                cb = vtkTimerCallback(self.animation_steps, self.iren, radius, self.cam)
                
                self.iren.AddObserver('TimerEvent', cb.execute)
                cb.timerId = self.iren.CreateRepeatingTimer(500)
                
                
            self.show()
            self.iren.Initialize()
            self.iren.Start()
            
    
            self.vtkWidget.Render()
            
            
        elif self.modality_cb.currentText() == 'Volume Rendering':
            
            # Volume Rendering
            
            
            window = [self.window_minimum, self.window_maximum]
            exe = VolumeRendering(array_files,readers, self.volume_lut, self.animation, 500, window,self.volume_transf,self.max_opacity, self.light_int, self.index)
            self.ren, self.actor, cam = exe.execute()
            
            self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
            self.renWin = self.vtkWidget.GetRenderWindow()
            self.iren = self.renWin.GetInteractor()
            
            # Add the volume actor to the renderer
            self.ren.AddActor(self.actor)
            
            
            # Set stereo
            self.renWin.GetStereoCapableWindow()
            self.renWin.StereoCapableWindowOn()
            self.renWin.SetStereoRender(1)
            self.renWin.SetStereoTypeToCrystalEyes()
            
            
            
            
            #animation_steps = 100
            radius = 500
            
            if self.animation == 'Yes':
                
                cb = vtkTimerCallback(self.animation_steps, self.iren, radius, cam)
                
                self.iren.AddObserver('TimerEvent', cb.execute)
                cb.timerId = self.iren.CreateRepeatingTimer(500)
            
            
            self.show()
            self.iren.Initialize()
            self.iren.Start()
            
    
            self.vtkWidget.Render()
            
            
        elif self.modality_cb.currentText() == 'Surface + Volume Rendering':
            
           # Surface + Volume Rendering
    
            window = [self.window_minimum, self.window_maximum]
            exe = SurfaceAndVolumeRendering(array_files,readers, self.volume_lut, self.surface_lut, self.animation, 500, window,self.volume_transf,self.max_opacity, self.light_int, self.index)
            self.ren, self.volume_actor, self.surface_actor, cam = exe.execute()
            
            # Add the volume actor and the surface actor to the renderer
            self.ren.AddActor(self.volume_actor)
            self.ren.AddActor(self.surface_actor)
           
            self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
            self.renWin = self.vtkWidget.GetRenderWindow()
            self.iren = self.renWin.GetInteractor()
        
            
            # Set stereo
            self.renWin.GetStereoCapableWindow()
            self.renWin.StereoCapableWindowOn()
            self.renWin.SetStereoRender(1)
            self.renWin.SetStereoTypeToCrystalEyes()
            
            
            #animation_steps = 500
            radius = 500
            
            if self.animation == 'Yes':
                
                cb = vtkTimerCallback(self.animation_steps, self.iren, radius, cam)
                
                self.iren.AddObserver('TimerEvent', cb.execute)
                cb.timerId = self.iren.CreateRepeatingTimer(500)
            
            
            self.show()
            self.iren.Initialize()
            self.iren.Start()
            
    
            self.vtkWidget.Render()
    
        elif self.modality_cb.currentText() == 'Glyphs':
            
            # Glyph visualization
            
            glyph = glyphProcessing(filenames,array_files, self.frame_value, self.slice_glyph, self.shape)
            self.ren = glyph.execute()
            
            self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
            self.renWin = self.vtkWidget.GetRenderWindow()
            self.iren = self.renWin.GetInteractor()
            
            
            self.frame.setLayout(self.vl)
            
            # Set stereo
            self.renWin.GetStereoCapableWindow()
            self.renWin.StereoCapableWindowOn()
            self.renWin.SetStereoRender(1)
            self.renWin.SetStereoTypeToCrystalEyes()
        
    
            
            self.show()
            self.iren.Initialize()
            self.iren.Start()
            
    
            self.vtkWidget.Render()
    
    
        
                
    def onAnimationChecked(self):
        
        # Actions to complete if the animation box is checked
        
        if self.animation_check.isChecked():
            
            self.animation = 'Yes'
            self.onRenderClicked()
            
        else:
            
            self.animation = 'No'
            self.onRenderClicked()

    def onOrientationClicked(self):
        
        # Actions to complete if the orientation buttons are checked
        
        if self.orientation_cb.currentText() == 'Axial':
            
            self.orientation = 'axial'
            self.sliceMPR_slider.setMaximum(array_files[self.index].shape[2])
            self.onRenderClicked()
            
        elif self.orientation_cb.currentText() == 'Coronal':
            
            self.orientation = 'coronal'
            self.sliceMPR_slider.setMaximum(array_files[self.index].shape[0])
            self.onRenderClicked()
            
        elif self.orientation_cb.currentText() == 'Sagittal':
            
            self.orientation = 'sagittal'
            self.sliceMPR_slider.setMaximum(array_files[self.index].shape[1])
            self.onRenderClicked()
            
            
    def onSurfaceLUTClicked(self):
        
        # Actions to complete if the Surface Rendering LUT buttons are checked
        
        if self.surfaceLUT_cb.currentText() == 'Grayscale':
            
            self.surface_lut = 'bw'
            self.onRenderClicked()
        
        elif self.surfaceLUT_cb.currentText() == 'Rainbow':
            
            self.surface_lut = 'rainbow'
            self.onRenderClicked()
        
        elif self.surfaceLUT_cb.currentText() == 'Red-Blue':
            
            self.surface_lut = 'rb'
            self.onRenderClicked()
        
        elif self.surfaceLUT_cb.currentText() == 'Blue-Red':
            
            self.surface_lut = 'br'
            self.onRenderClicked()
            
            
    def onVolumeLUTClicked(self):
        
        # Actions to complete if the Volume Rendering LUT buttons are checked
        
        if self.volumeLUT_cb.currentText() == 'Grayscale':
            
            self.volume_lut = 'bw'
            self.onRenderClicked()
        
        elif self.volumeLUT_cb.currentText() == 'Rainbow':
            
            self.volume_lut = 'rainbow'
            self.onRenderClicked()
        
        elif self.volumeLUT_cb.currentText() == 'Red-Blue':
            
            self.volume_lut = 'rb'
            self.onRenderClicked()
        
        elif self.volumeLUT_cb.currentText() == 'Blue-Red':
            
            self.volume_lut = 'br'
            self.onRenderClicked()
    

    def onDataClicked(self):
        
        # Actions to complete if the data buttons are checked

        if self.data_cb.currentText() == 'Speed':
            
            self.index = 0
            self.window_minimum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_minimum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.window_maximum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_maximum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.onRenderClicked()
            
        elif self.data_cb.currentText() == 'PC-MRA':
            
            self.index = 1
            self.window_minimum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_minimum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.window_maximum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_maximum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.onRenderClicked()
            
        elif self.data_cb.currentText() == 'T1 without contrast':
            
            self.index = -2
            self.window_minimum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_minimum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.window_maximum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_maximum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.onRenderClicked()
        
        elif self.data_cb.currentText() == 'T1 with contrast':
            
            self.index = -1
            self.window_minimum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_minimum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.window_maximum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
            self.window_maximum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
            self.onRenderClicked()
            
        
        
        
    def onOpacityDialMoved(self):
        
        # Actions to complete when the opacity dial is rotated
        
        self.max_opacity = self.opacity_dial.value()/1000.0
        self.onRenderClicked()
        
    
    def onVolumeOpacityClicked(self):
        
        # Actions to complete when the volume transfer function is clicked
        
        if self.volumeOpacity_cb.currentText() == 'Linear':
            
            self.volume_transf = 'linear'
            self.onRenderClicked()
            
        elif self.volumeOpacity_cb.currentText() == 'Logarithmic':
            
            self.volume_transf = 'logarithmic'
            self.onRenderClicked()
            
        elif self.volumeOpacity_cb.currentText() == 'Exponential':
            
            self.volume_transf = 'exponential'
            self.onRenderClicked()
        
        
        
    def onMinimumMoved(self):
        
        # Actions to complete when the minimum window slider is moved
        
        self.window_minimum = self.window_minimum_slider.value()
        
        if self.window_minimum_slider.value() > self.window_maximum_slider.value():
            
            self.window_minimum = self.window_maximum_slider.value()
        
        self.onRenderClicked()
    
    
    def onMaximumMoved(self):
        
        # Actions to complete when the maximum window slider is moved
        
        self.window_maximum = self.window_maximum_slider.value()
        
        if self.window_maximum_slider.value() < self.window_minimum_slider.value():
            
            self.window_maximum = self.window_minimum_slider.value()
        
        self.onRenderClicked()
                
    def onShapeClicked(self):

        # Actions to complete when the shape radiobuttons are clicked

        if self.glyph_cb.currentText() == 'Arrow':
            
            self.shape = 'arrow'
        
        elif self.glyph_cb.currentText() == 'Cube':
            
            self.shape = 'cube'
        
        elif self.glyph_cb.currentText() == 'Sphere':
            
            self.shape = 'sphere'
            
        elif self.glyph_cb.currentText() == 'Cone':
            
            self.shape = 'cone'
        
        self.onRenderClicked()
        
    def onFrameMoved(self):
        
        # Actions to complete when the frame slider is changed
        
        self.frame_value = self.frame_slider.value()
        
        self.onRenderClicked()
    
    
    def onSliceGlyphMoved(self):
        
        # Actions to complete when the slider for the glyph is moved
        
        self.slice_glyph = self.sliceGlyphs_slider.value()
        
        self.onRenderClicked()
    
    
    def onSliceMPRMoved(self):
        
        # Actions to complete when the slider for MPR is moved
        
        self.slice_MPR = self.sliceMPR_slider.value()
        
        self.onRenderClicked()
                
                
        
    def loader(self):
        
        
        # Data loading
        global filenames
        
        filenames = ['4DPC_M_FFE.mat' , '4DPC_vel_AP.mat' , '4DPC_vel_FH.mat'
             , '4DPC_vel_RL.mat' , 'carotid_segm.mhd' , '20121204_seg_final_cleaned.mat' , 'T1.mhd' , 'T1_Gd.mhd']
        loading = data_loader(filenames)
        vtk_files, array_files, readers = loading.process()
        
        return vtk_files, array_files, readers
        

    def setup_vtk_renderer(self):
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl = Qt.QVBoxLayout() 
        self.vl.addWidget(self.vtkWidget)

            
        
        

    def setup_ui(self):
        self.resize(700, 500)

        # central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setObjectName("centralwidget")

        # frame
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        
        # Grid Layout
        
        self.grid = QtWidgets.QGridLayout(self.centralwidget)
        self.grid.setSpacing(10)
        self.grid.addWidget(self.frame, 1, 0, 11, 7)
        #self.grid.setStretchFactor(self.frame,1)
        self.grid.setObjectName("gridLayout")
        
	
        # the translate mechanism
        QtCore.QMetaObject.connectSlotsByName(self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Carotid Visualization", "Carotid Visualization"))

        
        
        # Data ComboBox
        
        self.data_title = QtWidgets.QLabel('Data to be rendered')
        self.grid.addWidget(self.data_title, 1, 8)
        
        self.data_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.data_cb, 2, 8)
        self.data_cb.addItem("Speed")
        self.data_cb.addItem("PC-MRA")
        self.data_cb.addItem("T1 without contrast")
        self.data_cb.addItem("T1 with contrast")
        
        
        # Modality ComboBox
        
        self.modality_title = QtWidgets.QLabel('Visualization Modalities')
        self.grid.addWidget(self.modality_title, 4, 8)
        
        self.modality_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.modality_cb, 5, 8)
        self.modality_cb.addItem("MPR")
        self.modality_cb.addItem("MIP")
        self.modality_cb.addItem("Surface Rendering")
        self.modality_cb.addItem("Volume Rendering")
        self.modality_cb.addItem("Surface + Volume Rendering")
        self.modality_cb.addItem("Glyphs")
       
        
        
        # Animation checkbox
        self.animation_check = QtWidgets.QCheckBox("Animation")
        self.grid.addWidget(self.animation_check, 16, 9)
        self.animation_check.setText(_translate("Carotid Visualization","Animation"))
        
        
        # MIP Orientation combo box
        
        
        self.orientation_title = QtWidgets.QLabel('MIP/MPR orientations')
        self.grid.addWidget(self.orientation_title, 1, 9)
        
         
        self.orientation_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.orientation_cb, 2, 9)
        self.orientation_cb.addItem("Axial")
        self.orientation_cb.addItem("Coronal")
        self.orientation_cb.addItem("Sagittal")
        
        # Surface LUT button group
        
        
        self.surfaceLUT_title = QtWidgets.QLabel('Surface Rendering LUT')
        self.grid.addWidget(self.surfaceLUT_title, 4, 9)
        
        self.surfaceLUT_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.surfaceLUT_cb, 5, 9)
        self.surfaceLUT_cb.addItem("Grayscale")
        self.surfaceLUT_cb.addItem("Rainbow")
        self.surfaceLUT_cb.addItem("Red-Blue")
        self.surfaceLUT_cb.addItem("Blue-Red")
        
        
        self.volumeLUT_title = QtWidgets.QLabel('Volume Rendering LUT')
        self.grid.addWidget(self.volumeLUT_title, 7, 9)
        
        self.volumeLUT_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.volumeLUT_cb, 8, 9)
        self.volumeLUT_cb.addItem("Grayscale")
        self.volumeLUT_cb.addItem("Rainbow")
        self.volumeLUT_cb.addItem("Red-Blue")
        self.volumeLUT_cb.addItem("Blue-Red")
        
        
        self.volumeOpacity_title = QtWidgets.QLabel('Volume Rendering Opacity Function')
        self.grid.addWidget(self.volumeOpacity_title, 10, 9)
        
        self.volumeOpacity_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.volumeOpacity_cb, 11, 9)
        self.volumeOpacity_cb.addItem("Linear")
        self.volumeOpacity_cb.addItem("Logarithmic")
        self.volumeOpacity_cb.addItem("Exponential")
        
        
        
        
        
        # Max. opacity dial (volume rendering)
        
        self.opacity_title = QtWidgets.QLabel('Maximum opacity (Volume Rendering)')
        self.grid.addWidget(self.opacity_title, 1, 11)
        
        self.opacity_dial = QtWidgets.QSlider()
        self.opacity_dial.setMinimum(0.0)
        self.opacity_dial.setMaximum(1000.0)
        self.opacity_dial.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.opacity_dial.setTickInterval(0.05)
        self.grid.addWidget(self.opacity_dial, 2, 11)
        
        
        # Window selection
        
        # Minimum
        
        self.minimum_window_title = QtWidgets.QLabel("Window Minimum (Volume Rendering)")
        self.grid.addWidget(self.minimum_window_title, 5, 11)
        
        self.window_minimum_slider = QtWidgets.QSlider()
        self.window_minimum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
        self.window_minimum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
        self.window_minimum_slider.setValue(np.amin(array_files[self.index].flatten()))
        self.window_minimum_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.grid.addWidget(self.window_minimum_slider, 6, 11)
        
        
        # Maximum
        
        self.maximum_window_title = QtWidgets.QLabel("Window Maximum (Volume Rendering)")
        self.grid.addWidget(self.maximum_window_title, 5, 13)
        
        self.window_maximum_slider = QtWidgets.QSlider()
        self.window_maximum_slider.setMinimum(np.amin(array_files[self.index].flatten()))
        self.window_maximum_slider.setMaximum(np.amax(array_files[self.index].flatten()))
        self.window_maximum_slider.setValue(np.amax(array_files[self.index].flatten()))
        self.window_maximum_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.grid.addWidget(self.window_maximum_slider, 6, 13)
        
        
        
        # Glyph shape radiobuttons
        
        self.glyph_shape_title = QtWidgets.QLabel("Glyph Shape")
        self.grid.addWidget(self.glyph_shape_title, 13, 9)
        
        self.glyph_cb = QtWidgets.QComboBox()
        self.grid.addWidget(self.glyph_cb, 14, 9)
        self.glyph_cb.addItem("Arrow")
        self.glyph_cb.addItem("Cube")
        self.glyph_cb.addItem("Sphere")
        self.glyph_cb.addItem("Cone")
        
        # Frame slider
        self.frame_title = QtWidgets.QLabel("Dynamic frame regulator (for Speed in MPR and Glyphs)")
        self.grid.addWidget(self.frame_title, 1, 13)
        
        self.frame_slider = QtWidgets.QSlider()
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(array_files[0].shape[-1])
        self.frame_slider.setValue(0)
        self.frame_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.grid.addWidget(self.frame_slider, 2, 13)
        
        
        # Slice for glyphs slider
        self.sliceGlyphs_title = QtWidgets.QLabel("Glyph slice regulator")
        self.grid.addWidget(self.sliceGlyphs_title, 10, 11)
        
        self.sliceGlyphs_slider = QtWidgets.QSlider()
        self.sliceGlyphs_slider.setMinimum(0)
        self.sliceGlyphs_slider.setMaximum(array_files[0].shape[-2])
        self.sliceGlyphs_slider.setValue(int(array_files[0].shape[-2]//2))
        self.sliceGlyphs_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.grid.addWidget(self.sliceGlyphs_slider, 11, 11)
        
        
        # Slice for MPR slider
        self.sliceMPR_title = QtWidgets.QLabel("MPR slice regulator")
        self.grid.addWidget(self.sliceMPR_title, 10, 13)
        
        self.sliceMPR_slider = QtWidgets.QSlider()
        self.sliceMPR_slider.setMinimum(0)
        
        if self.orientation == 'axial':
            self.sliceMPR_slider.setMaximum(array_files[self.index].shape[2])
        
        elif self.orientation == 'coronal':
            self.sliceMPR_slider.setMaximum(array_files[self.index].shape[0])
        
        elif self.orientation == 'sagittal':
            self.sliceMPR_slider.setMaximum(array_files[self.index].shape[1])
        
        
        self.sliceMPR_slider.setValue(0)
        self.sliceMPR_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.grid.addWidget(self.sliceMPR_slider, 11, 13)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
