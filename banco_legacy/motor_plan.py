# -*- coding: utf-8 -*-
"""
engine/motor_plan.py

Convierte la LineaTiempo (perfil de giro, engine/motion_engine.py) en una lista de comandos
`MOVE revs rpm` para el firmware actual. Sin Qt ni serial: puro cálculo, testeable.

LIMITACIÓN DEL PROTOCOLO ACTUAL (importante): `MOVE` es BLOQUEANTE (responde OK al terminar)
y cada movimiento hace su propia rampa trapezoidal (ACEL fija) arrancando y terminando en
reposo. Un perfil de velocidad variable solo puede seguirse POR TRAMOS: la posición al final
de cada tramo es exacta, pero entre tramos el motor frena y vuelve a arrancar. Cuanto más
corto el tramo, más se nota (y hay un mínimo físico: ACEL·T² ≥ 4·s). Para seguir el perfil
de forma continua hace falta un comando de streaming en el firmware (ver respuesta).

Modelo de duración (el mismo que usa Motor.mover para su timeout):
    T = s/v + v/a      (trapecio completo)      |   T = 2·sqrt(s/a)   (triangular, s < v²/a)
con s en pasos, v = rpm·PASOS_REV/60 en pasos/s y a = ACEL en pasos/s².
"""
from __future__ import annotations

import math
from dataclasses import dataclass

PASOS_REV = 6400
ACEL = 8000.0



@dataclass
class AjustesMotor:
    """(Archivado) Motor paso a paso real (Arduino Mega por puerto serie, ver hardware/motor.py)."""
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
class Segmento:
    delta_sim_deg: float          # giro del piñón en este tramo (ángulo de simulación, °)
    revs: float                   # revoluciones del MOTOR (con relación y sentido aplicados)
    rpm: float
    duracion: float               # s estimados que tarda el comando
    pasos: float = 0.0
    v_pasos_s: float = 0.0
    alineacion: bool = False
    acel: float = ACEL


def duracion_trapecio(s: float, v: float, a: float = ACEL) -> float:
    if s <= 0 or v <= 0:
        return 0.0
    return s / v + v / a if s >= v * v / a else 2.0 * math.sqrt(s / a)


def posicion_trapecio(t: float, s: float, v: float, a: float = ACEL) -> float:
    """Pasos recorridos tras t segundos de un MOVE de s pasos con pico v (estimación)."""
    if s <= 0 or v <= 0:
        return 0.0
    vp = min(v, math.sqrt(a * s))
    T = duracion_trapecio(s, v, a)
    t = min(max(t, 0.0), T)
    ta = vp / a
    if t < ta:
        return 0.5 * a * t * t
    if t > T - ta:
        return s - 0.5 * a * (T - t) ** 2
    return 0.5 * a * ta * ta + vp * (t - ta)


def rpm_para_duracion(s: float, T: float, rpm_max: float, a: float = ACEL, pasos_rev: int = PASOS_REV):
    """rpm con la que un MOVE de s pasos dura T segundos. Devuelve (rpm, duración_real, ok)."""
    v_max = rpm_max * pasos_rev / 60.0
    d = a * a * T * T - 4.0 * a * s
    if d < 0:                                   # físicamente imposible en T: lo más rápido posible
        v = min(math.sqrt(a * s), v_max)
        return v * 60.0 / pasos_rev, duracion_trapecio(s, v, a), False
    v = (a * T - math.sqrt(d)) / 2.0            # raíz menor: trapecio completo
    if v > v_max:
        return rpm_max, duracion_trapecio(s, v_max, a), False
    return v * 60.0 / pasos_rev, T, True


def _segmento(delta_deg: float, rpm: float, T: float, aj, alineacion=False) -> Segmento:
    revs = (-1.0 if aj.invertir else 1.0) * delta_deg / 360.0 * aj.relacion
    pasos = abs(revs) * PASOS_REV
    return Segmento(delta_deg, revs, rpm, T, pasos, rpm * PASOS_REV / 60.0, alineacion, aj.acel)


def plan_alineacion(error_deg: float, aj) -> Segmento:
    """Un solo MOVE lento que lleva el motor a la posición de la simulación."""
    pasos = abs(error_deg) / 360.0 * aj.relacion * PASOS_REV
    v = aj.rpm_alineacion * PASOS_REV / 60.0
    return _segmento(error_deg, aj.rpm_alineacion, duracion_trapecio(pasos, v, aj.acel), aj, True)


def planificar(lt, t_desde: float, pos_motor_deg: float, aj):
    """Tramos de `aj.dt_segmento` s desde t_desde hasta el final. El desfase inicial entre el
    motor y la simulación (pos_motor_deg) se absorbe en el primer tramo.
    Devuelve (segmentos, avisos)."""
    segs, avisos = [], []
    pos = pos_motor_deg
    n = max(1, math.ceil((lt.t_fin - t_desde) / aj.dt_segmento - 1e-9))
    atrasados = 0
    for i in range(n):
        t0 = t_desde + i * aj.dt_segmento
        t1 = min(t0 + aj.dt_segmento, lt.t_fin)
        T = t1 - t0
        objetivo = lt.posicion_en(t1)
        delta = objetivo - pos
        pasos = abs(delta) / 360.0 * aj.relacion * PASOS_REV
        if pasos < 1.0:                                   # < 1 paso: solo esperar
            segs.append(_segmento(delta, 0.0, T, aj)); segs[-1].revs = 0.0
        else:
            rpm, Treal, ok = rpm_para_duracion(pasos, T, aj.rpm_max, aj.acel)
            atrasados += 0 if ok else 1
            segs.append(_segmento(delta, rpm, Treal, aj))
        pos = objetivo
    if atrasados:
        avisos.append(f"{atrasados} tramo(s) no caben en {aj.dt_segmento:g} s con ACEL/rpm_max: "
                      "el motor irá retrasado respecto a la simulación (alarga dt_segmento).")
    return segs, avisos
