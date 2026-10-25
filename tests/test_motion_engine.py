import numpy as np
from engine.motion_engine import FabricaPresets, LineaTiempo, PerfilMovimiento


def test_presets_sin_errores():
    for n in FabricaPresets.NOMBRES:
        lt = LineaTiempo.construir(FabricaPresets.crear(n))
        assert not lt.errores and np.all(np.isfinite(lt.pos))


def test_arranque_suave_recorre_1200_grados():
    lt = LineaTiempo.construir(FabricaPresets.crear("Arranque y parada suaves"))
    assert abs(lt.pos[-1] - 1200.0) < 1e-6


def test_json_ida_y_vuelta():
    p = FabricaPresets.crear("Indexer")
    assert PerfilMovimiento.from_dict(p.to_dict()).to_dict() == p.to_dict()
