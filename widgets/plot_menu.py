# -*- coding: utf-8 -*-
"""
widgets/plot_menu.py

Menú contextual (clic derecho) PROPIO y en español para todas las gráficas de PyQtGraph.
Sustituye al menú en inglés de pyqtgraph: no depende de sus textos ni de sus internos.

  Ver todo · Eje X / Eje Y (autoescala, límites, escala log, invertir) · Modo de ratón ·
  Opciones de la gráfica (cuadrícula y, solo si se pide, Transformadas) · Exportar imagen…

"Ver todo" encuadra ÚNICAMENTE el contenido visible (curvas y puntos), ignorando cursor de
inspección, líneas infinitas, etiquetas y la leyenda. Una gráfica puede aportar su propio
proveedor de encuadre con `plot._ver_todo = callable` (la simulación lo usa).

Transformadas (solo línea de tiempo): ninguna / FFT / derivada / integral. El menú solo
guarda el modo y emite `transformadaCambiada`; quien dibuja aplica `transformar()` a sus datos.
"""
from __future__ import annotations

from functools import partial

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

TRANSFORMADAS = (("ninguna", "Ninguna"),
                 ("fft", "Espectro de potencia (FFT)"),
                 ("derivada", "Derivada (dy/dx)"),
                 ("integral", "Integral (∫ y dx)"))
_TIPOS_CONTENIDO = (pg.PlotDataItem, pg.PlotCurveItem, pg.ScatterPlotItem)


def etiqueta_eje_x(modo: str) -> tuple[str, str]:
    return ("Frecuencia", "Hz") if modo == "fft" else ("Tiempo", "s")


