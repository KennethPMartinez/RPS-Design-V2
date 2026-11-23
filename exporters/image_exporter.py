# -*- coding: utf-8 -*-
"""
exporters/image_exporter.py

Exportación de gráficas (PyQtGraph) a imagen / vector / datos. Se invoca desde el clic derecho
de cada gráfica ("Exportar imagen…"). Formatos:
  PNG · JPG  -> raster, con ancho configurable (por defecto 1920 px, antialias)
  SVG        -> vectorial (editable en Inkscape / CAD)
  PDF        -> página A4 apaisada con la gráfica centrada
  CSV        -> datos X-Y de las curvas visibles
Se exporta tal como se ve (incluido el tema activo).
"""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from pyqtgraph.exporters import CSVExporter, ImageExporter, SVGExporter

FILTROS = ("Imagen PNG (*.png);;Imagen JPG (*.jpg);;Vectorial SVG (*.svg);;"
           "Documento PDF (*.pdf);;Datos CSV (*.csv)")


def exportar_grafica(plot_widget, ruta: str, ancho: int | None = None, op=None) -> None:
    """Exporta con lo elegido en Ajustes → Exportación (`op`): resolución, calidad JPEG, fondo transparente y
    antialias para PNG/JPEG; el ancho para SVG/PDF. `ancho` explícito (p. ej. en pruebas) prevalece sobre Ajustes."""
    from exporters import settings_adapter as ad
    if op is None:
        from ui.ajustes_runtime import runtime
        op = runtime.estado.exportacion
    item = plot_widget.getPlotItem()
    if getattr(plot_widget, "_inspector", None) is not None:
        plot_widget._inspector._ocultar()      # el cursor de inspección no debe salir en la imagen
    ext = Path(ruta).suffix.lower()
    tam = plot_widget.size()
    if ancho is None:
        ancho = ad.dimensiones_imagen(op, (tam.width(), tam.height()))[0]
    if ext in (".png", ".jpg", ".jpeg"):
        ad.guardar_imagen(plot_widget, ruta, op)
    elif ext == ".svg":
        try:
            SVGExporter(item).export(ruta)
        except Exception:        # SVGExporter de pyqtgraph falla con algunas combinaciones pyqtgraph/Qt
            _svg_qt(item, ruta, ancho)
    elif ext == ".csv":
        CSVExporter(item).export(ruta)
    elif ext == ".pdf":
        exp = ImageExporter(item)
        exp.parameters()["width"] = int(ancho)
        exp.parameters()["antialias"] = bool(op.antialias_export)
        img = exp.export(toBytes=True)
        w = QtGui.QPdfWriter(ruta)
        w.setPageSize(QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4))
        w.setPageOrientation(QtGui.QPageLayout.Orientation.Landscape)
        p = QtGui.QPainter(w)
        area = p.viewport()
        esc = min(area.width() / img.width(), area.height() / img.height())
        p.drawImage(QtCore.QRectF(0, 0, img.width() * esc, img.height() * esc), img)
        p.end()
    else:
        raise ValueError(f"Formato no soportado: '{ext}'")


def _svg_qt(item, ruta: str, ancho: int) -> None:
    """Respaldo: SVG generado por Qt (QSvgGenerator) renderizando la escena del plot."""
    from PySide6.QtSvg import QSvgGenerator
    src = item.sceneBoundingRect()
    w = int(ancho)
    h = max(1, int(w * src.height() / max(src.width(), 1.0)))
    gen = QSvgGenerator()
    gen.setFileName(ruta)
    gen.setSize(QtCore.QSize(w, h))
    gen.setViewBox(QtCore.QRect(0, 0, w, h))
    p = QtGui.QPainter(gen)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    item.scene().render(p, QtCore.QRectF(0, 0, w, h), src)
    p.end()


_POR_FORMATO = {"PNG": ("Imagen PNG (*.png)", ".png"), "JPEG": ("Imagen JPG (*.jpg)", ".jpg"),
                "SVG": ("Vectorial SVG (*.svg)", ".svg"), "PDF": ("Documento PDF (*.pdf)", ".pdf")}


def exportar_con_dialogo(plot_widget, parent, nombre_base: str = "grafica") -> None:
    from ui.ajustes_runtime import runtime
    op = runtime.estado.exportacion
    filtro_defecto, ext_defecto = _POR_FORMATO.get(op.formato_imagen, _POR_FORMATO["PNG"])
    nombre = nombre_base.lower().replace(" ", "_")
    ruta, filtro = QtWidgets.QFileDialog.getSaveFileName(parent, "Exportar gráfica", f"{nombre}{ext_defecto}", FILTROS,
                                                         filtro_defecto, runtime.opciones_guardado())
    if not ruta:
        return
    if not Path(ruta).suffix:
        ruta += {"PNG": ".png", "JPG": ".jpg", "SVG": ".svg", "PDF": ".pdf", "CSV": ".csv"}.get(
            next((k for k in ("PNG", "JPG", "SVG", "PDF", "CSV") if k in filtro), "PNG"), ".png")
    try:
        exportar_grafica(plot_widget, ruta, op=op)
    except Exception as e:
        QtWidgets.QMessageBox.warning(parent, "Exportar gráfica", f"No se pudo exportar:\n{e}")
        return
    if hasattr(parent, "statusBar"):
        parent.statusBar().showMessage(f"Gráfica exportada: {ruta}", 5000)
