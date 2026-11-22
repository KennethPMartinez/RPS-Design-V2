"""Ajustes con Qt real (offscreen): carga del .ui del repo, Aplicar/Cancelar, persistencia, tema y cadencia."""
import os
import sys
import unittest
import uuid
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PySide6")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6 import QtCore, QtWidgets  # noqa: E402

from config.app_settings import ajustes  # noqa: E402
from config.settings_store import SettingsStore  # noqa: E402
from simulation.frame_scheduler import FrameScheduler, configurar_timer  # noqa: E402
from ui.ajustes_runtime import AjustesRuntime  # noqa: E402
from ui.settings_window import SettingsWindow  # noqa: E402

APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _runtime():
    rt = AjustesRuntime()
    rt.store = SettingsStore("RPSDesignTest", "T" + uuid.uuid4().hex[:8])
    rt.estado = rt.store.load()
    from ui.theme_manager import ThemeManager
    rt.theme = ThemeManager(APP)
    return rt


class TestAjustesQt(unittest.TestCase):
    def setUp(self):
        self.rt = _runtime()
        self._lin, self._ang = ajustes.desviacion.desviacion_lineal_mm, ajustes.desviacion.desviacion_angular_grados

    def tearDown(self):
        ajustes.desviacion.desviacion_lineal_mm, ajustes.desviacion.desviacion_angular_grados = self._lin, self._ang
        self.rt.store._s.clear() if hasattr(self.rt.store, "_s") else None

    def _dlg(self):
        return SettingsWindow(None, on_apply=lambda e: self.rt.aplicar(e), store=self.rt.store, theme_manager=self.rt.theme)

    def test_carga_ui_y_alias(self):
        d = self._dlg()
        for n in ("btnAplicar", "btnAceptar", "btnCancelar", "btnRestaurar", "chkSimulacionPorContacto"):
            self.assertIsNotNone(d.w(n), n)

    def test_cancelar_no_persiste_y_aplicar_si(self):
        d = self._dlg()
        d.w("desviacionLinealSpin").setValue(0.0007)
        d.dialog.reject()
        self.assertAlmostEqual(self.rt.store.load().calculo.desviacion_lineal_mm, 0.0003, places=7)
        d.w("btnAplicar", QtWidgets.QPushButton).click()
        self.assertAlmostEqual(self.rt.store.load().calculo.desviacion_lineal_mm, 0.0007, places=7)
        self.assertAlmostEqual(ajustes.desviacion.desviacion_lineal_mm, 0.0007, places=7)

    def test_simulacion_por_contacto_se_persiste_sin_solver(self):
        d = self._dlg()
        d.w("chkSimulacionPorContacto", QtWidgets.QCheckBox).setChecked(True)
        d.w("btnAplicar", QtWidgets.QPushButton).click()
        self.assertTrue(self.rt.store.load().simulacion.basada_en_contacto)

    def test_tema_aplica_paleta_global(self):
        d = self._dlg()
        d.w("comboTema", QtWidgets.QComboBox).setCurrentText("Claro")
        d.w("btnAplicar", QtWidgets.QPushButton).click()
        fondo = self.rt.estado.apariencia.ui_colores["Fondo de ventana"]
        self.assertEqual(APP.palette().window().color().name().upper(), fondo.upper())
        import pyqtgraph as pg   # regresión: las vistas leen foreground[0], así que debe ser tupla RGB y no QColor
        self.assertIsInstance(pg.getConfigOption("foreground")[0], int)

    def test_trazos_en_pixeles_y_no_en_unidades_de_datos(self):
        """Regresión: al cambiar de tema las líneas se veían gruesísimas (el QPen no era cosmético)."""
        from ui.theme_manager import ThemeManager
        self.assertTrue(ThemeManager.pen("#FF0000", {"ancho": 2}).isCosmetic())
        from widgets.simulation_view import SimulationView
        v = SimulationView()
        d = self._dlg()
        d.w("btnAplicar", QtWidgets.QPushButton).click()
        self.rt.theme.apply_to_plot(v)
        self.assertTrue(v.c_patron.opts["pen"].isCosmetic())
        self.assertLess(v.c_patron.opts["pen"].widthF(), 10)

    def test_cadencia(self):
        w, t = QtWidgets.QWidget(), QtCore.QTimer()
        self.assertEqual(configurar_timer(t, w, "60 FPS", 120), 60)
        self.assertEqual(t.interval(), 17)
        self.assertEqual(configurar_timer(t, w, "Personalizado", 100), 100)
        self.assertEqual(t.interval(), 10)
        self.assertIsNone(configurar_timer(t, w, "Sin límite (Uncapped)", 120))
        self.assertEqual(t.interval(), 0)
        s = FrameScheduler(w, t, "30 FPS", 120, False)
        s.set_preferences("120 FPS", 120, False)
        self.assertEqual(t.interval(), 8)


if __name__ == "__main__":
    unittest.main()
