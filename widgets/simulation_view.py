# -*- coding: utf-8 -*-
"""
widgets/simulation_view.py

Vista de la simulación sobre PyQtGraph, para los sistemas ANGULARES (Epi/Hipotrocoidal) y el
LINEAL (Trocoidal). La geometría pesada se sube UNA vez a `PlotCurveItem` en su marco local y por
fotograma solo cambia la TRANSFORMACIÓN del item (O(1) en Python):
  - angular: el patrón (engranaje) gira alrededor del origen (`setRotation`);
  - lineal : el patrón (cremallera) se traslada (`setPos`) con `estado.traslacion_patron`.
El modo se deduce de la geometría: sin `radio_paso_engranaje` => lineal.

"Ver todo" (menú contextual) = `resetear_camara()`, que encuadra patrón + piñón completos.
"""
from __future__ import annotations

import math
import time

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from config.data_structures import AjustesVisibilidadSimulacion
from widgets.pg_helpers import configurar_menu_plot

C_PATRON = (77, 140, 242)
C_PINON = (242, 191, 51)
C_CONTACTO = (230, 64, 64)
C_ACCION = (242, 140, 38)
C_BASE = (110, 200, 120)      # curva generatriz base
C_CAMINO = (180, 110, 235)    # camino de contacto
C_PASO = (140, 140, 150)


def _circulos(cx, cy, radio: float, n: int = 40):
    """Varias circunferencias en UN solo arreglo (separadas por NaN)."""
    a = np.linspace(0.0, 2.0 * np.pi, n)
    cx, cy = np.atleast_1d(cx)[:, None], np.atleast_1d(cy)[:, None]
    x = np.hstack((cx + radio * np.cos(a)[None, :], np.full((cx.shape[0], 1), np.nan)))
    y = np.hstack((cy + radio * np.sin(a)[None, :], np.full((cy.shape[0], 1), np.nan)))
    return x.ravel(), y.ravel()


def _rot(x, y, ang):
    c, s = math.cos(ang), math.sin(ang)
    return c * x - s * y, s * x + c * y


