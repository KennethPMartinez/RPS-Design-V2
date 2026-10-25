# -*- coding: utf-8 -*-
"""
dialogs/mostrar_ocultar_dialog.py

Controladores de las 4 ventanas Mostrar_Ocultar_<sistema>.ui (Actividad 6,
Pasos_a_seguir_1307262.docx). Mismo patrón Adapter que VentanaSistemaBase/
DialogoDesviacion: una base común (DialogoMostrarOcultarBase) + un mapeo
canónico->objectName por subclase, porque los 4 .ui no comparten
exactamente el mismo set de checkboxes (ver
config.data_structures.AjustesVisibilidadSimulacion, que es la unión de
todos los campos posibles).

No modal (los 4 .ui ya traen `setWindowModality(NonModal)`): cada checkbox
se conecta a `toggled` para aplicar en caliente, sin esperar a un botón
Aceptar -- así se puede ver el efecto en la simulación con el diálogo
todavía abierto. `buttonBox.accepted`/`rejected` solo cierran la ventana;
no hay "cancelar y revertir" en esta primera versión (ver progress.md
§15, Actividad 6 -- simplificación deliberada para no duplicar estado).

Los checkboxes que vienen deshabilitados de fábrica en el .ui (p. ej.
"Epitrocoide base" o "Solo modo Orbitar") se saltan automáticamente: ver
`DialogoMostrarOcultarBase.__init__`, no se ofrecen todavía porque su
capa correspondiente no está implementada en el render (circulos_de_paso,
curva_base, lineas_de_accion -- ver
config.data_structures.AjustesVisibilidadSimulacion).
"""
from __future__ import annotations
from PySide6 import QtWidgets

from config.data_structures import AjustesVisibilidadSimulacion
from ui.errores import manejador_seguro


class DialogoMostrarOcultarBase(QtWidgets.QDialog):
    MODULO_UI: str = ""
    CLASE_UI: str = ""
    # canónico (campo de AjustesVisibilidadSimulacion) -> objectName real en el .ui
    MAPEO_CHECKBOXES: dict = {}
    # V2: capas que solo tienen sentido en un modo del piñón. canónico -> modo_alterno requerido
    # (False = "Fijo", True = "Orbitar"). Se habilitan/deshabilitan con `actualizar_modo()`.
    HABILITACION_POR_MODO: dict = {}

    def __init__(self, ajustes: AjustesVisibilidadSimulacion, callback_cambio, parent=None):
        super().__init__(parent)
        modulo = __import__(self.MODULO_UI)
        clase_ui = getattr(modulo, self.CLASE_UI)
        self.ui = clase_ui()
        self.ui.setupUi(self)
        self._ajustes = ajustes
        self._callback = callback_cambio

        self._checks = {}
        for nombre_canonico, nombre_real in self.MAPEO_CHECKBOXES.items():
            checkbox = getattr(self.ui, nombre_real, None)
            if checkbox is None:      # V2: ya NO se salta el deshabilitado de fábrica: ahora lo gobierna el modo
                continue
            self._checks[nombre_canonico] = checkbox
            checkbox.setChecked(getattr(self._ajustes, nombre_canonico))
            checkbox.toggled.connect(
                lambda valor, campo=nombre_canonico: self._aplicar(campo, valor))

        self.ui.buttonBox.accepted.connect(self.close)
        self.ui.buttonBox.rejected.connect(self.close)

    def actualizar_modo(self, modo_alterno: bool) -> None:
        """Habilita 'Camino de contacto' solo en modo Fijo y 'Epitrocoide base' solo en Orbitar
        (según HABILITACION_POR_MODO), junto con sus rótulos "Solo modo ..." del .ui."""
        for campo, requiere in self.HABILITACION_POR_MODO.items():
            cb = self._checks.get(campo)
            if cb is not None:
                cb.setEnabled(modo_alterno == requiere)
        for et in self.findChildren(QtWidgets.QLabel):
            t = et.text()
            if t.lstrip().lower().startswith("solo"):
                et.setEnabled(modo_alterno if "orbitar" in t.lower() else not modo_alterno)

    @manejador_seguro
    def _aplicar(self, campo: str, valor: bool):
        setattr(self._ajustes, campo, valor)
        self._callback(self._ajustes)


# Mapeo COMÚN a los 4 sistemas: los 4 diálogos comparten estos 5 checkboxes con el mismo
# significado (aunque no siempre habilitados) -- solo "curva_base" cambia de objectName
# entre sistemas (checkBox_trocoide_base / checkBox_epitrocoide_base /
# checkBox_eptrocoide_base), y Planetario no lo tiene.
_MAPEO_COMUN = {
    "circulos_de_paso": "checkBox_circulos_de_paso",
    "lineas_de_accion": "checkBox_lineas_de_accion",
    "camino_de_contacto": "checkBox_camino_de_contacto",
    "puntos_de_contacto": "checkBox_puntos_de_contacto",
    "etiquetas_de_rodillo": "checkBox_etiquetas_de_rodillo",
}


class DialogoMostrarOcultarCremallera(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Trocoide"
    CLASE_UI = "Ui_Opciones_trocoidal_sim"
    MAPEO_CHECKBOXES = {**_MAPEO_COMUN, "curva_base": "checkBox_trocoide_base"}


class DialogoMostrarOcultarEpitrocoidal(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Epitrocoide"
    CLASE_UI = "Ui_Opciones_epitrocoidal_sim"
    MAPEO_CHECKBOXES = {**_MAPEO_COMUN, "curva_base": "checkBox_epitrocoide_base"}
    HABILITACION_POR_MODO = {"camino_de_contacto": False, "curva_base": True}


class DialogoMostrarOcultarHipotrocoidal(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Hipotrocoide"
    CLASE_UI = "Ui_Opciones_hipotrocoidal_sim"
    MAPEO_CHECKBOXES = {**_MAPEO_COMUN, "curva_base": "checkBox_eptrocoide_base"}


class DialogoMostrarOcultarPlanetario(DialogoMostrarOcultarBase):
    MODULO_UI = "Mostrar_Ocultar_Planetario"
    # OJO: el .py de este diálogo reutiliza el mismo nombre de clase que el de
    # Epitrocoidal ("Ui_Opciones_epitrocoidal_sim") -- son módulos distintos así que no
    # colisionan, pero es fácil confundirlos al leer el código fuente.
    CLASE_UI = "Ui_Opciones_epitrocoidal_sim"
    MAPEO_CHECKBOXES = {
        "etiquetas_de_rodillo": "checkBox_etiquetas_de_rodillo",
        "lineas_de_accion": "checkBox_lineas_de_accion",
        "circulos_de_paso": "checkBox_circulos_de_paso",
        "puntos_de_contacto": "checkBox_puntos_de_contacto",
    }
