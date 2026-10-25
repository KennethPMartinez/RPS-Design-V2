# -*- coding: utf-8 -*-
"""
widgets/pg_helpers.py

Utilidades compartidas por las ventanas de V2 (antes cada ventana repetía esta lógica):
  - configurar_pyqtgraph(): opciones globales ANTES de crear cualquier widget de pg.
  - reemplazar_widget(): sustituye un placeholder de Qt Designer (QGraphicsView / QWidget
    vacío) por otro widget, en la misma celda de su layout.
  - AngleControl: dial + spinbox con encoder incremental (ángulo acumulado, vueltas
    incluidas). Mismo comportamiento que system_window.py de V1, extraído en una clase
    para usarlo en EpitrocoidalV2 y en Graficas_Window.
"""
from __future__ import annotations

import weakref

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

COLORES_TEMA = {True: {"bg": (28, 28, 33), "fg": (210, 210, 210)},
                False: {"bg": (255, 255, 255), "fg": (30, 30, 30)}}
_PLOTS: "weakref.WeakSet" = weakref.WeakSet()   # todos los PlotWidget vivos (tema / OpenGL en caliente)


def configurar_pyqtgraph(usar_opengl: bool = False, oscuro: bool = True) -> None:
    c = COLORES_TEMA[oscuro]
    pg.setConfigOptions(antialias=True, useOpenGL=usar_opengl, enableExperimental=False,
                        background=c["bg"], foreground=c["fg"])


def configurar_menu_plot(plot: pg.PlotWidget, titulo: str, geometrica: bool = False) -> pg.PlotWidget:
    """Menú contextual (clic derecho) de PyQtGraph: View All, X Axis, Y Axis, Mouse Mode y
    Plot Options -- TODAS menos 'Transforms'. En gráficas geométricas (perfil, camino de
    contacto, simulación) también se ocultan Downsample/Average, que no tienen sentido sobre
    una curva X-Y cerrada. Reemplaza 'Export...' de pyqtgraph por el exportador propio de
    imágenes (exporters/image_exporter.py) y registra el plot para tema / OpenGL en caliente."""
    from exporters.image_exporter import exportar_con_dialogo
    pi = plot.getPlotItem()
    pi.setMenuEnabled(True)
    pi.setContextMenuActionVisible("Transforms", False)
    if geometrica:
        pi.setContextMenuActionVisible("Downsample", False)
        pi.setContextMenuActionVisible("Average", False)
    plot.scene().contextMenu = []                       # quita 'Export...' genérico
    vb = pi.vb
    vb.menu.addSeparator()
    accion = vb.menu.addAction("Exportar imagen…")
    accion.triggered.connect(lambda *_: exportar_con_dialogo(plot, plot.window(), titulo))
    plot._accion_exportar = accion
    _PLOTS.add(plot)
    return plot


def desactivar_clic_leyenda(legend) -> None:
    """Por defecto, clic en una muestra de la leyenda oculta/muestra su curva: para eso están
    los checkbox de la UI, así que se anula."""
    for muestra, _ in legend.items:
        muestra.mouseClickEvent = lambda ev: None


def retemar_plots(oscuro: bool) -> None:
    c = COLORES_TEMA[oscuro]
    pg.setConfigOptions(background=c["bg"], foreground=c["fg"])
    for p in list(_PLOTS):
        try:
            p.setBackground(c["bg"])
            pi = p.getPlotItem()
            for ax in ("left", "bottom", "top", "right"):
                a = pi.getAxis(ax)
                a.setPen(pg.mkPen(c["fg"])); a.setTextPen(pg.mkPen(c["fg"]))
            if hasattr(p, "set_tema"):
                p.set_tema(oscuro)
        except RuntimeError:        # widget C++ ya destruido
            pass


