# -*- coding: utf-8 -*-
"""
ui/velocity_profile_window.py

Controlador de Perfildevelocidad_simulador_Window ("Editar línea de tiempo"): editor del perfil de
giro de la rueda motriz para el modo AUTOMÁTICO (modelo/motores en engine/motion_engine.py).

  Aceptar  -> emite `perfilAceptado(PerfilMovimiento)` y cierra.   Cancelar -> cierra sin cambios.

Páginas del QStackedWidget: 0 rampas · 1 sinusoidal · 2 polinómica · 3 lista de puntos · 4 spline.
Menú contextual de la gráfica: en español, con Transformadas (FFT, derivada, integral) que solo
cambian lo que se DIBUJA; el perfil no se toca.
"""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtWidgets

from engine.motion_engine import (LEYES, MAX_COEFICIENTES, UNIDADES, FabricaPresets, LineaTiempo,
                                  PerfilMovimiento, RegistroLeyes, Tramo, escalar_perfil)
from ui.errores import manejador_seguro
from widgets.plot_menu import etiqueta_eje_x, transformar
from widgets.pg_helpers import (InspectorCurvas, configurar_menu_plot, desactivar_clic_leyenda, embeber_en_contenedor,
                                reemplazar_widget)
from widgets.wheel_widget import WheelWidget

from Perfildevelocidad_simulador_Window import Ui_GiroImpuesto_window   # noqa: E402

_PAG = {"Sinusoidal": 1, "Polinómica": 2, "Lista de puntos": 3, "Spline": 4}   # el resto -> 0
_VELOCIDADES = ["0.25×", "0.5×", "1×", "2×", "4×"]


def _rango(sp, lo, hi, dec, paso=0.1):
    sp.setRange(lo, hi); sp.setDecimals(dec); sp.setSingleStep(paso); sp.setKeyboardTracking(False)


