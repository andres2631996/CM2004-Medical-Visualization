import sys
import vtk
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from renderers_qt.ImageSlicing import SliceRender
from renderers_qt.Volume import VolumeRender
from renderers_qt.Surface import SurfaceRender


def idx_from_shape(shape_):
    assert len(shape_) == 2
    retlist = list()
    for i_ in range(shape_[0]):
        for j_ in range(shape_[1]):
            retlist.append((i_, j_))

    return retlist


class MainWindow(Qt.QMainWindow):

    def __init__(self, render_list, shape, frame, parent = None):
        assert len(render_list) == shape[0] * shape[1]

        Qt.QMainWindow.__init__(self, parent)

        self.vl = Qt.QVBoxLayout()
        self.horizontalGroupBox = Qt.QGroupBox("LabisLab")
 
        self.vl.addWidget(self.horizontalGroupBox)
        self.layout = Qt.QGridLayout()
        # self.layout.setColumnStretch(1, 4)
        # self.layout.setColumnStretch(2, 4)

        self.frame = frame
        self.render = render_list

        self.vtk_widgets = [ren_.interactor for ren_ in self.render]

        self.layout_grid = idx_from_shape(shape)

        self.rens = list()
        self.irens = list()

        for idx, (wid_, grd_, ren_) in enumerate(zip(self.vtk_widgets,
            self.layout_grid, self.render)):
            self.layout.addWidget(wid_, grd_[0], grd_[1])

            self.rens.append(vtk.vtkRenderer()) 
            wid_.GetRenderWindow().AddRenderer(ren_.renderer)
            self.irens.append(wid_.GetRenderWindow().GetInteractor())

        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        for render_, ren_ in zip(self.render, self.rens):
            if isinstance(render_, SliceRender):
                ren_.AddActor(actor)
                ren_.ResetCamera()

        self.horizontalGroupBox.setLayout(self.layout)
        self.frame.setLayout(self.vl)

        self.setCentralWidget(self.horizontalGroupBox)

        self.show()

        for iren_ in self.irens:
            iren_.Initialize()
            iren_.Start()


if __name__ == "__main__":
    ### TODO set renders in function call  
    filename = '../data/head_self_t1.nii.gz' 

    app = Qt.QApplication(sys.argv)
    frame = Qt.QFrame()

    render = list()

    render.append(SliceRender(filename, orie='axial', 
                  frame=frame))
    render.append(SliceRender(filename, orie='coronal', 
                  frame=frame))
    render.append(SliceRender(filename, orie='sagittal', 
                  frame=frame))
    render.append(VolumeRender(filename, 
                  frame=frame))
    render.append(VolumeRender(filename, 
                  frame=frame))
    render.append(SurfaceRender(filename, 
                  frame=frame))
    ###

    window = MainWindow(render, (2, 3), frame)
    app.exec_()
