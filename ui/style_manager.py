# -*- coding: utf-8 -*-
"""ui/style_manager.py — tema claro/oscuro (Fusion + paleta) y color de fondo de pyqtgraph."""
from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


def _paleta(oscuro: bool) -> QtGui.QPalette:
    c, P = QtGui.QColor, QtGui.QPalette
    p = P()
    if oscuro:
        base = dict(Window=c(45, 45, 48), WindowText=c(220, 220, 220), Base=c(30, 30, 33), AlternateBase=c(45, 45, 48),
                    Text=c(220, 220, 220), Button=c(55, 55, 58), ButtonText=c(220, 220, 220), Highlight=c(31, 111, 235),
                    HighlightedText=c(255, 255, 255), ToolTipBase=c(60, 60, 60), ToolTipText=c(230, 230, 230),
                    PlaceholderText=c(130, 130, 130), Light=c(80, 80, 84), Mid=c(50, 50, 53), Dark=c(30, 30, 32))
        dis = c(120, 120, 120)
    else:
        base = dict(Window=c(240, 240, 240), WindowText=c(20, 20, 20), Base=c(255, 255, 255), AlternateBase=c(233, 233, 233),
                    Text=c(20, 20, 20), Button=c(225, 225, 225), ButtonText=c(20, 20, 20), Highlight=c(0, 120, 215),
                    HighlightedText=c(255, 255, 255), ToolTipBase=c(255, 255, 220), ToolTipText=c(20, 20, 20),
                    PlaceholderText=c(130, 130, 130), Light=c(255, 255, 255), Mid=c(190, 190, 190), Dark=c(150, 150, 150))
        dis = c(140, 140, 140)
    for nombre, color in base.items():
        p.setColor(getattr(P.ColorRole, nombre), color)
    for rol in (P.ColorRole.Text, P.ColorRole.ButtonText, P.ColorRole.WindowText):
        p.setColor(P.ColorGroup.Disabled, rol, dis)
    return p


def aplicar_tema(app: QtWidgets.QApplication, oscuro: bool) -> None:
    """Fusion + paleta EXPLÍCITA (clara = blanco / gris claro). Antes el modo claro usaba la
    paleta 'estándar', que en Windows con tema oscuro del sistema seguía siendo oscura."""
    app.setStyle("Fusion")
    try:   # Qt >= 6.8: fija el esquema para que el sistema no pise la paleta
        app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Dark if oscuro else QtCore.Qt.ColorScheme.Light)
    except Exception:
        pass
    app.setPalette(_paleta(oscuro))
    app.setStyleSheet("")
    from widgets.pg_helpers import retemar_plots
    retemar_plots(oscuro)       # fondo/ejes de TODAS las gráficas abiertas + las que se creen después
