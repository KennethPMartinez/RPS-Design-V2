# -*- coding: utf-8 -*-
"""
engine/system_context.py

Repositorio único de índices y constantes geométricas compartidas entre
RollerPinionEngine, los motores de curva (Cremallera/Epitrocoidal/
Hipotrocoidal), CinematicaEngine y ContactEngine. Antes cada uno de esos
módulos repetía (o recalculaba con su propio criterio) cosas como el paso
angular de un rodillo, el tipo de ensamble, la rotación de vista o la fase
inicial del piñón -- ContextoSistema es la ÚNICA fuente de verdad para todo
eso, construida una sola vez por instancia de motor concreto (ver
BaseEngine.__init__) y pasada por REFERENCIA a quien la necesite (no se
copia: si RollerPinionEngine puebla `radio_rodillo`, CinematicaEngine y
ContactEngine ya lo ven sin que nadie se los tenga que reenviar a mano).

No contiene lógica de cálculo pesado (curvas, contacto, cinemática): es
puramente un contenedor + un puñado de propiedades derivadas triviales
(paso_angular_rodillo, paso_angular_diente) que antes se recalculaban con
`2*np.pi/Zrp` sueltos en 3-4 sitios distintos del código.

PENSADO PARA LA PRÓXIMA UI DE ANIMACIÓN: al ser el único índice, agregar un
campo nuevo (p. ej. un identificador de "capa" para mostrar/ocultar, o un
límite de velocidad angular) se hace UNA vez aquí y queda disponible para
todo el pipeline (engine -> cinemática -> contacto -> render), en vez de
tener que tocar 3-4 archivos cada vez.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class ContextoSistema:
    """Índice único de identidad geométrica de una instancia de motor.

    Se llena en 3 tiempos:
      1) Al construirse (BaseEngine.__init__), con lo que ya se conoce por
         los parámetros de entrada (Zrp, Zg, tipo de ensamble, fases).
      2) Justo después, cuando RollerPinionEngine calcula los radios
         propios del piñón (radio_rodillo, radio_primitivo_pinon_rodillos).
      3) Cuando el motor de curva concreto (Epi/Hipotrocoidal) calcula su
         relación de transmisión y distancia entre centros -- Cremallera
         no toca `relacion_transmision` (queda None: no aplica) ni
         `perfil_interior` (queda False: no aplica).
    """
    tipo_ensamble: str  # "angular" | "lineal"
    numero_rodillos: int  # Zrp
    numero_dientes: Optional[int] = None  # Zg (None en Cremallera)
    rotacion_vista_grados: float = 0.0
    fase_inicial_pinon_rodillos_grados: float = 0.0

    # Poblado por RollerPinionEngine (ver rollerpinion_engine.py)
    radio_rodillo: Optional[float] = None
    radio_primitivo_pinon_rodillos: Optional[float] = None  # V2: = prrp (radio primitivo), usado por factor_giro_orbitar

    # Poblado por el motor de curva concreto (Epi/Hipotrocoidal)
    relacion_transmision: Optional[float] = None  # "i" = Zg/Zrp (None en Cremallera)
    distancia_centros_pinon: float = 0.0  # "cd" (0.0 en Cremallera: mismo eje)
    perfil_interior: bool = False  # True = Hipotrocoidal (engranaje anular)
    paso_lineal: Optional[float] = None  # Cremallera: paso entre dientes (mm)
    radio_paso_engranaje: Optional[float] = None  # "R1"/"pretg"/"prhtg" -- None en Cremallera
    # (no existe "engranaje" circular en una cremallera, ver linea_paso_cremallera_x/y)

    def __post_init__(self) -> None:
        if self.numero_rodillos <= 0:
            raise ValueError("numero_rodillos debe ser > 0 (ContextoSistema).")

    @property
    def paso_angular_rodillo(self) -> float:
        """2π/Zrp -- pitch angular entre 2 rodillos consecutivos del piñón."""
        return 2.0 * np.pi / self.numero_rodillos

    @property
    def paso_angular_diente(self) -> Optional[float]:
        """2π/Zg -- pitch angular entre 2 dientes consecutivos del engranaje
        (solo motores angulares; None en Cremallera, que usa paso_lineal)."""
        if self.numero_dientes is None:
            return None
        return 2.0 * np.pi / self.numero_dientes

    def normalizar_id_diente(self, indice_diente: int) -> int:
        """ID canónico 0..numero_dientes-1 (el patrón angular es periódico);
        en Cremallera (tipo_ensamble='lineal') el índice ya es único por
        diente físico -- no hay módulo que aplicar."""
        if self.tipo_ensamble == "angular":
            return indice_diente % self.numero_dientes
        return indice_diente
