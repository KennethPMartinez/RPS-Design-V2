# -*- coding: utf-8 -*-
"""
ui/planetary_window.py

Ventana del PLANETARIO (PlanetarioV2.ui). Hereda de VentanaSistemaBase: Manual/Automático, línea de tiempo,
motor real, grabación, abrir/guardar siguen siendo los mismos. El "ángulo del motor" es el ángulo del
COMPONENTE DE ENTRADA (sol, brazo o anular); el engine (engine/planetario_engine.py) reparte el giro a los
otros componentes según el componente bloqueado (Willis).
"""
from __future__ import annotations

import math

from PySide6 import QtCore, QtWidgets

from config.data_structures import Componente, ParametrosPlanetario
from dialogs.design_summary_dialog import DialogoResumenDiseno
from dialogs.mostrar_ocultar_dialog import DialogoMostrarOcultarPlanetario
from dialogs.visibility_dialog import DialogoMostrarOcultar
from engine.planetario_engine import PlanetarioEngine, planetas_validos
from exporters.excel_exporter import exportar_excel
from ui.errores import manejador_seguro
from ui.planetary_property_windows import VentanaPerfilDientePlanetario, VentanaPropiedadPlanetario
from ui.sistema_base import VentanaSistemaBase
from utils.design_report import informe_html
from widgets.pg_helpers import AngleControl, reemplazar_widget
from widgets.planetary_view import PlanetaryView

from PlanetarioV2 import Ui_PlanetarioV2   # noqa: E402


class _DlgVisSinUi(DialogoMostrarOcultar):
    """Respaldo (sin Mostrar_Ocultar_Planetario.py generado): mismas 4 capas, construido por código."""
    def actualizar_modo(self, *_):
        pass


def _dialogo_visibilidad(ajustes, callback, parent=None):
    try:
        return DialogoMostrarOcultarPlanetario(ajustes, callback, parent=parent)
    except ImportError:
        return _DlgVisSinUi(ajustes, callback, parent)


