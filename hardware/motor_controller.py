# -*- coding: utf-8 -*-
"""
hardware/motor_controller.py

Controlador del motor para la GUI: conexión, ejecución de un plan de `Segmento` en un hilo
(Motor.mover BLOQUEA hasta recibir OK: nunca se llama desde el hilo de la interfaz), parada
inmediata y estimación de la posición del motor.

`pos_deg` = posición estimada del motor en grados de SIMULACIÓN (° del piñón). Se actualiza
con cada tramo completado (exacto) y, si se detiene a mitad de un tramo, con el modelo
trapezoidal (estimación: no hay encoder ni realimentación en el protocolo actual).
"""
from __future__ import annotations

import dataclasses
import threading
import time
from typing import Optional

from PySide6 import QtCore

from config.app_settings import ajustes
from engine.motor_plan import Segmento, posicion_trapecio

_CTRL: Optional["ControladorMotor"] = None


def obtener_controlador() -> "ControladorMotor":
    global _CTRL
    if _CTRL is None:
        _CTRL = ControladorMotor()
        cargar_ajustes_motor()
    return _CTRL


# --- persistencia (QSettings): no hay que reescribir el puerto en cada sesión -----------
def cargar_ajustes_motor() -> None:
    qs = QtCore.QSettings("RPSDesign", "V2")
    for f in dataclasses.fields(ajustes.motor):
        v = qs.value(f"motor/{f.name}")
        if v is None:
            continue
        try:
            actual = getattr(ajustes.motor, f.name)
            nuevo = (str(v).lower() in ("true", "1")) if isinstance(actual, bool) else type(actual)(v)
            setattr(ajustes.motor, f.name, nuevo)
        except (TypeError, ValueError):
            pass
    ajustes.motor.habilitado = False          # nunca arrancar con el motor armado


def guardar_ajustes_motor() -> None:
    qs = QtCore.QSettings("RPSDesign", "V2")
    for f in dataclasses.fields(ajustes.motor):
        if f.name != "habilitado":
            qs.setValue(f"motor/{f.name}", getattr(ajustes.motor, f.name))


class _Hilo(QtCore.QThread):
    def __init__(self, ctrl, plan, etiqueta):
        super().__init__()
        self.ctrl, self.plan, self.etiqueta = ctrl, plan, etiqueta
        self.cancelado = False

    def _espera(self, seg_s: float):
        fin = time.perf_counter() + seg_s
        while not self.cancelado and time.perf_counter() < fin:
            time.sleep(0.01)

    def run(self):
        c, ok, msg = self.ctrl, True, ""
        try:
            for i, seg in enumerate(self.plan):
                if self.cancelado:
                    break
                with c._lock:
                    c._seg, c._t_seg = seg, time.perf_counter()
                if seg.revs == 0:
                    self._espera(seg.duracion)
                else:
                    c.motor.mover(seg.revs, seg.rpm)
                with c._lock:
                    if c._seg is seg:                 # no lo contabilizó ya detener()
                        c.pos_deg += seg.delta_sim_deg
                        c._seg = None
                if not self.cancelado:
                    c.progreso.emit(i + 1, len(self.plan))
        except Exception as e:                        # RuntimeError de Motor.mover, serie caída...
            if not self.cancelado:
                ok, msg = False, str(e)
                try:
                    c.motor.parar()
                except Exception:
                    pass
        if self.cancelado:
            ok = False
            ser = getattr(c.motor, "ser", None)       # descarta la respuesta tardía a "S"
            if ser is not None:
                try:
                    time.sleep(0.2); ser.reset_input_buffer()
                except Exception:
                    pass
        c.terminado.emit(ok, msg, self.etiqueta)


class ControladorMotor(QtCore.QObject):
    progreso = QtCore.Signal(int, int)        # tramo completado, total
    terminado = QtCore.Signal(bool, str, str)  # ok, mensaje, etiqueta ("perfil" | "alineacion")
    conexionCambiada = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
        self.motor = None
        self.pos_deg = 0.0
        self._hilo: Optional[_Hilo] = None
        self._lock = threading.Lock()
        self._seg: Optional[Segmento] = None
        self._t_seg = 0.0

    @property
    def conectado(self) -> bool:
        return self.motor is not None

    def ocupado(self) -> bool:
        return self._hilo is not None and self._hilo.isRunning()

    def conectar(self) -> None:
        a = ajustes.motor
        if self.conectado:
            self.desconectar()
        if a.simulado:
            from hardware.motor import MotorSimulado
            self.motor = MotorSimulado()
        else:
            from hardware.motor import Motor
            if not a.puerto:
                raise ValueError("Elige un puerto serie.")
            self.motor = Motor(a.puerto, a.baud)
            self.motor.ACEL = a.acel
        self.pos_deg = 0.0
        self.conexionCambiada.emit(True)

    def desconectar(self) -> None:
        self.detener()
        if self._hilo is not None:
            self._hilo.wait(4000)
        if self.motor is not None:
            try:
                self.motor.cerrar()
            except Exception:
                pass
        self.motor = None
        self.conexionCambiada.emit(False)

    def referenciar(self, angulo_sim_deg: float) -> None:
        """Declara que el motor está AHORA en este ángulo de simulación (sin moverlo)."""
        self.pos_deg = float(angulo_sim_deg)

    def ejecutar(self, plan, etiqueta: str = "perfil") -> None:
        if not self.conectado:
            raise RuntimeError("Motor no conectado.")
        if self.ocupado():
            raise RuntimeError("El motor sigue ocupado.")
        self._hilo = _Hilo(self, list(plan), etiqueta)
        self._hilo.start()

    def detener(self) -> None:
        """Parada inmediata ('S') y estimación de dónde quedó el motor. Seguro de llamar siempre."""
        h = self._hilo
        if h is None or not h.isRunning():
            return
        h.cancelado = True
        try:
            self.motor.parar()
        except Exception:
            pass
        with self._lock:
            seg = self._seg
            if seg is not None and seg.pasos > 0:
                hecho = posicion_trapecio(time.perf_counter() - self._t_seg, seg.pasos, seg.v_pasos_s, seg.acel)
                self.pos_deg += seg.delta_sim_deg * min(hecho / seg.pasos, 1.0)
            elif seg is not None:
                self.pos_deg += seg.delta_sim_deg * min((time.perf_counter() - self._t_seg) / max(seg.duracion, 1e-9), 1.0)
            self._seg = None
