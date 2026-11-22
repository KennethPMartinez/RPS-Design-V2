"""Selector de color estilo aplicación de arte para RPS Design V2.

Requiere PySide6. No modifica el archivo .ui ni aplica temas globales:
solo devuelve el QColor elegido y actualiza el árbol mediante ConectorColores.

Uso independiente: python selector_color_rps.py
Integración: ver integrar_selector_rps.md.
"""
from __future__ import annotations

import re

from PySide6 import QtCore, QtGui, QtWidgets


class AreaSaturacionBrillo(QtWidgets.QWidget):
    """Plano HSV (horizontal=saturación, vertical=brillo)."""
    cambiado = QtCore.Signal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._h, self._s, self._v = 43.0, 1.0, 1.0
        self.setMinimumSize(300, 225)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

    def ajustar(self, tono: float, saturacion: float, brillo: float) -> None:
        self._h = max(0., min(359., tono))
        self._s = max(0., min(1., saturacion))
        self._v = max(0., min(1., brillo))
        self.update()

    def _area(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.rect().adjusted(10, 10, -10, -10))

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        r = self._area()
        p.fillRect(r, QtGui.QColor.fromHsv(int(self._h), 255, 255))

        # Blanco a la izquierda; tono puro a la derecha.
        blanco = QtGui.QLinearGradient(r.left(), r.top(), r.right(), r.top())
        blanco.setColorAt(0, QtGui.QColor(255, 255, 255, 255))
        blanco.setColorAt(1, QtGui.QColor(255, 255, 255, 0))
        p.fillRect(r, QtGui.QBrush(blanco))

        # Brillo máximo arriba; negro abajo.
        sombra = QtGui.QLinearGradient(r.left(), r.top(), r.left(), r.bottom())
        sombra.setColorAt(0, QtGui.QColor(0, 0, 0, 0))
        sombra.setColorAt(1, QtGui.QColor(0, 0, 0, 255))
        p.fillRect(r, QtGui.QBrush(sombra))
        p.setPen(QtGui.QPen(self.palette().color(QtGui.QPalette.ColorRole.Mid), 1))
        p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        p.drawRect(r)

        x = r.left() + self._s * r.width()
        y = r.top() + (1.0 - self._v) * r.height()
        p.setPen(QtGui.QPen(QtGui.QColor("#101010"), 3))
        p.drawEllipse(QtCore.QPointF(x, y), 7, 7)
        p.setPen(QtGui.QPen(QtGui.QColor("white"), 2))
        p.drawEllipse(QtCore.QPointF(x, y), 7, 7)

    def _seleccionar(self, pos):
        r = self._area()
        self._s = max(0., min(1., (pos.x() - r.left()) / max(1., r.width())))
        self._v = max(0., min(1., 1. - (pos.y() - r.top()) / max(1., r.height())))
        self.update()
        self.cambiado.emit(self._s, self._v)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._seleccionar(event.position())

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self._seleccionar(event.position())


class BarraTono(QtWidgets.QWidget):
    """Barra horizontal de matices HSV 0–359°."""
    cambiado = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tono = 43
        self.setMinimumHeight(38)
        self.setMaximumHeight(46)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

    def ajustar(self, tono: int) -> None:
        self._tono = max(0, min(359, int(tono)))
        self.update()

    def _area(self):
        return QtCore.QRectF(self.rect().adjusted(10, 11, -10, -11))

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        r = self._area()
        grad = QtGui.QLinearGradient(r.left(), r.top(), r.right(), r.top())
        for i in range(7):
            grad.setColorAt(i / 6, QtGui.QColor.fromHsv(int((i % 6) * 60), 255, 255))
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QBrush(grad))
        p.drawRoundedRect(r, 4, 4)
        x = r.left() + (self._tono / 359.) * r.width()
        p.setBrush(QtGui.QColor.fromHsv(self._tono, 255, 255))
        p.setPen(QtGui.QPen(QtGui.QColor("white"), 2.5))
        p.drawEllipse(QtCore.QPointF(x, r.center().y()), 9, 9)

    def _seleccionar(self, pos):
        r = self._area()
        self._tono = round(359 * max(0., min(1., (pos.x() - r.left()) / max(1., r.width()))))
        self.update()
        self.cambiado.emit(self._tono)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._seleccionar(event.position())

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self._seleccionar(event.position())