def aplicar_opengl(activo: bool, parent=None) -> bool:
    """Cambia el viewport de TODAS las gráficas abiertas a/desde OpenGL sin reiniciar, con
    barra de progreso. Los plots que se creen después heredan la opción global."""
    if activo:      # sin contexto OpenGL válido el viewport queda en blanco: no se cambia nada
        ctx = QtGui.QOpenGLContext()
        if not ctx.create():
            print("[pg_helpers] OpenGL no disponible en este equipo; se mantiene el render por software.")
            return False
    pg.setConfigOptions(useOpenGL=activo)
    plots = [p for p in list(_PLOTS)]
    dlg = QtWidgets.QProgressDialog("Cambiando el render de las gráficas…", None, 0, max(1, len(plots)), parent)
    dlg.setWindowTitle("OpenGL" if activo else "Render por software")
    dlg.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
    dlg.setMinimumDuration(0); dlg.setCancelButton(None)
    ok = True
    for i, p in enumerate(plots):
        dlg.setLabelText(f"Cambiando el render de las gráficas… ({i + 1}/{len(plots)})")
        dlg.setValue(i)
        QtWidgets.QApplication.processEvents()
        try:
            p.useOpenGL(activo)
            p.getPlotItem().update()
        except Exception as e:      # driver sin soporte, etc.
            print(f"[pg_helpers] useOpenGL({activo}) falló: {e}")
            ok = False
    dlg.setValue(max(1, len(plots)))
    dlg.close()
    return ok


class InspectorCurvas(QtCore.QObject):
    """Cursor de inspección (como en Test_GráficaPyQTGraph.py): cruz de líneas punteadas que
    sigue al ratón; si hay un punto de alguna curva visible a <= `umbral_px` píxeles, la cruz
    se ancla a él y muestra nombre de la curva y coordenadas (X, Y) reales del dato."""

    def __init__(self, plot: pg.PlotWidget, curvas_fn, umbral_px: float = 14.0):
        super().__init__(plot)
        self.plot, self.vb = plot, plot.getPlotItem().vb
        self._curvas_fn, self._umbral = curvas_fn, umbral_px
        pen = pg.mkPen((230, 140, 30), width=1, style=QtCore.Qt.PenStyle.DashLine)
        self.v = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.h = pg.InfiniteLine(angle=0, movable=False, pen=pen)
        self.punto = pg.ScatterPlotItem(size=9, pen=None, brush=pg.mkBrush(230, 64, 64))
        self.texto = pg.TextItem(anchor=(0, 1), color=(255, 255, 255), fill=pg.mkBrush(0, 0, 0, 190))
        for it in (self.v, self.h, self.punto, self.texto):
            plot.addItem(it, ignoreBounds=True)
            it.setZValue(1000)
        self._ocultar()
        plot._inspector = self
        plot.scene().sigMouseMoved.connect(self._mover)

    def _ocultar(self):
        for it in (self.v, self.h, self.punto, self.texto):
            it.hide()

    def _mover(self, pos):
        if not self.plot.isVisible() or not self.vb.sceneBoundingRect().contains(pos):
            self._ocultar()
            return
        mp = self.vb.mapSceneToView(pos)
        mx, my = mp.x(), mp.y()
        pw, ph = self.vb.viewPixelSize()
        mejor = None
        for c in self._curvas_fn():
            if not c.isVisible():
                continue
            x, y = c.getData()
            if x is None or len(x) == 0:
                continue
            x, y = np.asarray(x, float), np.asarray(y, float)
            d2 = ((x - mx) / pw) ** 2 + ((y - my) / ph) ** 2
            d2[~(np.isfinite(x) & np.isfinite(y))] = np.inf
            i = int(np.argmin(d2))
            if np.isfinite(d2[i]) and (mejor is None or d2[i] < mejor[0]):
                mejor = (d2[i], x[i], y[i], c)
        self.v.show(); self.h.show()
        if mejor is not None and mejor[0] ** 0.5 <= self._umbral:
            _, sx, sy, curva = mejor
            nombre = curva.name() if hasattr(curva, "name") and curva.name() else ""
            self.v.setPos(sx); self.h.setPos(sy)
            self.punto.setData([sx], [sy]); self.punto.show()
            self.texto.setText((f"{nombre}\n" if nombre else "") + f"X: {sx:.6g}\nY: {sy:.6g}")
            self.texto.setPos(sx, sy); self.texto.show()
        else:
            self.v.setPos(mx); self.h.setPos(my)
            self.punto.hide()
            self.texto.setText(f"X: {mx:.4g}\nY: {my:.4g}"); self.texto.setPos(mx, my); self.texto.show()


