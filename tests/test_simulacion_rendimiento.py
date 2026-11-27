"""Ajustes → Simulación y rendimiento: detener ante inválido, conservar pausa y caché de geometría (Qt offscreen)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PySide6")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from PySide6 import QtWidgets  # noqa: E402

import main as M  # noqa: E402
from config.app_settings import ajustes  # noqa: E402
from config.settings_model import SettingsState  # noqa: E402

M.localizar_modulos_ui()
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from widgets.pg_helpers import configurar_pyqtgraph  # noqa: E402

configurar_pyqtgraph(False, True)

from ui.ajustes_runtime import runtime  # noqa: E402
from ui.epi_hipo_window import VentanaEpitrocoidal  # noqa: E402
from ui.trocoidal_window import VentanaTrocoidal  # noqa: E402

B = QtWidgets.QMessageBox.StandardButton


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["RPS_DATA_DIR"] = self._tmp.name
        self._antes, self._lin = runtime.estado, ajustes.desviacion.desviacion_lineal_mm
        runtime.estado = SettingsState()
        runtime.estado.general.restaurar_sesion = False     # que cada ventana arranque con los valores por defecto
        self.ventanas = []

    def tearDown(self):
        for w in self.ventanas:
            w._pausar(); w._t_auto.stop(); w.hide()
        runtime.estado = self._antes
        ajustes.desviacion.desviacion_lineal_mm = self._lin
        os.environ.pop("RPS_DATA_DIR", None)
        self._tmp.cleanup()

    def ventana(self, clase=VentanaEpitrocoidal):
        w = clase()
        self.ventanas.append(w)
        return w

    @staticmethod
    def recalcular(w):
        """Los spin recalculan con un debounce (QTimer); en las pruebas se dispara a mano."""
        w._debounce.stop()
        w._recalcular()

    @staticmethod
    def cambiar(w, nombre_campo=None):
        campo, nombre = (nombre_campo or w.MAPEO_PARAMETROS[0])
        sp = getattr(w.ui, nombre)
        antes = sp.value()
        sp.setValue(antes + 1)
        if sp.value() == antes:
            sp.setValue(antes - 1)
        assert sp.value() != antes
        return antes, sp.value()


class TestDetenerInvalido(Base):
    class _Invalido:
        def es_valido(self):
            return False

    def _auto(self):
        w = self.ventana()
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        w._play()
        self.assertTrue(w._anim.isActive())
        return w

    def test_parametros_invalidos_detienen_si_esta_activado(self):
        w = self._auto()
        with mock.patch.object(w, "leer_parametros", return_value=self._Invalido()):
            w._recalcular()
        self.assertFalse(w._anim.isActive())
        self.assertIn("detenida", w.statusBar().currentMessage())

    def test_parametros_invalidos_no_detienen_si_esta_apagado(self):
        runtime.estado.simulacion.detener_invalido = False
        w = self._auto()
        with mock.patch.object(w, "leer_parametros", return_value=self._Invalido()):
            w._recalcular()
        self.assertTrue(w._anim.isActive())

    def test_estado_roto_durante_la_reproduccion(self):
        for activado in (True, False):
            runtime.estado.simulacion.detener_invalido = activado
            w = self._auto()
            with mock.patch.object(w, "_estado_para", side_effect=RuntimeError("estado inválido")):
                w._tick()
            self.assertEqual(w._anim.isActive(), not activado, f"detener_invalido={activado}")
            w._pausar()


class TestConservarPausa(Base):
    def test_volver_a_automatico_conserva_posicion_y_linea(self):
        w = self.ventana()
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        lt, w._t = w.linea_tiempo, 3.0
        w.ui.comboBox_modo_sim.setCurrentIndex(0)
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        self.assertIs(w.linea_tiempo, lt)
        self.assertEqual(w._t, 3.0)

    def test_apagado_reinicia_y_reconstruye(self):
        runtime.estado.simulacion.conservar_pausa = False
        w = self.ventana()
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        lt, w._t = w.linea_tiempo, 3.0
        w.ui.comboBox_modo_sim.setCurrentIndex(0)
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        self.assertIsNot(w.linea_tiempo, lt)
        self.assertEqual(w._t, w.linea_tiempo.t_ini)

    def test_si_cambia_el_recorrido_se_reconstruye(self):
        w = self.ventana(VentanaTrocoidal)            # en Trocoidal la longitud L fija el recorrido válido
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        lt, w._t = w.linea_tiempo, 2.0
        w.ui.comboBox_modo_sim.setCurrentIndex(0)
        campo = next(c for c in w.MAPEO_PARAMETROS if c[0] == "longitud_cremallera")
        self.cambiar(w, campo)
        self.recalcular(w)
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        self.assertIsNot(w.linea_tiempo, lt)


class TestCacheGeometria(Base):
    def _contar(self, w):
        llamadas, original = [], w.CLASE_MOTOR
        w.CLASE_MOTOR = lambda p: (llamadas.append(1), original(p))[1]
        return llamadas

    def test_misma_geometria_no_se_recalcula_ni_se_vuelve_a_dibujar(self):
        w = self.ventana()
        llamadas = self._contar(w)
        with mock.patch.object(w.sim, "set_geometria") as dibuja:
            w._recalcular(); w._recalcular()
        self.assertEqual((len(llamadas), dibuja.call_count), (0, 0))

    def test_volver_a_parametros_anteriores_reutiliza_el_calculo(self):
        w = self.ventana()
        llamadas = self._contar(w)
        antes, _ = self.cambiar(w)
        self.recalcular(w)
        self.assertEqual(len(llamadas), 1)
        campo, nombre = w.MAPEO_PARAMETROS[0]
        getattr(w.ui, nombre).setValue(antes)
        self.recalcular(w)
        self.assertEqual(len(llamadas), 1, "los parámetros originales ya estaban calculados")

    def test_apagado_recalcula_siempre(self):
        runtime.estado.simulacion.cache_geometria = False
        w = self.ventana()
        llamadas = self._contar(w)
        w._recalcular(); w._recalcular()
        self.assertEqual(len(llamadas), 2)

    def test_cambiar_la_tolerancia_invalida_la_cache(self):
        from engine import sampling_preferences as sp
        pol0 = sp.politica_actual()
        try:
            sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_ADAPTATIVA, tol_mm=0.0003))
            w = self.ventana()
            llamadas = self._contar(w)
            w._recalcular()
            self.assertEqual(len(llamadas), 0)
            sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_ADAPTATIVA, tol_mm=0.0002))   # otra discretización
            w._recalcular()
            self.assertEqual(len(llamadas), 1)
        finally:
            sp.configurar_politica(pol0)

    def test_planetario(self):
        from ui import planetary_window as PW
        w = self.ventana(PW.VentanaPlanetario)
        llamadas, original = [], PW.PlanetarioEngine
        with mock.patch.object(PW, "PlanetarioEngine", lambda p: (llamadas.append(1), original(p))[1]):
            w._recalcular(); w._recalcular()
        self.assertEqual(len(llamadas), 0)


if __name__ == "__main__":
    unittest.main()
