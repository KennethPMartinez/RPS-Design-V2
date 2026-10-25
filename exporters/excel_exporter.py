# -*- coding: utf-8 -*-
"""
exporters/excel_exporter.py

Exportar -> libro XLSX (ModusOperandi.docx): una hoja por cada propiedad que muestran las
ventanas de propiedades (Perfil, Ángulo de presión, Radio de curvatura, Camino de contacto)
+ una hoja 'Parámetros' con los datos de entrada y resultados críticos.
"""
from __future__ import annotations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from utils.design_report import resumen_diseno

_ENC = PatternFill("solid", fgColor="1F3A5F")


def _hoja(wb, titulo, columnas: dict, primera=False):
    ws = wb.active if primera else wb.create_sheet()
    ws.title = titulo
    ws.append(list(columnas.keys()))
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = _ENC
        c.alignment = Alignment(horizontal="center")
    for fila in zip(*columnas.values()):
        ws.append([float(v) for v in fila])
    for i in range(1, len(columnas) + 1):
        ws.column_dimensions[get_column_letter(i)].width = 20
    ws.freeze_panes = "A2"
    return ws


def exportar_excel(ruta, motor, parametros, n_puntos: int = 1001) -> None:
    tab = motor.tabular_exportacion(n_puntos)   # xp según modo de hardware (backend_selector)
    nombre = motor.NOMBRE_CURVA
    wb = Workbook()
    # Hoja 1: puntos del perfil del diente listos para CAD (p. ej. Inventor: Spline desde hoja de
    # cálculo): columnas A,B,C = X, Y, Z en mm, de θ=-θ_lim a +θ_lim, con θ=0 en la raíz del diente.
    # Z = 0 (perfil plano); θ y la curva generatriz van DESPUÉS (columnas D-F) para no estorbar.
    th = tab["Theta"]
    _hoja(wb, "Perfil diente (CAD)", {"X (mm)": tab["Offset_X"], "Y (mm)": tab["Offset_Y"], "Z (mm)": 0.0 * th,
                                       "Theta (rad)": th, f"{nombre} X (mm)": tab[f"{nombre}_X"],
                                       f"{nombre} Y (mm)": tab[f"{nombre}_Y"]}, primera=True)
    _hoja(wb, "Ángulo de presión", {"Theta (rad)": tab["Theta"], "Ángulo de presión (°)": tab["Angulo_Presion_deg"]})
    _hoja(wb, "Radio de curvatura", {"Theta (rad)": tab["Theta"], "Radio de curvatura (mm)": tab["Radio_Curvatura"]})
    _hoja(wb, "Camino de contacto", {"Theta (rad)": tab["Theta"], "X (mm)": tab["Camino_Contacto_X"],
                                     "Y (mm)": tab["Camino_Contacto_Y"]})
    ws = wb.create_sheet("Resumen")        # al final
    ws.append(["Parámetro", "Valor", "Unidad"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = _ENC
    for etiqueta, valor, unidad in resumen_diseno(motor, parametros)["filas_excel"]:
        ws.append([etiqueta, valor, unidad])
    ws.column_dimensions["A"].width = 42; ws.column_dimensions["B"].width = 18
    wb.save(ruta)
