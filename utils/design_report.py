# -*- coding: utf-8 -*-
"""
utils/design_report.py

Ficha técnica (datos de entrada + geometría derivada + resultados críticos) y su versión HTML para la
ventana 'Resumen de diseño'. Sin Qt: el mismo diccionario alimenta la hoja 'Resumen' del Excel y el
informe. Sirve a los tres sistemas (Epi/Hipo/Trocoidal): solo lista lo que cada motor realmente tiene.
"""
from __future__ import annotations

import html
import numpy as np

# Referencia para el diagnóstico de subcorte: radio de la fresa de acabado de 3 mm.
RADIO_FRESA_REF_MM = 1.5

_DESCRIPCION = {"Epitrocoide": "engranaje epitrocoidal con piñón de rodillos",
                "Hipotrocoide": "engranaje hipotrocoidal (anular) con piñón de rodillos",
                "Trocoide": "cremallera trocoidal con piñón de rodillos"}


def resumen_diseno(motor, p) -> dict:
    r = motor.generar_perfil()                       # incluye análisis
    pos = r.theta > 0
    alpha = np.abs(r.angulo_presion_grados[pos])
    rho_min = float(r.radio_curvatura_minimo)
    lineal = motor.contexto.tipo_ensamble == "lineal"

    entrada = []
    if hasattr(p, "numero_dientes"):
        tipo = "anular" if motor.contexto.perfil_interior else "externo"
        entrada.append((f"Número de dientes (engranaje {tipo})", p.numero_dientes, ""))
    if hasattr(p, "longitud_cremallera"):
        entrada.append(("Longitud de la cremallera", p.longitud_cremallera, "mm"))
    entrada += [("Número de rodillos", p.numero_rodillos, ""),
                ("Diámetro de rodillos", p.diametro_rodillos, "mm"),
                ("Distancia entre centros de rodillos", p.distancia_centro_rodillos, "mm"),
                ("Ángulo de presión mínimo", p.angulo_presion_minimo, "°")]

    derivados = []
    if getattr(motor, "i", None) is not None:
        derivados.append(("Relación de transmisión i = Z/Zrp", motor.i, ""))
    derivados += [("Radio primitivo del piñón de rodillos (prrp)", motor.rodillo.prrp, "mm"),
                  ("Radio del círculo de centros de rodillos (mrrp)", motor.rodillo.mrrp, "mm")]
    if getattr(motor, "R1", None) is not None:
        derivados.append(("Radio primitivo del engranaje", motor.R1, "mm"))
    if motor.distancia_centros_pinon:
        derivados.append(("Distancia entre centros piñón-engranaje (cd)", motor.distancia_centros_pinon, "mm"))
    for etiqueta, valor in (("Radio de valle", motor.radio_valle), ("Radio de cresta", motor.radio_cresta)):
        if valor is not None:
            derivados.append((etiqueta, valor, "mm"))
    derivados.append(("Paso lineal entre dientes" if lineal else "θ límite del flanco",
                      r.paso if lineal else r.theta_lim, "mm" if lineal else "rad"))

    criticos = [("Radio de curvatura mínimo ρ_min", rho_min, "mm"),
                ("Ángulo de presión máximo (θ>0)", float(alpha.max()), "°"),
                ("Ángulo de presión mínimo (θ>0)", float(alpha.min()), "°")]
    sin_subcorte = rho_min >= RADIO_FRESA_REF_MM
    veredicto = (f"ρ_min = {rho_min:.4f} mm {'≥' if sin_subcorte else '<'} radio de fresa de referencia "
                 f"({RADIO_FRESA_REF_MM} mm): {'sin subcorte' if sin_subcorte else 'RIESGO DE SUBCORTE'}")
    filas_excel = (list(entrada) + [("", "", "")] + list(derivados) + [("", "", "")] + criticos
                   + [("Diagnóstico de subcorte", veredicto, "")])
    return {"entrada": entrada, "derivados": derivados, "criticos": criticos, "veredicto": veredicto,
            "sin_subcorte": sin_subcorte, "filas_excel": filas_excel,
            "descripcion": _DESCRIPCION.get(motor.NOMBRE_CURVA, motor.NOMBRE_CURVA)}


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
    return (f"<h2>RPS Design — Resumen de diseño</h2><p>Sistema: {html.escape(d['descripcion'])}.</p>"
            f"<h3>Ficha técnica · Datos de entrada</h3>{_tabla(d['entrada'])}"
            f"<h3>Geometría derivada</h3>{_tabla(d['derivados'])}"
            f"<h3>Resultados críticos</h3>{_tabla(d['criticos'])}"
            f"<p style='color:{color}'><b>{html.escape(d['veredicto'])}</b></p>")
