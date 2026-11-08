import math

import numpy as np
import pytest

from config.data_structures import ParametrosEpitrocoidal, ParametrosHipotrocoidal
from engine import math_utils as mu
from engine.cinematica_engine import SolverCinematico
from engine.epitrocoidal_engine import EpitrocoidalEngine
from engine.hipotrocoidal_engine import HipotrocoidalEngine
from engine.motion_engine import FabricaPresets, LineaTiempo, escalar_perfil


# ---------------------------------------------------------------- §6.2: muestreo de contactos
@pytest.mark.parametrize("clase,param", [(HipotrocoidalEngine, ParametrosHipotrocoidal(numero_dientes=36)),
                                         (EpitrocoidalEngine, ParametrosEpitrocoidal())])
def test_theta_local_coincide_con_busqueda_densa(clase, param):
    motor = clase(param)
    solver = SolverCinematico(motor.contexto)
    th = np.linspace(-motor.theta_lim, motor.theta_lim, 20001)
    ox, oy = motor.curva_offset(th)
    ox, oy = mu.rotar(ox, oy, math.radians(motor.ROTACION_VISTA_SIMULACION_GRADOS))
    n = 0
    for ang in (0.0, 1.0, 3.7, 9.1, 17.3, 41.0, 123.4):
        est = solver.resolver("angular", True, True, ang, 0.0)
        for c in motor.rodillos_en_contacto(est.angulo_relativo_generatriz_rad, modo_pinon_alterno=True,
                                            estado_cinematico=est):
            px, py = mu.rotar(ox, oy, c["indice_flanco"] * motor.contexto.paso_angular_diente)
            cx, cy = c["centro_rodillo"]
            k = int(np.argmin((px - cx) ** 2 + (py - cy) ** 2))
            assert abs(th[k] - c["theta_local"]) < 3e-4
            n += 1
    assert n > 0


# ---------------------------------------------------------------- §6.2: Trocoidal dentro de la cremallera
def _lt(nombre="Arranque y parada suaves"):
    return LineaTiempo.construir(FabricaPresets.crear(nombre))


def test_preset_se_escala_para_caber():
    nuevo, f, off, rec = _lt().ajustada(0.0, 300.0, escalar=True)
    assert f == pytest.approx(0.999 * 300.0 / 1200.0, rel=1e-3) and not rec
    assert nuevo.pos.min() >= -1e-6 and nuevo.pos.max() <= 300.0 + 1e-6


def test_perfil_con_negativos_se_desplaza():
    nuevo, f, off, rec = _lt("Backlash").ajustada(0.0, 100.0)
    assert f == 1.0 and off == pytest.approx(5.0, abs=1e-6) and nuevo.pos.min() >= -1e-6


def test_sin_escalar_se_recorta():
    nuevo, f, off, rec = _lt().ajustada(0.0, 300.0, escalar=False)
    assert rec and nuevo.pos.max() <= 300.0 + 1e-9


def test_si_ya_cabe_no_cambia():
    lt = _lt("Giro de 90°")
    nuevo, f, off, rec = lt.ajustada(0.0, 500.0)
    assert nuevo is lt and (f, off, rec) == (1.0, 0.0, False)


def test_escalar_perfil_equivale_a_escalar_la_tabla():
    for nombre in FabricaPresets.NOMBRES:
        p = FabricaPresets.crear(nombre)
        a, b = LineaTiempo.construir(escalar_perfil(p, 0.5)), LineaTiempo.construir(p)
        assert np.allclose(a.pos, 0.5 * b.pos, atol=1e-6, rtol=1e-6), nombre
