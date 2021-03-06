from ..Qt import QtGui
from .. import functions as fn
from .PlotDataItem import PlotDataItem
from .PlotCurveItem import PlotCurveItem

class FillBetweenItem(QtGui.QGraphicsPathItem):
    """
    GraphicsItem filling the space between two PlotDataItems.
    """
    def __init__(self, curve1=None, curve2=None, brush=None):
        QtGui.QGraphicsPathItem.__init__(self)
        self.curves = None
        if curve1 is not None and curve2 is not None:
            self.setCurves(curve1, curve2)
        elif curve1 is not None or curve2 is not None:
            raise Exception("Must specify two curves to fill between.")
        
        if brush is not None:
            self.setBrush(fn.mkBrush(brush))
        self.updatePath()

    def setCurves(self, curve1, curve2):
        """Set the curves to fill between.
        
        Arguments must be instances of PlotDataItem or PlotCurveItem."""
        
        if self.curves is not None:
            for c in self.curves:
                try:
                    c.sigPlotChanged.disconnect(self.curveChanged)
                except (TypeError, RuntimeError):
                    pass
        
        curves = [curve1, curve2]
        for c in curves:
            if not isinstance(c, PlotDataItem) and not isinstance(c, PlotCurveItem):
                raise TypeError("Curves must be PlotDataItem or PlotCurveItem.")
        self.curves = curves
        curve1.sigPlotChanged.connect(self.curveChanged)
        curve2.sigPlotChanged.connect(self.curveChanged)
        self.setZValue(min(curve1.zValue(), curve2.zValue())-1)
        self.curveChanged()
        
    def setBrush(self, *args, **kwds):
        """Change the fill brush. Acceps the same arguments as pg.mkBrush()"""
        QtGui.QGraphicsPathItem.setBrush(self, fn.mkBrush(*args, **kwds))

    def curveChanged(self):
        self.updatePath()

    def updatePath(self):
        if self.curves is None:
            self.setPath(QtGui.QPainterPath())
            return
        paths = []
        for c in self.curves:
            if isinstance(c, PlotDataItem):
                paths.append(c.curve.getPath())
            elif isinstance(c, PlotCurveItem):
                paths.append(c.getPath())
            
        path = QtGui.QPainterPath()
        p1 = paths[0].toSubpathPolygons()
        p2 = paths[1].toReversed().toSubpathPolygons()
        if len(p1) == 0 or len(p2) == 0:
            self.setPath(QtGui.QPainterPath())
            return
            
        path.addPolygon(p1[0] + p2[0])
        self.setPath(path)
