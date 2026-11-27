# -*- coding: utf-8 -*-
"""
ui/regimen_dinamico.py

Pestaña «Régimen dinámico / contacto» del editor de regímenes (Perfildevelocidad_simulador_Window.ui):
funciones 2–4, 9–23, 42–47, 52, 54–58, 62–64. Conecta los widgets del .ui (sin renombrarlos) con
`engine.estudio_fisico` a través del `GestorEstudio` de la ventana de sistema.

Los pocos campos que el .ui no trae (expresión del motor Custom, parámetros de la ley de carga, número de
muestras y costo del estudio) se crean en código DENTRO de las páginas existentes; si se añaden en Designer
con los mismos nombres (`editExpresionMotor`, `spinAmplitudCarga`, `spinFrecuenciaCarga`, `spinFaseCarga`,
`spinGradoCarga`, `spinPeriodoCarga`, `spinMuestrasEstudio`, `lblCostoEstudio`) se usan esos.

Identificación de curvas (función 16): [Prescrita] = trazo discontinuo, [Motor] = punteado (característica
del accionamiento), [Calculada] = continuo.
"""
from __future__ import annotations

import copy
import csv
import math

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtWidgets

from engine import accionamiento as acc
from engine import contacto_fisico as cf
from engine.cargas import CONSTANTE, DEP_OMEGA, DEP_T, DEP_THETA, DEPENDENCIAS, EN_ENTRADA, EN_SALIDA, CargaExterna
from engine.estudio_fisico import (ESCENARIO_LIBRE, ESCENARIO_NUEVO, ESCENARIO_PRESET, METODO_DINAMICO,
                                   METODO_ESTATICO, ConfigContacto, ConfigDinamica, ConfigSolucionador, Escenario)
from ui import estudio_qt as eq
from ui.errores import manejador_seguro
from utils.formato_numerico import fmt
from widgets.pg_helpers import configurar_menu_plot, desactivar_clic_leyenda, embeber_en_contenedor

DASH, DOT = QtCore.Qt.PenStyle.DashLine, QtCore.Qt.PenStyle.DotLine
C_PRES, C_CALC, C_MOT, C_AUX = (230, 126, 34), (41, 128, 185), (39, 174, 96), (142, 68, 173)


def _colores_tema():
    """[Prescrita], [Calculada], [Motor], auxiliar: colores técnicos del tema (se recalculan al retemar)."""
    global C_PRES, C_CALC, C_MOT, C_AUX
    from widgets.pg_helpers import color_tecnico
    C_PRES = color_tecnico("Piñón de rodillos", "#F2A33C")
    C_CALC = color_tecnico("Perfil / engranaje", "#388AE6")
    C_MOT = color_tecnico("Curva base", "#5DA878")
    C_AUX = color_tecnico("Línea de acción", "#AF85D5")
PALETA = [(41, 128, 185), (192, 57, 43), (39, 174, 96), (142, 68, 173), (243, 156, 18), (22, 160, 133),
          (211, 84, 0), (127, 140, 141), (44, 62, 80), (231, 76, 60)]


def _f(v, u: str = "") -> str:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return str(v)
    return "Indeterminado" if not math.isfinite(x) else fmt(x, u)


def _plot(contenedor, titulo: str, xl: str, xu: str, yl: str, yu: str) -> pg.PlotWidget:
    p = pg.PlotWidget()
    p.showGrid(x=True, y=True, alpha=0.25)
    p.setLabel("bottom", xl, units=xu)
    p.setLabel("left", yl, units=yu)
    p.hideButtons()
    p.addLegend(offset=(10, 10))
    configurar_menu_plot(p, titulo)
    embeber_en_contenedor(contenedor, p)
    return p


def _leer_tabla(tabla) -> list:
    filas = []
    for i in range(tabla.rowCount()):
        try:
            filas.append([float(tabla.item(i, j).text().replace(",", ".")) for j in range(tabla.columnCount())])
        except (AttributeError, ValueError):
            pass
    return filas


def _poner_tabla(tabla, filas) -> None:
    tabla.blockSignals(True)
    tabla.setRowCount(len(filas))
    for i, fila in enumerate(filas):
        for j, v in enumerate(fila):
            tabla.setItem(i, j, QtWidgets.QTableWidgetItem(repr(float(v)) if isinstance(v, float) else str(v)))
    tabla.blockSignals(False)


