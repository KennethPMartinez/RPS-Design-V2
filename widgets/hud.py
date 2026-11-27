# -*- coding: utf-8 -*-
"""
widgets/hud.py

HUD de las vistas de simulación (funciones 48–51) y capa de fuerzas de contacto calculadas (función 47).

  - FPS (medido del render, como antes) + velocidades instantáneas de entrada y salida + relación de
    transmisión instantánea, en rpm, rad/s o °/s (mm/s para la cremallera).
  - Las velocidades NUNCA se derivan del tiempo entre fotogramas: llegan de `LineaTiempo.vel` (modo
    automático) o de estados calculados. En modo manual no hay velocidad definida («—»).
  - La relación instantánea se obtiene del MAPA cinemático d(salida)/d(entrada), así que está definida
    incluso con velocidades nulas; si la salida no se mueve con la entrada se informa «∞» y si la relación
    no es determinable, «—». Conserva el signo (sentido de giro).
Opciones persistentes en QSettings («RPSDesign/V2», clave hud/v1), editables desde el menú contextual:
Opciones de la gráfica → Indicadores en pantalla.
"""
from __future__ import annotations

import json
import math

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore

UNIDADES = ("rpm", "rad/s", "°/s")
DEFECTO = {"fps": True, "velocidades": True, "relacion": False, "unidad": "rpm", "amplificacion": 1}
AMPLIFICACIONES = (1, 10, 100, 1000)
_CLAVE = "hud/v1"


def cargar_opciones() -> dict:
    try:
        raw = QtCore.QSettings("RPSDesign", "V2").value(_CLAVE)
        d = dict(DEFECTO, **json.loads(str(raw))) if raw else dict(DEFECTO)
    except Exception:
        d = dict(DEFECTO)
    if d.get("unidad") not in UNIDADES:
        d["unidad"] = "rpm"
    return d


def guardar_opciones(d: dict) -> None:
    try:
        QtCore.QSettings("RPSDesign", "V2").setValue(_CLAVE, json.dumps(d))
    except Exception:
        pass


def convertir_angular(deg_s: float, unidad: str) -> float:
    if unidad == "rpm":
        return deg_s / 6.0
    if unidad == "rad/s":
        return math.radians(deg_s)
    return deg_s


def texto_velocidades(w_in_deg_s, w_out, salida_lineal: bool, unidad: str, fmt) -> str:
    """w_in en °/s; w_out en °/s (o mm/s si la salida es lineal). None => «—» (sin velocidad definida)."""
    if w_in_deg_s is None or not np.isfinite(w_in_deg_s):
        return "ω entrada: —   ·   salida: —  (sin velocidad definida en modo manual)"
    ent = f"ω entrada: {fmt(convertir_angular(w_in_deg_s, unidad), unidad)}"
    if w_out is None or not np.isfinite(w_out):
        return ent + "   ·   salida: —"
    sal = fmt(w_out, "mm/s") if salida_lineal else fmt(convertir_angular(w_out, unidad), unidad)
    return f"{ent}   ·   {'v' if salida_lineal else 'ω'} salida: {sal}"


def texto_relacion(rel, salida_lineal: bool, fmt) -> str:
    """rel = d(salida)/d(entrada) [°/° o mm/°]. Para angulares se muestra i = ω_ent/ω_sal = 1/rel."""
    if rel is None or not np.isfinite(rel):
        return "i: — (no determinable)"
    if salida_lineal:
        return f"v/ω = {fmt(rel * 180.0 / math.pi, 'mm/rad')}"
    if abs(rel) < 1e-15:
        return "i = ω_ent/ω_sal: ∞ (salida inmóvil)"
    return f"i = ω_ent/ω_sal = {fmt(1.0 / rel)}"


class HUDMixin:
    """Para SimulationView y PlanetaryView (ambas tienen `lbl_fps`)."""

    def _init_hud(self):
        self.hud = cargar_opciones()
        self._hud_fps_txt = "-- FPS"
        self._hud_datos = None
        self.c_fuerzas = pg.PlotCurveItem(pen=pg.mkPen((255, 80, 200), width=2), connect="pairs")
        self.c_fuerzas._sin_encuadre = True
        self.s_fuerzas = pg.ScatterPlotItem(size=7, pen=None, brush=pg.mkBrush(255, 80, 200))
        self.s_fuerzas._sin_encuadre = True
        self.addItem(self.c_fuerzas, ignoreBounds=True)
        self.addItem(self.s_fuerzas, ignoreBounds=True)
        self._fuerzas_txt = ""
        menu = getattr(self, "_menu", None)
        if menu is not None and hasattr(menu, "indicadoresCambiados"):
            menu.set_indicadores(self.hud)
            menu.indicadoresCambiados.connect(self._opciones_hud)

    def _opciones_hud(self, d: dict):
        self.hud = dict(self.hud, **d)
        guardar_opciones(self.hud)
        self._pintar_hud()
        cb = getattr(self, "on_hud_cambiado", None)
        if cb is not None:                 # p. ej. la amplificación cambia lo que se dibuja
            cb()

    def set_datos_hud(self, w_in, w_out, salida_lineal: bool, rel) -> None:
        self._hud_datos = (w_in, w_out, salida_lineal, rel)
        self._pintar_hud()

    def _hud_fps(self, texto: str) -> None:
        self._hud_fps_txt = texto
        self._pintar_hud()

    def _pintar_hud(self):
        from utils.formato_numerico import fmt
        lineas = []
        if self.hud.get("fps", True):
            lineas.append(self._hud_fps_txt)
        if self._hud_datos is not None:
            w_in, w_out, lin, rel = self._hud_datos
            if self.hud.get("velocidades", True):
                t = texto_velocidades(w_in, w_out, lin, self.hud.get("unidad", "rpm"), fmt)
                if getattr(self, "manual_estimada", False) and w_in is not None:
                    t += "  (manual: derivada del control respecto al reloj real)"
                lineas.append(t)
            if self.hud.get("relacion", False):
                lineas.append(texto_relacion(rel, lin, fmt))
        if self._fuerzas_txt:
            amp = self.hud.get("amplificacion", 1)
            lineas.append(self._fuerzas_txt + (f" · deformación ×{amp}" if amp and amp != 1 else ""))
        self.lbl_fps.setVisible(bool(lineas))
        self.lbl_fps.setText("\n".join(lineas))
        self.lbl_fps.adjustSize()

    # -- fuerzas calculadas sobre la geometría ----------------------------------------------------
    def set_fuerzas(self, px=None, py=None, fx=None, fy=None, texto: str = "") -> None:
        """Flechas de la fuerza normal SOBRE el rodillo en cada punto de contacto (mundo, mm/N)."""
        if px is None or len(px) == 0:
            self.c_fuerzas.setData([], [])
            self.s_fuerzas.setData([], [])
            self._fuerzas_txt = texto
            self._pintar_hud()
            return
        px, py, fx, fy = (np.asarray(v, float) for v in (px, py, fx, fy))
        fmax = float(np.nanmax(np.hypot(fx, fy))) if len(fx) else 0.0
        escala = 0.18 * getattr(self, "_ext", 20.0) / fmax if fmax > 0 else 0.0
        xs = np.empty(2 * len(px)); ys = np.empty(2 * len(px))
        xs[0::2], ys[0::2] = px, py
        xs[1::2], ys[1::2] = px + escala * fx, py + escala * fy
        self.c_fuerzas.setData(xs, ys)
        self.s_fuerzas.setData(px, py)
        self._fuerzas_txt = texto
        self._pintar_hud()