class VentanaPlanetario(VentanaSistemaBase):
    SISTEMA = "PLANETARIO"
    NOMBRE = "Planetario"
    CLASE_UI = Ui_PlanetarioV2
    CLASE_PARAMETROS = ParametrosPlanetario
    CLASE_MOTOR = PlanetarioEngine
    CLASE_DIALOGO_VISIBILIDAD = staticmethod(_dialogo_visibilidad)
    ARCHIVO_EXCEL = "planetario.xlsx"
    MAPEO_PARAMETROS = (("numero_dientes_sol", "spinBox_numerodedientes"),
                        ("numero_rodillos", "spinBox_numeroderodillos"),
                        ("diametro_rodillos", "doubleSpinBox_diametro_rodillos"),
                        ("distancia_centro_rodillos", "doubleSpinBox_distancia_centro_rodillos"),
                        ("angulo_presion_minimo", "doubleSpinBox_angulo_presion_minimo"))

    # ------------------------------------------------------------------ ganchos de la base
    def _preparar_ui(self):
        self.setWindowTitle("Planetario")

    def _crear_vista(self):
        return reemplazar_widget(self.ui.graphicsView_plan, PlanetaryView())

    def _crear_control(self):
        return AngleControl(self.ui.dial_posicion_theta, self.ui.doubleSpinBox_posicion_theta, self)

    def _widgets_control_manual(self):
        return (self.ui.dial_posicion_theta, self.ui.doubleSpinBox_posicion_theta)

    def _alterno(self) -> bool:
        return False

    def _combos_modo(self, s: dict) -> tuple:
        return ()

    def _sim_dict(self) -> dict:
        return {"modo": self.ui.comboBox_modo_sim.currentIndex(),
                "valor_manual": self.control.acumulado,
                "predeterminado": self.ui.checkBox_valpredeterminados.isChecked()}

    def _conectar_modo_pinon(self):
        for c in self._combos():
            c.currentIndexChanged.connect(lambda *_: self._componentes_cambiados())

    def _conectar_propiedades(self):
        u = self.ui
        u.actionPerfil_del_diente.triggered.connect(
            lambda *_: self._abrir_aux(lambda: VentanaPerfilDientePlanetario(self)))
        for accion, tipo in ((u.action_ngulo_de_Presi_n, "angulo"), (u.actionRadio_de_Curvatura, "curvatura"),
                             (u.actionCamino_de_Contacto, "contacto")):
            accion.triggered.connect(lambda *_, t=tipo: self._abrir_aux(lambda: VentanaPropiedadPlanetario(self, t)))

    # ------------------------------------------------------------------ parámetros
    def _combos(self):
        u = self.ui
        return (u.comboBox_componentedeentrada, u.comboBox_componente_bloqueado, u.comboBox_numero_planetas)

    @manejador_seguro
    def _componentes_cambiados(self, *_):
        u = self.ui
        ent, blo = u.comboBox_componentedeentrada, u.comboBox_componente_bloqueado
        if ent.currentText() == blo.currentText():          # la entrada no puede ser el bloqueado
            blo.blockSignals(True)
            blo.setCurrentText("Brazo" if ent.currentText() == "Anular" else "Anular")
            blo.blockSignals(False)
            self.statusBar().showMessage("La entrada no puede ser el componente bloqueado: se cambió el bloqueado.", 4000)
        self._debounce.start()

    def _refrescar_planetas(self):
        """Rellena el combo con los N que cumplen N | (Zs+Za) y D_ap < 2·cd·sin(π/N)."""
        u = self.ui
        validos = planetas_validos(u.spinBox_numerodedientes.value(), u.spinBox_numeroderodillos.value(),
                                   u.doubleSpinBox_diametro_rodillos.value(),
                                   u.doubleSpinBox_distancia_centro_rodillos.value(),
                                   u.doubleSpinBox_angulo_presion_minimo.value())
        c = u.comboBox_numero_planetas
        if validos == [c.itemData(i) for i in range(c.count())]:
            return
        actual = c.currentData()
        c.blockSignals(True)
        c.clear()
        for n in validos:
            c.addItem(str(n), n)
        if actual in validos:
            c.setCurrentIndex(validos.index(actual))
        elif validos:
            c.setCurrentIndex(len(validos) - 1)              # el mayor reparte mejor la carga
        c.blockSignals(False)

    def leer_parametros(self):
        p = super().leer_parametros()
        u = self.ui
        p.componente_entrada = Componente(u.comboBox_componentedeentrada.currentText())
        p.componente_bloqueado = Componente(u.comboBox_componente_bloqueado.currentText())
        p.numero_planetas = u.comboBox_numero_planetas.currentData()
        return p

    def _escribir_parametros(self, p) -> None:
        super()._escribir_parametros(p)
        u = self.ui
        self._refrescar_planetas()
        for combo, texto in ((u.comboBox_componentedeentrada, p.componente_entrada.value),
                             (u.comboBox_componente_bloqueado, p.componente_bloqueado.value)):
            combo.blockSignals(True)
            combo.setCurrentText(texto)
            combo.blockSignals(False)
        i = u.comboBox_numero_planetas.findData(p.numero_planetas)
        if i >= 0:
            u.comboBox_numero_planetas.blockSignals(True)
            u.comboBox_numero_planetas.setCurrentIndex(i)
            u.comboBox_numero_planetas.blockSignals(False)

    # ------------------------------------------------------------------ motor y estado
    @manejador_seguro
    def _recalcular(self, *_):
        self._refrescar_planetas()
        p = self.leer_parametros()
        if not p.es_valido():
            self.statusBar().showMessage("Parámetros fuera de rango o entrada = bloqueado: no se recalcula.", 4000)
            return
        if p.numero_planetas is None:
            self.statusBar().showMessage("Ningún número de planetas cumple N | (Zs+Za) y D_ap < 2·cd·sin(π/N).", 6000)
            return
        motor = PlanetarioEngine(p)
        self.motor_actual = self.perfil_actual = motor
        self.sim.set_geometria(motor)
        self.perfilActualizado.emit(motor)
        self._emitir_estado()
        self.statusBar().showMessage(motor.razones_texto(), 6000)

    def _estado_para(self, angulo_grados: float):
        est = self.motor_actual.estado(math.radians(angulo_grados))
        return est, self.motor_actual.contactos(est)

    # ------------------------------------------------------------------ menú
    @manejador_seguro
    def _exportar(self, *_):
        e = self.motor_actual
        if e is None:
            return
        ruta, _f = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar a Excel (se crean _sol y _anular)",
                                                         self.ARCHIVO_EXCEL, "Libro de Excel (*.xlsx)")
        if not ruta:
            return
        base = ruta[:-5] if ruta.lower().endswith(".xlsx") else ruta
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            exportar_excel(base + "_sol.xlsx", e.sol, e.p_sol)
            exportar_excel(base + "_anular.xlsx", e.anular, e.p_anular)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self.statusBar().showMessage(f"Excel exportado: {base}_sol.xlsx y {base}_anular.xlsx", 5000)

    @manejador_seguro
    def _resumen(self, *_):
        e = self.motor_actual
        if e is None:
            return
        html = (e.resumen_html() + "<h2>Sol (engranaje externo)</h2>" + informe_html(e.sol, e.p_sol)
                + "<hr><h2>Anular (engranaje interno)</h2>" + informe_html(e.anular, e.p_anular))
        dlg = DialogoResumenDiseno(e.sol, e.p_sol, self)
        dlg._html = html                                     # el PDF exportado usa _html
        dlg.findChild(QtWidgets.QTextBrowser).setHtml(html)
        dlg.exec()
