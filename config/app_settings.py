# -*- coding: utf-8 -*-
"""
Ajustes globales de la aplicación: apariencia, backend de cálculo (CPU/GPU) y
desviación de simulación. El control del banco físico ya NO vive aquí (ver banco_legacy/). Reemplaza al viejo config_rendimiento.py del
prototipo anterior: en vez de constantes sueltas a nivel de módulo, un
objeto mutable con una única instancia (singleton de módulo) que la UI
actualiza y que cualquier otra capa (engine, widgets) puede leer sin
acoplarse a Qt.
"""
from dataclasses import dataclass, field

from config.data_structures import AjustesDesviacion


@dataclass
class AjustesAplicacion:
    modo_oscuro: bool = True
    modo_hardware: str = "CPU"  # "CPU" | "GPU" | "Hibrido"
    # V2: PyQtGraph con viewport OpenGL (se aplica al iniciar la app; la grabación de
    # video usa widget.grab(), que es más fiable con render por software -> default False).
    render_opengl: bool = False
    desviacion: AjustesDesviacion = field(default_factory=AjustesDesviacion)


# Única fuente de verdad para toda la app. Se importa así:
#   from config.app_settings import ajustes
ajustes = AjustesAplicacion()
