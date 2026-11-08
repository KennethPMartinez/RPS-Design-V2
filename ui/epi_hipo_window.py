# -*- coding: utf-8 -*-
"""
ui/epi_hipo_window.py

Epitrocoidal e Hipotrocoidal comparten ventana (Epi_HipotrocoidalV2.ui): un único controlador
`VentanaEpiHipo` parametrizado por motor, parámetros y diálogo de visibilidad. Sistema ANGULAR:
control manual = dial + spinbox (ángulo acumulado del piñón).
"""
from __future__ import annotations

import numpy as np

from config.data_structures import ParametrosEpitrocoidal, ParametrosHipotrocoidal
from dialogs.mostrar_ocultar_dialog import DialogoMostrarOcultarEpitrocoidal, DialogoMostrarOcultarHipotrocoidal
from engine import math_utils as mu
from engine.epitrocoidal_engine import EpitrocoidalEngine
from engine.hipotrocoidal_engine import HipotrocoidalEngine
from ui.sistema_base import VentanaSistemaBase
from widgets.pg_helpers import AngleControl

from Epi_HipotrocoidalV2 import Ui_Epi_HipotrocoidalV2   # noqa: E402


class VentanaEpiHipo(VentanaSistemaBase):
    CLASE_UI = Ui_Epi_HipotrocoidalV2
    MAPEO_PARAMETROS = (("numero_dientes", "spinBox_numerodedientes"),
                        ("numero_rodillos", "spinBox_numeroderodillos"),
                        ("diametro_rodillos", "doubleSpinBox_diametro_rodillos"),
                        ("distancia_centro_rodillos", "doubleSpinBox_distancia_centros_rodillos"),
                        ("angulo_presion_minimo", "doubleSpinBox_angulo_presion_minimo"))

    def _crear_control(self):
        return AngleControl(self.ui.dial_posicion_theta, self.ui.doubleSpinBox_posicion_theta, self)

    def _widgets_control_manual(self):
        return (self.ui.dial_posicion_theta, self.ui.doubleSpinBox_posicion_theta)

    def _resolver_estado(self, alterno, angulo_grados):
        return self._solver.resolver("angular", True, alterno, angulo_grados, 0.0)

    def _curva_base(self, motor):
        """Curva generatriz del diente 0 para θ ∈ [0, 2π], en el marco de vista."""
        bx, by = motor.curva_generatriz(np.linspace(0.0, 2.0 * np.pi, 2001))
        return mu.rotar(bx, by, np.radians(motor.ROTACION_VISTA_SIMULACION_GRADOS))


class VentanaEpitrocoidal(VentanaEpiHipo):
    SISTEMA = "EPITROCOIDAL"
    NOMBRE = "Epitrocoidal"
    CLASE_PARAMETROS = ParametrosEpitrocoidal
    CLASE_MOTOR = EpitrocoidalEngine
    CLASE_DIALOGO_VISIBILIDAD = DialogoMostrarOcultarEpitrocoidal
    ARCHIVO_EXCEL = "epitrocoidal.xlsx"

    def _preparar_ui(self):
        self.setWindowTitle("Epitrocoidal")


class VentanaHipotrocoidal(VentanaEpiHipo):
    SISTEMA = "HIPOTROCOIDAL"
    NOMBRE = "Hipotrocoidal"
    CLASE_PARAMETROS = ParametrosHipotrocoidal
    CLASE_MOTOR = HipotrocoidalEngine
    CLASE_DIALOGO_VISIBILIDAD = DialogoMostrarOcultarHipotrocoidal
    ARCHIVO_EXCEL = "hipotrocoidal.xlsx"

    def _preparar_ui(self):
        """Mismo .ui que Epitrocoidal: se ajustan el título, el rótulo y el valor por defecto (36 = anular)."""
        self.setWindowTitle("Hipotrocoidal")
        self.ui.label.setText("Número de dientes \n(Engranaje Anular)")
        self.ui.spinBox_numerodedientes.setValue(36)
