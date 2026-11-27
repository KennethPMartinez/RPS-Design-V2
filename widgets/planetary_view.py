# -*- coding: utf-8 -*-
"""
widgets/planetary_view.py

Vista de la simulación del PLANETARIO (PyQtGraph). Sol (epitrocoidal) y anular (hipotrocoidal) giran
alrededor del origen con `setRotation`; los N planetas se redibujan por fotograma con numpy (las N·Zrp
circunferencias en UN solo arreglo). Mismo criterio de rendimiento que widgets/simulation_view.py.

`actualizar(estado, (contactos_sol, contactos_anular))`: ver engine/planetario_engine.py.
"""
from __future__ import annotations

import math
import time

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from config.data_structures import AjustesVisibilidadSimulacion
from widgets.hud import HUDMixin
from widgets.pg_helpers import configurar_menu_plot
from widgets.simulation_view import C_ACCION, C_CONTACTO, C_PASO, C_PATRON, C_PINON, _circulos, _rot

C_ANULAR = (110, 200, 120)


class PlanetaryView(HUDMixin, pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAspectLocked(True)
        self.showGrid(x=True, y=True, alpha=0.12)
        self.setLabel("bottom", "X", units="mm")
        self.setLabel("left", "Y", units="mm")
        self.getViewBox().disableAutoRange()
        configurar_menu_plot(self, "simulacion_planetario", geometrica=True, indicadores=True)
        self._ver_todo = self.resetear_camara

        mk, dash = pg.mkPen, QtCore.Qt.PenStyle.DashLine
        self.c_paso_sol = pg.PlotCurveItem(pen=mk(C_PASO, width=1, style=dash))
        self.c_paso_anu = pg.PlotCurveItem(pen=mk(C_PASO, width=1, style=dash))
        self.c_paso_pla = pg.PlotCurveItem(pen=mk(C_PASO, width=1, style=dash), connect="finite")
        self.c_sol = pg.PlotCurveItem(pen=mk(C_PATRON, width=1), connect="finite")
        self.c_anu = pg.PlotCurveItem(pen=mk(C_ANULAR, width=1), connect="finite")
        self.c_pla = pg.PlotCurveItem(pen=mk(C_PINON, width=1), connect="finite")
        self.c_roll_act = pg.PlotCurveItem(pen=mk((255, 235, 120), width=2.2), connect="finite")
        self.c_accion = pg.PlotCurveItem(pen=mk(C_ACCION, width=1.2), connect="pairs")
        self.s_contactos = pg.ScatterPlotItem(size=9, pen=None, brush=pg.mkBrush(C_CONTACTO))
        for it in (self.c_paso_sol, self.c_paso_anu, self.c_paso_pla, self.c_sol, self.c_anu, self.c_pla,
                   self.c_roll_act, self.c_accion, self.s_contactos):
            self.addItem(it, ignoreBounds=True)

        self._eng = None
        self._lab_rod: list = []
        self._lab_dient: list = []
        self._vis = AjustesVisibilidadSimulacion()
        self._ultimo = None
        self._ext = 20.0
        self._n_fps, self._t_fps = 0, time.perf_counter()
        self.lbl_fps = QtWidgets.QLabel(self)
        self.lbl_fps.setStyleSheet("color:#c8c8c8; background:rgba(0,0,0,110); padding:2px 6px;"
                                   "font:9pt 'Consolas';")
        self.lbl_fps.move(8, 8)
        self.lbl_fps.setText("-- FPS")
        self.lbl_fps.adjustSize()
        self._init_hud()                 # FPS + velocidades + relación (widgets/hud.py) y capa de fuerzas

    # ------------------------------------------------------------------
    def set_geometria(self, eng) -> None:
        self._eng, self._ultimo = eng, None
        rs, ra = eng.res_sol, eng.res_anular
        self.c_sol.setData(rs.patron_x, rs.patron_y)
        self.c_anu.setData(ra.patron_x, ra.patron_y)
        self.c_paso_sol.setData(*_circulos(0.0, 0.0, rs.radio_paso_engranaje, 128))
        self.c_paso_anu.setData(*_circulos(0.0, 0.0, ra.radio_paso_engranaje, 192))
        self._ext = 1.1 * max(float(np.nanmax(np.abs(ra.patron_x))), float(np.nanmax(np.abs(ra.patron_y))), 1.0)
        self._rehacer_etiquetas(eng.N, eng.Zrp, eng.Zs, eng.Za)
        self.resetear_camara()

    def _rehacer_etiquetas(self, n_pla: int, n_rod: int, n_sol: int, n_anu: int) -> None:
        for t in self._lab_rod + self._lab_dient:
            self.removeItem(t)
        oscuro = pg.getConfigOption("foreground")[0] > 128
        self._color_rod = (255, 255, 255) if oscuro else (20, 20, 20)
        self._color_dient = (150, 200, 255) if oscuro else (20, 90, 170)
        f = QtGui.QFont("Consolas", 8)

        def nuevo(txt, color):
            ti = pg.TextItem(txt, color=color, anchor=(0, 1))
            ti.setFont(f)
            self.addItem(ti, ignoreBounds=True)
            return ti
        self._lab_rod = [nuevo(str(k), self._color_rod) for _ in range(n_pla) for k in range(n_rod)]
        self._lab_dient = ([nuevo(str(k), self._color_dient) for k in range(n_sol)]
                           + [nuevo(str(k), self._color_dient) for k in range(n_anu)])

    def set_tema(self, oscuro: bool) -> None:
        self._color_rod = (255, 255, 255) if oscuro else (20, 20, 20)
        self._color_dient = (150, 200, 255) if oscuro else (20, 90, 170)
        for t in self._lab_rod:
            t.setColor(self._color_rod)
        for t in self._lab_dient:
            t.setColor(self._color_dient)
        self.c_pla.setPen(pg.mkPen(C_PINON if oscuro else (190, 125, 0), width=1))
        self.c_sol.setPen(pg.mkPen(C_PATRON if oscuro else (25, 90, 200), width=1))
        self.c_anu.setPen(pg.mkPen(C_ANULAR if oscuro else (30, 130, 50), width=1))
        self.c_roll_act.setPen(pg.mkPen((255, 235, 120) if oscuro else (200, 140, 0), width=2.2))
        self.lbl_fps.setStyleSheet(("color:#c8c8c8; background:rgba(0,0,0,110);" if oscuro else
                                    "color:#202020; background:rgba(255,255,255,150);") +
                                   "padding:2px 6px; font:9pt 'Consolas';")

    def resetear_camara(self) -> None:
        e = self._ext
        self.setRange(xRange=(-e, e), yRange=(-e, e), padding=0)

    def set_visibilidad(self, ajustes: AjustesVisibilidadSimulacion) -> None:
        self._vis = ajustes
        if self._ultimo is not None:
            self.actualizar(*self._ultimo)

    # ------------------------------------------------------------------
    def actualizar(self, est, contactos) -> None:
        e, v = self._eng, self._vis
        if e is None:
            return
        self._ultimo = (est, contactos)
        cs, ca = contactos
        todos = cs + ca
        self.c_sol.setRotation(math.degrees(est.fi_sol))
        self.c_anu.setRotation(math.degrees(est.fi_anular))
        rx, ry = e.centros_rodillos_mundo(est)                 # (N, Zrp)
        rr = e.sol.radio_rodillo
        self.c_pla.setData(*_circulos(rx.ravel(), ry.ravel(), rr))

        for it in (self.c_paso_sol, self.c_paso_anu, self.c_paso_pla):
            it.setVisible(v.circulos_de_paso)
        if v.circulos_de_paso:
            self.c_paso_pla.setData(*_circulos(est.centros[:, 0], est.centros[:, 1], e.prrp, 64))

        if todos and v.puntos_de_contacto:
            self.s_contactos.setData([d["punto_contacto_mundo"][0] for d in todos],
                                     [d["punto_contacto_mundo"][1] for d in todos])
            act = sorted({(d["planeta"], d["indice"]) for d in todos})
            self.c_roll_act.setData(*_circulos(np.array([rx[i, k] for i, k in act]),
                                               np.array([ry[i, k] for i, k in act]), rr, 24))
        else:
            self.s_contactos.setData([], [])
            self.c_roll_act.setData([], [])

        if todos and v.lineas_de_accion:
            xs, ys = [], []
            for d in todos:
                if "punto_cir_mundo" in d:
                    a, b = d["punto_contacto_mundo"], d["punto_cir_mundo"]
                    xs += [a[0], b[0]]
                    ys += [a[1], b[1]]
            self.c_accion.setData(xs, ys)
        else:
            self.c_accion.setData([], [])

        mostrar = v.etiquetas_de_rodillo
        for t in self._lab_rod + self._lab_dient:
            t.setVisible(mostrar)
        if mostrar:
            for t, x, y in zip(self._lab_rod, rx.ravel(), ry.ravel()):
                t.setPos(x, y)
            sx, sy = _rot(np.asarray(e.res_sol.diente_centros_x), np.asarray(e.res_sol.diente_centros_y), est.fi_sol)
            ax, ay = _rot(np.asarray(e.res_anular.diente_centros_x), np.asarray(e.res_anular.diente_centros_y),
                          est.fi_anular)
            for t, x, y in zip(self._lab_dient, np.concatenate((sx, ax)), np.concatenate((sy, ay))):
                t.setPos(x, y)

        self._n_fps += 1
        ahora = time.perf_counter()
        if ahora - self._t_fps >= 0.5:
            fps = self._n_fps / (ahora - self._t_fps)
            self._hud_fps(f"{fps:5.1f} FPS ({1000.0 / max(fps, 1e-6):5.1f} ms)")
            self._n_fps, self._t_fps = 0, ahora

    def fotograma(self) -> QtGui.QImage:
        return self.grab().toImage()
