# -*- coding: utf-8 -*-
"""
ui/property_windows.py

Ventanas de propiedades que se abren desde el menú "Propiedades físicas" de EpitrocoidalV2.
Son ventanas INDEPENDIENTES (no cierran ni ocultan la principal): se pueden abrir varias a la
vez y todas se refrescan cuando cambian los parámetros (señal `perfilActualizado`).

  - VentanaPerfilDiente  -> ToothProfile_Window.py : tabla de puntos + perfil en PyQtGraph.
  - VentanaPropiedad     -> Graficas_Window.py     : una sola clase para Ángulo de presión,
    Radio de curvatura y Camino de contacto (cambia `tipo`). Dos tablas (coordenadas de la
    gráfica / rodillos activos) y un dial que mueve θ del piñón, igual que el slider del Excel:
    marca sobre la gráfica el punto donde está cada rodillo en contacto.

NOTA: ToothProfile_Window.py y Graficas_Window.py definen ambos la clase `Ui_Graficas_Window`
(mismo nombre generado por Qt Designer); aquí se importan con alias para no pisarse.
"""
from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtWidgets

from engine.cinematica_engine import SolverCinematico
from ui.errores import manejador_seguro
from widgets.pg_helpers import (AngleControl, InspectorCurvas, configurar_menu_plot, desactivar_clic_leyenda,
                                reemplazar_widget)

from Graficas_Window import Ui_Graficas_Window as Ui_Propiedad          # noqa: E402
from ToothProfile_Window import Ui_Graficas_Window as Ui_PerfilDiente   # noqa: E402


def _llenar_tabla(tabla: QtWidgets.QTableWidget, columnas, encabezados, fmt="{:.6g}") -> None:
    tabla.setUpdatesEnabled(False)
    tabla.clearContents()
    tabla.setColumnCount(len(encabezados))
    tabla.setHorizontalHeaderLabels(encabezados)
    tabla.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    n = len(columnas[0]) if columnas else 0
    tabla.setRowCount(n)
    for j, col in enumerate(columnas):
        for i, v in enumerate(col):
            tabla.setItem(i, j, QtWidgets.QTableWidgetItem(v if isinstance(v, str) else fmt.format(v)))
    tabla.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    tabla.setUpdatesEnabled(True)


def _plot_base(aspecto_1a1: bool, x: str, y: str, titulo: str = "grafica") -> pg.PlotWidget:
    p = pg.PlotWidget()
    p.showGrid(x=True, y=True, alpha=0.25)
    p.setLabel("bottom", x)
    p.setLabel("left", y)
    if aspecto_1a1:
        p.setAspectLocked(True)
    return configurar_menu_plot(p, titulo, geometrica=aspecto_1a1)


class _VentanaAuxiliar(QtWidgets.QMainWindow):
    """Base: se destruye al cerrar y sigue a la ventana principal."""

    def __init__(self, principal, ui_cls, titulo: str):
        super().__init__(principal)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.principal = principal
        self.ui = ui_cls()
        self.ui.setupUi(self)
        self.setWindowTitle(titulo)
        principal.perfilActualizado.connect(self._refrescar)

    @manejador_seguro
    def _refrescar(self, *_):
        raise NotImplementedError


class VentanaPerfilDiente(_VentanaAuxiliar):
    def __init__(self, principal):
        super().__init__(principal, Ui_PerfilDiente, "Perfil del diente")
        self.plot = reemplazar_widget(self.ui.graphicsView, _plot_base(True, "X (mm)", "Y (mm)", "perfil_diente"))
        self.c_gen = self.plot.plot(pen=pg.mkPen((136, 136, 136), style=QtCore.Qt.PenStyle.DotLine), name="Curva generatriz")
        self.c_off = self.plot.plot(pen=pg.mkPen((31, 111, 235), width=1), name="Perfil (offset)")
        desactivar_clic_leyenda(self.plot.addLegend(offset=(10, 10)))
        self.inspector = InspectorCurvas(self.plot, lambda: [self.c_gen, self.c_off])
        self._primera = True
        if principal.perfil_actual is not None:
            self._refrescar(principal.perfil_actual)

    @manejador_seguro
    def _refrescar(self, r=None):
        r = r or self.principal.perfil_actual
        if r is None:
            return
        self.c_gen.setData(r.curva_x, r.curva_y)
        self.c_off.setData(r.offset_x, r.offset_y)
        if self._primera:
            self.plot.autoRange(); self._primera = False
        _llenar_tabla(self.ui.table_coordinates, [r.theta, r.offset_x, r.offset_y],
                      ["θ (rad)", "X (mm)", "Y (mm)"])


