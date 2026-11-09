# -*- coding: utf-8 -*-
"""
ui/trocoidal_window.py

Ventana del sistema TROCOIDAL (antes "Cremallera"; TrocoidalV2.ui). Sistema LINEAL: el piñón rueda
sin deslizar sobre la cremallera, X = prrp·θ. Control manual = slider + spinbox de X (mm), con rango
[0, longitud de la cremallera]. El perfil de la línea de tiempo sigue siendo el ángulo del piñón (°).
Nombres internos (CremalleraEngine, ParametrosCremallera) se conservan.
"""
from __future__ import annotations

import math

import numpy as np

from config.data_structures import ParametrosCremallera
from dialogs.mostrar_ocultar_dialog import DialogoMostrarOcultarTrocoidal
from engine.cremallera_engine import CremalleraEngine
from ui.sistema_base import VentanaSistemaBase
from widgets.pg_helpers import ControlLineal

from TrocoidalV2 import Ui_TrocoidalV2   # noqa: E402


class VentanaTrocoidal(VentanaSistemaBase):
    SISTEMA = "TROCOIDAL"
    NOMBRE = "Trocoidal"
    LINEAL = True
    CLASE_UI = Ui_TrocoidalV2
    CLASE_PARAMETROS = ParametrosCremallera
    CLASE_MOTOR = CremalleraEngine
    CLASE_DIALOGO_VISIBILIDAD = DialogoMostrarOcultarTrocoidal
    ARCHIVO_EXCEL = "trocoidal.xlsx"
    MAPEO_PARAMETROS = (("longitud_cremallera", "doubleSpinBox_Longitudcremallera"),
                        ("numero_rodillos", "SpinBox_numeroderodillos"),
                        ("diametro_rodillos", "doubleSpinBox_diametro_rodillos"),
                        ("distancia_centro_rodillos", "doubleSpinBox_distancia_centros_rodillos"),
                        ("angulo_presion_minimo", "doubleSpinBox_angulo_presion_minimo"))

    def _preparar_ui(self):
        sp = self.ui.doubleSpinBox_posicion_angular_motor      # solo lectura: muestra el ángulo del piñón
        sp.setRange(-1e9, 1e9)

    def _crear_control(self):
        return ControlLineal(self.ui.horizontalSlider_posicion_x, self.ui.doubleSpinBox_posicion_x, self)

    def _widgets_control_manual(self):
        return (self.ui.doubleSpinBox_posicion_x, self.ui.horizontalSlider_posicion_x)

    def _actualizar_rango_control(self, parametros):
        self.control.set_rango(0.0, float(parametros.longitud_cremallera))

    def _prrp(self) -> float:
        return self.motor_actual.rodillo.prrp if self.motor_actual is not None else 1.0

    def _rango_angulo_auto(self):
        """El piñón rueda sin deslizar: X = prrp·θ debe quedar en [0, L] -> θ en [0, L/prrp] (°)."""
        if self.motor_actual is None:
            return None
        return 0.0, math.degrees(float(self.motor_actual.parametros.longitud_cremallera) / self._prrp())

    # rodadura sin deslizamiento: X = prrp·θ(rad)
    def _angulo_desde_valor(self, x_mm):
        return math.degrees(x_mm / self._prrp())

    def _valor_desde_angulo(self, angulo_grados):
        return math.radians(angulo_grados) * self._prrp()

    def _resolver_estado(self, alterno, angulo_grados):
        return self._solver.resolver("lineal", True, alterno, angulo_grados, self._valor_desde_angulo(angulo_grados))

    def _curva_base(self, motor):
        """Trocoide generatriz sobre el largo visible de la cremallera (θ = ±L/prrp)."""
        th_max = self.motor_actual.parametros.longitud_cremallera / motor.rodillo.prrp
        return motor.curva_generatriz(np.linspace(-th_max, th_max, 4001))

    def _refrescar_indicadores(self, angulo_grados):
        sp = self.ui.doubleSpinBox_posicion_angular_motor
        sp.blockSignals(True); sp.setValue(angulo_grados); sp.blockSignals(False)
