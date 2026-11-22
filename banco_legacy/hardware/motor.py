# -*- coding: utf-8 -*-
"""
hardware/motor.py

Motor paso a paso (Arduino Mega por serie). `Motor` es la clase tal como la definió Kenneth
(protocolo: "MOVE <revs> <rpm>\\n" -> "OK" al terminar; "S" detiene). Únicos cambios:
`import serial` diferido (el programa abre sin pyserial si no se usa el motor) y
`MotorSimulado`, con la misma interfaz, para probar todo el flujo sin hardware.
"""
import threading
import time

from engine.motor_plan import ACEL, PASOS_REV, duracion_trapecio


class Motor:
    PASOS_REV = PASOS_REV
    ACEL = ACEL

    def __init__(self, puerto, baud=115200):
        import serial                     # pip install pyserial
        self.ser = serial.Serial(puerto, baud, timeout=2)
        time.sleep(2)                     # la Mega se reinicia al abrir el puerto
        self.ser.reset_input_buffer()

    def mover(self, revs, rpm=100):
        # Estimar duración para fijar el timeout
        v = rpm * self.PASOS_REV / 60
        t_rampa = v / self.ACEL
        t_est = abs(revs) * 60 / rpm + t_rampa + 3
        self.ser.timeout = t_est

        self.ser.write(f"MOVE {revs} {rpm}\n".encode())
        resp = self.ser.readline().decode().strip()
        if resp != "OK":
            raise RuntimeError(f"Respuesta inesperada: {resp!r}")

    def parar(self):
        self.ser.write(b"S")

    def cerrar(self):
        self.ser.close()


class MotorSimulado:
    """Misma interfaz que Motor; `mover` bloquea lo que duraría el movimiento real."""
    PASOS_REV = PASOS_REV
    ACEL = ACEL

    def __init__(self):
        self._alto = threading.Event()
        self.historial = []               # [(revs, rpm)] para verificar en pruebas

    def mover(self, revs, rpm=100):
        self._alto.clear()
        self.historial.append((revs, rpm))
        s, v = abs(revs) * self.PASOS_REV, rpm * self.PASOS_REV / 60
        self._alto.wait(duracion_trapecio(s, v, self.ACEL))

    def parar(self):
        self._alto.set()

    def cerrar(self):
        pass
