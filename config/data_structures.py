# -*- coding: utf-8 -*-
"""
Estructuras de datos que definen el contrato de parámetros entre la capa
UI y la capa engine. Ningún widget de Qt cruza esta frontera: solo estos
dataclasses, ya leídos y validados, con tipos nativos de Python.

Mantener esta separación es lo que permite que la UI siga funcionando
aunque el motor de cálculo falle (o todavía no exista): la UI solo sabe
construir y validar estos objetos, nunca conoce a QDoubleSpinBox más allá
de system_window.py.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class TipoSistema(Enum):
    CREMALLERA = auto()
    HIPOTROCOIDAL = auto()
    EPITROCOIDAL = auto()
    PLANETARIO = auto()


class ComponenteBloqueado(Enum):
    ANULAR = "Anular"
    BRAZO = "Brazo"
    SOL = "Sol"


@dataclass
class ParametrosRodillos:
    """Parámetros comunes a los 4 sistemas: la corona de rodillos
    generatriz del perfil. Los rangos reflejan los límites ya impuestos
    por los QSpinBox/QDoubleSpinBox en los .ui (min/max, decimals), pero
    se revalidan aquí porque este dataclass puede construirse también
    fuera de la UI (tests, importación de archivos .rpsf, etc.)."""
    numero_rodillos: int = 12
    diametro_rodillos: float = 3.0
    distancia_centro_rodillos: float = 8.5
    angulo_presion_minimo: float = 17.0  # grados, rango [1°, 45°]

    def es_valido(self) -> bool:
        return (
            self.numero_rodillos >= 3
            and self.diametro_rodillos > 0
            and self.distancia_centro_rodillos > 0
            and 1.0 <= self.angulo_presion_minimo <= 45.0
        )


@dataclass
class ParametrosCremallera(ParametrosRodillos):
    """La cremallera no tiene 'número de dientes' (es infinita en teoría);
    en su lugar se limita por longitud física."""
    longitud_cremallera: float = 100.0

    def es_valido(self) -> bool:
        return super().es_valido() and self.longitud_cremallera > 0


@dataclass
class ParametrosHipotrocoidal(ParametrosRodillos):
    numero_dientes: int = 12  # dientes del anillo hipotrocoidal (Zhtg)

    def es_valido(self) -> bool:
        return super().es_valido() and self.numero_dientes >= 3


@dataclass
class ParametrosEpitrocoidal(ParametrosRodillos):
    numero_dientes: int = 12  # dientes del piñón epitrocoidal (Zetg)

    def es_valido(self) -> bool:
        return super().es_valido() and self.numero_dientes >= 3


@dataclass
class ParametrosPlanetario(ParametrosRodillos):
    numero_dientes_sol: int = 12
    componente_bloqueado: ComponenteBloqueado = ComponenteBloqueado.ANULAR
    # No es un valor libre: lo resuelve el motor (ver Cálculo_de_numero_de_
    # planetas). Se deja pendiente a propósito hasta implementar esa regla.
    numero_planetas: Optional[int] = None

    def es_valido(self) -> bool:
        return super().es_valido() and self.numero_dientes_sol >= 3


@dataclass
class ParametrosSimulacion:
    """Estado de la Pestaña 5. 'modo' distingue Cremallera (lineal) del
    resto (angular): sus widgets de simulación son físicamente distintos
    (slider + spinbox lineal, contra dial + spinbox angular)."""
    activa: bool = False
    modo: str = "angular"  # "angular" | "lineal"
    posicion_theta_grados: float = 0.0          # modo angular
    posicion_x_mm: float = 0.0                  # modo lineal (Cremallera)
    posicion_angular_motor_grados: float = 0.0  # solo lectura, informativo
    # Lee comboBox_modo_pinon (Pasos_a_seguir_1407262.docx, items 7 y 13): False = índice 0
    # del combo ("Fijo en Origen"/"Fijo en X+" -- el piñón queda quieto y es el patrón el
    # que se mueve, comportamiento que ya existía). True = índice 1 ("Trasladar"/"Orbitar"
    # -- ahora es el piñón el que se mueve y el patrón el que queda fijo). Nombre genérico
    # porque el significado exacto de "moverse" difiere entre Cremallera (traslada) y
    # Epi/Hipotrocoidal (orbita) -- ver widgets/opengl_widget.py, que sí distingue.
    modo_pinon_alterno: bool = False


@dataclass
class AjustesVisibilidadSimulacion:
    """Refleja los checkboxes de Mostrar_Ocultar_<sistema>.ui (Pasos_a_seguir_1307262.docx,
    Actividad 6): qué capas opcionales se dibujan en la Pestaña 5 (y, para contacto, también
    en la Pestaña 1) -- pensado para que el usuario pueda desacoplarlas por rendimiento. Los
    4 diálogos no comparten exactamente el mismo set de checkboxes; este dataclass es la
    UNIÓN de todos, cada diálogo concreto (ver dialogs/mostrar_ocultar_dialog.py) solo
    lee/escribe los campos para los que tiene checkbox habilitado en su .ui.
    'circulos_de_paso', 'curva_base' y 'lineas_de_accion' quedan declarados aquí para que el
    contrato esté completo, pero el render de esas 3 capas aún NO está implementado (ver
    progress.md §15) -- togglearlos hoy no tiene efecto visual todavía."""
    circulos_de_paso: bool = False
    curva_base: bool = False
    lineas_de_accion: bool = False
    camino_de_contacto: bool = False
    puntos_de_contacto: bool = True    # ya se dibujaban siempre antes de esta actividad
    etiquetas_de_rodillo: bool = True  # ídem


@dataclass
class AjustesDesviacion:
    """Corresponde a Desviacion.ui: controla la resolución de muestreo de
    la simulación (Pestaña 5), no la geometría del diente."""
    desviacion_lineal_mm: float = 0.0003     # rango [0, 0.1] mm, paso 0.0001
    desviacion_angular_grados: float = 0.5   # rango [0, 1]°, paso 0.0001
    no_mostrar_de_nuevo: bool = False
