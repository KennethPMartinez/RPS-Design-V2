# -*- coding: utf-8 -*-
"""dialogs/design_summary_dialog.py — 'Resumen de diseño': informe + ficha técnica, exportable a PDF."""
from __future__ import annotations

from PySide6 import QtGui, QtWidgets

from ui.errores import manejador_seguro
from utils.design_report import informe_html


class DialogoResumenDiseno(QtWidgets.QDialog):
    def __init__(self, motor, parametros, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resumen de diseño")
        self.resize(620, 720)
        self._html = informe_html(motor, parametros)
        lay = QtWidgets.QVBoxLayout(self)
        vista = QtWidgets.QTextBrowser()
        vista.setHtml(self._html)
        lay.addWidget(vista)
        fila = QtWidgets.QHBoxLayout()
        b_pdf = QtWidgets.QPushButton("Exportar PDF…")
        b_pdf.clicked.connect(self._exportar_pdf)
        b_cerrar = QtWidgets.QPushButton("Cerrar")
        b_cerrar.clicked.connect(self.close)
        fila.addStretch(1); fila.addWidget(b_pdf); fila.addWidget(b_cerrar)
        lay.addLayout(fila)

    @manejador_seguro
    def _exportar_pdf(self, *_):
        ruta, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar resumen", "resumen_diseno.pdf", "PDF (*.pdf)")
        if not ruta:
            return
        escritor = QtGui.QPdfWriter(ruta)
        escritor.setPageSize(QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4))
        doc = QtGui.QTextDocument()
        doc.setHtml(self._html)
        doc.print_(escritor)
