# -*- coding: utf-8 -*-
"""
ui/ajustes_runtime.py — única instancia de SettingsStore + ThemeManager + estado de preferencias.

Arranque (main.py):  runtime.iniciar(app)  →  configurar pyqtgraph / aplicar_tema  →  runtime.aplicar_tema_guardado()
Ventanas:            runtime.cambiado (Signal[SettingsState]) avisa tras Aplicar/Aceptar; runtime.abrir_dialogo(parent).
Plots nuevos:        widgets.pg_helpers.configurar_menu_plot llama runtime.tema_a_plot(plot).

Qué se aplica de verdad hoy: tema/paleta/fuentes/estilos de trazo (ThemeManager), OpenGL, backend CPU/GPU/Híbrido
(ajustes.modo_hardware), desviaciones, cadencia visual (FrameScheduler). Se PERSISTEN pero aún no actúan: V-Sync,
simulación por contacto, detener ante inválido, conservar pausa, caché de geometría, guardado automático,
restaurar sesión, confirmar salida y muestreo adaptativo (ver progress.md §13).
"""
from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from config.app_settings import ajustes
from config.settings_model import SettingsState
from config.settings_store import SettingsStore
from ui.theme_manager import ThemeManager


class AjustesRuntime(QtCore.QObject):
    cambiado = QtCore.Signal(object)            # SettingsState ya aplicado

    def __init__(self):
        super().__init__()
        self.store: SettingsStore | None = None
        self.theme: ThemeManager | None = None
        self.estado: SettingsState = SettingsState()
        self._dialogo = None

    # ------------------------------------------------------------------ arranque
    def iniciar(self, app: QtWidgets.QApplication) -> SettingsState:
        """Lee QSettings (con fallback a valores por defecto si es incompatible) y sincroniza `ajustes`."""
        self.store = SettingsStore()
        try:
            self.estado = self.store.load()
        except Exception as e:                  # configuración corrupta/incompatible: no se borra nada, se ignora
            print(f"[ajustes] preferencias ilegibles, se usan las predeterminadas: {e}")
            self.estado = SettingsState()
        self.theme = ThemeManager(app)
        self._sincronizar_ajustes(self.estado)
        ajustes.render_opengl = self.estado.simulacion.render == "OpenGL"
        return self.estado

    def aplicar_tema_guardado(self) -> None:
        if self.theme is not None:
            self.theme.apply(self.estado.apariencia)

    # ------------------------------------------------------------------ aplicar (Aplicar / Aceptar)
    def aplicar(self, estado: SettingsState, parent: QtWidgets.QWidget | None = None) -> None:
        self._sincronizar_ajustes(estado)
        usar_gl = estado.simulacion.render == "OpenGL"
        if usar_gl != ajustes.render_opengl:
            from widgets.pg_helpers import aplicar_opengl
            if not aplicar_opengl(usar_gl, parent):
                raise RuntimeError("No se pudo aplicar OpenGL; se conserva la preferencia anterior")
            ajustes.render_opengl = usar_gl
        self.estado = estado
        self.theme.apply(estado.apariencia)
        self.cambiado.emit(estado)

    @staticmethod
    def _sincronizar_ajustes(estado: SettingsState) -> None:
        ajustes.modo_hardware = estado.simulacion.backend.split(" — ")[0].replace("Híbrido", "Hibrido")
        ajustes.desviacion.desviacion_lineal_mm = estado.calculo.desviacion_lineal_mm
        ajustes.desviacion.desviacion_angular_grados = estado.calculo.desviacion_angular_grados
        fondo = QtGui.QColor(estado.apariencia.ui_colores.get("Fondo de ventana", "#222222"))
        ajustes.modo_oscuro = fondo.lightness() < 128

    # ------------------------------------------------------------------ utilidades
    def tema_a_plot(self, plot) -> None:
        """Aplica el tema vigente a una gráfica recién creada (sin tocar visibilidad, rangos ni menús)."""
        if self.theme is not None:
            try:
                self.theme.apply_to_plot(plot)
            except RuntimeError:
                pass

    def abrir_dialogo(self, parent: QtWidgets.QWidget | None = None) -> int:
        from ui.settings_window import SettingsWindow
        dlg = SettingsWindow(parent, on_apply=lambda est: self.aplicar(est, parent), store=self.store,
                             theme_manager=self.theme)
        self._dialogo = dlg                     # SettingsWindow no es QDialog: se conserva la referencia
        try:
            return dlg.exec()
        finally:
            self._dialogo = None


runtime = AjustesRuntime()
