import numpy as np
from engine.motion_engine import FabricaPresets, LineaTiempo
from banco_legacy.motor_plan import (AjustesMotor, PASOS_REV, duracion_trapecio, planificar, posicion_trapecio, rpm_para_duracion)


def test_rpm_reproduce_la_duracion():
    s, T = 2844.0, 2.0
    rpm, Treal, ok = rpm_para_duracion(s, T, 600)
    assert ok and abs(Treal - T) < 1e-9
    assert abs(duracion_trapecio(s, rpm * PASOS_REV / 60) - T) < 1e-6


def test_trapecio_llega_a_s():
    s, v = 3000.0, 1500.0
    assert abs(posicion_trapecio(duracion_trapecio(s, v), s, v) - s) < 1e-6


def test_plan_suma_el_recorrido_del_perfil():
    lt = LineaTiempo.construir(FabricaPresets.crear("Arranque y parada suaves"))
    segs, _ = planificar(lt, 0.0, 0.0, AjustesMotor())
    assert abs(sum(s.delta_sim_deg for s in segs) - lt.posicion_en(lt.t_fin)) < 1e-6
    assert abs(sum(s.revs for s in segs) - 1200 / 360) < 1e-6


def test_aviso_si_el_tramo_no_cabe():
    lt = LineaTiempo.construir(FabricaPresets.crear("Arranque y parada suaves"))
    _, avisos = planificar(lt, 0.0, 0.0, AjustesMotor(dt_segmento=0.2))
    assert avisos
