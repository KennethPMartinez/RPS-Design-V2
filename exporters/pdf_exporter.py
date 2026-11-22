# -*- coding: utf-8 -*-
"""
exporters/pdf_exporter.py

Informe de ingeniería en PDF (ModusOperandi.docx): parámetros de entrada (incluidas las tolerancias lineal y
angular de representación), contrastados con los resultados críticos (radio de curvatura mínimo -> diagnóstico de
subcorte; ángulos de presión máximo y mínimo) y las gráficas de las 4 pestañas analíticas: perfil del diente,
ángulo de presión, radio de curvatura y camino de contacto. Un engranaje por sección (el planetario aporta Sol y
Anular más su resumen cinemático en `html_extra`). Solo Qt (QTextDocument + QPdfWriter): sin dependencias nuevas.
"""
from __future__ import annotations

import html
from datetime import datetime

from PySide6 import QtCore, QtGui

from exporters.base_exporter import DatosPerfil
from exporters.plot_figures import figura
from utils.design_report import RADIO_FRESA_REF_MM, _tabla

AZUL, ROJO, VERDE, MORADO, GRIS = (31, 111, 235), (209, 36, 47), (26, 127, 55), (130, 80, 223), (136, 136, 136)
ANCHO_IMG_PX = 600


def _figuras(d: DatosPerfil) -> list[tuple[str, object]]:
    t, r = d.tab, d.resumen
    gx, gy = d.generatriz
    rho_min = next((v for e, v, _ in r["criticos"] if e.startswith("Radio de curvatura")), None)
    y_rho = None
    if rho_min:
        y_rho = (min(0.0, 0.9 * rho_min), max(6.0 * rho_min, rho_min + 1.0))      # recorta los picos
    return [
        ("Perfil del diente", figura([(gx, gy, GRIS, "Curva generatriz", "dot"), (d.x, d.y, AZUL, "Perfil (offset)", "solid")],
                                     "X (mm)", "Y (mm)", "Perfil del diente", aspecto=True)),
        ("Ángulo de presión", figura([(d.theta, t["Angulo_Presion_deg"], ROJO, "α", "solid")],
                                    "θ (rad)", "Ángulo de presión (°)", "Ángulo de presión")),
        ("Radio de curvatura", figura([(d.theta, t["Radio_Curvatura"], VERDE, "ρ", "solid")],
                                     "θ (rad)", "Radio de curvatura (mm)", "Radio de curvatura", yrange=y_rho,
                                     lineas_h=[(RADIO_FRESA_REF_MM, f"fresa ref. {RADIO_FRESA_REF_MM} mm", (200, 90, 0))])),
        ("Camino de contacto", figura([(t["Camino_Contacto_X"], t["Camino_Contacto_Y"], MORADO, "Camino de contacto", "solid")],
                                      "X (mm)", "Y (mm)", "Camino de contacto", aspecto=True)),
    ]


def _seccion(d: DatosPerfil, doc: QtGui.QTextDocument, indice: int, tolerancias: dict, n_puntos: int,
             hay_portada: bool = False) -> str:
    r = d.resumen
    titulo = f"Engranaje {d.etiqueta.lower()}" if d.etiqueta else "Diseño"
    color = "#1a7f37" if r["sin_subcorte"] else "#c0392b"
    tol = [("Desviación lineal de representación", tolerancias["lineal_mm"], "mm"),
           ("Desviación angular de representación", tolerancias["angular_grados"], "°"),
           ("Puntos del perfil exportado", n_puntos, "")]
    salto = " style='page-break-before:always'" if indice > 0 else ""
    h = [f"<h2{salto}>{html.escape(titulo)} — {html.escape(r['descripcion'])}</h2>",
         "<h3>1. Parámetros de entrada</h3>", _tabla(r["entrada"]),
         "<h3>2. Tolerancias de representación</h3>", _tabla(tol),
         "<h3>3. Geometría derivada</h3>", _tabla(r["derivados"]),
         "<h3>4. Resultados críticos</h3>", _tabla(r["criticos"]),
         f"<p style='color:{color}'><b>{html.escape(r['veredicto'])}</b></p>",
         "<h3>5. Gráficas</h3>"]
    for k, (nombre, img) in enumerate(_figuras(d)):
        clave = f"fig_{indice}_{k}"
        doc.addResource(QtGui.QTextDocument.ResourceType.ImageResource, QtCore.QUrl(clave), img)
        alto = int(ANCHO_IMG_PX * img.height() / img.width())
        h.append(f"<p align='center'><img src='{clave}' width='{ANCHO_IMG_PX}' height='{alto}'/><br/>"
                 f"<i>Figura {indice + 1}.{k + 1} — {nombre}</i></p>")
    return "".join(h)


def exportar_pdf(ruta, datos: list[DatosPerfil], sistema: str, html_extra: str, tolerancias: dict) -> None:
    doc = QtGui.QTextDocument()
    doc.setDefaultFont(QtGui.QFont("Arial", 10))
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    cuerpo = [f"<h1>RPS Design — Informe de ingeniería</h1><p><b>Sistema:</b> {html.escape(sistema)}<br/>"
              f"<b>Fecha:</b> {ahora}</p>", html_extra]
    for i, d in enumerate(datos):
        cuerpo.append(_seccion(d, doc, i, tolerancias, len(d.theta), bool(html_extra.strip())))
    doc.setHtml("".join(cuerpo))
    w = QtGui.QPdfWriter(str(ruta))
    w.setPageSize(QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4))
    w.setPageMargins(QtCore.QMarginsF(15, 15, 15, 20), QtGui.QPageLayout.Unit.Millimeter)
    w.setTitle(f"RPS Design — {sistema}")
    w.setCreator("RPS Design V2")
    _imprimir(doc, w)


def _imprimir(doc: QtGui.QTextDocument, w: QtGui.QPdfWriter) -> None:
    """Pagina a mano (QTextDocument.print_ con QPdfWriter a 1200 dpi deja el contenido en media página):
    el documento se maqueta en unidades de 96 dpi y se escala a la resolución del PDF."""
    area = w.pageLayout().paintRectPixels(w.resolution())
    escala = w.resolution() / 96.0
    ancho, alto = area.width() / escala, area.height() / escala
    doc.setPageSize(QtCore.QSizeF(ancho, alto))
    n = doc.pageCount()
    p = QtGui.QPainter(w)
    pie = QtGui.QFont("Arial", 8)
    for i in range(n):
        if i:
            w.newPage()
        p.save()
        p.scale(escala, escala)
        p.translate(0, -i * alto)
        doc.drawContents(p, QtCore.QRectF(0, i * alto, ancho, alto))
        p.restore()
        p.setFont(pie)
        mm = w.resolution() / 25.4
        p.drawText(QtCore.QRectF(0, area.height() + 4 * mm, area.width(), 6 * mm),
                   QtCore.Qt.AlignmentFlag.AlignRight, f"RPS Design · Página {i + 1} de {n}")
    p.end()
