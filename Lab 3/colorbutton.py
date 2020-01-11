import vtk
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog
from PyQt5 import Qt

from random import random


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setup_ui() 
        self.setup_vtk_renderer()

        # [4]
        # connect button click
        
        self.pushButton.clicked.connect(self.on_button_clicked)
        
    # [3] define the button click functon
    
    def on_button_clicked(self):
        r = random()
        g = random()
        b = random()
        self.actor.GetProperty().SetColor(r,g,b)
        self.vtkWidget.Render()

    def setup_vtk_renderer(self):
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl = Qt.QVBoxLayout() 
        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # [1]
        # Create source
        src = vtk.vtkSphereSource()
        
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(src.GetOutputPort())
        # Create an actor
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

        self.ren.AddActor(self.actor)

        self.frame.setLayout(self.vl)

        self.show()
        self.iren.Initialize()
        self.iren.Start()

    def setup_ui(self):
        self.resize(743, 430)

        # central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setObjectName("centralwidget")

        # frame
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        # horizontal layout
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretchFactor(self.frame,1)
        self.horizontalLayout.setObjectName("horizontalLayout")
	
        # the translate mechanism
        QtCore.QMetaObject.connectSlotsByName(self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # [2]
        # add the button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton)
        self.horizontalLayout.setStretchFactor(self.pushButton,1)
        self.pushButton.setText(_translate("MainWindow","PushButton"))
        self.pushButton.setObjectName("PushButton")
        
    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