class VentanaPerfilVelocidad(QtWidgets.QMainWindow):
    perfilAceptado = QtCore.Signal(object)

    def __init__(self, perfil: PerfilMovimiento, parent=None, rango=None):
        super().__init__(parent)
        self._rango = rango            # (mín, máx) ° del recorrido permitido (Trocoidal) o None
        self._msg_preset = ""
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.ui = Ui_GiroImpuesto_window()
        self.ui.setupUi(self)
        self.reg = RegistroLeyes()
        self.perfil = copy.deepcopy(perfil)
        self.lt: LineaTiempo | None = None
        self._cargando = False
        self._t = 0.0
        self._velocidad = 1.0
        self._reproduciendo = False
        self._construir_widgets()
        self._conectar()
        self._sincronizar_todo(0)
        self._marcar_curva_de_entrada()
        self._recalcular()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------ construcción
    def _construir_widgets(self):
        u = self.ui
        self.plot = pg.PlotWidget()
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setLabel("bottom", "Tiempo", units="s")
        self.plot.hideButtons()                      # sin el botón "A" (autorango) de pyqtgraph
        desactivar_clic_leyenda(self.plot.addLegend(offset=(10, 10)))
        configurar_menu_plot(self.plot, "linea_de_tiempo", transformadas=True)
        self.plot._menu.transformadaCambiada.connect(self._transformada_cambiada)
        self.curvas = {
            "Posición": self.plot.plot(pen=pg.mkPen((192, 57, 43), width=1.4), name="Posición"),
            "Velocidad": self.plot.plot(pen=pg.mkPen((44, 160, 44), width=1.6), name="Velocidad"),
            "Aceleración": self.plot.plot(pen=pg.mkPen((36, 104, 215), width=1.2), name="Aceleración"),
        }
        self.marca_tramo = pg.ScatterPlotItem(size=9, pen=None, brush=pg.mkBrush("#e74c3c"))
        self.plot.addItem(self.marca_tramo)
        self.inspector = InspectorCurvas(self.plot, lambda: list(self.curvas.values()))
        embeber_en_contenedor(u.widget_grafica, self.plot)
        self.rueda = reemplazar_widget(u.graphicsView_ruedamovil, WheelWidget())
        self.checks = {"Posición": u.checkBox_Posicion, "Velocidad": u.checkBox_Velocidad,
                       "Aceleración": u.checkBox_Aceleracion}

        for sp in (u.doubleSpinBox_tiempoini, u.doubleSpinBox_tiempofin):
            _rango(sp, -1e6, 1e6, 4)
        for sp in (u.doubleSpinBox_yini, u.doubleSpinBox_yfin, u.doubleSpinBox_pendientegen,
                   u.doubleSpinBox_amplitud, u.doubleSpinBox_Fase, u.doubleSpinBox_pendienteini,
                   u.doubleSpinBox_pendientefin):
            _rango(sp, -1e9, 1e9, 6)
        _rango(u.doubleSpinBox_frecuencia, 0.0, 1e6, 6)
        u.spinBox_gradocurva.setRange(0, MAX_COEFICIENTES - 1)
        _rango(u.doubleSpinBox_5, 0.0, 1.0, 3)
        u.comboBox_4.addItems(_VELOCIDADES); u.comboBox_4.setCurrentText("1×")
        for tabla, cols in ((u.tableWidget_coeficientes, ["Coeficiente"]), (u.tableWidget_listapuntos, ["X (s)", "Y"]),
                            (u.tableWidget_Listapuntosspline, ["X (s)", "Y"])):
            tabla.setColumnCount(len(cols)); tabla.setHorizontalHeaderLabels(cols)
            tabla.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def _conectar(self):
        u = self.ui
        u.pushButton_Aplicar_preset.clicked.connect(self._aplicar_preset)
        u.listWidget_tramo.currentRowChanged.connect(self._tramo_seleccionado)
        u.pushButton_ponertramo.clicked.connect(self._poner_tramo)
        u.pushButton_quitartramo.clicked.connect(self._quitar_tramo)
        for sp in (u.doubleSpinBox_tiempoini, u.doubleSpinBox_tiempofin, u.doubleSpinBox_yini, u.doubleSpinBox_yfin):
            sp.valueChanged.connect(self._intervalo_cambiado)
        u.listWidget_Ley.currentRowChanged.connect(self._ley_seleccionada)
        u.pushButton_ponerfuncion.clicked.connect(self._poner_ley)
        u.pushButton_quitarfuncion.clicked.connect(self._quitar_ley)
        u.pushButton_reemplazarfuncion.clicked.connect(self._reemplazar_ley)
        for sp in (u.doubleSpinBox_pendientegen, u.doubleSpinBox_amplitud, u.doubleSpinBox_frecuencia,
                   u.doubleSpinBox_Fase, u.doubleSpinBox_pendienteini, u.doubleSpinBox_pendientefin,
                   u.spinBox_gradocurva):
            sp.valueChanged.connect(self._params_cambiados)
        for tabla in (u.tableWidget_coeficientes, u.tableWidget_listapuntos, u.tableWidget_Listapuntosspline):
            tabla.itemChanged.connect(self._params_cambiados)
        u.pushButton_ponercoeficiente.clicked.connect(lambda: self._fila_tabla(u.tableWidget_coeficientes, 1))
        u.pushButton_quitarcoeficiente.clicked.connect(lambda: self._fila_tabla(u.tableWidget_coeficientes, -1))
        u.pushButton_ponerpunto.clicked.connect(lambda: self._fila_tabla(u.tableWidget_listapuntos, 1))
        u.pushButton_quitarpunto.clicked.connect(lambda: self._fila_tabla(u.tableWidget_listapuntos, -1))
        u.pushButton_ponerpuntospline.clicked.connect(lambda: self._fila_tabla(u.tableWidget_Listapuntosspline, 1))
        u.pushButton_quitarpuntospline.clicked.connect(lambda: self._fila_tabla(u.tableWidget_Listapuntosspline, -1))
        for c in self.checks.values():
            c.toggled.connect(self._actualizar_curvas)
        u.pushButton_reproducir.clicked.connect(self._reproducir)
        u.pushButton_pausar.clicked.connect(self._pausar)
        u.pushButton_Reiniciar.clicked.connect(self._reiniciar)
        u.doubleSpinBox_5.valueChanged.connect(self._buscar)
        u.comboBox_4.currentTextChanged.connect(lambda s: setattr(self, "_velocidad", float(s.replace("×", ""))))
        u.pushButton_9.clicked.connect(self._aceptar)
        u.pushButton_10.clicked.connect(self.close)
        u.actionAbrid.triggered.connect(self._abrir)
        u.actionGuardar.triggered.connect(self._guardar)
        u.actionExportar_CSV.triggered.connect(self._exportar_csv)
        u.actionCerra.triggered.connect(self.close)
        u.actionGu_a_Tecnica.triggered.connect(lambda: QtWidgets.QMessageBox.information(
            self, "Guía técnica", "La guía técnica se desarrollará más adelante."))

    # ------------------------------------------------------------------ selección y listas
    def _tramo(self):
        i = self.ui.listWidget_tramo.currentRow()
        return self.perfil.tramos[i] if 0 <= i < len(self.perfil.tramos) else None

    def _ley(self):
        t, i = self._tramo(), self.ui.listWidget_Ley.currentRow()
        return t.leyes[i] if t is not None and 0 <= i < len(t.leyes) else None

    def _sincronizar_todo(self, tramo_sel: int, ley_sel: int = 0):
        self._cargando = True
        self.perfil.tramos.sort(key=lambda t: t.inicio)
        lw = self.ui.listWidget_tramo
        lw.blockSignals(True); lw.clear()
        for i, t in enumerate(self.perfil.tramos):
            lw.addItem(f"{i + 1}. {t.inicio:g}–{t.fin:g} s")
        lw.setCurrentRow(max(0, min(tramo_sel, lw.count() - 1)))
        lw.blockSignals(False)
        self._cargando = False
        self._cargar_intervalo()
        self._sincronizar_leyes(ley_sel)

    def _cargar_intervalo(self):
        t = self._tramo()
        if t is None:
            return
        u = self.ui
        self._cargando = True
        for sp, v in ((u.doubleSpinBox_tiempoini, t.inicio), (u.doubleSpinBox_tiempofin, t.fin),
                      (u.doubleSpinBox_yini, t.y_ini), (u.doubleSpinBox_yfin, t.y_fin)):
            sp.blockSignals(True); sp.setValue(v); sp.blockSignals(False)
        u.groupBox_5.setTitle(f"Intervalo · {self.perfil.propiedad} ({UNIDADES[self.perfil.propiedad]})")
        self._cargando = False

    def _sincronizar_leyes(self, sel: int = 0):
        t, lw = self._tramo(), self.ui.listWidget_Ley
        self._cargando = True
        lw.blockSignals(True); lw.clear()
        if t is not None:
            for i, ley in enumerate(t.leyes):
                lw.addItem(f"{i + 1}. {ley.nombre}")
            if t.leyes:
                lw.setCurrentRow(max(0, min(sel, len(t.leyes) - 1)))
        lw.blockSignals(False)
        self._cargando = False
        self._mostrar_params()

    @manejador_seguro
    def _tramo_seleccionado(self, fila):
        if self._cargando or fila < 0:
            return
        self._cargar_intervalo()
        self._sincronizar_leyes(0)
        self._actualizar_marcas()

    @manejador_seguro
    def _ley_seleccionada(self, fila):
        if not self._cargando:
            self._mostrar_params()

    # ------------------------------------------------------------------ parámetros de la ley
    def _mostrar_params(self):
        u, t, ley = self.ui, self._tramo(), self._ley()
        self._cargando = True
        if t is None or ley is None:
            self._cargando = False
            return
        p = ley.params
        pag = _PAG.get(ley.nombre, 0)
        u.stackedWidget.setCurrentIndex(pag)
        if pag == 0:
            pend = p.get("pendiente")
            idx = t.leyes.index(ley)
            por_defecto = (t.y_fin - t.y_ini) / t.duracion if idx == 0 else 0.0
            u.doubleSpinBox_pendientegen.setValue(por_defecto if pend is None else float(pend))
        elif pag == 1:
            u.doubleSpinBox_amplitud.setValue(float(p.get("amplitud", 10.0)))
            u.doubleSpinBox_frecuencia.setValue(float(p.get("frecuencia", 1.0)))
            u.doubleSpinBox_Fase.setValue(float(p.get("fase", 0.0)))
        elif pag == 2:
            self._poner_tabla(u.tableWidget_coeficientes, [[c] for c in p.get("coeficientes", [0.0])],
                              [f"a{i}" for i in range(len(p.get("coeficientes", [0.0])))])
        elif pag == 3:
            u.spinBox_gradocurva.setValue(int(p.get("grado", 1)))
            self._poner_tabla(u.tableWidget_listapuntos, p.get("puntos", []))
        else:
            u.doubleSpinBox_pendienteini.setValue(float(p.get("pendiente_ini", 0.0)))
            u.doubleSpinBox_pendientefin.setValue(float(p.get("pendiente_fin", 0.0)))
            self._poner_tabla(u.tableWidget_Listapuntosspline, p.get("puntos", []))
        self._cargando = False

    @staticmethod
    def _poner_tabla(tabla, filas, etiquetas=None):
        tabla.blockSignals(True)
        tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, v in enumerate(fila):
                tabla.setItem(i, j, QtWidgets.QTableWidgetItem(f"{float(v):.6g}"))
        if etiquetas:
            tabla.setVerticalHeaderLabels(etiquetas)
        tabla.blockSignals(False)

    @staticmethod
    def _leer_tabla(tabla):
        filas = []
        for i in range(tabla.rowCount()):
            try:
                filas.append([float(tabla.item(i, j).text()) for j in range(tabla.columnCount())])
            except (AttributeError, ValueError):
                pass
        return filas

    @manejador_seguro
    def _params_cambiados(self, *_):
        if self._cargando:
            return
        u, ley, t = self.ui, self._ley(), self._tramo()
        if ley is None:
            return
        pag = _PAG.get(ley.nombre, 0)
        if pag == 0:
            ley.params["pendiente"] = u.doubleSpinBox_pendientegen.value()   # manual
        elif pag == 1:
            ley.params.update(amplitud=u.doubleSpinBox_amplitud.value(), frecuencia=u.doubleSpinBox_frecuencia.value(),
                              fase=u.doubleSpinBox_Fase.value())
        elif pag == 2:
            ley.params["coeficientes"] = [f[0] for f in self._leer_tabla(u.tableWidget_coeficientes)]
        elif pag == 3:
            ley.params.update(grado=u.spinBox_gradocurva.value(), puntos=self._leer_tabla(u.tableWidget_listapuntos))
        else:
            ley.params.update(pendiente_ini=u.doubleSpinBox_pendienteini.value(),
                              pendiente_fin=u.doubleSpinBox_pendientefin.value(),
                              puntos=self._leer_tabla(u.tableWidget_Listapuntosspline))
        self._recalcular()

    @manejador_seguro
    def _fila_tabla(self, tabla, signo: int):
        ley, t = self._ley(), self._tramo()
        if ley is None or t is None:
            return
        n = tabla.rowCount()
        if signo > 0:
            if tabla is self.ui.tableWidget_coeficientes:
                if n >= MAX_COEFICIENTES:
                    return
                fila = [0.0]
            else:
                pts = self._leer_tabla(tabla)
                fila = ([(pts[-2][0] + pts[-1][0]) / 2, (pts[-2][1] + pts[-1][1]) / 2] if len(pts) >= 2
                        else [t.fin, t.y_fin])
            filas = self._leer_tabla(tabla) + [fila]
            if tabla is not self.ui.tableWidget_coeficientes:
                filas.sort(key=lambda f: f[0])
        else:
            minimo = 1 if tabla is self.ui.tableWidget_coeficientes else 2
            if n <= minimo:
                return
            fila_sel = tabla.currentRow() if tabla.currentRow() >= 0 else n - 1
            filas = self._leer_tabla(tabla)
            filas.pop(min(fila_sel, len(filas) - 1))
        self._poner_tabla(tabla, filas, [f"a{i}" for i in range(len(filas))]
                          if tabla is self.ui.tableWidget_coeficientes else None)
        self._params_cambiados()

    # ------------------------------------------------------------------ tramos y leyes
    @manejador_seguro
    def _intervalo_cambiado(self, *_):
        t = self._tramo()
        if self._cargando or t is None:
            return
        u = self.ui
        ini, fin = u.doubleSpinBox_tiempoini.value(), u.doubleSpinBox_tiempofin.value()
        if fin <= ini:
            self.statusBar().showMessage("El final del tramo debe ser mayor que el inicio.", 4000)
            return
        t.inicio, t.fin = ini, fin
        t.y_ini, t.y_fin = u.doubleSpinBox_yini.value(), u.doubleSpinBox_yfin.value()
        for ley in t.leyes:     # los extremos de las leyes por puntos siguen al tramo
            pts = ley.params.get("puntos")
            if ley.nombre in ("Spline", "Lista de puntos") and pts and len(pts) >= 2:
                pts[0], pts[-1] = [ini, t.y_ini], [fin, t.y_fin]
        self._sincronizar_todo(self.perfil.tramos.index(t), self.ui.listWidget_Ley.currentRow())
        self._recalcular()

    @manejador_seguro
    def _poner_tramo(self, *_):
        tr = sorted(self.perfil.tramos, key=lambda x: x.inicio)
        if tr:
            ult = tr[-1]
            nuevo = Tramo(ult.fin, ult.fin + max(1.0, ult.duracion * 0.5), ult.y_fin, ult.y_fin)
        else:
            nuevo = Tramo(0.0, 5.0, 0.0, 0.0)
        nuevo.leyes = [self.reg.nueva_ley("Rampa lineal")]
        self.perfil.tramos.append(nuevo)
        self._sincronizar_todo(sorted(self.perfil.tramos, key=lambda x: x.inicio).index(nuevo))
        self._recalcular()

    @manejador_seguro
    def _quitar_tramo(self, *_):
        t = self._tramo()
        if t is None:
            return
        if len(self.perfil.tramos) == 1:
            QtWidgets.QMessageBox.information(self, "Tramos", "El perfil debe conservar al menos un tramo.")
            return
        i = self.perfil.tramos.index(t)
        self.perfil.tramos.remove(t)
        self._sincronizar_todo(max(0, i - 1))
        self._recalcular()

    def _nueva(self, nombre, t, aditiva):
        return self.reg.nueva_ley(nombre, t, aditiva)

    @manejador_seguro
    def _poner_ley(self, *_):
        t = self._tramo()
        if t is None:
            return
        if any(l.nombre == "Spline" for l in t.leyes):
            QtWidgets.QMessageBox.information(self, "Spline", "Spline es independiente: no admite sumar otras leyes en el mismo tramo.")
            return
        nombre = self.ui.comboBox_tipodefuncion.currentText()
        if nombre == "Spline":
            t.leyes = [self._nueva(nombre, t, False)]
        else:
            t.leyes.append(self._nueva(nombre, t, bool(t.leyes)))
        self._sincronizar_leyes(len(t.leyes) - 1)
        self._recalcular()

    @manejador_seguro
    def _reemplazar_ley(self, *_):
        t = self._tramo()
        if t is None:
            return
        nombre = self.ui.comboBox_tipodefuncion.currentText()
        fila = max(0, self.ui.listWidget_Ley.currentRow())
        if nombre == "Spline" or not t.leyes:
            t.leyes = [self._nueva(nombre, t, False)]; fila = 0
        else:
            t.leyes[fila] = self._nueva(nombre, t, fila > 0)
        self._sincronizar_leyes(fila)
        self._recalcular()

    @manejador_seguro
    def _quitar_ley(self, *_):
        t, fila = self._tramo(), self.ui.listWidget_Ley.currentRow()
        if t is None or not (0 <= fila < len(t.leyes)):
            return
        t.leyes.pop(fila)
        self._sincronizar_leyes(max(0, fila - 1))
        self._recalcular()

    @manejador_seguro
    def _aplicar_preset(self, *_):
        self._pausar()
        self.perfil = self._encajar_preset(FabricaPresets.crear(self.ui.comboBox_preset.currentText()))
        self._sincronizar_todo(0)
        self._marcar_curva_de_entrada()
        self._t = 0.0
        self._recalcular()
        if self._msg_preset:
            self.statusBar().showMessage(self._msg_preset, 6000)
            self._msg_preset = ""
        if self._msg_preset:
            self.statusBar().showMessage(self._msg_preset, 6000)
            self._msg_preset = ""
        if self._msg_preset:
            self.statusBar().showMessage(self._msg_preset, 6000)
            self._msg_preset = ""

    def _encajar_preset(self, perfil):
        """Con un rango de recorrido el preset se escala para que el piñón no se salga."""
        if self._rango is None:
            return perfil
        lo, hi = self._rango
        try:
            pmin, pmax = LineaTiempo.construir(perfil, RegistroLeyes(), 1600).rango_posicion()
        except Exception:
            return perfil
        if pmax - pmin <= hi - lo + 1e-9:
            return perfil
        f = 0.999 * (hi - lo) / (pmax - pmin)
        self._msg_preset = f"Preset escalado ×{f:.3f} para caber en el recorrido del piñón ({hi - lo:.1f}°)."
        return escalar_perfil(perfil, f)

    def _marcar_curva_de_entrada(self):
        for nombre, c in self.checks.items():
            c.blockSignals(True); c.setChecked(nombre == self.perfil.propiedad); c.blockSignals(False)

    # ------------------------------------------------------------------ cálculo y gráficas
    def _recalcular(self):
        try:
            self.lt = LineaTiempo.construir(self.perfil, self.reg, 1600)
        except Exception as e:
            self.statusBar().showMessage(f"Perfil inválido: {e}", 6000)
            return
        if self.lt.errores:
            self.statusBar().showMessage("Aviso: " + " | ".join(self.lt.errores[-3:]), 6000)
        else:
            self.statusBar().clearMessage()
            if self._rango is not None:
                pmin, pmax = self.lt.rango_posicion()
                if pmax - pmin > self._rango[1] - self._rango[0] + 1e-9:
                    self.statusBar().showMessage("El perfil excede el recorrido del piñón: la simulación lo recortará.", 8000)
        sp = self.ui.doubleSpinBox_5
        sp.blockSignals(True); sp.setRange(self.lt.t_ini, self.lt.t_fin); sp.blockSignals(False)
        self._t = min(max(self._t, self.lt.t_ini), self.lt.t_fin)
        self._actualizar_curvas()
        self._actualizar_marcas()
        self._mostrar_tiempo(self._t)

    def _actualizar_curvas(self, *_):
        """Dibuja las curvas aplicando la transformada elegida en el menú contextual (solo visual)."""
        if self.lt is None:
            return
        modo = self.plot._menu.modo_transformada
        datos = {"Posición": self.lt.pos, "Velocidad": self.lt.vel, "Aceleración": self.lt.acc}
        for nombre, curva in self.curvas.items():
            x, y = transformar(modo, self.lt.t, datos[nombre])
            curva.setData(x, y)
            curva.setVisible(self.checks[nombre].isChecked())
        self.marca_tramo.setVisible(modo == "ninguna")      # las marcas de tramo solo tienen sentido en el tiempo

    @manejador_seguro
    def _transformada_cambiada(self, modo: str):
        etiqueta, unidad = etiqueta_eje_x(modo)
        self.plot.setLabel("bottom", etiqueta, units=unidad)
        self._actualizar_curvas()
        self.plot._menu.ver_todo()

    def _actualizar_marcas(self):
        t = self._tramo()
        if self.lt is None or t is None:
            return
        v = {"Posición": self.lt.pos, "Velocidad": self.lt.vel, "Aceleración": self.lt.acc}[self.perfil.propiedad]
        ys = np.interp([t.inicio, t.fin], self.lt.t, v)
        self.marca_tramo.setData([t.inicio, t.fin], list(ys))

    # ------------------------------------------------------------------ reproducción
    def _mostrar_tiempo(self, t: float):
        if self.lt is None:
            return
        self._t = t
        self.rueda.set_angle(self.lt.posicion_en(t))
        dur = max(self.lt.duracion, 1e-9)
        self.ui.progressBar.setValue(int(round((t - self.lt.t_ini) / dur * 100)))
        sp = self.ui.doubleSpinBox_5
        sp.blockSignals(True); sp.setValue(t); sp.blockSignals(False)

    def _buscar(self, t):
        self._mostrar_tiempo(float(t))

    def _reproducir(self):
        if self.lt is None:
            return
        if self._t >= self.lt.t_fin:
            self._t = self.lt.t_ini
        self._reproduciendo = True
        self.timer.start()

    def _pausar(self):
        self._reproduciendo = False
        if hasattr(self, "timer"):
            self.timer.stop()

    def _reiniciar(self):
        self._pausar()
        if self.lt is not None:
            self._mostrar_tiempo(self.lt.t_ini)

    @manejador_seguro
    def _tick(self):
        t = self._t + self.timer.interval() / 1000.0 * self._velocidad
        if t >= self.lt.t_fin:
            t = self.lt.t_fin
            self._pausar()
        self._mostrar_tiempo(t)

    # ------------------------------------------------------------------ archivo
    @manejador_seguro
    def _aceptar(self, *_):
        self.perfil.validar()
        self.perfilAceptado.emit(copy.deepcopy(self.perfil))
        self.close()

    @manejador_seguro
    def _guardar(self, *_):
        ruta, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar perfil de movimiento", "perfil_movimiento.json", "JSON (*.json)")
        if ruta:
            self.perfil.validar()
            Path(ruta).write_text(json.dumps(self.perfil.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @manejador_seguro
    def _abrir(self, *_):
        ruta, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir perfil de movimiento", "", "JSON (*.json)")
        if not ruta:
            return
        self._pausar()
        self.perfil = PerfilMovimiento.from_dict(json.loads(Path(ruta).read_text(encoding="utf-8")))
        self._sincronizar_todo(0)
        self._marcar_curva_de_entrada()
        self._recalcular()

    @manejador_seguro
    def _exportar_csv(self, *_):
        if self.lt is None:
            return
        ruta, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar datos", "movimiento.csv", "CSV (*.csv)")
        if not ruta:
            return
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["t_s", "posicion_deg", "velocidad_deg_s", "aceleracion_deg_s2"])
            w.writerows(zip(self.lt.t, self.lt.pos, self.lt.vel, self.lt.acc))

    def closeEvent(self, e):
        self._pausar()
        super().closeEvent(e)