def _tabla_texto(tabla, filas) -> None:
    tabla.setUpdatesEnabled(False)
    tabla.setRowCount(len(filas))
    for i, fila in enumerate(filas):
        for j, v in enumerate(fila):
            it = QtWidgets.QTableWidgetItem(str(v))
            it.setFlags(it.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            tabla.setItem(i, j, it)
    tabla.setUpdatesEnabled(True)


def _leer_csv(ruta: str) -> list:
    filas = []
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(2048)
        f.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t")
        except csv.Error:
            dialecto = csv.excel
        for fila in csv.reader(f, dialecto):
            try:
                filas.append([float(fila[0].replace(",", ".")), float(fila[1].replace(",", "."))])
            except (ValueError, IndexError):
                continue                                # cabeceras o filas no numéricas
    return filas


class PanelRegimenDinamico(QtCore.QObject):
    def __init__(self, editor):
        super().__init__(editor)
        self.w = editor
        self.u = editor.ui
        self.gestor = getattr(editor.parent(), "gestor_estudio", None)
        self._cargando = False
        self._base = Escenario()             # versión guardada del escenario seleccionado (para «sin guardar»)
        self._seleccion = ESCENARIO_LIBRE
        self._t_cursor = None
        self._ad_cache = (None, None)
        self._crear_campos()
        self._crear_graficas()
        self._conectar()
        if self.gestor is None:
            self.u.tabDinamico.setEnabled(False)
            self.u.tabDinamico.setToolTip("Abra el editor desde una ventana de sistema para usar el régimen de contacto.")
            return
        self._poblar_combo_escenarios()
        self._escribir(self.gestor.escenario)
        self._base = copy.deepcopy(self.gestor.escenario)
        self._seleccion = self.gestor.seleccion if self.gestor.seleccion else ESCENARIO_LIBRE
        self._sel_combo(self._seleccion)
        self.gestor.estadoCambiado.connect(self._estado_gestor)
        self.gestor.progreso.connect(self._progreso)
        self.gestor.resultadoListo.connect(self._resultado_listo)      # métodos ligados: se desconectan solos al
        try:                                                           # destruirse el editor (WA_DeleteOnClose)
            from ui.ajustes_runtime import runtime
            runtime.cambiado.connect(self._ajustes_cambiaron)
        except Exception:
            pass
        self._estado_gestor(self.gestor.estado, self.gestor.detalle)
        self._tabla_componentes()
        self._actualizar_prescritas()
        if self.gestor.resultado is not None:
            self._mostrar_resultado()

    # ================================================================== construcción
    def _fila(self, layout, indice, etiqueta, widget, nombre):
        w = getattr(self.u, nombre, None)
        if w is not None:
            return w
        widget.setObjectName(nombre)
        fila = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(etiqueta)
        fila.addWidget(lbl)
        fila.addWidget(widget, 1)
        layout.insertLayout(indice, fila) if indice >= 0 else layout.addLayout(fila)
        setattr(self.u, nombre, widget)
        setattr(self.u, "lbl_" + nombre, lbl)
        return widget

    @staticmethod
    def _spin(lo, hi, dec, valor=0.0, sufijo=""):
        s = QtWidgets.QDoubleSpinBox()
        s.setRange(lo, hi); s.setDecimals(dec); s.setValue(valor); s.setKeyboardTracking(False)
        if sufijo:
            s.setSuffix(sufijo)
        return s

    def _crear_campos(self):
        u = self.u
        la = u.layoutPaginaAccionamiento
        i = la.indexOf(u.groupCurvaCaracteristica)
        e = QtWidgets.QLineEdit()
        e.setPlaceholderText("T(n) en N·m, n en rpm (w en rad/s). Ej.: 0.45*(1 - n/600)")
        self._fila(la, i, "Expresión T(n) (Custom)", e, "editExpresionMotor")
        self._fila(la, la.indexOf(u.groupCurvaCaracteristica),
                   "Inercia de entrada: motor + piñón (0 = sin masa)", self._spin(0, 1e9, 4, 0.0, " kg·mm²"),
                   "spinInerciaEntrada")
        if getattr(u, "lblInfoMotor", None) is None:
            u.lblInfoMotor = QtWidgets.QLabel()
            u.lblInfoMotor.setWordWrap(True)
            la.insertWidget(la.indexOf(u.groupCurvaCaracteristica) + 1, u.lblInfoMotor)
        lc = u.layoutPaginaCargas
        i = lc.indexOf(u.tablaPuntosCarga)
        self._fila(lc, i, "Amplitud", self._spin(-1e9, 1e9, 6), "spinAmplitudCarga")
        self._fila(lc, i + 1, "Frecuencia (ciclos/unidad de abscisa)", self._spin(0, 1e6, 6, 1.0), "spinFrecuenciaCarga")
        self._fila(lc, i + 2, "Fase", self._spin(-360, 360, 4, 0.0, " °"), "spinFaseCarga")
        g = QtWidgets.QSpinBox(); g.setRange(0, 5); g.setValue(1)
        self._fila(lc, i + 3, "Grado (lista de puntos)", g, "spinGradoCarga")
        self._fila(lc, i + 4, "Periodo de la abscisa (0 = no periódica)", self._spin(0, 1e9, 6), "spinPeriodoCarga")
        self._fila(lc, i + 5, "Inercia de la salida (0 = sin masa)", self._spin(0, 1e9, 4, 0.0, " kg·mm²"),
                   "spinInerciaSalida")
        self._fila(lc, i + 6, "Inercia de cada planeta, giro propio (0 = sin masa)",
                   self._spin(0, 1e9, 4, 0.0, " kg·mm²"), "spinInerciaPlaneta")
        if getattr(u, "lblAyudaCarga", None) is None:
            u.lblAyudaCarga = QtWidgets.QLabel()
            u.lblAyudaCarga.setWordWrap(True)
            lc.insertWidget(lc.indexOf(u.tablaPuntosCarga), u.lblAyudaCarga)
        ls = u.layoutPaginaSolucionador
        if u.comboMetodoSolucion.findText(METODO_DINAMICO) < 0:       # el régimen dinámico gobierna (por defecto)
            u.comboMetodoSolucion.insertItem(0, METODO_DINAMICO)
        u.comboMetodoSolucion.setCurrentIndex(u.comboMetodoSolucion.findText(METODO_DINAMICO))
        self._fila(ls, 3, "Paso de integración (0 = automático)", self._spin(0, 100, 4, 0.0, " ms"), "spinPasoIntegracion")
        cu = QtWidgets.QSpinBox(); cu.setRange(50, 20000); cu.setValue(1500)
        self._fila(ls, 4, "Instantes guardados (animación y consulta)", cu, "spinCuadrosDinamica")
        n = QtWidgets.QSpinBox(); n.setRange(3, 100000); n.setValue(201)
        self._fila(ls, 3, "Muestras del estudio (inicial si es adaptativa)", n, "spinMuestrasEstudio")
        if getattr(u, "lblCostoEstudio", None) is None:
            fila = QtWidgets.QHBoxLayout()
            u.lblCostoEstudio = QtWidgets.QLabel("Costo: sin estimar")
            u.lblCostoEstudio.setWordWrap(True)
            u.btnEstimarCosto = QtWidgets.QPushButton("Estimar costo")
            fila.addWidget(u.lblCostoEstudio, 1); fila.addWidget(u.btnEstimarCosto)
            ls.addLayout(fila)
        for t in (u.tablaCurvaMotor, u.tablaPuntosCarga, u.tablaComponentesContacto, u.tablaTabFuerzasContacto,
                  u.tablaTabMomentos, u.tablaTabEventos, u.tablaDiagnosticoEstudio):
            t.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        u.tablaTabFuerzasContacto.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        u.tablaTabFuerzasContacto.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        u.chkIncluirFriccion.setToolTip("Contacto normal sin fricción en esta formulación; las leyes tangenciales "
                                        "quedan separadas para una versión futura.")

    def _crear_graficas(self):
        u = self.u
        self.p_t = _plot(u.widgetGraficaTabParTiempo, "par_tiempo", "Tiempo", "s", "Par", "N·m")
        self.p_th = _plot(u.widgetGraficaTabParAngulo, "par_angulo", "θ", "°", "Par", "N·m")
        self.p_w = _plot(u.widgetGraficaTabParVelocidad, "par_velocidad", "n", "rpm", "Par", "N·m")
        self.p_f = _plot(u.widgetGraficaTabFuerzasContacto, "fuerzas_contacto", "Tiempo", "s", "Fn", "N")
        self.p_m = _plot(u.widgetGraficaTabMomentos, "momentos", "Tiempo", "s", "Par", "N·m")
        self.p_e = _plot(u.widgetGraficaTabEventos, "eventos", "Tiempo", "s", "Contactos activos", "")
        self.p_d = _plot(u.widgetGraficaDiagnostico, "diagnostico", "Tiempo", "s", "Residuo", "")
        _colores_tema()
        for p in (self.p_t, self.p_th, self.p_w, self.p_f, self.p_m, self.p_e, self.p_d):
            p._retemar = self._retemar
        self.cursores = []
        for p in (self.p_t, self.p_f, self.p_m, self.p_e, self.p_d):
            c = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen((230, 140, 30), width=1.5))
            c._sin_encuadre = True
            c.setVisible(False)
            p.addItem(c, ignoreBounds=True)
            c.sigPositionChanged.connect(self._cursor_movido)
            self.cursores.append(c)

    def _conectar(self):
        u = self.u
        u.listSeccionesEstudio.currentRowChanged.connect(u.stackConfiguracion.setCurrentIndex)
        u.listSeccionesEstudio.setCurrentRow(0)
        u.comboTipoMotor.currentIndexChanged.connect(lambda *_: (self._visibilidad_motor(), self._editado()))
        u.comboModoAccionamiento.currentIndexChanged.connect(lambda *_: self._editado())
        for s in (u.spinPotenciaNominal, u.spinVelocidadNominal, u.spinParRetencion, u.spinFrecuenciaRed,
                  u.spinNumeroPolos, u.spinParResistente, u.spinRigidezNormal, u.spinToleranciaBrecha,
                  u.spinAmortiguamientoNormal, u.spinToleranciaEquilibrio, u.spinToleranciaMomento,
                  u.spinMaxIteraciones, u.spinAmplitudCarga, u.spinFrecuenciaCarga, u.spinFaseCarga,
                  u.spinGradoCarga, u.spinPeriodoCarga, u.spinMuestrasEstudio, u.spinInerciaEntrada,
                  u.spinInerciaSalida, u.spinInerciaPlaneta, u.spinPasoIntegracion, u.spinCuadrosDinamica):
            s.valueChanged.connect(lambda *_: self._editado())
        u.editExpresionMotor.editingFinished.connect(self._editado)
        for c in (u.comboDependenciaPar, u.comboTipoLeyCarga, u.comboModeloContacto, u.comboMuestreoEstudio,
                  u.comboMetodoSolucion):
            c.currentIndexChanged.connect(lambda *_: (self._visibilidad_carga(), self._editado()))
        u.comboComponenteCarga.activated.connect(self._componente_carga)
        for c in (u.chkRepartoMulticontacto, u.chkRegistrarContactos, u.chkPararNoConvergencia,
                  u.chkInformarResultadosIndeterminados, u.chkGuardarDiagnosticos):
            c.toggled.connect(lambda *_: self._editado())
        for t in (u.tablaCurvaMotor, u.tablaPuntosCarga):
            t.itemChanged.connect(lambda *_: self._editado())
        u.btnAgregarPuntoMotor.clicked.connect(lambda: self._fila_tabla(u.tablaCurvaMotor, 1))
        u.btnQuitarPuntoMotor.clicked.connect(lambda: self._fila_tabla(u.tablaCurvaMotor, -1))
        u.btnAgregarPuntoCarga.clicked.connect(lambda: self._fila_tabla(u.tablaPuntosCarga, 1))
        u.btnQuitarPuntoCarga.clicked.connect(lambda: self._fila_tabla(u.tablaPuntosCarga, -1))
        u.btnImportarCurvaMotor.clicked.connect(lambda: self._importar(u.tablaCurvaMotor))
        u.btnImportarCarga.clicked.connect(lambda: self._importar(u.tablaPuntosCarga))
        u.comboEscenarioDinamico.activated.connect(self._escenario_elegido)
        u.btnGuardarEscenario.clicked.connect(self._guardar_escenario)
        u.btnRestaurarEscenario.clicked.connect(self._restaurar_escenario)
        u.btnGuardarEscenario.setEnabled(True)
        for b in (u.btnAgregarPuntoMotor, u.btnQuitarPuntoMotor, u.btnImportarCurvaMotor, u.btnAgregarPuntoCarga,
                  u.btnQuitarPuntoCarga, u.btnImportarCarga):       # deshabilitados en el .ui hasta conectarlos
            b.setEnabled(True)
        u.btnGuardarEscenario.setToolTip("Guarda el escenario: asociado al preset, como personalizado o como uno nuevo.")
        u.btnRestaurarEscenario.setToolTip("Descarta los cambios sin guardar del escenario seleccionado.")
        u.comboBox_preset.currentIndexChanged.connect(self._preset_cambiado)
        u.btnEjecutarEstudio.clicked.connect(self._ejecutar)
        u.btnCancelarEstudio.clicked.connect(lambda: self.gestor and self.gestor.cancelar())
        u.btnVerResultados.clicked.connect(self.ver_resultados)
        u.btnExportarResultadosEstudio.clicked.connect(self._exportar)
        u.btnEstimarCosto.clicked.connect(self._estimar)
        u.tablaTabFuerzasContacto.itemSelectionChanged.connect(self._graficar_fuerzas)
        for chk in (u.chkMostrarPrescritaTabParTiempo, u.chkMostrarCalculadaTabParTiempo,
                    u.chkMostrarPrescritaTabParAngulo, u.chkMostrarCalculadaTabParAngulo,
                    u.chkMostrarPrescritaTabParVelocidad, u.chkMostrarCalculadaTabParVelocidad):
            chk.toggled.connect(lambda *_: self._graficar_pares())

    def _retemar(self):
        """Lo invoca el tema por CADA gráfica: se agrupa en un solo repintado."""
        if getattr(self, "_retemar_pendiente", False):
            return
        self._retemar_pendiente = True
        QtCore.QTimer.singleShot(0, self._retemar_ahora)

    def _retemar_ahora(self):
        self._retemar_pendiente = False
        if getattr(self, "_retemando", False):
            return
        self._retemando = True
        try:
            _colores_tema()
            if self.gestor is not None:
                self._graficar_pares()
                if self.gestor.resultado is not None:
                    self._mostrar_resultado()
        finally:
            self._retemando = False

    # ================================================================== formulario <-> escenario
    def leer(self) -> Escenario:
        u = self.u
        motor = acc.ModeloMotor(
            tipo=acc.tipo_desde_texto(u.comboTipoMotor.currentText()), modo=u.comboModoAccionamiento.currentText(),
            potencia_nominal_w=u.spinPotenciaNominal.value(), velocidad_nominal_rpm=u.spinVelocidadNominal.value(),
            par_retencion_nm=u.spinParRetencion.value(), frecuencia_hz=u.spinFrecuenciaRed.value(),
            polos=u.spinNumeroPolos.value(), curva=_leer_tabla(u.tablaCurvaMotor),
            expresion=u.editExpresionMotor.text().strip())
        comp = u.comboComponenteCarga.property("componente") or EN_SALIDA
        carga = CargaExterna(
            dependencia=DEPENDENCIAS[max(0, u.comboDependenciaPar.currentIndex())],
            ley=u.comboTipoLeyCarga.currentText() or CONSTANTE, constante=u.spinParResistente.value(),
            puntos=_leer_tabla(u.tablaPuntosCarga), amplitud=u.spinAmplitudCarga.value(),
            frecuencia=u.spinFrecuenciaCarga.value(), fase_deg=u.spinFaseCarga.value(),
            grado=u.spinGradoCarga.value(), periodo=u.spinPeriodoCarga.value(), componente=comp)
        contacto = ConfigContacto(
            modelo=u.comboModeloContacto.currentText(), rigidez_n_mm=u.spinRigidezNormal.value(),
            tolerancia_brecha_mm=u.spinToleranciaBrecha.value(), reparto=u.chkRepartoMulticontacto.isChecked(),
            registrar_todos=u.chkRegistrarContactos.isChecked(),
            amortiguamiento_n_s_mm=u.spinAmortiguamientoNormal.value()
            if u.spinAmortiguamientoNormal.isEnabled() else 0.0)
        sol = ConfigSolucionador(
            metodo=u.comboMetodoSolucion.currentText(), muestreo=u.comboMuestreoEstudio.currentText(),
            muestras=u.spinMuestrasEstudio.value(), tol_equilibrio_n=u.spinToleranciaEquilibrio.value(),
            tol_momento_n_mm=u.spinToleranciaMomento.value(), max_iteraciones=u.spinMaxIteraciones.value(),
            parar_no_convergencia=u.chkPararNoConvergencia.isChecked(),
            informar_indeterminados=u.chkInformarResultadosIndeterminados.isChecked(),
            guardar_diagnosticos=u.chkGuardarDiagnosticos.isChecked())
        din = ConfigDinamica(inercia_entrada_kg_mm2=u.spinInerciaEntrada.value(),
                             inercia_salida=u.spinInerciaSalida.value(),
                             inercia_planeta_kg_mm2=u.spinInerciaPlaneta.value(),
                             paso_ms=u.spinPasoIntegracion.value(), cuadros=u.spinCuadrosDinamica.value())
        return Escenario(self._seleccion, motor, carga, contacto, sol, din)

    def _escribir(self, e: Escenario):
        u = self.u
        self._cargando = True
        try:
            m = e.motor
            u.comboTipoMotor.setCurrentIndex({acc.STEPPER: 0, acc.AC: 1, acc.CUSTOM: 2}.get(m.tipo, 0))
            i = u.comboModoAccionamiento.findText(m.modo)
            u.comboModoAccionamiento.setCurrentIndex(max(0, i))
            for s, v in ((u.spinPotenciaNominal, m.potencia_nominal_w), (u.spinVelocidadNominal, m.velocidad_nominal_rpm),
                         (u.spinParRetencion, m.par_retencion_nm), (u.spinFrecuenciaRed, m.frecuencia_hz),
                         (u.spinNumeroPolos, m.polos)):
                s.setValue(v)
            u.editExpresionMotor.setText(m.expresion)
            _poner_tabla(u.tablaCurvaMotor, m.curva)
            c = e.carga
            u.comboDependenciaPar.setCurrentIndex(DEPENDENCIAS.index(c.dependencia) if c.dependencia in DEPENDENCIAS else 0)
            u.comboTipoLeyCarga.setCurrentIndex(max(0, u.comboTipoLeyCarga.findText(c.ley)))
            u.spinParResistente.setValue(c.constante)
            for s, v in ((u.spinAmplitudCarga, c.amplitud), (u.spinFrecuenciaCarga, c.frecuencia),
                         (u.spinFaseCarga, c.fase_deg), (u.spinGradoCarga, c.grado), (u.spinPeriodoCarga, c.periodo)):
                s.setValue(v)
            _poner_tabla(u.tablaPuntosCarga, c.puntos)
            u.comboComponenteCarga.setProperty("componente", c.componente)
            u.comboComponenteCarga.setCurrentIndex(1 if c.componente == EN_ENTRADA else 0)
            k = e.contacto
            u.comboModeloContacto.setCurrentIndex(max(0, u.comboModeloContacto.findText(k.modelo)))
            u.spinRigidezNormal.setValue(k.rigidez_n_mm)
            u.spinToleranciaBrecha.setValue(k.tolerancia_brecha_mm)
            u.chkRepartoMulticontacto.setChecked(k.reparto)
            u.chkRegistrarContactos.setChecked(k.registrar_todos)
            u.spinAmortiguamientoNormal.setValue(k.amortiguamiento_n_s_mm)
            s = e.solucionador
            u.comboMetodoSolucion.setCurrentIndex(max(0, u.comboMetodoSolucion.findText(s.metodo)))
            d = e.dinamica
            for sp, v in ((u.spinInerciaEntrada, d.inercia_entrada_kg_mm2), (u.spinInerciaSalida, d.inercia_salida),
                          (u.spinInerciaPlaneta, d.inercia_planeta_kg_mm2), (u.spinPasoIntegracion, d.paso_ms),
                          (u.spinCuadrosDinamica, d.cuadros)):
                sp.setValue(v)
            u.comboMuestreoEstudio.setCurrentIndex(max(0, u.comboMuestreoEstudio.findText(s.muestreo)))
            u.spinMuestrasEstudio.setValue(s.muestras)
            u.spinToleranciaEquilibrio.setValue(s.tol_equilibrio_n)
            u.spinToleranciaMomento.setValue(s.tol_momento_n_mm)
            u.spinMaxIteraciones.setValue(s.max_iteraciones)
            u.chkPararNoConvergencia.setChecked(s.parar_no_convergencia)
            u.chkInformarResultadosIndeterminados.setChecked(s.informar_indeterminados)
            u.chkGuardarDiagnosticos.setChecked(s.guardar_diagnosticos)
        finally:
            self._cargando = False
        self._visibilidad_motor()
        self._visibilidad_carga()

    def _sucio(self) -> bool:
        a, b = self.leer(), copy.deepcopy(self._base)
        b.nombre = a.nombre
        return a.huella() != b.huella()

    @manejador_seguro
    def _editado(self, *_):
        if self._cargando or self.gestor is None:
            return
        e = self.leer()
        self.gestor.escenario_edicion = copy.deepcopy(e)        # lo que se ve gobierna también el modo manual
        self.u.btnRestaurarEscenario.setEnabled(self._sucio())
        self.u.lblInfoMotor.setText(self._texto_motor(e.motor))
        self._actualizar_prescritas()
        if self.gestor.resultado is not None:       # cambios físicos invalidan el resultado mostrado
            if self.gestor.resultado.huella != self.gestor.huella(self.w.perfil, e) and self.gestor.estado == eq.FINALIZADO:
                self.u.lblEstadoEstudio.setText("Desactualizado: la configuración cambió (vuelva a ejecutar)")

    # ================================================================== visibilidad y textos
    def _texto_motor(self, m: acc.ModeloMotor) -> str:
        partes = []
        if m.tipo == acc.AC:
            ns = m.velocidad_sincrona_rpm
            partes.append(f"Velocidad síncrona n_s = 120·f/p = {_f(ns, 'rpm')}" if ns else "n_s no definida")
            if ns and m.velocidad_nominal_rpm:
                partes.append(f"real (nominal) {_f(m.velocidad_nominal_rpm, 'rpm')} · deslizamiento "
                              f"{_f(100 * (ns - m.velocidad_nominal_rpm) / ns, '%')}")
        if m.tipo == acc.STEPPER:
            partes.append("El par de retención solo vale en reposo; a otras velocidades se usa la curva par–velocidad.")
        partes.append("La potencia nominal es capacidad (régimen continuo), no potencia entregada.")
        err = m.validar()
        if err:
            partes.append("⚠ " + "; ".join(err))
        return "\n".join(partes)

    def _visibilidad_motor(self):
        u = self.u
        tipo = acc.tipo_desde_texto(u.comboTipoMotor.currentText())
        for w in (u.spinParRetencion, u.lblSpinParRetencion):
            w.setVisible(tipo in (acc.STEPPER, acc.CUSTOM))
        for w in (u.spinFrecuenciaRed, u.lblSpinFrecuenciaRed, u.spinNumeroPolos, u.lblSpinNumeroPolos):
            w.setVisible(tipo == acc.AC)
        for w in (u.editExpresionMotor, getattr(u, "lbl_editExpresionMotor", None)):
            if w is not None:
                w.setVisible(tipo == acc.CUSTOM)
        if tipo == acc.STEPPER:
            u.lblSpinParRetencion.setText("Par de retención (Stepper)")
        elif tipo == acc.CUSTOM:
            u.lblSpinParRetencion.setText("Par constante hasta n_nom (Custom por valores)")
        try:
            u.lblInfoMotor.setText(self._texto_motor(self.leer().motor))
        except Exception:
            pass

    def _unidades_carga(self):
        lin = self.gestor is not None and self.gestor.v.LINEAL and self._componente() == EN_SALIDA
        dep = DEPENDENCIAS[max(0, self.u.comboDependenciaPar.currentIndex())]
        abscisa = {DEP_T: ("t", "s"), DEP_THETA: ("x", "mm") if lin else ("θ", "°"),
                   DEP_OMEGA: ("v", "mm/s") if lin else ("ω", "°/s")}[dep]
        return abscisa, ("Fuerza", "N") if lin else ("Par", "N·m")

    def _componente(self) -> str:
        return self.u.comboComponenteCarga.property("componente") or EN_SALIDA

    def _visibilidad_carga(self):
        u = self.u
        ley = u.comboTipoLeyCarga.currentText()
        (xn, xu), (yn, yu) = self._unidades_carga()
        u.tablaPuntosCarga.setHorizontalHeaderLabels(
            ["i (potencia)", f"a_i ({yu}/{xu}^i)"] if ley == "Polinómica" else [f"{xn} ({xu})", f"{yn} ({yu})"])
        u.spinParResistente.setSuffix(f" {yu}")
        u.lblSpinParResistente.setText("Valor medio (offset)" if ley == "Sinusoidal" else
                                       "Par/fuerza resistente constante" if ley == CONSTANTE else "Valor (no usado)")
        sin = ley == "Sinusoidal"
        for nombre in ("spinAmplitudCarga", "spinFrecuenciaCarga", "spinFaseCarga"):
            for w in (getattr(u, nombre), getattr(u, "lbl_" + nombre, None)):
                if w is not None:
                    w.setVisible(sin)
        for w in (u.spinGradoCarga, getattr(u, "lbl_spinGradoCarga", None)):
            if w is not None:
                w.setVisible(ley == "Lista de puntos")
        tab = ley not in (CONSTANTE, "Sinusoidal", "Polinómica")
        for w in (u.spinPeriodoCarga, getattr(u, "lbl_spinPeriodoCarga", None)):
            if w is not None:
                w.setVisible(tab)
        u.tablaPuntosCarga.setVisible(ley not in (CONSTANTE, "Sinusoidal"))
        for b in (u.btnAgregarPuntoCarga, u.btnQuitarPuntoCarga, u.btnImportarCarga):
            b.setVisible(ley not in (CONSTANTE, "Sinusoidal"))
        ayuda = {CONSTANTE: "Valor constante en toda la trayectoria.",
                 "Sinusoidal": f"T = offset + A·sin(2π·f·{xn} + fase). Definida para toda abscisa.",
                 "Polinómica": f"T = Σ a_i·{xn}^i (fila i = coeficiente a_i). Definida para toda abscisa."}.get(
            ley, f"Ley «{ley}» entre el primer y el último punto ({xn} en {xu}). Fuera de ese dominio la carga es "
                 "INDETERMINADA, salvo que declare un periodo.")
        u.lblAyudaCarga.setText(ayuda + f"\nValor positivo = {yn.lower()} resistente (opuesto al sentido positivo "
                                         f"del componente). Aplicada en: "
                                         f"{'eje de entrada' if self._componente() == EN_ENTRADA else 'componente de salida'}.")
        lin = self.gestor is not None and self.gestor.v.LINEAL
        u.spinInerciaSalida.setSuffix(" kg" if lin else " kg·mm²")
        if getattr(u, "lbl_spinInerciaSalida", None) is not None:
            u.lbl_spinInerciaSalida.setText(("Masa de la salida (cremallera o carro)" if lin else "Inercia de la salida")
                                            + " (0 = sin masa)")
        plan = self.gestor is not None and self.gestor.v.SISTEMA == "PLANETARIO"
        for w in (u.spinInerciaPlaneta, getattr(u, "lbl_spinInerciaPlaneta", None)):
            if w is not None:
                w.setVisible(plan)
        dinam = u.comboMetodoSolucion.currentText() == METODO_DINAMICO
        for nombre, visible in (("spinPasoIntegracion", dinam), ("spinCuadrosDinamica", dinam),
                                ("spinMuestrasEstudio", not dinam)):
            for w in (getattr(u, nombre), getattr(u, "lbl_" + nombre, None)):
                if w is not None:
                    w.setVisible(visible)
        u.comboMuestreoEstudio.setEnabled(not dinam)
        u.comboMetodoSolucion.setToolTip(
            "Integración temporal: la dinámica de contacto GOBIERNA el movimiento (salida movida por las fuerzas "
            "de contacto; con «Evaluación de capacidad» el motor puede perder sincronismo). Requiere rigidez > 0.\n"
            "Equilibrio cuasiestático: fuerzas por posición sobre la trayectoria prescrita.")
        penal = u.comboModeloContacto.currentText() == cf.MODELO_PENALIZACION
        u.spinAmortiguamientoNormal.setEnabled(penal)
        u.spinAmortiguamientoNormal.setToolTip(
            "Solo con penalización: F = k·δ + c·δ̇, con δ̇ de las velocidades relativas PRESCRITAS. En reposo (ω = 0) "
            "no actúa. No representa dinámica transitoria (no hay inercias).")
        u.spinRigidezNormal.setEnabled(penal)
        u.spinRigidezNormal.setToolTip("Rigidez normal equivalente por contacto (dato de entrada; 0 = no definida, "
                                       "no se asume ningún valor).")

    @manejador_seguro
    def _componente_carga(self, i: int):
        u = self.u
        comp = EN_SALIDA if i == 0 else EN_ENTRADA if i == 1 else None
        if comp is None and self.gestor is not None:
            try:
                ad = self._adaptador()
                opciones = [f"{c.nombre} — {c.vinculo}" for c in ad.componentes()
                            if c.vinculo.startswith(("Entrada", "Salida"))]
            except Exception:
                opciones = []
            if not opciones:
                return
            txt, ok = QtWidgets.QInputDialog.getItem(self.w, "Aplicación de carga",
                                                     "Componente (solo entrada o salida admiten carga externa):",
                                                     opciones, 0, False)
            if not ok:
                u.comboComponenteCarga.setCurrentIndex(1 if self._componente() == EN_ENTRADA else 0)
                return
            comp = EN_ENTRADA if "Entrada" in txt else EN_SALIDA
            u.comboComponenteCarga.setCurrentIndex(1 if comp == EN_ENTRADA else 0)
        u.comboComponenteCarga.setProperty("componente", comp)
        self._visibilidad_carga()
        self._editado()

    @manejador_seguro
    def _fila_tabla(self, tabla, signo):
        filas = _leer_tabla(tabla)
        if signo > 0:
            filas.append([filas[-1][0] + 1.0, filas[-1][1]] if filas else [0.0, 0.0])
        elif filas:
            r = tabla.currentRow()
            filas.pop(r if 0 <= r < len(filas) else -1)
        _poner_tabla(tabla, filas)
        self._editado()

    @manejador_seguro
    def _importar(self, tabla):
        ruta, _ = QtWidgets.QFileDialog.getOpenFileName(self.w, "Importar puntos", "", "CSV/TXT (*.csv *.txt)")
        if not ruta:
            return
        filas = _leer_csv(ruta)
        if not filas:
            QtWidgets.QMessageBox.warning(self.w, "Importar", "El archivo no contiene pares numéricos (x, y).")
            return
        _poner_tabla(tabla, filas)
        self._editado()

    # ================================================================== escenarios (funciones 9–11)
    def _poblar_combo_escenarios(self):
        c = self.u.comboEscenarioDinamico
        c.blockSignals(True)
        c.clear()
        c.addItems([ESCENARIO_LIBRE, ESCENARIO_PRESET, ESCENARIO_NUEVO])
        for nombre in sorted(self.gestor.biblioteca.personalizados):
            c.addItem(nombre)
        c.blockSignals(False)

    def _sel_combo(self, nombre: str):
        c = self.u.comboEscenarioDinamico
        clave = ESCENARIO_PRESET if nombre.startswith(ESCENARIO_PRESET) else nombre
        i = c.findText(clave)
        c.blockSignals(True); c.setCurrentIndex(max(0, i)); c.blockSignals(False)

    def _preguntar_sin_guardar(self) -> bool:
        """True si se puede continuar (guardado o descartado)."""
        if not self._sucio():
            return True
        r = QtWidgets.QMessageBox.question(
            self.w, "Escenario modificado", "El escenario actual tiene cambios sin guardar. ¿Guardarlos?",
            QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard
            | QtWidgets.QMessageBox.StandardButton.Cancel)
        if r == QtWidgets.QMessageBox.StandardButton.Cancel:
            return False
        if r == QtWidgets.QMessageBox.StandardButton.Save:
            return self._guardar_escenario()
        return True

    def _cargar_escenario(self, nombre: str, esc: Escenario):
        self._seleccion = nombre
        self._escribir(esc)
        self._base = copy.deepcopy(esc)
        self.gestor.escenario = copy.deepcopy(esc)
        self.gestor.escenario.nombre = nombre
        self.gestor.seleccion = nombre
        self.u.btnRestaurarEscenario.setEnabled(False)
        self._sel_combo(nombre)
        self._actualizar_prescritas()

    @manejador_seguro
    def _escenario_elegido(self, i: int):
        texto = self.u.comboEscenarioDinamico.itemText(i)
        if not self._preguntar_sin_guardar():
            self._sel_combo(self._seleccion)
            return
        b = self.gestor.biblioteca
        if texto == ESCENARIO_LIBRE:
            self._cargar_escenario(ESCENARIO_LIBRE, Escenario())
        elif texto == ESCENARIO_PRESET:
            preset = self.u.comboBox_preset.currentText()
            self._cargar_escenario(f"{ESCENARIO_PRESET}: {preset}", b.de_preset(preset))
        elif texto == ESCENARIO_NUEVO:
            nombre = self._pedir_nombre()
            if not nombre:
                self._sel_combo(self._seleccion)
                return
            b.guardar_personalizado(nombre, self.leer())          # duplica el formulario vigente
            self._poblar_combo_escenarios()
            self._cargar_escenario(nombre, b.personalizados[nombre])
        else:
            self._cargar_escenario(texto, copy.deepcopy(b.personalizados[texto]))

    def _pedir_nombre(self) -> str:
        b = self.gestor.biblioteca
        n, ok = QtWidgets.QInputDialog.getText(self.w, "Nuevo escenario", "Nombre del escenario:",
                                               text=f"Escenario {len(b.personalizados) + 1}")
        n = n.strip()
        if not ok or not n:
            return ""
        if n in (ESCENARIO_LIBRE, ESCENARIO_PRESET, ESCENARIO_NUEVO) or n.startswith(ESCENARIO_PRESET):
            QtWidgets.QMessageBox.warning(self.w, "Nuevo escenario", "Ese nombre está reservado.")
            return ""
        return n

    @manejador_seguro
    def _guardar_escenario(self, *_) -> bool:
        b, sel, e = self.gestor.biblioteca, self._seleccion, self.leer()
        if sel.startswith(ESCENARIO_PRESET):
            preset = sel.split(": ", 1)[-1]
            b.asociar(preset, e)
            nombre = f"{ESCENARIO_PRESET}: {preset}"
        elif sel in b.personalizados:
            b.guardar_personalizado(sel, e)
            nombre = sel
        else:                                   # «sin carga externa» es la base: se guarda como copia nueva
            nombre = self._pedir_nombre()
            if not nombre:
                return False
            b.guardar_personalizado(nombre, e)
            self._poblar_combo_escenarios()
        e.nombre = nombre
        self._cargar_escenario(nombre, e)
        self.w.statusBar().showMessage(f"Escenario guardado: {nombre}", 4000)
        return True

    @manejador_seguro
    def _restaurar_escenario(self, *_):
        self._cargar_escenario(self._seleccion, copy.deepcopy(self._base))

    @manejador_seguro
    def _preset_cambiado(self, *_):
        """Con «asociado al preset», elegir otro preset recupera su escenario (respetando cambios sin guardar)."""
        if self.gestor is None or not self._seleccion.startswith(ESCENARIO_PRESET):
            return
        preset = self.u.comboBox_preset.currentText()
        if self._seleccion == f"{ESCENARIO_PRESET}: {preset}":
            return
        if not self._preguntar_sin_guardar():
            return
        self._cargar_escenario(f"{ESCENARIO_PRESET}: {preset}", self.gestor.biblioteca.de_preset(preset))

    # ================================================================== ejecución
    def _adaptador(self):
        clave = getattr(self.gestor.v, "_clave_pintada", None), self.gestor.v._alterno()
        if self._ad_cache[0] != clave:
            self._ad_cache = (clave, self.gestor.adaptador())
        return self._ad_cache[1]

    def _resultado_listo(self, *_):
        self._mostrar_resultado()

    def _ajustes_cambiaron(self, *_):
        self._habilitacion()
        if self.gestor is not None:
            self._estado_gestor(self.gestor.estado, self.gestor.detalle)

    def _habilitacion(self):
        if self.gestor is None:
            return
        on = eq.contacto_habilitado()
        calc = self.gestor.calculando()
        u = self.u
        u.btnEjecutarEstudio.setEnabled(on and not calc)
        u.btnEjecutarEstudio.setToolTip("" if on else "Active «Habilitar análisis basado en contacto» en Ajustes → Simulación.")
        u.btnCancelarEstudio.setEnabled(calc)
        ok = self.gestor.resultado is not None
        u.btnVerResultados.setEnabled(ok)
        u.btnExportarResultadosEstudio.setEnabled(ok)

    def _estado_gestor(self, estado: str, detalle: str):
        texto = estado + (f": {detalle}" if detalle else "")
        if not eq.contacto_habilitado() and estado != eq.CALCULANDO:
            texto += "  ·  (análisis por contacto desactivado en Ajustes → Simulación)"
        self.u.lblEstadoEstudio.setText(texto)
        if estado != eq.CALCULANDO:
            self.u.progressEstudio.setValue(100 if estado == eq.FINALIZADO else 0)
        self._habilitacion()

    def _progreso(self, i: int, n: int):
        self.u.progressEstudio.setValue(int(100 * min(i, n) / max(n, 1)))

    @manejador_seguro
    def _ejecutar(self, *_):
        e = self.leer()
        self.gestor.escenario = copy.deepcopy(e)
        self.gestor.seleccion = self._seleccion
        self.w.perfil.validar()
        self.gestor.ejecutar(copy.deepcopy(self.w.perfil), e)

    @manejador_seguro
    def _estimar(self, *_):
        d = self.gestor.estimar(self.w.perfil, self.leer())
        self.u.lblCostoEstudio.setText(
            f"ESTIMACIÓN (calibrada con {d['calibracion']} muestras medidas): {_f(1000 * d['segundos_por_muestra'], 'ms')}"
            f"/muestra × {d['muestras']} = {_f(d['estimado_s'], 's')} ({d['estrategia']}; máx. {d['n_max']} muestras). "
            "No es la duración real; la medida se informa al terminar.")

    def ver_resultados(self, *_):
        u = self.u
        u.tabRegimenes.setCurrentWidget(u.tabDinamico)
        u.tabGraficasEstudio.setCurrentWidget(u.tabResultadosDinamicos)

    @manejador_seguro
    def _exportar(self, *_):
        r = self.gestor.resultado if self.gestor else None
        if r is None:
            return
        ruta, filtro = QtWidgets.QFileDialog.getSaveFileName(self.w, "Exportar resultados del estudio",
                                                             "estudio_contacto.csv", "CSV (*.csv);;JSON (*.json)")
        if not ruta:
            return
        if ruta.lower().endswith(".json") or "JSON" in filtro:
            r.exportar_json(ruta if ruta.lower().endswith(".json") else ruta + ".json")
            self.w.statusBar().showMessage(f"Exportado: {ruta}", 5000)
        else:
            rutas = r.exportar_csv(ruta if ruta.lower().endswith(".csv") else ruta + ".csv")
            self.w.statusBar().showMessage("Exportado: " + " · ".join(rutas), 6000)

    # ================================================================== gráficas
    def _actualizar_prescritas(self):
        if self.gestor is None:
            return
        try:
            self._graficar_pares()
            self._tabla_componentes()
        except Exception as ex:
            self.w.statusBar().showMessage(f"No se pudo evaluar la carga prescrita: {ex}", 5000)

    def _tabla_componentes(self):
        try:
            ad = self._adaptador()
        except Exception:
            return
        th = self.w.lt.posicion_en(self.w._t) if self.w.lt is not None else 0.0
        try:
            c = ad.contactos(th)
            tol = self.u.spinToleranciaBrecha.value()
            n_eng = {}
            for g, gp in zip(c.engranaje, c.gap):
                if gp <= tol:
                    n_eng[g] = n_eng.get(g, 0) + 1
        except Exception:
            n_eng = {}
        filas = []
        for comp in ad.componentes():
            n = n_eng.get(comp.nombre, "")
            filas.append([comp.nombre, comp.vinculo, n if n != "" else "—"])
        _tabla_texto(self.u.tablaComponentesContacto, filas)

    def _curva(self, p, x, y, nombre, color, estilo=None, ancho=1.5):
        pen = pg.mkPen(color, width=ancho, style=estilo) if estilo else pg.mkPen(color, width=ancho)
        return p.plot(np.asarray(x, float), np.asarray(y, float), pen=pen, name=nombre, connect="finite")

    def _graficar_pares(self):
        u = self.u
        for p in (self.p_t, self.p_th, self.p_w):
            for it in list(p.listDataItems()):
                p.removeItem(it)
            if p.plotItem.legend is not None:
                p.plotItem.legend.clear()
        e = self.leer()
        (xn, xu), (yn, yu) = self._unidades_carga()
        # --- prescritas sobre la trayectoria cinemática (no requieren estudio) ---
        lt = self.w.lt
        r = self.gestor.resultado if self.gestor.estado in (eq.FINALIZADO, eq.DESACTUALIZADO) else None
        if lt is not None:
            try:
                ad = self._adaptador()
                t = lt.t[:: max(1, len(lt.t) // 800)]
                th = np.interp(t, lt.t, lt.pos)
                om = np.interp(t, lt.t, lt.vel)
                ent = e.carga.componente == EN_ENTRADA
                rel = np.array([ad.relacion(x) for x in th])
                sal = np.array([ad.salida_desde_entrada(x) for x in th])
                x = {DEP_T: t, DEP_THETA: th if ent else sal, DEP_OMEGA: om if ent else rel * om}[e.carga.dependencia]
                T = e.carga.evaluar(x)
                nombre = f"[Prescrita] {'carga en la entrada' if ent else 'carga en ' + ad.salida} ({yu})"
                if u.chkMostrarPrescritaTabParTiempo.isChecked():
                    self._curva(self.p_t, t, T, nombre, C_PRES, DASH)
                if u.chkMostrarPrescritaTabParAngulo.isChecked():
                    self._curva(self.p_th, th if ent else sal, T, nombre + f" vs {'θ entrada' if ent else xn}", C_PRES, DASH)
                if u.chkMostrarPrescritaTabParVelocidad.isChecked() and not (self.gestor.v.LINEAL and not ent):
                    self._curva(self.p_w, (om if ent else rel * om) / 6.0, T,
                                nombre + (" vs n entrada" if ent else " vs n de la salida"), C_PRES, DASH)
            except Exception as ex:
                self.w.statusBar().showMessage(f"Carga prescrita no evaluable: {ex}", 4000)
        # --- característica del motor ---
        if u.chkMostrarPrescritaTabParVelocidad.isChecked():
            m = e.motor
            n_max = max([abs(x[0]) for x in m.curva] + [m.velocidad_sincrona_rpm or 0.0, m.velocidad_nominal_rpm, 1.0])
            ns = np.linspace(0.0, n_max * 1.05, 300)
            Td = np.array([m.par_disponible(n)[0] if m.par_disponible(n)[0] is not None else np.nan for n in ns])
            if np.isfinite(Td).any():
                self._curva(self.p_w, ns, Td, "[Motor] par disponible", C_MOT, DOT, 2.0)
                self._curva(self.p_w, -ns, Td, None, C_MOT, DOT, 2.0)
        # --- calculadas ---
        if r is not None:
            t = r.arr("t")
            tm = r.arr("par_motor")
            if u.chkMostrarCalculadaTabParTiempo.isChecked():
                self._curva(self.p_t, t, tm, "[Calculada] par motor requerido", C_CALC)
                self._curva(self.p_t, t, r.arr("par_transmitido"), f"[Calculada] transmitido a la salida ({yu})", C_AUX)
                if r.par_disponible:
                    self._curva(self.p_t, t, r.arr("par_disponible"), "[Motor] disponible a la velocidad requerida", C_MOT, DOT, 2.0)
            if u.chkMostrarCalculadaTabParAngulo.isChecked():
                self._curva(self.p_th, r.arr("theta_in"), tm, "[Calculada] par motor vs θ entrada (multivaluada)", C_CALC)
            if u.chkMostrarCalculadaTabParVelocidad.isChecked():
                self._curva(self.p_w, r.arr("omega_in") / 6.0, tm, "[Calculada] par motor vs n entrada", C_CALC)
        self.p_th.setLabel("bottom", "θ (entrada) / abscisa de la carga", units="")
        self.p_w.setLabel("bottom", "n (entrada)", units="rpm")

    def _mostrar_resultado(self):
        r = self.gestor.resultado
        if r is None:
            return
        u = self.u
        self._graficar_pares()
        t = r.arr("t")
        for c in self.cursores:
            c.blockSignals(True); c.setVisible(True); c.setBounds((t[0], t[-1])); c.setValue(t[0]); c.blockSignals(False)
        # momentos
        for it in list(self.p_m.listDataItems()):
            self.p_m.removeItem(it)
        self.p_m.plotItem.legend.clear()
        self._curva(self.p_m, t, r.arr("par_motor"), "[Calculada] par motor (entrada)", C_CALC, ancho=2)
        self._curva(self.p_m, t, r.arr("carga"), "[Prescrita] par/fuerza resistente", C_PRES, DASH)
        self._curva(self.p_m, t, r.arr("par_transmitido"), "[Calculada] transmitido por contactos a la salida", C_AUX)
        for i, (k, v) in enumerate(r.momentos.items()):
            unidad = "N" if k in r.meta.get("traslacion", []) else "N·m"
            self._curva(self.p_m, t, v, f"[Calculada] {k} ({unidad})", PALETA[(i + 3) % len(PALETA)], ancho=1)
        # eventos
        for it in list(self.p_e.listDataItems()):
            self.p_e.removeItem(it)
        self.p_e.plotItem.legend.clear()
        self.p_e.plot(t, r.arr("n_activos"), pen=pg.mkPen(C_CALC, width=1.5), stepMode=None, name="contactos activos")
        _tabla_texto(u.tablaTabEventos, [[fmt(a, ""), b, c, d] for a, b, c, d in r.eventos])
        # diagnóstico
        for it in list(self.p_d.listDataItems()):
            self.p_d.removeItem(it)
        self.p_d.plotItem.legend.clear()
        res = r.arr("residuo")
        if np.isfinite(res).any():
            self.p_d.plot(t, np.abs(res), pen=pg.mkPen(C_CALC), name="|residuo| máx. (N·mm o N)", connect="finite")
        self.p_d.plot(t, r.arr("delta_max"), pen=pg.mkPen(C_PRES, style=DASH), name="aproximación elástica máx. (mm)",
                      connect="finite")
        filas = []
        for i in range(len(r.t)):
            obs = r.mensaje[i]
            if r.par_motor_origen[i] == "trabajo virtual":
                obs = (obs + " · " if obs else "") + "par motor por trabajo virtual"
            if r.capacidad:
                obs = (obs + " · " if obs else "") + f"motor: {r.capacidad[i]}" + (f" ({r.causa_capacidad[i]})"
                                                                              if r.causa_capacidad[i] else "")
            filas.append([i, r.estado[i], _f(r.residuo[i]), obs])
        _tabla_texto(u.tablaDiagnosticoEstudio, filas)
        self._cursor_en(float(t[0]))
        self._habilitacion()

    def _cursor_movido(self, linea):
        t = float(linea.value())
        if self._t_cursor is not None and abs(t - self._t_cursor) < 1e-12:
            return
        for c in self.cursores:
            if c is not linea:
                c.blockSignals(True); c.setValue(t); c.blockSignals(False)
        self._cursor_en(t)

    def _cursor_en(self, t: float):
        """Cursor temporal de inspección (función 47): tablas en ese instante + geometría en la ventana."""
        r = self.gestor.resultado if self.gestor else None
        if r is None:
            return
        self._t_cursor = t
        i = r.indice_en(t)
        ti = r.t[i]
        sel = {it.text() for it in self.u.tablaTabFuerzasContacto.selectedItems() if it.column() == 1}
        filas = [[fmt(ti, ""), c["clave"], _f(c["Fn"]), _f(c["Fr"]), _f(c["Ft"])] for c in r.contactos[i]]
        tabla = self.u.tablaTabFuerzasContacto
        tabla.blockSignals(True)
        _tabla_texto(tabla, filas)
        for fila, f in enumerate(filas):
            if f[1] in sel:
                tabla.selectRow(fila)
        tabla.blockSignals(False)
        estado = r.estado[i]
        momentos = [[fmt(ti, ""), "Par motor (entrada)", _f(r.par_motor[i]),
                     estado + (" · trabajo virtual" if r.par_motor_origen[i] == "trabajo virtual" else "")],
                    [fmt(ti, ""), "Carga prescrita", _f(r.carga[i]), "prescrita"]]
        for k, v in r.momentos.items():
            momentos.append([fmt(ti, ""), k, _f(v[i]), estado])
        _tabla_texto(self.u.tablaTabMomentos, momentos)
        self._graficar_fuerzas()
        if self.gestor is not None:
            self.gestor.inspeccion.emit(float(ti))
        try:
            self.w._mostrar_tiempo(float(min(max(ti, self.w.lt.t_ini), self.w.lt.t_fin)))
        except Exception:
            pass

    def _graficar_fuerzas(self):
        r = self.gestor.resultado if self.gestor else None
        for it in list(self.p_f.listDataItems()):
            self.p_f.removeItem(it)
        self.p_f.plotItem.legend.clear()
        if r is None:
            return
        claves = sorted({it.text() for it in self.u.tablaTabFuerzasContacto.selectedItems() if it.column() == 1})
        if not claves:              # por defecto: los contactos con más carga en el instante del cursor
            i = r.indice_en(self._t_cursor if self._t_cursor is not None else r.t[0])
            carg = sorted((c for c in r.contactos[i] if c["Fn"] == c["Fn"]), key=lambda c: -c["Fn"])
            claves = [c["clave"] for c in carg[:3]]
        t = r.arr("t")
        for j, k in enumerate(claves):
            self._curva(self.p_f, t, r.historial(k, "Fn"), f"[Calculada] Fn {k}", PALETA[j % len(PALETA)])