class MuestraColor(QtWidgets.QWidget):
    """Previsualización con tablero de transparencia."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QtGui.QColor("#FCBA03")
        self.setMinimumWidth(140)
        self.setMinimumHeight(225)

    def ajustar(self, color: QtGui.QColor) -> None:
        self._color = QtGui.QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        r = self.rect().adjusted(1, 1, -1, -1)
        paso = 12
        for y in range(r.top(), r.bottom() + 1, paso):
            for x in range(r.left(), r.right() + 1, paso):
                gris = "#bcbcbc" if ((x-r.left())//paso + (y-r.top())//paso) % 2 else "#f4f4f4"
                p.fillRect(QtCore.QRect(x, y, min(paso, r.right()-x+1),
                                        min(paso, r.bottom()-y+1)), QtGui.QColor(gris))
        p.fillRect(r, self._color)
        p.setPen(QtGui.QPen(self.palette().color(QtGui.QPalette.ColorRole.Mid)))
        p.drawRect(r)


class SelectorColorRPS(QtWidgets.QDialog):
    """Diálogo de color con vista de arte y entrada multiformato sincronizada.

    selectedColor() devuelve QColor; getColor() devuelve QColor inválido al cancelar.
    colorCambiado(QColor) permite una previsualización en vivo, sin guardar cambios.
    """
    colorCambiado = QtCore.Signal(QtGui.QColor)

    def __init__(self, color="#FCBA03", parent=None, titulo="Selector de color"):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumSize(760, 630)
        self._color = QtGui.QColor(color)
        if not self._color.isValid():
            self._color = QtGui.QColor("#FCBA03")
        self._tono = 43
        self._campos = {}
        self._crear_interfaz()
        self._actualizar(self._color)

    def _crear_interfaz(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        titulo = QtWidgets.QLabel("Seleccionar color")
        f = titulo.font(); f.setPointSize(max(12, f.pointSize()+3)); f.setBold(True)
        titulo.setFont(f)
        layout.addWidget(titulo)

        fila = QtWidgets.QHBoxLayout()
        self.muestra = MuestraColor()
        fila.addWidget(self.muestra, 0)
        self.area = AreaSaturacionBrillo()
        fila.addWidget(self.area, 1)
        layout.addLayout(fila, 1)

        self.tono = BarraTono()
        layout.addWidget(self.tono)

        hex_fila = QtWidgets.QHBoxLayout()
        hex_fila.addWidget(QtWidgets.QLabel("HEX"))
        self.hex = QtWidgets.QLineEdit()
        self.hex.setPlaceholderText("#RRGGBB o #RRGGBBAA")
        self.hex.setMaxLength(9)
        self.hex.setClearButtonEnabled(True)
        hex_fila.addWidget(self.hex, 1)
        copiar = QtWidgets.QPushButton("Copiar")
        copiar.setToolTip("Copiar valor hexadecimal al portapapeles")
        copiar.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(self.hex.text()))
        hex_fila.addWidget(copiar)
        layout.addLayout(hex_fila)

        grupos = QtWidgets.QGridLayout()
        for index, (nombre, etiquetas, limite) in enumerate((
            ("RGB", "RGB", 255),
            ("CMYK", "CMYK", 100),
            ("HSV", "HSV", 100),
            ("HSL", "HSL", 100),
        )):
            group = QtWidgets.QGroupBox(nombre)
            form = QtWidgets.QFormLayout(group)
            form.setContentsMargins(10, 10, 10, 10)
            form.setSpacing(5)
            self._campos[nombre] = []
            for j, label in enumerate(etiquetas):
                s = QtWidgets.QSpinBox()
                s.setRange(0, 359 if nombre in ("HSV", "HSL") and j == 0 else limite)
                s.setSuffix("%" if nombre in ("HSV", "HSL", "CMYK") and not (nombre in ("HSV", "HSL") and j == 0) else "")
                s.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
                self._campos[nombre].append(s)
                form.addRow(label + ":", s)
                s.valueChanged.connect(lambda _v, mod=nombre: self._desde_modelo(mod))
            grupos.addWidget(group, 0, index)
        layout.addLayout(grupos)

        alpha_fila = QtWidgets.QHBoxLayout()
        alpha_fila.addWidget(QtWidgets.QLabel("Opacidad"))
        self.alpha_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        alpha_fila.addWidget(self.alpha_slider, 1)
        self.alpha_num = QtWidgets.QSpinBox()
        self.alpha_num.setRange(0, 255)
        self.alpha_num.setSuffix(" / 255")
        alpha_fila.addWidget(self.alpha_num)
        layout.addLayout(alpha_fila)

        ayuda = QtWidgets.QLabel("CMYK se convierte matemáticamente desde RGB; no sustituye un perfil ICC de impresión.")
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: palette(mid);")
        layout.addWidget(ayuda)

        botones = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        botones.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Aceptar")
        botones.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

        self.area.cambiado.connect(self._desde_area)
        self.tono.cambiado.connect(self._desde_tono)
        self.hex.editingFinished.connect(self._desde_hex)
        self.alpha_slider.valueChanged.connect(self._desde_alpha)
        self.alpha_num.valueChanged.connect(self._desde_alpha)

    def _actualizar(self, color: QtGui.QColor):
        if not color.isValid():
            return
        self._color = QtGui.QColor(color)
        h, s, v, a = self._color.getHsv()
        if h >= 0:
            self._tono = h
        self.area.ajustar(self._tono, s / 255., v / 255.)
        self.tono.ajustar(self._tono)
        self.muestra.ajustar(self._color)
        texto = self._color.name(QtGui.QColor.NameFormat.HexRgb)
        if a < 255:
            texto += f"{a:02x}"  # RRGGBBAA (convención CSS)
        with QtCore.QSignalBlocker(self.hex):
            self.hex.setText(texto.upper())
        valores = {
            "RGB": list(self._color.getRgb()[:3]),
            "CMYK": [round(i*100/255) for i in self._color.getCmyk()[:4]],
            "HSV": [self._tono, round(s*100/255), round(v*100/255)],
            "HSL": [max(0, self._color.hslHue()), round(self._color.hslSaturation()*100/255),
                    round(self._color.lightness()*100/255)],
        }
        for modelo, lista in self._campos.items():
            for campo, valor in zip(lista, valores[modelo]):
                with QtCore.QSignalBlocker(campo):
                    campo.setValue(valor)
        for control in (self.alpha_slider, self.alpha_num):
            with QtCore.QSignalBlocker(control):
                control.setValue(a)
        self.colorCambiado.emit(QtGui.QColor(self._color))

    def _desde_area(self, s: float, v: float):
        self._actualizar(QtGui.QColor.fromHsv(self._tono, round(s*255), round(v*255),
                                              self._color.alpha()))

    def _desde_tono(self, h: int):
        self._tono = h
        _, s, v, a = self._color.getHsv()
        self._actualizar(QtGui.QColor.fromHsv(h, s, v, a))

    def _desde_alpha(self, alpha: int):
        c = QtGui.QColor(self._color)
        c.setAlpha(alpha)
        self._actualizar(c)

    def _desde_modelo(self, modelo: str):
        vals = [s.value() for s in self._campos[modelo]]
        a = self._color.alpha()
        if modelo == "RGB":
            c = QtGui.QColor.fromRgb(*vals, a)
        elif modelo == "CMYK":
            c = QtGui.QColor.fromCmyk(*[round(x*255/100) for x in vals], a)
        elif modelo == "HSV":
            self._tono = vals[0]
            c = QtGui.QColor.fromHsv(vals[0], round(vals[1]*255/100), round(vals[2]*255/100), a)
        else:
            c = QtGui.QColor.fromHsl(vals[0], round(vals[1]*255/100), round(vals[2]*255/100), a)
        self._actualizar(c)

    def _desde_hex(self):
        texto = self.hex.text().strip().lstrip("#")
        if re.fullmatch(r"[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", texto):
            c = QtGui.QColor("#" + texto[:6])
            if len(texto) == 8:
                c.setAlpha(int(texto[6:8], 16))
            else:
                c.setAlpha(self._color.alpha())
            self._actualizar(c)
        else:
            self._actualizar(self._color)  # Revierte una entrada inválida.

    def selectedColor(self) -> QtGui.QColor:
        return QtGui.QColor(self._color)

    @classmethod
    def getColor(cls, inicial, parent=None, titulo="Selector de color") -> QtGui.QColor:
        dlg = cls(inicial, parent, titulo)
        return dlg.selectedColor() if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted else QtGui.QColor()


class ConectorColores(QtCore.QObject):
    """Conecta el selector con los QTreeWidget existentes en Ajustes.ui.

    Recibe como argumento la ventana QDialog cargada o el Ui_* de pyside6-uic.
    Los árboles conservan todas las modificaciones realizadas en Qt Designer.
    """
    colorConfirmado = QtCore.Signal(str, str, QtGui.QColor)  # categoria, rol, color

    def __init__(self, interfaz, parent=None):
        super().__init__(parent)
        self.interfaz = interfaz
        for categoria, nombre_arbol, nombre_boton, nombre_label in (
            ("interfaz", "treeColoresUI", "btnColorUI", "lblColorUISeleccion"),
            ("tecnicos", "treeColoresTecnicos", "btnColorTecnico", "lblColorTecnicoSeleccion"),
        ):
            arbol = self._buscar(QtWidgets.QTreeWidget, nombre_arbol)
            boton = self._buscar(QtWidgets.QPushButton, nombre_boton)
            etiqueta = self._buscar(QtWidgets.QLabel, nombre_label)
            if arbol is None or boton is None:
                raise RuntimeError(f"No se encontraron {nombre_arbol} o {nombre_boton} en Ajustes.ui")
            for i in range(arbol.topLevelItemCount()):
                item = arbol.topLevelItem(i)
                self._icono(item)
            arbol.itemDoubleClicked.connect(lambda _it, _col, c=categoria, a=arbol: self.abrir(a, c))
            boton.clicked.connect(lambda _checked=False, c=categoria, a=arbol: self.abrir(a, c))
            if etiqueta is not None:
                arbol.currentItemChanged.connect(
                    lambda item, _prev, e=etiqueta: e.setText(
                        f"Personalizar: {item.text(0)}" if item else "Selecciona un rol para modificarlo."))
            if arbol.currentItem() is None and arbol.topLevelItemCount():
                arbol.setCurrentItem(arbol.topLevelItem(0))

    def _buscar(self, cls, nombre):
        obj = getattr(self.interfaz, nombre, None)
        if obj is None and isinstance(self.interfaz, QtCore.QObject):
            obj = self.interfaz.findChild(cls, nombre)
        return obj

    @staticmethod
    def _icono(item):
        c = QtGui.QColor(item.text(1))
        if c.isValid():
            pixmap = QtGui.QPixmap(15, 15)
            pixmap.fill(c)
            item.setIcon(0, QtGui.QIcon(pixmap))

    def abrir(self, arbol, categoria):
        item = arbol.currentItem()
        if item is None:
            return
        original = QtGui.QColor(item.text(1))
        if not original.isValid():
            original = QtGui.QColor("#FFFFFF")
        nuevo = SelectorColorRPS.getColor(original, arbol.window(), f"Color · {item.text(0)}")
        if not nuevo.isValid():
            return  # Cancelar no modifica el valor.
        valor = nuevo.name(QtGui.QColor.NameFormat.HexRgb).upper()
        if nuevo.alpha() < 255:
            valor += f"{nuevo.alpha():02X}"
        item.setText(1, valor)
        self._icono(item)
        self.colorConfirmado.emit(categoria, item.text(0), nuevo)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialogo = SelectorColorRPS("#FCBA03")
    if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
        print("Color seleccionado:", dialogo.selectedColor().name())
    sys.exit(0)
