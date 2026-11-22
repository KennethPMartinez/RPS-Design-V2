import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")      # el PDF dibuja gráficas: Qt sin ventana

import numpy as np
import openpyxl
import pytest

from config.data_structures import ParametrosCremallera, ParametrosEpitrocoidal, ParametrosPlanetario
from engine.cremallera_engine import CremalleraEngine
from engine.epitrocoidal_engine import EpitrocoidalEngine
from engine.planetario_engine import PlanetarioEngine
from exporters.base_exporter import PUNTOS_EXPORTACION
from exporters.export_manager import exportar

SISTEMAS = [(EpitrocoidalEngine, ParametrosEpitrocoidal()), (CremalleraEngine, ParametrosCremallera())]


@pytest.fixture(scope="module")
def app():
    from PySide6 import QtWidgets
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.mark.parametrize("clase,p", SISTEMAS)
def test_excel_hoja_cad_solo_xyz(clase, p, tmp_path):
    motor = clase(p)
    (ruta,) = exportar(tmp_path / "a.xlsx", [("", motor, p)], "x")
    wb = openpyxl.load_workbook(ruta)
    ws = wb.worksheets[0]
    assert [c.value for c in ws[1]] == ["X (mm)", "Y (mm)", "Z (mm)"] and ws.max_column == 3
    assert ws.max_row == PUNTOS_EXPORTACION + 1
    assert all(ws.cell(row=r, column=3).value == 0 for r in (2, 500, ws.max_row))
    assert wb.sheetnames[-1] == "Resumen" and len(wb.sheetnames) == 6


@pytest.mark.parametrize("clase,p", SISTEMAS)
def test_csv_txt_nube_de_puntos(clase, p, tmp_path):
    motor = clase(p)
    (csv_,) = exportar(tmp_path / "a.csv", [("", motor, p)], "x")
    filas = open(csv_).read().splitlines()
    assert filas[0] == "X_mm,Y_mm,Z_mm,Theta_rad" and len(filas) == PUNTOS_EXPORTACION + 1
    datos = np.loadtxt(csv_, delimiter=",", skiprows=1)
    assert np.allclose(datos[:, 2], 0.0) and datos[0, 3] == pytest.approx(-motor.theta_lim)
    (txt,) = exportar(tmp_path / "a.txt", [("", motor, p)], "x")
    assert np.loadtxt(txt, comments="#").shape == (PUNTOS_EXPORTACION, 4)


@pytest.mark.parametrize("clase,p", SISTEMAS)
def test_dxf_polilinea_de_alta_densidad(clase, p, tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    motor = clase(p)
    (ruta,) = exportar(tmp_path / "a.dxf", [("", motor, p)], "x")
    doc = ezdxf.readfile(ruta)
    pol = {e.dxf.layer: e for e in doc.modelspace()}
    assert len(list(pol["PERFIL_DIENTE"].vertices)) == PUNTOS_EXPORTACION and "GENERATRIZ" in pol


def test_planetario_un_archivo_por_engranaje_y_un_pdf(app, tmp_path):
    e = PlanetarioEngine(ParametrosPlanetario(numero_planetas=3))
    items = [("Sol", e.sol, e.p_sol), ("Anular", e.anular, e.p_anular)]
    salidas = exportar(tmp_path / "pl.xlsx", items, "Planetario")
    assert [os.path.basename(s) for s in salidas] == ["pl_sol.xlsx", "pl_anular.xlsx"]
    (pdf,) = exportar(tmp_path / "pl.pdf", items, "Planetario", e.resumen_html())
    cab = open(pdf, "rb").read(5)
    assert cab == b"%PDF-" and os.path.getsize(pdf) > 20_000
