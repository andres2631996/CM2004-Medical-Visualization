__author__ = 'fabian sinzinger'
__email__ = 'fabiansi@kth.se'

import vtk


class StyleCallback:
    def __init__(self, rens_inters, interactor):
        self.interactor = interactor
        self.map_dict = dict()

        for _ren, _inter_style in rens_inters:
            self.map_dict[_ren] = _inter_style

    def __call__(self, obj, ev):
        _x, _y = obj.GetEventPosition()
        render_ref = obj.FindPokedRenderer(_x, _y)
        self.interactor.SetInteractorStyle(self.map_dict[render_ref])


class CombinedWindow:
    def __init__(self, renderer_list, layout):
        assert len(layout) == 2
        assert layout[0] * layout[1] == len(renderer_list)

        self.renderer_list = renderer_list
        self.layout = layout

    def _get_borders(self):
        xl, yl = self.layout
        x_borders = [(_num/xl, (_num+1)/xl) for _num in range(xl)] 
        y_borders = [(_num/yl, (_num+1)/yl) for _num in range(yl)] 
        borders = list()

        for xb in x_borders:
            for yb in y_borders:
                borders.append((xb[0], yb[0], xb[1], yb[1]))

        return borders

    def render(self):
        ren_win = vtk.vtkRenderWindow()
        iren = vtk.vtkRenderWindowInteractor()
        borders = self._get_borders()

        for _ren, _bord in zip(self.renderer_list, borders):
            _ren.renderer.SetViewport(*_bord)
            ren_win.AddRenderer(_ren.renderer)

        iren.SetRenderWindow(ren_win)

        rens_inters = [(_ren.renderer, _ren.inter_style) for _ren in
                self.renderer_list]

        iren.RemoveObservers('MouseMoveEvent')
        iren.AddObserver('MouseMoveEvent', StyleCallback(rens_inters, iren), 1.)

        ren_win.Render()
        iren.Start()


