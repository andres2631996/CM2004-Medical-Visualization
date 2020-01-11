import vtk


class SliceRenderer:
    def __init__(self, source, orie='sagittal'):
        # Calculate the center of the volume
        source.Update()

        (xMin, xMax, yMin, yMax, zMin, zMax) = source.GetExecutive().GetWholeExtent(
                                                    source.GetOutputInformation(0))
        (xSpacing, ySpacing, zSpacing) = source.GetOutput().GetSpacing()
        (x0, y0, z0) = source.GetOutput().GetOrigin()

        self.center = [x0 + xSpacing * 0.5 * (xMin + xMax),
                       y0 + ySpacing * 0.5 * (yMin + yMax),
                       z0 + zSpacing * 0.5 * (zMin + zMax)]

        # Matrices for axial, coronal, sagittal, oblique view orientations
        orie_mat = self._get_orie_mat(orie=orie)

        # Extract a slice in the desired orientation
        self.reslice = vtk.vtkImageReslice()
        self.reslice.SetInputConnection(source.GetOutputPort())
        self.reslice.SetOutputDimensionality(2)
        self.reslice.SetResliceAxes(orie_mat)
        self.reslice.SetInterpolationModeToLinear()

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
        color.SetInputConnection(self.reslice.GetOutputPort())

        # Display the image
        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(color.GetOutputPort())

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(actor)

        # Set up the interaction
        self.inter_style = vtk.vtkInteractorStyleImage()

        # Create callbacks for slicing the image
        self.actions = {}
        self.actions["Slicing"] = 0

        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        self.inter_style.AddObserver("LeftButtonPressEvent", self.ButtonCallback)
        self.inter_style.AddObserver("LeftButtonReleaseEvent", self.ButtonCallback)


    def _get_orie_mat(self, orie):
        trans_mat = vtk.vtkMatrix4x4()
        center = self.center

        if orie == 'axial':
            trans_mat.DeepCopy((1, 0, 0, center[0],
                            0, 1, 0, center[1],
                            0, 0, 1, center[2],
                            0, 0, 0, 1))
        elif orie == 'coronal':
            trans_mat.DeepCopy((1, 0, 0, center[0],
                              0, 0, 1, center[1],
                              0,-1, 0, center[2],
                              0, 0, 0, 1))
        elif orie == 'sagittal':
            trans_mat.DeepCopy((0, 0,-1, center[0],
                               1, 0, 0, center[1],
                               0,-1, 0, center[2],
                               0, 0, 0, 1))
        elif orie == 'oblique':
            trans_mat.DeepCopy((1, 0, 0, center[0],
                              0, 0.866025, -0.5, center[1],
                              0, 0.5, 0.866025, center[2],
                              0, 0, 0, 1))
        else:
            raise ValueError

        return trans_mat


    def ButtonCallback(self, obj, event):
        if event == "LeftButtonPressEvent":
            self.actions["Slicing"] = 1
        else:
            self.actions["Slicing"] = 0


    def MouseMoveCallback(self, obj, event):
        center = self.center

        inter = obj.GetInteractor()

        (lastX, lastY) = inter.GetLastEventPosition()
        (mouseX, mouseY) = inter.GetEventPosition()
        if self.actions["Slicing"] == 1:
            deltaY = mouseY - lastY
            self.reslice.Update()
            sliceSpacing = self.reslice.GetOutput().GetSpacing()[2]
            matrix = self.reslice.GetResliceAxes()
            # move the center point that we are slicing through
            center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
            matrix.SetElement(0, 3, center[0])
            matrix.SetElement(1, 3, center[1])
            matrix.SetElement(2, 3, center[2])

            current_window = inter.GetRenderWindow()
            current_window.Render()
        else:
            self.inter_style.OnMouseMove()


