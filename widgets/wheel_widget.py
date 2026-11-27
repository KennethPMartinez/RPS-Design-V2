# -*- coding: utf-8 -*-
"""widgets/wheel_widget.py — rueda que gira según el ángulo del perfil de movimiento (vista previa del editor)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from utils.formato_numerico import fmt


class WheelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.setMinimumSize(200, 200)
        self.colores = {"fondo": "#f6f8fb", "aro": "#283747", "disco": "#dce3eb", "rayos": "#526779",
                        "aguja": "#d35400", "cubo": "#34495e", "texto": "#253746"}

    def set_colores(self, **c) -> None:
        """Colores del tema (los pasa el editor de regímenes al aplicar el tema)."""
        self.colores.update({k: v for k, v in c.items() if v})
        self.update()

    def set_angle(self, grados: float) -> None:
        self.angle = float(grados) % 360.0
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        C = {k: QColor(*v) if isinstance(v, tuple) else QColor(v) for k, v in self.colores.items()}
        p.fillRect(self.rect(), C["fondo"])
        lado = min(self.width(), self.height()) - 34
        cx, cy, r = self.width() / 2.0, self.height() / 2.0, (min(self.width(), self.height()) - 34) / 2.0
        p.setPen(QPen(C["aro"], 2)); p.setBrush(C["disco"])
        p.drawEllipse(int(cx - r), int(cy - r), int(lado), int(lado))
        p.save(); p.translate(cx, cy); p.rotate(-self.angle)
        p.setPen(QPen(C["rayos"], max(3, int(r * .045)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for i in range(8):
            p.save(); p.rotate(i * 45)
            p.drawLine(0, int(-r * .16), 0, int(-r * .76))
            p.restore()
        p.setPen(QPen(C["aguja"], max(4, int(r * .05)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(0, 0, 0, int(-r * .82))
        p.restore()
        p.setBrush(C["cubo"]); p.setPen(QPen(C["fondo"], 2))
        p.drawEllipse(int(cx - r * .14), int(cy - r * .14), int(r * .28), int(r * .28))
        p.setPen(C["texto"]); p.setFont(QFont("Segoe UI", 9))
        p.drawText(8, self.height() - 8, f"Ángulo: {fmt(self.angle, '°')}")
        p.end()
