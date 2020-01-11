__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk
import sys


if __name__ == '__main__':
    # 1 get data path from the first argument given

    # 2 set up the source

    # 3 set up the volume mapper

    # 4 transfer functions for color and opacity
    #   for now: map value 0   -> black: (0., 0., 0.) 
    #                      512 -> black: (1., 1., 1.) 

    # 5 assign also an alpha (opacity) gradient to the values
    #   for now: map value 0   -> 0. 
    #                      256 -> .01
    
    # 6 set up the volume properties with linear interpolation

    # 7 set up the actor and connect it to the mapper

    # 8 set up the camera and the renderer
    #   for now: up-vector:       (0., 1., 0.)
    #            camera position: (-500, 100, 100)
    #            focal point:     (100, 100, 100)

    # 9 set the color of the renderers background to black (0., 0., 0.)

    # 10 set the renderers canera as active

    # 11 add the volume actor to the renderer

    # 12 create a render window

    # 13 add renderer to the render window

    # 14 create an interactor

    # 15 connect interactor to the render window

    # 16 start displaying the render window

    # 17 make the window interactive (start the interactor)
