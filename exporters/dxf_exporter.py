# -*- coding: utf-8 -*-
"""
exporters/dxf_exporter.py

Perfil del diente como POLILÍNEA de alta densidad en DXF (formato R12/AC1009, ASCII, escrito a mano: sin
dependencias; lo abren AutoCAD, Inventor, SolidWorks, LibreCAD...). Unidades: mm (R12 no declara unidades: al
insertar/importar en CAD elige milímetros). Marco del diente: θ = 0 en la raíz, igual que la hoja CAD del Excel.

Capas:  PERFIL_DIENTE (perfil real, offset de la generatriz)  ·  GENERATRIZ (curva de referencia, sin offset).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from exporters.base_exporter import DatosPerfil

CAPAS = (("PERFIL_DIENTE", 7), ("GENERATRIZ", 3))     # (nombre, color ACI)


def _g(codigo, valor) -> str:
    return f"{codigo:>3}\n{valor}\n"


def _polilinea(capa: str, x, y) -> str:
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    partes = ["  0\nPOLYLINE\n" + _g(8, capa) + _g(66, 1) + _g(10, "0.0") + _g(20, "0.0") + _g(30, "0.0")
              + _g(70, 0)]
    for xi, yi in zip(x, y):
        partes.append("  0\nVERTEX\n" + _g(8, capa) + _g(10, f"{xi:.9f}") + _g(20, f"{yi:.9f}") + _g(30, "0.0"))
    partes.append("  0\nSEQEND\n" + _g(8, capa))
    return "".join(partes)


def exportar_dxf(ruta, d: DatosPerfil) -> None:
    gx, gy = d.generatriz
    s = ["  0\nSECTION\n  2\nHEADER\n" + _g(9, "$ACADVER") + _g(1, "AC1009") + "  0\nENDSEC\n",
         "  0\nSECTION\n  2\nTABLES\n",
         "  0\nTABLE\n  2\nLTYPE\n" + _g(70, 1) + "  0\nLTYPE\n" + _g(2, "CONTINUOUS") + _g(70, 0)
         + _g(3, "Solid line") + _g(72, 65) + _g(73, 0) + _g(40, "0.0") + "  0\nENDTAB\n",
         "  0\nTABLE\n  2\nLAYER\n" + _g(70, len(CAPAS))]
    for nombre, color in CAPAS:
        s.append("  0\nLAYER\n" + _g(2, nombre) + _g(70, 0) + _g(62, color) + _g(6, "CONTINUOUS"))
    s.append("  0\nENDTAB\n  0\nENDSEC\n")
    s.append("  0\nSECTION\n  2\nENTITIES\n")
    s.append(_polilinea("GENERATRIZ", gx, gy))
    s.append(_polilinea("PERFIL_DIENTE", d.x, d.y))
    s.append("  0\nENDSEC\n  0\nEOF\n")
    with Path(ruta).open("w", encoding="ascii", newline="\r\n") as f:
        f.write("".join(s))
