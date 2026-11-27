# -*- coding: utf-8 -*-
"""
ui/ajustes_runtime.py — única instancia de SettingsStore + ThemeManager + estado de preferencias.

Arranque (main.py):  runtime.iniciar(app)  →  configurar pyqtgraph / aplicar_tema  →  runtime.aplicar_tema_guardado()
Ventanas:            runtime.cambiado (Signal[SettingsState]) avisa tras Aplicar/Aceptar; runtime.abrir_dialogo(parent).
Plots nuevos:        widgets.pg_helpers.configurar_menu_plot llama runtime.tema_a_plot(plot).

Qué se aplica de verdad: tema/paleta/fuentes/trazos (ThemeManager), OpenGL, backend CPU/GPU/Híbrido
(ajustes.modo_hardware), cadencia visual (FrameScheduler), pestañas General y Exportación, Simulación
(inválido, pausa, caché) y Cálculo y precisión (decimales -> utils.formato_numerico; estrategia, muestras y
tolerancias -> engine.sampling_preferences; indicador de costo). Se PERSISTEN pero no actúan: V-Sync y simulación
por contacto (ver progress.md §14).
"""
from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from config.app_settings import ajustes
from config.settings_model import SettingsState
from config.settings_store import SettingsStore
from engine import sampling_preferences as sp
from ui.theme_manager import ThemeManager
from utils import formato_numerico


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
                from widgets import pg_helpers
                motivo = pg_helpers.ULTIMO_ERROR_OPENGL or "motivo no informado por el controlador"
                raise RuntimeError(f"No se pudo aplicar OpenGL ({motivo}); se conserva la preferencia anterior")
            ajustes.render_opengl = usar_gl
        self.estado = estado
        self.theme.apply(estado.apariencia)
        self.cambiado.emit(estado)

    @staticmethod
    def _sincronizar_ajustes(estado: SettingsState) -> None:
        ajustes.modo_hardware = estado.simulacion.backend.split(" — ")[0].replace("Híbrido", "Hibrido")
        ajustes.desviacion.desviacion_lineal_mm = estado.calculo.desviacion_lineal_mm
        ajustes.desviacion.desviacion_angular_grados = estado.calculo.desviacion_angular_grados
        c = estado.calculo                      # Ajustes → Cálculo: discretización del perfil y formato de números
        sp.configurar_politica(sp.Politica(
            sp.ESTRATEGIA_ADAPTATIVA if "Adaptativa" in c.estrategia_muestreo else sp.ESTRATEGIA_UNIFORME,
            int(c.muestras_uniformes), int(c.max_muestras), float(c.desviacion_lineal_mm),
            float(c.desviacion_angular_grados), bool(c.mostrar_estimacion)))
        formato_numerico.configurar(c.decimales)
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

    def opciones_guardado(self) -> QtWidgets.QFileDialog.Option:
        """«Confirmar sobrescritura»: con la preferencia apagada, los diálogos de guardar no preguntan."""
        if self.estado.general.confirmar_sobrescritura:
            return QtWidgets.QFileDialog.Option(0)
        return QtWidgets.QFileDialog.Option.DontConfirmOverwrite

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
