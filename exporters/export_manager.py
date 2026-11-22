# -*- coding: utf-8 -*-
"""
exporters/export_manager.py

Punto único de "Archivo -> Exportar": el filtro del cuadro de diálogo (o la extensión escrita) decide el formato.
  .xlsx  Libro (hoja 1 = X, Y, Z para CAD)   .csv / .txt  Nube de puntos [X, Y, Z, Theta]
  .dxf   Polilínea del perfil                 .pdf         Informe de ingeniería
Un sistema con varios engranajes (planetario: sol y anular) genera un archivo por engranaje (sufijo _sol / _anular)
salvo el PDF, que es un solo documento.
`items` = [(etiqueta, motor, parametros)].
"""
from __future__ import annotations

import re
from pathlib import Path

from exporters.base_exporter import PUNTOS_EXPORTACION, recopilar

FILTROS = ("Libro de Excel (*.xlsx);;Nube de puntos CSV (*.csv);;Nube de puntos TXT (*.txt);;"
           "Perfil DXF (*.dxf);;Informe PDF (*.pdf)")
EXTENSIONES = (".xlsx", ".csv", ".txt", ".dxf", ".pdf")


def _escritor(ext: str):
    if ext == ".xlsx":
        from exporters.excel_exporter import exportar_excel_datos as f
    elif ext == ".csv":
        from exporters.csv_exporter import exportar_csv as f
    elif ext == ".txt":
        from exporters.csv_exporter import exportar_txt as f
    elif ext == ".dxf":
        from exporters.dxf_exporter import exportar_dxf as f
    else:
        raise ValueError(f"Formato no soportado: '{ext}'")
    return f


def _tolerancias() -> dict:
    from config.app_settings import ajustes
    return {"lineal_mm": ajustes.desviacion.desviacion_lineal_mm,
            "angular_grados": ajustes.desviacion.desviacion_angular_grados}


def exportar(ruta, items, sistema: str, html_extra: str = "", n_puntos: int = PUNTOS_EXPORTACION) -> list[str]:
    ruta = Path(ruta)
    ext = ruta.suffix.lower()
    if ext not in EXTENSIONES:
        raise ValueError(f"Formato no soportado: '{ext}'")
    datos = [recopilar(et, motor, p, n_puntos) for et, motor, p in items]
    if ext == ".pdf":
        from exporters.pdf_exporter import exportar_pdf
        exportar_pdf(ruta, datos, sistema, html_extra, _tolerancias())
        return [str(ruta)]
    escribir, salidas = _escritor(ext), []
    for d in datos:
        destino = ruta if len(datos) == 1 else ruta.with_name(f"{ruta.stem}_{d.etiqueta.lower()}{ext}")
        escribir(destino, d)
        salidas.append(str(destino))
    return salidas


def exportar_con_dialogo(ventana, items, sistema: str, archivo_defecto: str, html_extra: str = "") -> None:
    from PySide6 import QtCore, QtWidgets
    ruta, filtro = QtWidgets.QFileDialog.getSaveFileName(ventana, "Exportar", archivo_defecto, FILTROS)
    if not ruta:
        return
    if not Path(ruta).suffix:                                # sin extensión: la del filtro elegido
        m = re.search(r"\(\*(\.\w+)\)", filtro)
        ruta += m.group(1) if m else ".xlsx"
    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
    try:
        salidas = exportar(ruta, items, sistema, html_extra)
    except Exception as e:
        QtWidgets.QApplication.restoreOverrideCursor()
        QtWidgets.QMessageBox.warning(ventana, "Exportar", f"No se pudo exportar:\n{e}")
        return
    QtWidgets.QApplication.restoreOverrideCursor()
    ventana.statusBar().showMessage("Exportado: " + " · ".join(salidas), 8000)
