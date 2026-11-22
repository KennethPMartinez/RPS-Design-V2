# -*- coding: utf-8 -*-
"""
exporters/plot_figures.py

Figuras para el informe PDF: gráficas de PyQtGraph sobre FONDO BLANCO (independiente del tema de la app),
renderizadas fuera de pantalla con ImageExporter. Devuelven QImage.
"""
from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from PySide6 import QtCore, QtWidgets

NEGRO = pg.mkPen("k")


def _rango(valores, margen=0.06):
    v = np.concatenate([np.asarray(a, float)[np.isfinite(a)] for a in valores])
    lo, hi = float(v.min()), float(v.max())
    d = (hi - lo) or abs(lo) * 0.1 or 1.0
    return lo - d * margen, hi + d * margen


def figura(curvas, xlabel: str, ylabel: str, titulo: str, aspecto: bool = False, yrange=None,
           lineas_h=(), ancho: int = 1800):
    """curvas: [(x, y, (r,g,b), nombre, 'solid'|'dot')]  ·  lineas_h: [(y, texto, (r,g,b))]."""
    previo = pg.getConfigOption("useOpenGL")
    pg.setConfigOptions(useOpenGL=False)                  # el viewport OpenGL no se renderiza fuera de pantalla
    try:
        w = pg.PlotWidget(background="w")
        pi = w.getPlotItem()
        for eje in ("left", "bottom"):
            a = pi.getAxis(eje)
            a.setPen(NEGRO)
            a.setTextPen(NEGRO)
        pi.showGrid(x=True, y=True, alpha=0.3)
        pi.setLabel("bottom", xlabel, color="k")
        pi.setLabel("left", ylabel, color="k")
        pi.setTitle(titulo, color="k", size="14pt")
        if len(curvas) > 1:
            pi.addLegend(offset=(10, 10), labelTextColor="k")
        for x, y, color, nombre, estilo in curvas:
            pen = pg.mkPen(color, width=2.2, style=QtCore.Qt.PenStyle.DotLine if estilo == "dot"
                           else QtCore.Qt.PenStyle.SolidLine)
            pi.plot(np.asarray(x, float), np.asarray(y, float), pen=pen, name=nombre)
        for y, texto, color in lineas_h:
            linea = pg.InfiniteLine(pos=y, angle=0, pen=pg.mkPen(color, width=1.6, style=QtCore.Qt.PenStyle.DashLine),
                                    label=texto, labelOpts={"color": color, "position": 0.9})
            pi.addItem(linea)
        for eje in ("left", "bottom"):
            pi.getAxis(eje).enableAutoSIPrefix(False)      # sin "(x0.001)" en los rótulos
        w.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        w.resize(1000, 560)
        w.show()                                           # maqueta ejes/título sin mostrar la ventana
        QtWidgets.QApplication.processEvents()
        xr = _rango([c[0] for c in curvas])
        yr = yrange or _rango([c[1] for c in curvas] + [[y] for y, _, _ in lineas_h])
        if aspecto:
            w.setAspectLocked(True)
        pi.vb.setRange(xRange=xr, yRange=yr, padding=0)
        QtWidgets.QApplication.processEvents()
        exp = ImageExporter(pi)
        exp.parameters()["width"] = ancho
        exp.parameters()["antialias"] = True
        img = exp.export(toBytes=True)
        w.close()
        w.deleteLater()
        return img
    finally:
        pg.setConfigOptions(useOpenGL=previo)
