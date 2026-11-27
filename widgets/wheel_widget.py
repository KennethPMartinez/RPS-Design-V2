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

    def set_angle(self, grados: float) -> None:
        self.angle = float(grados) % 360.0
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#f6f8fb"))
        lado = min(self.width(), self.height()) - 34
        cx, cy, r = self.width() / 2.0, self.height() / 2.0, (min(self.width(), self.height()) - 34) / 2.0
        p.setPen(QPen(QColor("#283747"), 2)); p.setBrush(QColor("#dce3eb"))
        p.drawEllipse(int(cx - r), int(cy - r), int(lado), int(lado))
        p.save(); p.translate(cx, cy); p.rotate(-self.angle)
        p.setPen(QPen(QColor("#526779"), max(3, int(r * .045)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for i in range(8):
            p.save(); p.rotate(i * 45)
            p.drawLine(0, int(-r * .16), 0, int(-r * .76))
            p.restore()
        p.setPen(QPen(QColor("#d35400"), max(4, int(r * .05)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(0, 0, 0, int(-r * .82))
        p.restore()
        p.setBrush(QColor("#34495e")); p.setPen(QPen(QColor("#ffffff"), 2))
        p.drawEllipse(int(cx - r * .14), int(cy - r * .14), int(r * .28), int(r * .28))
        p.setPen(QColor("#253746")); p.setFont(QFont("Segoe UI", 9))
        p.drawText(8, self.height() - 8, f"Ángulo: {fmt(self.angle, '°')}")
        p.end()
