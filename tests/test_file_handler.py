import pytest

from config.data_structures import AjustesVisibilidadSimulacion, ParametrosCremallera, ParametrosEpitrocoidal
from utils.file_handler import ArchivoInvalido, abrir_proyecto, guardar_proyecto


def test_ida_y_vuelta_trocoidal(tmp_path):
    ruta = tmp_path / "p.json"
    guardar_proyecto(ruta, "TROCOIDAL", ParametrosCremallera(longitud_cremallera=120.0),
                     {"modo": 1, "valor_manual": 12.5}, None, AjustesVisibilidadSimulacion())
    d = abrir_proyecto(ruta, "TROCOIDAL")
    assert d["parametros"].longitud_cremallera == 120.0
    assert d["simulacion"]["valor_manual"] == 12.5


def test_sistema_distinto_se_rechaza(tmp_path):
    ruta = tmp_path / "p.json"
    guardar_proyecto(ruta, "EPITROCOIDAL", ParametrosEpitrocoidal(), {}, None, AjustesVisibilidadSimulacion())
    with pytest.raises(ArchivoInvalido):
        abrir_proyecto(ruta, "TROCOIDAL")
