# -*- coding: utf-8 -*-
"""
engine/epitrocoidal_engine.py

Geometría de la curva EPITROCOIDAL: curva generatriz + su normal (offset =
perfil real de diente), ángulo de presión, camino de contacto, curvatura, e
indexación/posicionamiento de sus dientes en el patrón de ensamble ANGULAR
(CurvaRotada del PDF). Fórmulas de Perfil_Epitrocoidal.pdf (ver progress.md
§4.2).

La geometría del piñón de rodillos (mrrp/prrp) la resuelve
RollerPinionEngine (self.rodillo, ver rollerpinion_engine.py); los signos
de giro del piñón (factor_giro_pinon_fijo/orbitar) los resuelve
CinematicaEngine.SolverCinematico a partir de `contexto.perfil_interior`
(False aquí: engranaje exterior) -- ya no son una propiedad propia de este
motor (antes casi idéntica a la de hipotrocoidal_engine.py, solo con el
signo cambiado -- ver progress.md).
"""
from __future__ import annotations
import numpy as np

from engine.base_engine import BaseEngine
from engine import math_utils as mu
from engine import backend_selector
from engine.cinematica_engine import SolverCinematico
from config.data_structures import ParametrosEpitrocoidal


class EpitrocoidalEngine(BaseEngine):
    SIGNO_NORMAL = False
    NOMBRE_CURVA = "Epitrocoide"
    TIPO_ENSAMBLE = "angular"
    # ROTACION_VISTA_SIMULACION_GRADOS de -90° ya rota el círculo del piñón; partiendo de
    # 180° aquí (antes de esa rotación), el rodillo "0" termina a la IZQUIERDA (-X), pedido
    # por Kenneth (progress.md §24).
    ROTACION_VISTA_SIMULACION_GRADOS = -90.0
    FASE_INICIAL_PINON_RODILLOS_GRADOS = 180.0

    def __init__(self, parametros: ParametrosEpitrocoidal):
        super().__init__(parametros)
        Zrp = parametros.numero_rodillos
        Zetg = parametros.numero_dientes

        self.i = Zetg / Zrp
        self.r = self.rodillo.prrp       # "r" en el PDF
        self.d = self.rodillo.mrrp       # "d"/"rdrp" en el PDF
        self.R1 = self.r * self.i        # "pretg" en el PDF
        self.pretg = self.R1
        self._k = (self.R1 + self.r) / self.r

        self.contexto.relacion_transmision = self.i
        self.contexto.distancia_centros_pinon = self.distancia_centros_pinon
        # Necesario para que engine.cinematica_engine.calcular_cir() (usado por
        # ContactEngine._cir_global) pueda calcular el CIR sin pedirlo prestado
        # al motor de curva -- ver contact_engine.py.
        self.contexto.radio_paso_engranaje = self.R1
        # perfil_interior queda en False (default de ContextoSistema): Epitrocoidal es
        # engranaje exterior-exterior.

    @property
    def distancia_centros_pinon(self) -> float:
        """cd = prrp + pretg (CONFIRMADO por Kenneth)."""
        return self.r + self.R1

    @property
    def radio_valle(self) -> float:
        return self.distancia_centros_pinon - self.radio_pinon_rodillos

    @property
    def radio_cresta(self) -> float:
        gx, gy = self.curva_generatriz(self.theta_lim)
        return float(np.hypot(gx, gy))

    def curva_generatriz(self, theta, xp=np):
        R1, r, d, k = self.R1, self.r, self.d, self._k
        x = (R1 + r) * xp.sin(theta) - d * xp.sin(k * theta)
        y = (R1 + r) * xp.cos(theta) - d * xp.cos(k * theta)
        return x, y

    def tangente_generatriz(self, theta, xp=np):
        R1, r, d, k = self.R1, self.r, self.d, self._k
        dx = (R1 + r) * xp.cos(theta) - d * k * xp.cos(k * theta)
        dy = -(R1 + r) * xp.sin(theta) + d * k * xp.sin(k * theta)
        return dx, dy

    def calcular_paso(self) -> float:
        """paso = 2*pi/Zrp — pitch angular del rodillo generatriz (valor de
        referencia; no el incremento del patrón de ensamble)."""
        return 2.0 * np.pi / self.parametros.numero_rodillos

    def calcular_theta_lim(self, theta_max_busqueda: float = np.pi / 2 - 1e-6) -> float:
        semipaso_angular = np.pi / self.parametros.numero_dientes

        def diferencia(theta):
            ox, oy = self.curva_offset(theta)
            return np.arctan2(ox, oy) - semipaso_angular

        return mu.resolver_raiz_biseccion(diferencia, theta_min=1e-4,
                                           theta_max=theta_max_busqueda)

    def cir(self, theta, xp=np):
        """CIR(θ) = (pretg*sin θ, pretg*cos θ)."""
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
        segmentos = []
        for i in range(num_unidades):
            beta = (2.0 * np.pi * i) / num_unidades
            segmentos.append(mu.rotar(ox, oy, beta, xp=xp))
        patron_x, patron_y = mu.concatenar_segmentos(segmentos, xp=xp)
        resultado.patron_x = backend_selector.a_numpy(patron_x)
        resultado.patron_y = backend_selector.a_numpy(patron_y)
        resultado.patron_indices_diente = list(range(num_unidades))
        return resultado

    def generar_patron(self):
        resultado = self.generar_patron_angular()
        resultado.patron_x, resultado.patron_y = mu.rotar(
            resultado.patron_x, resultado.patron_y,
            np.radians(self.ROTACION_VISTA_SIMULACION_GRADOS))
        cx, cy = self.centros_rodillos_pinon()
        resultado.pinon_centros_x, resultado.pinon_centros_y = mu.rotar(
            cx, cy, np.radians(self.ROTACION_VISTA_SIMULACION_GRADOS))
        resultado.pinon_plantilla_x, resultado.pinon_plantilla_y = self.plantilla_rodillo_pinon()
        resultado.rotacion_vista_grados = self.ROTACION_VISTA_SIMULACION_GRADOS
        resultado.distancia_centros_pinon = self.distancia_centros_pinon

        # Factores de giro del piñón: ver CinematicaEngine.SolverCinematico
        # (única fórmula, signo derivado de contexto.perfil_interior=False).
        solver = SolverCinematico(self.contexto)
        resultado.factor_giro_pinon_fijo = solver.factor_giro_fijo()
        resultado.factor_giro_pinon_orbitar = solver.factor_giro_orbitar()

        resultado.radio_paso_engranaje = self.R1
        resultado.radio_paso_pinon = self.r
        resultado.radio_rodillo = self.radio_rodillo

        cx0, cy0 = self.curva_generatriz(0.0)
        betas = np.arange(self.parametros.numero_dientes) * (2.0 * np.pi / self.parametros.numero_dientes)
        dcx, dcy = mu.rotar(cx0, cy0, betas)
        dcx, dcy = mu.rotar(dcx, dcy, np.radians(self.ROTACION_VISTA_SIMULACION_GRADOS))
        resultado.diente_centros_x = dcx
        resultado.diente_centros_y = dcy
        return resultado
