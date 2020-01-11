__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk
import sys

from GridWindow import CombinedWindow
from renderers.MyRendererFile import myRenderer, myNewRenderer
from renderers.ImageSlicing import SliceRenderer


if __name__ == '__main__':
    # 1 create sources
    filename = sys.argv[1]
    reader_src = vtk.vtkNIFTIImageReader()
    reader_src.SetFileName(filename)

    # 2 create renderers
    renderers = list()
    renderers.append(SliceRenderer(reader_src, 'axial'))
    renderers.append(SliceRenderer(reader_src, 'sagittal'))
    renderers.append(SliceRenderer(reader_src, 'coronal'))
    renderers.append(SliceRenderer(reader_src, 'oblique'))
    renderers.append(myRenderer(reader_src))
    renderers.append(myNewRenderer(reader_src))


    # 3 define layout
    layout = (3, 2)

    # 4 render the window
    win = CombinedWindow(renderers, layout)
    win.render()