class SimulationView(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAspectLocked(True)
        self.showGrid(x=True, y=True, alpha=0.12)
        self.setLabel("bottom", "X", units="mm")
        self.setLabel("left", "Y", units="mm")
        self.getViewBox().disableAutoRange()
        configurar_menu_plot(self, "simulacion", geometrica=True)
        self._ver_todo = self.resetear_camara          # proveedor de encuadre para "Ver todo"

        mk = pg.mkPen
        self.c_paso_eng = pg.PlotCurveItem(pen=mk(C_PASO, width=1, style=QtCore.Qt.PenStyle.DashLine))
        self.c_paso_pin = pg.PlotCurveItem(pen=mk(C_PASO, width=1, style=QtCore.Qt.PenStyle.DashLine))
        # Ancho 1 = pluma cosmética (con antialias, anchos >1 pasaban de ~7 ms a ~37 ms por fotograma)
        self.c_patron = pg.PlotCurveItem(pen=mk(C_PATRON, width=1), connect="finite")
        self.c_pinon = pg.PlotCurveItem(pen=mk(C_PINON, width=1), connect="finite")
        self.c_roll_act = pg.PlotCurveItem(pen=mk((255, 235, 120), width=2.2), connect="finite")
        self.c_accion = pg.PlotCurveItem(pen=mk(C_ACCION, width=1.2), connect="pairs")
        self.c_base = pg.PlotCurveItem(pen=mk(C_BASE, width=1, style=QtCore.Qt.PenStyle.DashLine), connect="finite")
        self.c_camino = pg.PlotCurveItem(pen=mk(C_CAMINO, width=1.6))
        self.s_contactos = pg.ScatterPlotItem(size=9, pen=None, brush=pg.mkBrush(C_CONTACTO))
        self.s_centro = pg.ScatterPlotItem(size=6, pen=None, brush=pg.mkBrush(C_PINON))
        for it in (self.c_paso_eng, self.c_paso_pin, self.c_base, self.c_camino, self.c_patron, self.c_pinon,
                   self.c_roll_act, self.c_accion, self.s_contactos, self.s_centro):
            self.addItem(it, ignoreBounds=True)

        self._geom = None
        self._lineal = False
        self._labels_rod: list = []
        self._labels_dient: list = []
        self._vis = AjustesVisibilidadSimulacion()
        self._ultimo = None          # (estado, contactos) para repintar al cambiar visibilidad
        self._ext = 20.0
        self._n_fps, self._t_fps = 0, time.perf_counter()
        self.lbl_fps = QtWidgets.QLabel(self)
        self.lbl_fps.setStyleSheet("color:#c8c8c8; background:rgba(0,0,0,110); padding:2px 6px;"
                                   "font:9pt 'Consolas';")
        self.lbl_fps.move(8, 8)
        self.lbl_fps.setText("-- FPS")
        self.lbl_fps.adjustSize()

    # ------------------------------------------------------------------
    def set_geometria(self, res) -> None:
        """res: ResultadoPerfil con patron_* / pinon_* / diente_centros_* (motor.generar_patron())."""
        self._geom = res
        if res is None or res.patron_x is None:
            for it in (self.c_patron, self.c_pinon, self.c_paso_eng, self.c_paso_pin, self.c_roll_act,
                       self.c_accion, self.s_contactos, self.s_centro, self.c_base, self.c_camino):
                it.clear() if hasattr(it, "clear") else None
            return
        self._lineal = res.radio_paso_engranaje is None
        self.c_patron.setData(res.patron_x, res.patron_y)
        rr = res.radio_rodillo or 1.0
        self.c_pinon.setData(*_circulos(res.pinon_centros_x, res.pinon_centros_y, rr))
        if self._lineal:        # línea de paso de la cremallera (se traslada con el patrón)
            self.c_paso_eng.setData(res.linea_paso_cremallera_x, res.linea_paso_cremallera_y)
        else:
            self.c_paso_eng.setData(*_circulos(0.0, 0.0, res.radio_paso_engranaje, 128))
        self.c_paso_pin.setData(*_circulos(0.0, 0.0, res.radio_paso_pinon or 0.0, 96))
        self._construir_capas_opcionales(res)
        ext_patron = float(np.nanmax(np.abs(np.concatenate((res.patron_x, res.patron_y))))) * 1.15
        r_pinon = 0.0
        if not self._lineal:    # el piñón orbita a cd: debe caber completo en "Ver todo"
            r_pinon = 1.1 * (res.distancia_centros_pinon
                             + float(np.max(np.hypot(res.pinon_centros_x, res.pinon_centros_y))) + rr)
        self._ext = max(ext_patron, r_pinon, 1.0)
        self._rehacer_etiquetas(len(res.pinon_centros_x), len(res.diente_centros_x))
        self.resetear_camara()
        if self._ultimo is not None:
            self.actualizar(*self._ultimo)

    def _construir_capas_opcionales(self, res) -> None:
        """Camino de contacto (res.camino_contacto_*) con la rotación de vista. La curva base
        la entrega la ventana con set_curva_base()."""
        rv = math.radians(res.rotacion_vista_grados)
        if res.camino_contacto_x is not None:
            self.c_camino.setData(*_rot(np.asarray(res.camino_contacto_x), np.asarray(res.camino_contacto_y), rv))

    def set_curva_base(self, x, y) -> None:
        """Curva generatriz base (sin offset), ya en el marco de vista."""
        self.c_base.setData(np.asarray(x), np.asarray(y))

    def _rehacer_etiquetas(self, n_rod: int, n_dient: int) -> None:
        for t in self._labels_rod + self._labels_dient:
            self.removeItem(t)
        f = QtGui.QFont("Consolas", 8)
        self._color_rod = pg.getConfigOption("foreground")
        self._color_dient = (150, 200, 255) if pg.getConfigOption("foreground")[0] > 128 else (20, 90, 170)

        def nuevo(txt, color):
            ti = pg.TextItem(txt, color=color, anchor=(0, 1))
            ti.setFont(f)
            self.addItem(ti, ignoreBounds=True)
            return ti
        self._labels_rod = [nuevo(str(k), self._color_rod) for k in range(n_rod)]
        self._labels_dient = [nuevo(str(k), self._color_dient) for k in range(n_dient)]

    def set_tema(self, oscuro: bool) -> None:
        """Recolorea lo que depende del fondo (etiquetas, piñón, patrón, FPS)."""
        self._color_rod = (255, 255, 255) if oscuro else (20, 20, 20)
        self._color_dient = (150, 200, 255) if oscuro else (20, 90, 170)
        for t in self._labels_rod:
            t.setColor(self._color_rod)
        for t in self._labels_dient:
            t.setColor(self._color_dient)
        self.c_pinon.setPen(pg.mkPen(C_PINON if oscuro else (190, 125, 0), width=1))
        self.c_patron.setPen(pg.mkPen(C_PATRON if oscuro else (25, 90, 200), width=1))
        self.c_roll_act.setPen(pg.mkPen((255, 235, 120) if oscuro else (200, 140, 0), width=2.2))
        self.c_base.setPen(pg.mkPen(C_BASE if oscuro else (30, 130, 50), width=1, style=QtCore.Qt.PenStyle.DashLine))
        self.c_camino.setPen(pg.mkPen(C_CAMINO if oscuro else (120, 50, 190), width=1.6))
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
    def actualizar(self, estado, contactos) -> None:
        """estado: EstadoCinematico; contactos: lista de dicts de rodillos_en_contacto()."""
        self._ultimo = (estado, contactos)
        g, v = self._geom, self._vis
        if g is None or g.patron_x is None:
            return
        cx, cy = estado.centro_pinon
        spin = estado.angulo_pinon_rad

        if self._lineal:        # la cremallera se TRASLADA (solo si el piñón es el fijo)
            dx, dy = (0.0, 0.0) if estado.patron_fijo else estado.traslacion_patron
            for it in (self.c_patron, self.c_base, self.c_paso_eng):
                it.setPos(dx, dy)

            def a_patron(x, y):
                return x + dx, y + dy
        else:                   # el engranaje GIRA
            ang_pat = 0.0 if estado.patron_fijo else estado.angulo_patron_rad
            self.c_patron.setRotation(math.degrees(ang_pat))
            self.c_base.setRotation(math.degrees(ang_pat))

            def a_patron(x, y):
                return _rot(x, y, ang_pat)

        # Capas por modo: camino de contacto SOLO con el piñón fijo (camino estático); curva base SOLO
        # con el patrón fijo (piñón orbitando/trasladándose).
        alterno = estado.patron_fijo
        self.c_base.setVisible(v.curva_base and alterno)
        self.c_camino.setVisible(v.camino_de_contacto and not alterno)
        self.c_pinon.setPos(cx, cy)
        self.c_pinon.setRotation(math.degrees(spin))
        self.s_centro.setData([cx], [cy])
        self.c_paso_pin.setPos(cx, cy)
        self.c_paso_eng.setVisible(v.circulos_de_paso)
        self.c_paso_pin.setVisible(v.circulos_de_paso)

        if contactos and v.puntos_de_contacto:
            px = np.array([c["punto_contacto"][0] for c in contactos])
            py = np.array([c["punto_contacto"][1] for c in contactos])
            self.s_contactos.setData(*a_patron(px, py))
            lx = np.array([g.pinon_centros_x[c["indice"]] for c in contactos])
            ly = np.array([g.pinon_centros_y[c["indice"]] for c in contactos])
            wx, wy = _rot(lx, ly, spin)
            self.c_roll_act.setData(*_circulos(cx + wx, cy + wy, g.radio_rodillo or 1.0, 24))
        else:
            self.s_contactos.setData([], [])
            self.c_roll_act.setData([], [])

        if contactos and v.lineas_de_accion:
            xs, ys = [], []
            for c in contactos:
                if "punto_cir" not in c:
                    continue
                a = a_patron(*c["punto_contacto"])
                b = a_patron(*c["punto_cir"])
                xs += [a[0], b[0]]; ys += [a[1], b[1]]
            self.c_accion.setData(xs, ys)
        else:
            self.c_accion.setData([], [])

        mostrar = v.etiquetas_de_rodillo
        for t in self._labels_rod + self._labels_dient:
            t.setVisible(mostrar)
        if mostrar:
            wx, wy = _rot(np.asarray(g.pinon_centros_x), np.asarray(g.pinon_centros_y), spin)
            for k, t in enumerate(self._labels_rod):
                t.setPos(cx + wx[k], cy + wy[k])
            tx, ty = a_patron(np.asarray(g.diente_centros_x), np.asarray(g.diente_centros_y))
            for k, t in enumerate(self._labels_dient):
                t.setPos(tx[k], ty[k])

        self._n_fps += 1
        ahora = time.perf_counter()
        if ahora - self._t_fps >= 0.5:
            fps = self._n_fps / (ahora - self._t_fps)
            self.lbl_fps.setText(f"{fps:5.1f} FPS ({1000.0 / max(fps, 1e-6):5.1f} ms)")
            self.lbl_fps.adjustSize()
            self._n_fps, self._t_fps = 0, ahora

    def fotograma(self) -> QtGui.QImage:
        """Captura de la vista tal cual se ve (para la grabación de video)."""
        return self.grab().toImage()
