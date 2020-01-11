Instructions to execute the code:

You must have the required data in the same folder as all the .py files. 

Data can be accessed here (KTH BOX folder): https://kth.box.com/s/4ob1snsbx6xdqo58t2bvfm8nyhrd6nas

You must have the following libraries: NumPy, VTK, NiBabel, PyQt5, SciPy and SimpleITK

The file to run is "qt_menu.py". This file displays the User Interface for carotid visualization, designed on PyQt5.
This file can be executed in some interface as Spyder.

The rest of the files are connected to "qt_menu.py".
- "data_loading.py" prepares and pre-processes the data to adapt it to VTK.
- "surface_rendering.py" performs surface rendering given the data and carotid segmentations. It also allows some interactions.
- "volume_rendering_mip.py" performs volume rendering given the data. It allows interactions on the color and opacity transfer functions.
- "mip.py" performs Maximum Intensity Projection given the data and some orientation.
- "glyphProcessor.py" performs glyphs given an axial MPR slice and a glyph shape.
- "mpr.py" performs Multi-Planar Reconstructions given the data, the slice location and the orientation.
- "surface_volume_rendering.py" performs both surface and volume rendering at the same time, given the data and extra interaction options.