class VentanaPropiedad(_VentanaAuxiliar):
    # tipo -> (título, etiqueta X, etiqueta Y, aspecto 1:1)
    TIPOS = {
        "angulo": ("Ángulo de presión", "θ (rad)", "Ángulo de presión (°)", False),
        "curvatura": ("Radio de curvatura", "θ (rad)", "Radio de curvatura (mm)", False),
        "contacto": ("Camino de contacto", "X (mm)", "Y (mm)", True),
    }

    def __init__(self, principal, tipo: str):
        titulo, lx, ly, aspecto = self.TIPOS[tipo]
        super().__init__(principal, Ui_Propiedad, titulo)
        self.tipo = tipo
        self.plot = reemplazar_widget(self.ui.graphicsView, _plot_base(aspecto, lx, ly, titulo))
        self.c_prop = self.plot.plot(pen=pg.mkPen((209, 36, 47) if tipo == "angulo"
                                                  else (26, 127, 55) if tipo == "curvatura" else (130, 80, 223), width=1.4))
        self.marcas = pg.ScatterPlotItem(size=10, pen=pg.mkPen("w"), brush=pg.mkBrush(230, 64, 64))
        self.plot.addItem(self.marcas)
        self.inspector = InspectorCurvas(self.plot, lambda: [self.c_prop])
        self._etiquetas: list[pg.TextItem] = []
        self._primera = True
        self.control = AngleControl(self.ui.dial_posicion_theta, self.ui.doubleSpinBox_posicion_theta, self)
        self.control.cambiado.connect(self._actualizar_rodillos)
        if principal.perfil_actual is not None:
            self._refrescar(principal.perfil_actual)

    # -- datos de la gráfica ------------------------------------------------
    def _serie(self, r):
        if self.tipo == "angulo":
            return r.theta, r.angulo_presion_grados, [r.theta, r.angulo_presion_grados], ["θ (rad)", "α (°)"]
        if self.tipo == "curvatura":
            return r.theta, r.radio_curvatura, [r.theta, r.radio_curvatura], ["θ (rad)", "ρ (mm)"]
        return (r.camino_contacto_x, r.camino_contacto_y,
                [r.theta, r.camino_contacto_x, r.camino_contacto_y], ["θ (rad)", "X (mm)", "Y (mm)"])

    @manejador_seguro
    def _refrescar(self, r=None):
        r = r or self.principal.perfil_actual
        if r is None:
            return
        x, y, cols, enc = self._serie(r)
        self.c_prop.setData(x, y)
        if self._primera:
            self.plot.autoRange()
            if self.tipo == "curvatura" and r.radio_curvatura_minimo:
                m = r.radio_curvatura_minimo        # como V1: recortar picos para ver la zona útil
                self.plot.setYRange(min(0.0, 0.9 * m), max(6.0 * m, m + 1.0))
            self._primera = False
        _llenar_tabla(self.ui.table_coordinates, cols, enc)
        self._actualizar_rodillos(self.control.acumulado)

    # -- rodillos activos ---------------------------------------------------
    @manejador_seguro
    def _actualizar_rodillos(self, angulo_grados: float):
        motor = self.principal.motor_actual
        if motor is None:
            return
        solver = SolverCinematico(motor.contexto)
        estado = solver.resolver("angular", True, False, angulo_grados, 0.0)   # piñón fijo, θ manual
        contactos = motor.rodillos_en_contacto(estado.angulo_relativo_generatriz_rad,
                                               modo_pinon_alterno=False, estado_cinematico=estado)
        puntos = []
        for c in contactos:
            th = c["theta_local"]
            if self.tipo == "angulo":
                px, py = th, c["angulo_presion_local_deg"]
            elif self.tipo == "curvatura":
                px, py = th, float(motor.radio_curvatura(np.float64(th)))
            else:
                cx, cy = motor.camino_de_contacto(np.float64(th))
                px, py = float(cx), float(cy)
            puntos.append((px, py, c["indice"]))
        self.marcas.setData([p[0] for p in puntos], [p[1] for p in puntos])
        for t in self._etiquetas:
            self.plot.removeItem(t)
        self._etiquetas = []
        for px, py, k in puntos:
            t = pg.TextItem(f"R{k}", color=pg.getConfigOption("foreground"), anchor=(0, 1))
            t.setPos(px, py)
            self.plot.addItem(t, ignoreBounds=True)
            self._etiquetas.append(t)
        filas = [[f"R{c['indice']}" for c in contactos], [str(c["indice_flanco"]) for c in contactos],
                 [c["theta_local"] for c in contactos], [c["punto_contacto"][0] for c in contactos],
                 [c["punto_contacto"][1] for c in contactos], [c["angulo_presion_local_deg"] for c in contactos]]
        _llenar_tabla(self.ui.table_Rodillos, filas,
                      ["Rodillo", "Diente", "θ local (rad)", "X (mm)", "Y (mm)", "α local (°)"])
