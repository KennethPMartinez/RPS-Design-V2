# -*- coding: utf-8 -*-
"""
ui/planetary_property_windows.py

Ventanas de "Propiedades físicas" del planetario (reutilizan los helpers de ui/property_windows.py):
  - VentanaPerfilDientePlanetario -> ToothProfile_Window_PlanetarioV2.py (sol y anular).
  - VentanaPropiedadPlanetario    -> Graficas_Window_PlanetarioV2.py: ángulo de presión / radio de curvatura /
    camino de contacto de sol y anular, con los rodillos en contacto en el ángulo de ENTRADA elegido
    (movimiento real: componente bloqueado y entrada de la ventana principal).
"""
from __future__ import annotations

import math

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore

from ui.errores import manejador_seguro
from ui.property_windows import _llenar_tabla, _plot_base, _VentanaAuxiliar
from widgets.pg_helpers import AngleControl, InspectorCurvas, desactivar_clic_leyenda, reemplazar_widget

from Graficas_Window_PlanetarioV2 import Ui_Graficas_Window as Ui_PropPlan          # noqa: E402
from ToothProfile_Window_PlanetarioV2 import Ui_Graficas_Window as Ui_DientePlan    # noqa: E402


class VentanaPerfilDientePlanetario(_VentanaAuxiliar):
    def __init__(self, principal):
        super().__init__(principal, Ui_DientePlan, "Perfil del diente — planetario")
        u = self.ui
        self._v = {}
        for clave, vista, tabla in (("sol", u.graphicsView_sun, u.table_coordinates_sun),
                                    ("anular", u.graphicsView_anular, u.table_coordinates_anular)):
            plot = reemplazar_widget(vista, _plot_base(True, "X (mm)", "Y (mm)", f"perfil_{clave}"))
            gen = plot.plot(pen=pg.mkPen((136, 136, 136), style=QtCore.Qt.PenStyle.DotLine), name="Curva generatriz")
            off = plot.plot(pen=pg.mkPen((31, 111, 235), width=1), name="Perfil (offset)")
            desactivar_clic_leyenda(plot.addLegend(offset=(10, 10)))
            InspectorCurvas(plot, lambda g=gen, o=off: [g, o])
            self._v[clave] = {"plot": plot, "gen": gen, "off": off, "tabla": tabla, "primera": True}
        if principal.perfil_actual is not None:
            self._refrescar(principal.perfil_actual)

    @manejador_seguro
    def _refrescar(self, eng=None):
        eng = eng or self.principal.perfil_actual
        if eng is None:
            return
        for clave, r in (("sol", eng.res_sol), ("anular", eng.res_anular)):
            g = self._v[clave]
            g["gen"].setData(r.curva_x, r.curva_y)
            g["off"].setData(r.offset_x, r.offset_y)
            if g["primera"]:
                g["plot"]._menu.ver_todo()
                g["primera"] = False
            _llenar_tabla(g["tabla"], [r.theta, r.offset_x, r.offset_y], ["θ (rad)", "X (mm)", "Y (mm)"])


