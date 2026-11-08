# -*- coding: utf-8 -*-
"""
engine/hipotrocoidal_engine.py

Geometría de la curva HIPOTROCOIDAL (perfil interior/anular): curva generatriz + su normal (offset
invertido, SIGNO_NORMAL=True), ángulo de presión, camino de contacto, curvatura e indexación de dientes
en el patrón angular. `contexto.perfil_interior=True` es lo único que distingue el signo de los factores
de giro respecto a Epitrocoidal (mismo SolverCinematico). La curva base la dibuja la ventana
(no depende de BaseEngine.curva_base_completa).
"""
from __future__ import annotations
import numpy as np

from engine.base_engine import BaseEngine
from engine import math_utils as mu
from engine import backend_selector
from engine.cinematica_engine import SolverCinematico
from config.data_structures import ParametrosHipotrocoidal


class HipotrocoidalEngine(BaseEngine):
    SIGNO_NORMAL = True   # offset hacia el lado opuesto (perfil interior/anular)
    NOMBRE_CURVA = "Hipotrocoide"
    TIPO_ENSAMBLE = "angular"
    ROTACION_VISTA_SIMULACION_GRADOS = -90.0
    FASE_INICIAL_PINON_RODILLOS_GRADOS = 0.0     # deja al rodillo "0" a la DERECHA (+X) tras la rotación de vista

    def __init__(self, parametros: ParametrosHipotrocoidal):
        super().__init__(parametros)
        Zrp = parametros.numero_rodillos
        Zhtg = parametros.numero_dientes

        self.i = Zhtg / Zrp
        self.r = self.rodillo.prrp       # "r" en el PDF
        self.d = self.rodillo.mrrp       # "d"/"rdrp" en el PDF
        self.R1 = self.r * self.i        # "prhtg" en el PDF
        self.prhtg = self.R1
        self._m = (self.R1 - self.r) / self.r

        self.contexto.perfil_interior = True
        self.contexto.relacion_transmision = self.i
        self.contexto.distancia_centros_pinon = self.distancia_centros_pinon
        self.contexto.radio_paso_engranaje = self.R1     # para calcular_cir()

    @property
    def distancia_centros_pinon(self) -> float:
        """cd = prhtg - prrp."""
        return self.R1 - self.r

    @property
    def radio_valle(self) -> float:
        return self.distancia_centros_pinon - self.radio_pinon_rodillos

    @property
    def radio_cresta(self) -> float:
        gx, gy = self.curva_generatriz(self.theta_lim)
        return float(np.hypot(gx, gy))

    @property
    def radio_circulo_centro_rodillo_raiz(self) -> float:
        """Signo invertido respecto al caso externo (interior/anular)."""
        return self.distancia_centros_pinon + self.radio_pinon_rodillos

    def curva_generatriz(self, theta, xp=np):
        R1, r, d, m = self.R1, self.r, self.d, self._m
        x = (R1 - r) * xp.sin(theta) - d * xp.sin(m * theta)
        y = (R1 - r) * xp.cos(theta) + d * xp.cos(m * theta)
        return x, y

    def tangente_generatriz(self, theta, xp=np):
        R1, r, d, m = self.R1, self.r, self.d, self._m
        dx = (R1 - r) * xp.cos(theta) - d * m * xp.cos(m * theta)
        dy = -(R1 - r) * xp.sin(theta) - d * m * xp.sin(m * theta)
        return dx, dy

    def calcular_paso(self) -> float:
        return 2.0 * np.pi / self.parametros.numero_rodillos

    def calcular_theta_lim(self, theta_max_busqueda: float = np.pi / 2 - 1e-6) -> float:
        semipaso_angular = np.pi / self.parametros.numero_dientes

        def diferencia(theta):
            ox, oy = self.curva_offset(theta)
            return np.arctan2(ox, oy) - semipaso_angular

        return mu.resolver_raiz_biseccion(diferencia, theta_min=1e-4, theta_max=theta_max_busqueda)

    def cir(self, theta, xp=np):
        """CIR(θ) = (prhtg*sin θ, prhtg*cos θ)."""
        return self.R1 * xp.sin(theta), self.R1 * xp.cos(theta)

    def vector_referencia_cir(self, theta, xp=np):
        return xp.cos(theta), -xp.sin(theta)

    def camino_de_contacto(self, theta, xp=np):
        ox, oy = self.curva_offset(theta, xp=xp)
        cx, cy = self.cir(theta, xp=xp)
        rx, ry = mu.rotar(ox - cx, oy - cy, theta, xp=xp)
        return rx, ry + self.R1

    def generar_patron_angular(self, num_unidades: int | None = None):
        resultado = self.generar_perfil()
        if num_unidades is None:
            num_unidades = self.parametros.numero_dientes
        xp = backend_selector.xp_para(num_unidades * resultado.offset_x.size)
        ox = xp.asarray(resultado.offset_x)
        oy = xp.asarray(resultado.offset_y)
        segmentos = [mu.rotar(ox, oy, (2.0 * np.pi * i) / num_unidades, xp=xp) for i in range(num_unidades)]
        patron_x, patron_y = mu.concatenar_segmentos(segmentos, xp=xp)
        resultado.patron_x = backend_selector.a_numpy(patron_x)
        resultado.patron_y = backend_selector.a_numpy(patron_y)
        resultado.patron_indices_diente = list(range(num_unidades))
        return resultado

    def generar_patron(self):
        resultado = self.generar_patron_angular()
        rot = np.radians(self.ROTACION_VISTA_SIMULACION_GRADOS)
        resultado.patron_x, resultado.patron_y = mu.rotar(resultado.patron_x, resultado.patron_y, rot)
        cx, cy = self.centros_rodillos_pinon()
        resultado.pinon_centros_x, resultado.pinon_centros_y = mu.rotar(cx, cy, rot)
        resultado.pinon_plantilla_x, resultado.pinon_plantilla_y = self.plantilla_rodillo_pinon()
        resultado.rotacion_vista_grados = self.ROTACION_VISTA_SIMULACION_GRADOS
        resultado.distancia_centros_pinon = self.distancia_centros_pinon

        solver = SolverCinematico(self.contexto)
        resultado.factor_giro_pinon_fijo = solver.factor_giro_fijo()
        resultado.factor_giro_pinon_orbitar = solver.factor_giro_orbitar()

        resultado.radio_paso_engranaje = self.R1
        resultado.radio_paso_pinon = self.r
        resultado.radio_rodillo = self.radio_rodillo

        cx0, cy0 = self.curva_generatriz(0.0)
        betas = np.arange(self.parametros.numero_dientes) * (2.0 * np.pi / self.parametros.numero_dientes)
        dcx, dcy = mu.rotar(cx0, cy0, betas)
        resultado.diente_centros_x, resultado.diente_centros_y = mu.rotar(dcx, dcy, rot)
        return resultado
