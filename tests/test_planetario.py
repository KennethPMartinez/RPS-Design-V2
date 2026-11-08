import math

import numpy as np
import pytest

from config.data_structures import Componente as C
from config.data_structures import ParametrosPlanetario
from engine.planetario_engine import PlanetarioEngine, coeficientes_giro, planetas_validos

COMBOS = ((C.SOL, C.ANULAR), (C.SOL, C.BRAZO), (C.BRAZO, C.ANULAR), (C.ANULAR, C.BRAZO))


def test_willis_las_cuatro_combinaciones():
    Zs, Za = 12, 36
    for ent, blo in COMBOS:
        ks, kc, ka = coeficientes_giro(Zs, Za, ent, blo)
        assert Zs * ks + Za * ka == pytest.approx((Zs + Za) * kc)
        k = {C.SOL: ks, C.BRAZO: kc, C.ANULAR: ka}
        assert k[ent] == 1.0 and k[blo] == 0.0


def test_relaciones_conocidas():
    assert coeficientes_giro(12, 36, C.SOL, C.ANULAR)[1] == pytest.approx(0.25)      # brazo = sol/4
    assert coeficientes_giro(12, 36, C.SOL, C.BRAZO)[2] == pytest.approx(-1 / 3)     # anular = -sol·Zs/Za


def test_entrada_igual_a_bloqueado():
    with pytest.raises(ValueError):
        coeficientes_giro(12, 36, C.SOL, C.SOL)


def test_planetas_validos_caso_del_pdf():
    assert planetas_validos(12, 12, 3.0, 8.5, 17.0) == [2, 3, 4]


@pytest.mark.parametrize("ent,blo", COMBOS)
def test_cada_planeta_engrana_con_sol_y_anular(ent, blo):
    eng = PlanetarioEngine(ParametrosPlanetario(componente_entrada=ent, componente_bloqueado=blo,
                                                numero_planetas=3))
    assert eng.montaje_valido
    for th in np.radians([0.0, 7.0, 33.3, 90.0, 151.0]):
        cs, ca = eng.contactos(eng.estado(th))
        assert {c["planeta"] for c in cs} == {0, 1, 2}
        assert {c["planeta"] for c in ca} == {0, 1, 2}


def test_rodillo_activo_coincide_con_su_posicion_en_el_mundo():
    """Valida etiquetas (incl. desfase del anular) y transformaciones al marco del mundo."""
    eng = PlanetarioEngine(ParametrosPlanetario(numero_planetas=4))
    for th in np.radians([0.0, 11.0, 47.0, 123.0]):
        est = eng.estado(th)
        rx, ry = eng.centros_rodillos_mundo(est)
        cs, ca = eng.contactos(est)
        for c in cs + ca:
            cx, cy = c["centro_rodillo_mundo"]
            assert math.hypot(rx[c["planeta"], c["indice"]] - cx, ry[c["planeta"], c["indice"]] - cy) < 0.05
