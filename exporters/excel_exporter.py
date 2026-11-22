# -*- coding: utf-8 -*-
"""
exporters/excel_exporter.py

Exportar -> libro XLSX (ModusOperandi.docx). Hojas:
  1. 'Perfil diente (CAD)'  SOLO X, Y, Z en mm (A, B, C) de θ = -θ_lim a +θ_lim, con θ = 0 en la raíz del diente
     y Z = 0 (perfil plano): se copia tal cual a CAD (p. ej. Inventor: Spline desde hoja de cálculo).
  2. 'Perfil'               θ, X, Y del perfil y de la curva generatriz.
  3. 'Ángulo de presión' · 4. 'Radio de curvatura' · 5. 'Camino de contacto'  (una por pestaña de propiedades).
  6. 'Resumen'              parámetros de entrada, geometría derivada y resultados críticos.
"""
from __future__ import annotations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from exporters.base_exporter import PUNTOS_EXPORTACION, DatosPerfil, recopilar

_ENC = PatternFill("solid", fgColor="1F3A5F")


def _encabezado(ws) -> None:
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = _ENC
        c.alignment = Alignment(horizontal="center")


def _hoja(wb, titulo, columnas: dict, primera=False):
    ws = wb.active if primera else wb.create_sheet()
    ws.title = titulo
    ws.append(list(columnas.keys()))
    _encabezado(ws)
    for fila in zip(*columnas.values()):
        ws.append([float(v) for v in fila])
    for i in range(1, len(columnas) + 1):
        ws.column_dimensions[get_column_letter(i)].width = 20
    ws.freeze_panes = "A2"
    return ws


def exportar_excel_datos(ruta, d: DatosPerfil) -> None:
    t, n = d.tab, d.nombre_curva
    wb = Workbook()
    _hoja(wb, "Perfil diente (CAD)", {"X (mm)": d.x, "Y (mm)": d.y, "Z (mm)": d.z}, primera=True)
    _hoja(wb, "Perfil", {"Theta (rad)": d.theta, "X (mm)": d.x, "Y (mm)": d.y,
                         f"{n} X (mm)": t[f"{n}_X"], f"{n} Y (mm)": t[f"{n}_Y"]})
    _hoja(wb, "Ángulo de presión", {"Theta (rad)": d.theta, "Ángulo de presión (°)": t["Angulo_Presion_deg"]})
    _hoja(wb, "Radio de curvatura", {"Theta (rad)": d.theta, "Radio de curvatura (mm)": t["Radio_Curvatura"]})
    _hoja(wb, "Camino de contacto", {"Theta (rad)": d.theta, "X (mm)": t["Camino_Contacto_X"],
                                     "Y (mm)": t["Camino_Contacto_Y"]})
    ws = wb.create_sheet("Resumen")
    ws.append(["Parámetro", "Valor", "Unidad"])
    _encabezado(ws)
    for etiqueta, valor, unidad in d.resumen["filas_excel"]:
        ws.append([etiqueta, valor, unidad])
    ws.column_dimensions["A"].width = 46
    ws.column_dimensions["B"].width = 22
    wb.save(ruta)


def exportar_excel(ruta, motor, parametros, n_puntos: int = PUNTOS_EXPORTACION) -> None:
    """Compatibilidad con la firma anterior."""
    exportar_excel_datos(ruta, recopilar("", motor, parametros, n_puntos))
