# -*- coding: utf-8 -*-
"""
engine/rollerpinion_engine.py

Geometría del PIÑÓN DE RODILLOS: diámetros/radios de interés, reparto e
indexación de sus Zrp rodillos, y la plantilla reutilizable para dibujarlos.
Antes esta lógica vivía repartida entre BaseEngine (radio_rodillo,
plantilla_rodillo_pinon, centros_rodillos_pinon) y cada motor concreto
(mrrp/d con variantes de la misma fórmula copiadas 3 veces, ver
progress.md §6). RollerPinionEngine es ahora la ÚNICA fuente de esa
fórmula y de la indexación angular del piñón.

CORRECCIÓN DE FÓRMULA: este valor pasó por 2 versiones intermedias durante
la reestructuración (ver historial del chat) antes de la confirmada por
Kenneth el 27 jul 2026: mrrp = rd / Sin(2*pi/Zrp). Única definición en todo
el programa -- los 3 motores de curva la consumen de aquí en vez de
recalcularla cada uno por su lado.

No conoce la curva del diente (eso es CurvaBase/*Engine) ni la cinemática
del ensamble en vivo (eso es CinematicaEngine): solo geometría ESTÁTICA del
propio piñón, en su marco local sin rotar.
"""
from __future__ import annotations
import numpy as np

from config.data_structures import ParametrosRodillos
from engine.system_context import ContextoSistema


class RollerPinionEngine:
    def __init__(self, parametros: ParametrosRodillos, contexto: ContextoSistema):
        self.parametros = parametros
        self.contexto = contexto

        Zrp = parametros.numero_rodillos
        rd = parametros.distancia_centro_rodillos
        Fr = 1.0 / np.cos(np.radians(parametros.angulo_presion_minimo))

        self.radio_rodillo = parametros.diametro_rodillos / 2.0
        # Fórmula confirmada por Kenneth (27 jul 2026) -- reemplaza la versión
        # anterior (2*rd*Cos(pi/Zrp)) usada durante la reestructuración.
        self.mrrp = rd / (2.0*np.sin(np.pi / Zrp))
        self.prrp = self.mrrp * Fr

        contexto.radio_rodillo = self.radio_rodillo
        # V2: el factor de giro en modo Orbitar es cd/prrp (confirmado por Kenneth), no cd/mrrp.
        contexto.radio_primitivo_pinon_rodillos = self.prrp

    # ------------------------------------------------------------------
    # Geometría estática (marco local del piñón, sin rotar)
    # ------------------------------------------------------------------
    def plantilla_rodillo(self, n_puntos: int = 1001):
        """Círculo unitario (radio=radio_rodillo) centrado en el origen --
        se traslada Zrp veces a cada centro en vez de regenerarse (un
        círculo es rotacionalmente simétrico, no hace falta rotarlo)."""
        angulos = np.linspace(0, 2 * np.pi, n_puntos)
        return self.radio_rodillo * np.cos(angulos), self.radio_rodillo * np.sin(angulos)

    def centros_rodillos(self):
        """Centros SIN ROTAR de los Zrp rodillos, repartidos uniformemente
        cada `paso_angular_rodillo` sobre un círculo de radio mrrp.
        `fase_inicial_pinon_rodillos_grados` (progress.md §24) decide dónde
        arranca el rodillo "0"; puramente estético/de encuadre inicial, no
        afecta la indexación de contacto (ver contact_engine.py, que indexa
        por ángulo motor, no por esta fase)."""
        Zrp = self.parametros.numero_rodillos
        fase = np.radians(self.contexto.fase_inicial_pinon_rodillos_grados)
        fi = fase + np.arange(Zrp) * self.contexto.paso_angular_rodillo
        return self.mrrp * np.sin(fi), self.mrrp * np.cos(fi)

    def muestrear_circulo(self, radio: float, n_puntos: int = 96):
        """Círculo de referencia genérico (círculos de paso, etc.), centrado
        en el origen -- geometría trivial y chica, siempre NumPy."""
        angulos = np.linspace(0, 2 * np.pi, n_puntos)
        return radio * np.cos(angulos), radio * np.sin(angulos)
