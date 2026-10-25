# -*- coding: utf-8 -*-
"""
dialogs/visibility_dialog.py

Mostrar/Ocultar de la simulación (sustituye a los 4 mostrar_ocultar_dialog + .ui de V1 por
UN diálogo construido por código: solo ofrece las capas que SÍ están implementadas en
widgets/simulation_view.py). No modal: cada casilla se aplica en caliente.
"""
from __future__ import annotations

from PySide6 import QtWidgets

from config.data_structures import AjustesVisibilidadSimulacion
from ui.errores import manejador_seguro

CAPAS = [
    ("circulos_de_paso", "Círculos de paso"),
    ("lineas_de_accion", "Líneas de acción (contacto → CIR)"),
    ("puntos_de_contacto", "Puntos de contacto y rodillos activos"),
    ("etiquetas_de_rodillo", "Etiquetas de rodillos y dientes"),
]


class DialogoMostrarOcultar(QtWidgets.QDialog):
    def __init__(self, ajustes: AjustesVisibilidadSimulacion, callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mostrar / Ocultar")
        self._ajustes, self._callback = ajustes, callback
        lay = QtWidgets.QVBoxLayout(self)
        for campo, texto in CAPAS:
            cb = QtWidgets.QCheckBox(texto)
            cb.setChecked(getattr(ajustes, campo))
            cb.toggled.connect(lambda v, c=campo: self._aplicar(c, v))
            lay.addWidget(cb)
        cerrar = QtWidgets.QPushButton("Cerrar")
        cerrar.clicked.connect(self.close)
        lay.addWidget(cerrar)

    @manejador_seguro
    def _aplicar(self, campo, valor):
        setattr(self._ajustes, campo, valor)
        self._callback(self._ajustes)
