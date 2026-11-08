# -*- coding: utf-8 -*-
"""
dialogs/mostrar_ocultar_dialog.py

Controladores de las ventanas Mostrar_Ocultar_<sistema> (Epitrocoidal, Hipotrocoidal, Trocoidal,
Planetario). Una base común (DialogoMostrarOcultarBase) + un mapeo canónico->objectName por subclase,
porque los .ui no comparten exactamente el mismo set de checkboxes. No modal: cada checkbox se aplica
en caliente (`toggled`); Aceptar/Cancelar solo cierran la ventana.

`actualizar_modo(modo_alterno)` habilita 'camino_de_contacto' solo con el piñón FIJO y 'curva_base'
solo en modo ALTERNO (Orbitar/Trasladar), junto con sus rótulos "Solo modo …" del .ui.
"""
from __future__ import annotations

from PySide6 import QtWidgets

from config.data_structures import AjustesVisibilidadSimulacion
from ui.errores import manejador_seguro


class DialogoMostrarOcultarBase(QtWidgets.QDialog):
    MODULO_UI: str = ""
    CLASE_UI: str = ""
    MAPEO_CHECKBOXES: dict = {}          # canónico (campo de AjustesVisibilidadSimulacion) -> objectName
    HABILITACION_POR_MODO: dict = {}     # canónico -> modo_alterno requerido (False=Fijo, True=Alterno)

    def __init__(self, ajustes: AjustesVisibilidadSimulacion, callback_cambio, parent=None):
        super().__init__(parent)
        modulo = __import__(self.MODULO_UI)
        self.ui = getattr(modulo, self.CLASE_UI)()
        self.ui.setupUi(self)
        self._ajustes = ajustes
        self._callback = callback_cambio
        self._checks = {}
        for canonico, real in self.MAPEO_CHECKBOXES.items():
            cb = getattr(self.ui, real, None)
            if cb is None:
                continue
            self._checks[canonico] = cb
            cb.setChecked(getattr(self._ajustes, canonico))
            cb.toggled.connect(lambda valor, campo=canonico: self._aplicar(campo, valor))
        self.ui.buttonBox.accepted.connect(self.close)
        self.ui.buttonBox.rejected.connect(self.close)

    def actualizar_modo(self, modo_alterno: bool) -> None:
        for campo, requiere in self.HABILITACION_POR_MODO.items():
            cb = self._checks.get(campo)
            if cb is not None:
                cb.setEnabled(modo_alterno == requiere)
        for et in self.findChildren(QtWidgets.QLabel):
            t = et.text().lstrip().lower()
            if t.startswith("solo"):
                es_alterno = "orbitar" in t or "trasladar" in t
                et.setEnabled(modo_alterno if es_alterno else not modo_alterno)

    @manejador_seguro
    def _aplicar(self, campo: str, valor: bool):
        setattr(self._ajustes, campo, valor)
        self._callback(self._ajustes)


_MAPEO_COMUN = {
    "circulos_de_paso": "checkBox_circulos_de_paso",
    "lineas_de_accion": "checkBox_lineas_de_accion",
    "camino_de_contacto": "checkBox_camino_de_contacto",
    "puntos_de_contacto": "checkBox_puntos_de_contacto",
    "etiquetas_de_rodillo": "checkBox_etiquetas_de_rodillo",
}
_POR_MODO = {"camino_de_contacto": False, "curva_base": True}


class DialogoMostrarOcultarTrocoidal(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Trocoidal"
    CLASE_UI = "Ui_Opciones_trocoidal_sim"
    MAPEO_CHECKBOXES = {**_MAPEO_COMUN, "curva_base": "checkBox_trocoide_base"}
    HABILITACION_POR_MODO = _POR_MODO


class DialogoMostrarOcultarEpitrocoidal(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Epitrocoidal"
    CLASE_UI = "Ui_Opciones_epitrocoidal_sim"
    MAPEO_CHECKBOXES = {**_MAPEO_COMUN, "curva_base": "checkBox_epitrocoide_base"}
    HABILITACION_POR_MODO = _POR_MODO


class DialogoMostrarOcultarHipotrocoidal(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Hipotrocoidal"
    CLASE_UI = "Ui_Opciones_hipotrocoidal_sim"
    MAPEO_CHECKBOXES = {**_MAPEO_COMUN, "curva_base": "checkBox_hipotrocoide_base"}
    HABILITACION_POR_MODO = _POR_MODO


class DialogoMostrarOcultarPlanetario(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Planetario"
    CLASE_UI = "Ui_Opciones_epitrocoidal_sim"      # el .py generado reutiliza ese nombre de clase
    MAPEO_CHECKBOXES = {
        "etiquetas_de_rodillo": "checkBox_etiquetas_de_rodillo",
        "lineas_de_accion": "checkBox_lineas_de_accion",
        "circulos_de_paso": "checkBox_circulos_de_paso",
        "puntos_de_contacto": "checkBox_puntos_de_contacto",
    }