class VentanaPropiedadPlanetario(_VentanaAuxiliar):
    TIPOS = {
        "angulo": ("Ángulo de presión", "θ (rad)", "Ángulo de presión (°)", False),
        "curvatura": ("Radio de curvatura", "θ (rad)", "Radio de curvatura (mm)", False),
        "contacto": ("Camino de contacto", "X (mm)", "Y (mm)", True),
    }

    def __init__(self, principal, tipo: str):
        titulo, lx, ly, aspecto = self.TIPOS[tipo]
        super().__init__(principal, Ui_PropPlan, titulo + " — planetario")
        u = self.ui
        self.tipo = tipo
        u.label_5.setText("Posición angular del\ncomponente de entrada θ (°)")
        self.control = AngleControl(u.dial_posicion_theta, u.doubleSpinBox_posicion_theta, self)
        color = (209, 36, 47) if tipo == "angulo" else (26, 127, 55) if tipo == "curvatura" else (130, 80, 223)
        self._g = {}
        for clave, vista, t_coord, t_rod in (
                ("sol", u.graphicsView_sun, u.table_coordinates_sun, u.table_Rodillos_sun),
                ("anular", u.graphicsView_anular, u.table_coordinates_anular, u.table_Rodillos_anular)):
            plot = reemplazar_widget(vista, _plot_base(aspecto, lx, ly, f"{tipo}_{clave}"))
            curva = plot.plot(pen=pg.mkPen(color, width=1.4))
            marcas = pg.ScatterPlotItem(size=10, pen=pg.mkPen("w"), brush=pg.mkBrush(230, 64, 64))
            plot.addItem(marcas)
            InspectorCurvas(plot, lambda c=curva: [c])
            self._g[clave] = {"plot": plot, "curva": curva, "marcas": marcas, "t_coord": t_coord,
                              "t_rod": t_rod, "etiquetas": [], "primera": True}
        self.control.cambiado.connect(self._actualizar_rodillos)
        if principal.perfil_actual is not None:
            self._refrescar(principal.perfil_actual)

    def _serie(self, r):
        if self.tipo == "angulo":
            return r.theta, r.angulo_presion_grados, [r.theta, r.angulo_presion_grados], ["θ (rad)", "α (°)"]
        if self.tipo == "curvatura":
            return r.theta, r.radio_curvatura, [r.theta, r.radio_curvatura], ["θ (rad)", "ρ (mm)"]
        return (r.camino_contacto_x, r.camino_contacto_y,
                [r.theta, r.camino_contacto_x, r.camino_contacto_y], ["θ (rad)", "X (mm)", "Y (mm)"])

    @manejador_seguro
    def _refrescar(self, eng=None):
        eng = eng or self.principal.perfil_actual
        if eng is None:
            return
        for clave, r in (("sol", eng.res_sol), ("anular", eng.res_anular)):
            g = self._g[clave]
            x, y, cols, enc = self._serie(r)
            g["curva"].setData(x, y)
            if g["primera"]:
                g["plot"]._menu.ver_todo()
                if self.tipo == "curvatura" and r.radio_curvatura_minimo:
                    m = r.radio_curvatura_minimo
                    g["plot"].setYRange(min(0.0, 0.9 * m), max(6.0 * m, m + 1.0))
                g["primera"] = False
            _llenar_tabla(g["t_coord"], cols, enc)
        self._actualizar_rodillos(self.control.acumulado)

    @manejador_seguro
    def _actualizar_rodillos(self, valor: float):
        eng = self.principal.motor_actual
        if eng is None:
            return
        cs, ca = eng.contactos(eng.estado(math.radians(valor)))
        for clave, motor, cont in (("sol", eng.sol, cs), ("anular", eng.anular, ca)):
            g = self._g[clave]
            puntos = []
            for c in cont:
                th = c["theta_local"]
                if self.tipo == "angulo":
                    px, py = th, c["angulo_presion_local_deg"]
                elif self.tipo == "curvatura":
                    px, py = th, float(motor.radio_curvatura(np.float64(th)))
                else:
                    cx, cy = motor.camino_de_contacto(np.float64(th))
                    px, py = float(cx), float(cy)
                puntos.append((px, py, c))
            g["marcas"].setData([p[0] for p in puntos], [p[1] for p in puntos])
            for t in g["etiquetas"]:
                g["plot"].removeItem(t)
            g["etiquetas"] = []
            for px, py, c in puntos:
                t = pg.TextItem(f"P{c['planeta'] + 1}·R{c['indice']}", color=pg.getConfigOption("foreground"),
                                anchor=(0, 1))
                t.setPos(px, py)
                g["plot"].addItem(t, ignoreBounds=True)
                g["etiquetas"].append(t)
            filas = [[f"P{c['planeta'] + 1}" for c in cont], [f"R{c['indice']}" for c in cont],
                     [str(c["indice_flanco"]) for c in cont], [c["theta_local"] for c in cont],
                     [c["punto_contacto"][0] for c in cont], [c["punto_contacto"][1] for c in cont],
                     [c["angulo_presion_local_deg"] for c in cont]]
            _llenar_tabla(g["t_rod"], filas,
                          ["Planeta", "Rodillo", "Diente", "θ local (rad)", "X (mm)", "Y (mm)", "α local (°)"])
