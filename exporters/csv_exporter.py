# -*- coding: utf-8 -*-
"""
exporters/csv_exporter.py

Nube de puntos del perfil del diente [X, Y, Z, Theta] (ModusOperandi.docx). X, Y, Z en mm; Z = 0 (perfil plano);
Theta en rad, con θ = 0 en la raíz del diente.
  CSV: delimitador coma, punto decimal, UTF-8 (lo abre Excel/LibreOffice y cualquier script).
  TXT: delimitador tabulador y cabecera comentada con '#', listo para importar en CAD o en gnuplot/MATLAB.
"""
from __future__ import annotations

import csv
from pathlib import Path

from exporters.base_exporter import DatosPerfil

ENCABEZADO = ("X_mm", "Y_mm", "Z_mm", "Theta_rad")


def _filas(d: DatosPerfil):
    return zip(d.x, d.y, d.z, d.theta)


def exportar_csv(ruta, d: DatosPerfil) -> None:
    with Path(ruta).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(ENCABEZADO)
        for fila in _filas(d):
            w.writerow([f"{v:.9g}" for v in fila])


def exportar_txt(ruta, d: DatosPerfil) -> None:
    with Path(ruta).open("w", newline="", encoding="utf-8") as f:
        f.write("# RPS Design - nube de puntos del perfil del diente"
                f"{' (' + d.etiqueta + ')' if d.etiqueta else ''}\n")
        f.write("# " + "\t".join(ENCABEZADO) + "\n")
        for fila in _filas(d):
            f.write("\t".join(f"{v:.9g}" for v in fila) + "\n")
