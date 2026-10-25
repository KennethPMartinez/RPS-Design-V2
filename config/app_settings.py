# -*- coding: utf-8 -*-
"""
Ajustes globales de la aplicación: apariencia, backend de hardware y
desviación de simulación. Reemplaza al viejo config_rendimiento.py del
prototipo anterior: en vez de constantes sueltas a nivel de módulo, un
objeto mutable con una única instancia (singleton de módulo) que la UI
actualiza y que cualquier otra capa (engine, widgets) puede leer sin
acoplarse a Qt.
"""
from dataclasses import dataclass, field

from config.data_structures import AjustesDesviacion


@dataclass
class AjustesMotor:
    """Motor paso a paso real (Arduino Mega por puerto serie, ver hardware/motor.py)."""
    habilitado: bool = False          # ejecutar en el motor al dar Play (modo automático)
    simulado: bool = False            # MotorSimulado: prueba el flujo sin hardware
    puerto: str = ""                  # "COM3", "/dev/ttyACM0"...
    baud: int = 115200
    relacion: float = 1.0             # vueltas del MOTOR por vuelta del piñón (reductor)
    invertir: bool = False            # invierte el sentido de giro
    rpm_max: float = 600.0            # tope de seguridad (rpm del motor)
    acel: float = 8000.0              # pasos/s² (debe coincidir con ACEL del firmware)
    rpm_alineacion: float = 30.0      # velocidad al alinear motor y simulación
    dt_segmento: float = 1.0          # s por comando MOVE al seguir el perfil
    tolerancia_silenciosa_deg: float = 3.0   # desfase que se absorbe sin preguntar


@dataclass
class AjustesAplicacion:
    modo_oscuro: bool = True
    modo_hardware: str = "CPU"  # "CPU" | "GPU" | "Hibrido"
    # V2: PyQtGraph con viewport OpenGL (se aplica al iniciar la app; la grabación de
    # video usa widget.grab(), que es más fiable con render por software -> default False).
    render_opengl: bool = False
    desviacion: AjustesDesviacion = field(default_factory=AjustesDesviacion)
    motor: AjustesMotor = field(default_factory=AjustesMotor)


# Única fuente de verdad para toda la app. Se importa así:
#   from config.app_settings import ajustes
ajustes = AjustesAplicacion()
