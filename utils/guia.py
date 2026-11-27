# -*- coding: utf-8 -*-
"""utils/guia.py — abre la guía técnica (manual de usuario en PDF) con el visor del sistema."""
from __future__ import annotations

from pathlib import Path

RUTA_GUIA = Path(__file__).resolve().parents[1] / "docs" / "Guia_tecnica_RPS_Design_V2.pdf"


def abrir_guia(parent=None) -> bool:
    from PySide6 import QtCore, QtGui, QtWidgets
    if not RUTA_GUIA.exists():
        QtWidgets.QMessageBox.warning(parent, "Guía técnica", f"No se encontró la guía:\n{RUTA_GUIA}")
        return False
    ok = QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(RUTA_GUIA)))
    if not ok:
        QtWidgets.QMessageBox.information(parent, "Guía técnica", f"Abra manualmente el archivo:\n{RUTA_GUIA}")
    return ok
