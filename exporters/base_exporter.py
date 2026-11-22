# -*- coding: utf-8 -*-
"""
exporters/base_exporter.py

Datos comunes a TODOS los formatos de exportación (XLSX, CSV/TXT, DXF, PDF). Se calculan UNA vez por engranaje
(`recopilar`) y cada exportador solo los escribe: así los cinco formatos salen siempre del mismo cálculo.
Sin Qt. Unidades: mm y rad. Marco del diente: θ = 0 en la raíz del diente (igual que la hoja CAD del Excel).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from utils.design_report import resumen_diseno

PUNTOS_EXPORTACION = 2001      # polilínea de alta densidad (impar: incluye θ = 0 exacto)


@dataclass
class DatosPerfil:
    etiqueta: str              # "" (sistema simple) | "Sol" | "Anular"
    nombre_curva: str          # "Epitrocoide" | "Hipotrocoide" | "Trocoide"
    tab: dict                  # motor.tabular_exportacion(n)
    resumen: dict              # utils.design_report.resumen_diseno()

    @property
    def theta(self) -> np.ndarray:
        return np.asarray(self.tab["Theta"], float)

    @property
    def x(self) -> np.ndarray:
        return np.asarray(self.tab["Offset_X"], float)

    @property
    def y(self) -> np.ndarray:
        return np.asarray(self.tab["Offset_Y"], float)

    @property
    def z(self) -> np.ndarray:
        return np.zeros_like(self.x)

    @property
    def generatriz(self) -> tuple[np.ndarray, np.ndarray]:
        n = self.nombre_curva
        return np.asarray(self.tab[f"{n}_X"], float), np.asarray(self.tab[f"{n}_Y"], float)


def recopilar(etiqueta: str, motor, parametros, n_puntos: int = PUNTOS_EXPORTACION) -> DatosPerfil:
    return DatosPerfil(etiqueta, motor.NOMBRE_CURVA, motor.tabular_exportacion(n_puntos),
                       resumen_diseno(motor, parametros))