def transformar(modo: str, x, y):
    """Aplica la transformada `modo` a la curva (x, y). Devuelve (x', y')."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or modo == "ninguna":
        return x, y
    if modo == "fft":
        dt = (x[-1] - x[0]) / (len(x) - 1)
        if dt <= 0:
            return x, y
        f = np.fft.rfftfreq(len(y), dt)
        p = np.abs(np.fft.rfft(y - y.mean())) ** 2 / len(y) ** 2
        return f[1:], p[1:]
    if modo == "derivada":
        return x, np.gradient(y, x)
    if modo == "integral":
        return x, np.concatenate(([0.0], np.cumsum((y[:-1] + y[1:]) * 0.5 * np.diff(x))))
    return x, y


def limites_contenido(plot):
    """(xmin, xmax, ymin, ymax) del contenido visible, o None si no hay nada."""
    vb = plot.getPlotItem().vb
    x0 = y0 = np.inf
    x1 = y1 = -np.inf
    for it in list(vb.addedItems):
        if not isinstance(it, _TIPOS_CONTENIDO) or getattr(it, "_sin_encuadre", False) or not it.isVisible():
            continue
        p = it.pos()
        if p.x() or p.y() or it.rotation():      # items con transformación propia: no se miden
            continue
        try:
            x, y = it.getData()
        except Exception:
            continue
        if x is None or y is None or len(x) == 0:
            continue
        x, y = np.asarray(x, float), np.asarray(y, float)
        ok = np.isfinite(x) & np.isfinite(y)
        if not ok.any():
            continue
        x0, x1 = min(x0, x[ok].min()), max(x1, x[ok].max())
        y0, y1 = min(y0, y[ok].min()), max(y1, y[ok].max())
    return None if not np.isfinite(x0) else (x0, x1, y0, y1)


def _con_margen(lo: float, hi: float, frac: float = 0.05):
    d = hi - lo
    if d <= 0:
        d = abs(lo) * 0.1 or 1.0
        return lo - d, hi + d
    return lo - d * frac, hi + d * frac


UNIDADES_HUD = ("rpm", "rad/s", "°/s")


class MenuGrafica(QtCore.QObject):
    transformadaCambiada = QtCore.Signal(str)
    indicadoresCambiados = QtCore.Signal(dict)     # {"fps", "velocidades", "relacion", "unidad"}

    def __init__(self, plot: pg.PlotWidget, titulo: str, transformadas: bool = False, indicadores: bool = False):
        super().__init__(plot)
        self._plot, self._titulo = plot, titulo
        self.modo_transformada = "ninguna"
        self._log = {"x": False, "y": False}
        self._cuadricula = True
        pi = plot.getPlotItem()
        self._vb = pi.vb
        self._vb.setMenuEnabled(True)                # para que el clic derecho llegue a raiseContextMenu
        self._vb.raiseContextMenu = self._mostrar     # y aquí se muestra NUESTRO menú
        plot.scene().contextMenu = []                 # sin el "Export..." genérico de la escena
        self._acc: dict = {}
        self._indicadores = {"fps": True, "velocidades": True, "relacion": False, "unidad": "rpm", "amplificacion": 1}
        self._con_indicadores = indicadores
        self._menu = self._construir(transformadas)

    # ------------------------------------------------------------------ construcción
    @staticmethod
    def _accion(menu, texto, slot, checkable=False, grupo=None):
        a = QtGui.QAction(texto, menu)
        if checkable:
            a.setCheckable(True)
            a.toggled.connect(lambda v, f=slot: f(v))
        else:
            a.triggered.connect(lambda *_, f=slot: f())
        if grupo is not None:
            grupo.addAction(a)
        menu.addAction(a)
        return a

    def _construir(self, transformadas: bool) -> QtWidgets.QMenu:
        m = QtWidgets.QMenu(self._plot)
        self._accion(m, "Ver todo", partial(self.ver_todo, "xy"))
        for eje in ("x", "y"):
            sub = m.addMenu(f"Eje {eje.upper()}")
            self._accion(sub, "Autoescala", partial(self.ver_todo, eje))
            self._accion(sub, "Establecer límites…", partial(self._fijar_limites, eje))
            self._acc[f"log_{eje}"] = self._accion(sub, "Escala logarítmica", partial(self._set_log, eje), True)
            self._acc[f"inv_{eje}"] = self._accion(sub, "Invertir eje", partial(self._invertir, eje), True)
        raton = m.addMenu("Modo de ratón")
        g = QtGui.QActionGroup(raton)
        self._acc["pan"] = self._accion(raton, "Desplazar", partial(self._modo_raton, False), True, g)
        self._acc["zoom"] = self._accion(raton, "Zoom a una región", partial(self._modo_raton, True), True, g)
        opc = m.addMenu("Opciones de la gráfica")
        self._acc["grid"] = self._accion(opc, "Mostrar cuadrícula", self._set_grid, True)
        if transformadas:
            tr = opc.addMenu("Transformadas")
            gt = QtGui.QActionGroup(tr)
            for clave, texto in TRANSFORMADAS:
                self._acc[f"tr_{clave}"] = self._accion(tr, texto, partial(self._set_transformada, clave), True, gt)
        if self._con_indicadores:          # HUD de las ventanas de simulación (FPS, velocidades, relación, unidades)
            ind = opc.addMenu("Indicadores en pantalla")
            for clave, texto in (("fps", "FPS"), ("velocidades", "Velocidades instantáneas (entrada y salida)"),
                                 ("relacion", "Relación de transmisión instantánea")):
                self._acc[f"hud_{clave}"] = self._accion(ind, texto, partial(self._set_indicador, clave), True)
            uni = ind.addMenu("Unidades angulares")
            gu = QtGui.QActionGroup(uni)
            for u in UNIDADES_HUD:
                self._acc[f"hud_u_{u}"] = self._accion(uni, u, partial(self._set_unidad_hud, u), True, gu)
            nota = QtGui.QAction("La cremallera se muestra siempre en mm/s", uni)
            nota.setEnabled(False)
            uni.addAction(nota)
            amp = ind.addMenu("Amplificación de deformaciones (contacto)")
            ga = QtGui.QActionGroup(amp)
            for f in (1, 10, 100, 1000):
                self._acc[f"hud_a_{f}"] = self._accion(amp, f"×{f}", partial(self._set_amplificacion, f), True, ga)
        m.addSeparator()
        self._accion(m, "Exportar imagen…", self._exportar)
        m.aboutToShow.connect(self._sincronizar)
        return m

    def _sincronizar(self):
        estado = {"log_x": self._log["x"], "log_y": self._log["y"],
                  "inv_x": self._vb.xInverted(), "inv_y": self._vb.yInverted(),
                  "grid": self._cuadricula,
                  "zoom": self._vb.state["mouseMode"] == pg.ViewBox.RectMode}
        estado["pan"] = not estado["zoom"]
        for clave, _ in TRANSFORMADAS:
            estado[f"tr_{clave}"] = clave == self.modo_transformada
        for clave in ("fps", "velocidades", "relacion"):
            estado[f"hud_{clave}"] = self._indicadores.get(clave, False)
        for u in UNIDADES_HUD:
            estado[f"hud_u_{u}"] = self._indicadores.get("unidad") == u
        for f in (1, 10, 100, 1000):
            estado[f"hud_a_{f}"] = int(self._indicadores.get("amplificacion", 1)) == f
        for k, v in estado.items():
            a = self._acc.get(k)
            if a is not None:
                a.blockSignals(True)
                a.setChecked(bool(v))
                a.blockSignals(False)

    def _mostrar(self, ev=None):
        self._menu.popup(QtGui.QCursor.pos())

    # ------------------------------------------------------------------ acciones
    def ver_todo(self, ejes: str = "xy"):
        propio = getattr(self._plot, "_ver_todo", None)
        if ejes == "xy" and propio is not None:
            propio()
            return
        lim = limites_contenido(self._plot)
        if lim is None:
            self._vb.autoRange()
            return
        x0, x1, y0, y1 = lim
        if "x" in ejes:
            self._vb.setXRange(*_con_margen(x0, x1), padding=0)
        if "y" in ejes:
            self._vb.setYRange(*_con_margen(y0, y1), padding=0)

    def _fijar_limites(self, eje: str):
        actual = self._vb.viewRange()[0 if eje == "x" else 1]
        ventana = self._plot.window()
        bajo, ok = QtWidgets.QInputDialog.getDouble(ventana, "Límites del eje", f"Eje {eje.upper()} · mínimo",
                                                    float(actual[0]), -1e12, 1e12, 6)
        if not ok:
            return
        alto, ok = QtWidgets.QInputDialog.getDouble(ventana, "Límites del eje", f"Eje {eje.upper()} · máximo",
                                                    float(actual[1]), -1e12, 1e12, 6)
        if not ok:
            return
        if alto <= bajo:
            QtWidgets.QMessageBox.warning(ventana, "Límites del eje", "El máximo debe ser mayor que el mínimo.")
            return
        (self._vb.setXRange if eje == "x" else self._vb.setYRange)(bajo, alto, padding=0)

    def _set_log(self, eje: str, v: bool):
        self._log[eje] = bool(v)
        self._plot.getPlotItem().setLogMode(x=self._log["x"], y=self._log["y"])
        self.ver_todo("xy" if getattr(self._plot, "_ver_todo", None) is None else eje)

    def _invertir(self, eje: str, v: bool):
        (self._vb.invertX if eje == "x" else self._vb.invertY)(bool(v))

    def _modo_raton(self, region: bool, marcado: bool):
        if marcado:
            self._vb.setMouseMode(pg.ViewBox.RectMode if region else pg.ViewBox.PanMode)

    def _set_grid(self, v: bool):
        self._cuadricula = bool(v)
        self._plot.showGrid(x=v, y=v, alpha=0.25 if v else 0.0)

    def _set_transformada(self, clave: str, marcado: bool):
        if marcado and clave != self.modo_transformada:
            self.modo_transformada = clave
            self.transformadaCambiada.emit(clave)

    def set_indicadores(self, d: dict) -> None:
        self._indicadores = dict(self._indicadores, **d)

    def indicadores(self) -> dict:
        return dict(self._indicadores)

    def _set_indicador(self, clave: str, v: bool):
        self._indicadores[clave] = bool(v)
        self.indicadoresCambiados.emit(dict(self._indicadores))

    def _set_amplificacion(self, f: int, marcado: bool):
        if marcado:
            self._indicadores["amplificacion"] = int(f)
            self.indicadoresCambiados.emit(dict(self._indicadores))

    def _set_unidad_hud(self, u: str, marcado: bool):
        if marcado:
            self._indicadores["unidad"] = u
            self.indicadoresCambiados.emit(dict(self._indicadores))

    def _exportar(self):
        from exporters.image_exporter import exportar_con_dialogo
        exportar_con_dialogo(self._plot, self._plot.window(), self._titulo)