def reemplazar_widget(placeholder: QtWidgets.QWidget, nuevo: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """Pone `nuevo` donde estaba `placeholder` (misma fila/columna/span si es grid)."""
    padre = placeholder.parentWidget()
    layout = padre.layout() if padre is not None else None
    if layout is None:  # contenedor sin layout (p. ej. widget_grafica): se le crea uno
        layout = QtWidgets.QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(nuevo)
        return nuevo
    nuevo.setParent(padre)
    idx = layout.indexOf(placeholder)
    if isinstance(layout, QtWidgets.QGridLayout) and idx != -1:
        fila, col, sf, sc = layout.getItemPosition(idx)
        layout.removeWidget(placeholder)
        placeholder.hide(); placeholder.setParent(None); placeholder.deleteLater()
        layout.addWidget(nuevo, fila, col, sf, sc)
    elif idx != -1:
        layout.removeWidget(placeholder)
        placeholder.hide(); placeholder.setParent(None); placeholder.deleteLater()
        layout.insertWidget(idx, nuevo)
    else:
        layout.addWidget(nuevo)
    return nuevo


def embeber_en_contenedor(contenedor: QtWidgets.QWidget, nuevo: QtWidgets.QWidget) -> None:
    """Para QWidgets vacíos tipo 'widget_grafica' que se usan como contenedor."""
    layout = contenedor.layout() or QtWidgets.QVBoxLayout(contenedor)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(nuevo)


class AngleControl(QtCore.QObject):
    """Dial (rango [90, 450] con wrapping, 0° visual arriba) + spinbox [0, 360].

    `acumulado` = vueltas*360 + ángulo del dial (encoder incremental). Emite `cambiado`
    solo cuando el USUARIO mueve dial/spin; `mostrar()` actualiza los widgets sin emitir
    (la usa el modo automático para que el dial siga a la simulación).
    """
    cambiado = QtCore.Signal(float)

    def __init__(self, dial, spin, parent=None):
        super().__init__(parent)
        self.dial, self.spin = dial, spin
        self.acumulado = float(spin.value())
        self._previo = self.acumulado % 360.0
        dial.valueChanged.connect(self._desde_dial)
        spin.valueChanged.connect(self._desde_spin)

    def _acumular(self, local: float) -> None:
        delta = local - self._previo
        if delta > 180.0:
            delta -= 360.0
        elif delta < -180.0:
            delta += 360.0
        self.acumulado += delta
        self._previo = local

    def _desde_dial(self, valor_dial: int) -> None:
        local = float(valor_dial - 90)
        self.spin.blockSignals(True); self.spin.setValue(local); self.spin.blockSignals(False)
        self._acumular(local)
        self.cambiado.emit(self.acumulado)

    def _desde_spin(self, valor: float) -> None:
        self.dial.blockSignals(True); self.dial.setValue(90 + int(valor) % 360); self.dial.blockSignals(False)
        self._acumular(float(valor))
        self.cambiado.emit(self.acumulado)

    def mostrar(self, angulo_grados: float) -> None:
        """Refleja un ángulo externo en dial y spin sin emitir ni alterar el acumulado manual."""
        local = angulo_grados % 360.0
        for w, v in ((self.spin, local), (self.dial, 90 + int(local) % 360)):
            w.blockSignals(True); w.setValue(v); w.blockSignals(False)

    def reiniciar(self, angulo_grados: float = 0.0) -> None:
        self.acumulado = float(angulo_grados)
        self._previo = angulo_grados % 360.0
        self.mostrar(angulo_grados)
