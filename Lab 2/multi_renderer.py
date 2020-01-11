__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk
import sys

from GridWindow import CombinedWindow

from renderers.ImageSlicing import SliceRenderer
from renderers.surface_renderer import surface_renderer, triangle_renderer
from renderers.Marching_TEMPLATE import MarchingRenderer

if __name__ == '__main__':
    # 1 create sources
    filename = sys.argv[1] # '../data/head_self_t1.nii.gz' 
    reader_src = vtk.vtkNIFTIImageReader()
    reader_src.SetFileName(filename)

    # 2 create renderers
    renderers = list()
    renderers.append(triangle_renderer())
    renderers.append(MarchingRenderer(reader_src))
    #renderers.append(SliceRenderer(reader_src, 'coronal'))

    #renderers.append(SliceRenderer(reader_src, 'axial'))
    #renderers.append(VolumeRenderer(reader_src))
    #renderers.append(VolumeRenderer(reader_src))

    # 3 define layout
    layout = (2, 1)

    # 4 render the window
    win = CombinedWindow(renderers, layout)
    win.render()
