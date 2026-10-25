# -*- coding: utf-8 -*-
"""
utils/design_report.py

Cálculo de la ficha técnica (datos de entrada + geometría derivada + resultados críticos)
y su versión HTML para la ventana 'Resumen de diseño'. Sin Qt: el mismo diccionario
alimenta la hoja 'Parámetros' del Excel y el informe.
"""
from __future__ import annotations

import html
import numpy as np

# Referencia para el diagnóstico de subcorte: radio de la fresa de acabado de 3 mm.
# (Se podrá editar desde Settings_window cuando exista.)
RADIO_FRESA_REF_MM = 1.5


def resumen_diseno(motor, p) -> dict:
    r = motor.generar_perfil()                       # incluye análisis
    th = r.theta
    pos = th > 0
    alpha = np.abs(r.angulo_presion_grados[pos])
    rho_min = float(r.radio_curvatura_minimo)
    entrada = [
        ("Número de dientes (engranaje externo)", p.numero_dientes, ""),
        ("Número de rodillos", p.numero_rodillos, ""),
        ("Diámetro de rodillos", p.diametro_rodillos, "mm"),
        ("Distancia entre centros de rodillos", p.distancia_centro_rodillos, "mm"),
        ("Ángulo de presión mínimo", p.angulo_presion_minimo, "°"),
    ]
    derivados = [
        ("Relación de transmisión i = Z/Zrp", motor.i, ""),
        ("Radio primitivo del piñón de rodillos (prrp)", motor.r, "mm"),
        ("Radio del círculo de centros de rodillos (mrrp)", motor.d, "mm"),
        ("Radio primitivo del engranaje (pretg)", motor.R1, "mm"),
        ("Distancia entre centros piñón-engranaje (cd)", motor.distancia_centros_pinon, "mm"),
        ("Radio de valle", motor.radio_valle, "mm"),
        ("Radio de cresta", motor.radio_cresta, "mm"),
        ("θ límite del flanco", r.theta_lim, "rad"),
    ]
    criticos = [
        ("Radio de curvatura mínimo ρ_min", rho_min, "mm"),
        ("Ángulo de presión máximo (θ>0)", float(alpha.max()), "°"),
        ("Ángulo de presión mínimo (θ>0)", float(alpha.min()), "°"),
    ]
    sin_subcorte = rho_min >= RADIO_FRESA_REF_MM
    veredicto = (f"ρ_min = {rho_min:.4f} mm {'≥' if sin_subcorte else '<'} radio de fresa de referencia "
                 f"({RADIO_FRESA_REF_MM} mm): {'sin subcorte' if sin_subcorte else 'RIESGO DE SUBCORTE'}")
    filas_excel = ([(a, b, c) for a, b, c in entrada] + [("", "", "")] + [(a, b, c) for a, b, c in derivados]
                   + [("", "", "")] + criticos + [("Diagnóstico de subcorte", veredicto, "")])
    return {"entrada": entrada, "derivados": derivados, "criticos": criticos, "veredicto": veredicto,
            "sin_subcorte": sin_subcorte, "filas_excel": filas_excel}


def _tabla(filas) -> str:
    out = ["<table cellspacing='0' cellpadding='4' width='100%' style='border-collapse:collapse'>"]
    for a, b, c in filas:
        v = f"{b:.4f}" if isinstance(b, float) else str(b)
        out.append(f"<tr><td style='border-bottom:1px solid #999'>{html.escape(a)}</td>"
                   f"<td align='right' style='border-bottom:1px solid #999'><b>{v}</b> {html.escape(c)}</td></tr>")
    out.append("</table>")
    return "".join(out)


def informe_html(motor, p) -> str:
    d = resumen_diseno(motor, p)
    color = "#1a7f37" if d["sin_subcorte"] else "#c0392b"
    return (f"<h2>RPS Design — Resumen de diseño</h2><p>Sistema: engranaje epitrocoidal con piñón de rodillos.</p>"
            f"<h3>Ficha técnica · Datos de entrada</h3>{_tabla(d['entrada'])}"
            f"<h3>Geometría derivada</h3>{_tabla(d['derivados'])}"
            f"<h3>Resultados críticos</h3>{_tabla(d['criticos'])}"
            f"<p style='color:{color}'><b>{html.escape(d['veredicto'])}</b></p>")
