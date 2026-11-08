# -*- coding: utf-8 -*-
"""
engine/cremallera_engine.py  (sistema TROCOIDAL en V2; se conserva el nombre interno)

Geometría de la curva TROCOIDAL: curva generatriz + su normal (offset = perfil real de diente), ángulo de
presión, camino de contacto, curvatura e indexación de dientes en el patrón LINEAL. La geometría del
piñón de rodillos la calcula RollerPinionEngine (self.rodillo). La curva base la dibuja la ventana.
"""
from __future__ import annotations
import numpy as np

from engine.base_engine import BaseEngine
from engine import math_utils as mu
from engine import backend_selector
from config.data_structures import ParametrosCremallera


class CremalleraEngine(BaseEngine):
    SIGNO_NORMAL = False
    NOMBRE_CURVA = "Trocoide"
    TIPO_ENSAMBLE = "lineal"
    FASE_INICIAL_PINON_RODILLOS_GRADOS = 180.0     # rodillo "0" abajo (-Y); sin rotación de vista

    def __init__(self, parametros: ParametrosCremallera):
        super().__init__(parametros)
        self.mrrp = self.rodillo.mrrp
        self.prrp = self.rodillo.prrp
        self.contexto.paso_lineal = self.calcular_paso()

    @property
    def radio_pinon_rodillos(self) -> float:
        return self.mrrp

    def curva_generatriz(self, theta, xp=np):
        a, b = self.prrp, self.mrrp
        return a * theta - b * xp.sin(theta), a - b * xp.cos(theta) - self.prrp

    def tangente_generatriz(self, theta, xp=np):
        a, b = self.prrp, self.mrrp
        return a - b * xp.cos(theta), b * xp.sin(theta)

    def calcular_paso(self) -> float:
        """paso = (2*pi*prrp) / Zrp — pitch LINEAL entre dientes consecutivos de la cremallera."""
        return (2.0 * np.pi * self.prrp) / self.parametros.numero_rodillos

    def calcular_theta_lim(self, theta_max_busqueda: float = np.pi / 2 - 1e-6) -> float:
        semipaso = self.calcular_paso() / 2.0

        def diferencia(theta):
            ox, _oy = self.curva_offset(theta)
            return ox - semipaso

        return mu.resolver_raiz_biseccion(diferencia, theta_min=1e-4, theta_max=theta_max_busqueda)

    def vector_referencia_cir(self, theta, xp=np):
        """CIRTangentvector = (1,0), constante: rodadura lineal a lo largo de X."""
        theta_arr = xp.asarray(theta, dtype=float)
        return xp.ones_like(theta_arr), xp.zeros_like(theta_arr)

    def camino_de_contacto(self, theta, xp=np):
        ox, oy = self.curva_offset(theta, xp=xp)
        return ox - self.prrp * theta, oy

    def generar_patron_lineal(self, num_dientes: int | None = None):
        """Ensambla varios dientes trasladados en X (CurvaTrasladada del PDF)."""
        resultado = self.generar_perfil()
        paso = resultado.paso
        if num_dientes is None:
            longitud = getattr(self.parametros, "longitud_cremallera", paso * 2)
            num_dientes = max(1, int(round(longitud / paso / 2.0)))
        n_copias = (2 * num_dientes + 2) + (-2)      # rango asimétrico -2..2*num_dientes+2 (validado visualmente)
        xp = backend_selector.xp_para(n_copias * resultado.offset_x.size)
        ox = xp.asarray(resultado.offset_x)
        oy = xp.asarray(resultado.offset_y)
        segmentos = [mu.trasladar(ox, oy, i * paso) for i in range(-2, 2 * num_dientes + 2)]
        patron_x, patron_y = mu.concatenar_segmentos(segmentos, xp=xp)
        resultado.patron_x = backend_selector.a_numpy(patron_x)
        resultado.patron_y = backend_selector.a_numpy(patron_y)
        resultado.patron_indices_diente = list(range(-2, 2 * num_dientes + 2))
        return resultado

    def generar_patron(self):
        resultado = self.generar_patron_lineal()
        resultado.pinon_centros_x, resultado.pinon_centros_y = self.centros_rodillos_pinon()
        resultado.pinon_plantilla_x, resultado.pinon_plantilla_y = self.plantilla_rodillo_pinon()
        resultado.rotacion_vista_grados = self.ROTACION_VISTA_SIMULACION_GRADOS
        resultado.distancia_centros_pinon = self.distancia_centros_pinon
        resultado.radio_paso_pinon = self.prrp
        if resultado.patron_x is not None and resultado.patron_x.size:
            x_min, x_max = float(np.nanmin(resultado.patron_x)), float(np.nanmax(resultado.patron_x))
        else:
            x_min = x_max = 0.0
        resultado.linea_paso_cremallera_x = np.array([x_min, x_max])
        resultado.linea_paso_cremallera_y = np.array([0.0, 0.0])
        resultado.radio_rodillo = self.radio_rodillo
        cx0, cy0 = self.curva_generatriz(0.0)
        num_dientes_estim = max(1, int(round(
            getattr(self.parametros, "longitud_cremallera", resultado.paso * 2) / resultado.paso / 2.0)))
        indices = np.arange(0, 2 * num_dientes_estim + 4)
        resultado.diente_centros_x = cx0 + indices * resultado.paso
        resultado.diente_centros_y = np.full_like(resultado.diente_centros_x, cy0, dtype=float)
        return resultado
