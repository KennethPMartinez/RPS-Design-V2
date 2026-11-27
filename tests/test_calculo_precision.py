"""Ajustes → Cálculo y precisión: decimales (solo presentación), discretización uniforme/adaptativa y costo."""
import copy
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PySide6")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from PySide6 import QtWidgets  # noqa: E402

import main as M  # noqa: E402
from config.settings_model import SettingsState  # noqa: E402
from config.settings_store import SettingsStore  # noqa: E402
from engine import sampling_preferences as sp  # noqa: E402
from engine.epitrocoidal_engine import EpitrocoidalEngine  # noqa: E402
from config.data_structures import ParametrosEpitrocoidal  # noqa: E402
from utils import costo_calculo, formato_numerico as fn  # noqa: E402

M.localizar_modulos_ui()
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from widgets.pg_helpers import configurar_pyqtgraph  # noqa: E402

configurar_pyqtgraph(False, True)

from ui.ajustes_runtime import runtime  # noqa: E402
from ui.epi_hipo_window import VentanaEpitrocoidal, VentanaHipotrocoidal  # noqa: E402
from ui.planetary_window import VentanaPlanetario  # noqa: E402
from ui.theme_manager import ThemeManager  # noqa: E402
from ui.trocoidal_window import VentanaTrocoidal  # noqa: E402

L = 1.2
R = 10.0


def curva(t):
    """Epitrocoide de prueba con zona de alta curvatura."""
    t = np.asarray(t, dtype=float)
    return np.column_stack([R * np.cos(t) + 3 * np.cos(5 * t), R * np.sin(t) + 3 * np.sin(5 * t)])


def error_real_denso(t, p, n=400_001):
    """Distancia máxima real entre la curva (muy densa) y la polilínea (t, p): referencia independiente del algoritmo."""
    td = np.linspace(t[0], t[-1], n)
    q = curva(td)
    i = np.clip(np.searchsorted(t, td, side="right") - 1, 0, t.size - 2)
    a, b = p[i], p[i + 1]
    ab = b - a
    s = np.clip(((q - a) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-300), 0, 1)
    return float(np.hypot(*(q - (a + s[:, None] * ab)).T).max())


class Restaura(unittest.TestCase):
    def setUp(self):
        self._pol = sp.politica_actual()
        self._fmt = fn.clave()

    def tearDown(self):
        sp.configurar_politica(self._pol)
        fn.configurar("6 decimales" if not self._fmt[0] else "Automático")


class TestFormato(Restaura):
    def test_decimales_fijos_y_notacion(self):
        for txt, esperado in (("4 decimales", "3.1416"), ("6 decimales", "3.141593"), ("8 decimales", "3.14159265"),
                              ("12 decimales", "3.141592653590")):
            fn.configurar(txt)
            self.assertEqual(fn.fmt(np.pi), esperado)
        fn.configurar("4 decimales")
        self.assertEqual(fn.fmt(1.2e-7), "1.2000e-07")        # no se muestra como 0.0000
        self.assertEqual(fn.fmt(-1e-12), "-1.0000e-12")
        self.assertEqual(fn.fmt(0.0), "0.0000")
        self.assertEqual(fn.fmt(2.5, "mm"), "2.5000 mm")
        self.assertEqual(fn.fmt_signo(0.25), "+0.2500")
        self.assertEqual(fn.fmt(float("nan")), "nan")
        fn.configurar("Automático")
        self.assertEqual(fn.fmt(np.pi), "3.1415927")
        self.assertEqual(fn.fmt(1.2e-7), "1.2e-07")
        fn.configurar("texto raro")
        self.assertEqual(fn.decimales(), 6)

    def test_los_decimales_no_tocan_los_datos(self):
        sp.configurar_politica(sp.Politica())
        m = EpitrocoidalEngine(ParametrosEpitrocoidal())
        fn.configurar("12 decimales")
        a = m.generar_perfil()
        fn.configurar("4 decimales")
        b = m.generar_perfil()
        for campo in ("theta", "offset_x", "offset_y", "radio_curvatura", "angulo_presion_grados"):
            self.assertTrue(np.array_equal(getattr(a, campo), getattr(b, campo)), campo)
        from ui.property_windows import _llenar_tabla
        tabla = QtWidgets.QTableWidget()
        _llenar_tabla(tabla, [b.theta[:3], b.offset_x[:3]], ["θ", "X"])
        self.assertEqual(tabla.item(1, 1).text(), f"{b.offset_x[1]:.4f}")
        fn.configurar("8 decimales")
        _llenar_tabla(tabla, [b.theta[:3], b.offset_x[:3]], ["θ", "X"])
        self.assertEqual(tabla.item(1, 1).text(), f"{b.offset_x[1]:.8f}")
        self.assertEqual(float(b.offset_x[1]), float(m.generar_perfil().offset_x[1]), "el dato interno no se redondea")


class TestDiscretizacion(Restaura):
    def test_uniforme_respeta_la_cantidad(self):
        t, info = sp.uniforme_vec(curva, -L, L, 1001)
        self.assertEqual((t.size, info.n_muestras, info.ajustado_a_impar), (1001, 1001, False))
        self.assertEqual((t[0], t[-1], 0.0 in t), (-L, L, True))
        self.assertTrue(np.allclose(np.diff(t), 2 * L / 1000))
        t, info = sp.uniforme_vec(curva, -L, L, 1000)        # par: n+1 para conservar θ = 0 (se informa)
        self.assertEqual((t.size, info.ajustado_a_impar, 0.0 in t), (1001, True, True))
        with self.assertRaises(ValueError):
            sp.uniforme_vec(curva, -L, L, 2)

    def test_adaptativa_cumple_la_tolerancia_medida_aparte(self):
        for tol in (1e-2, 3e-4, 3e-5):
            t, info = sp.adaptativa_vec(curva, -L, L, tol, 0.5, 30001)
            p = curva(t)
            self.assertTrue(info.cumple and not info.limite_alcanzado, tol)
            self.assertLessEqual(info.error_mm, tol)
            self.assertLessEqual(info.giro_grados, 0.5)
            self.assertLessEqual(error_real_denso(t, p), tol * 1.05, f"error real frente a la tolerancia {tol}")

    def test_extremos_y_cero_exactos_y_orden(self):
        t, _ = sp.adaptativa_vec(curva, -L, L, 3e-5, 0.5, 30001)
        self.assertEqual((t[0], t[-1]), (-L, L))
        self.assertIn(0.0, t)
        self.assertTrue(np.all(np.diff(t) > 0))

    def test_limite_de_muestras_se_respeta_y_se_informa(self):
        for maximo in (65, 120, 300, 1500):
            t, info = sp.adaptativa_vec(curva, -L, L, 1e-7, 0.001, maximo)
            self.assertLessEqual(t.size, maximo)
            self.assertTrue(info.limite_alcanzado and info.cumple is False, maximo)
            self.assertEqual((t[0], t[-1]), (-L, L))
        t, info = sp.adaptativa_vec(curva, -L, L, 0.0, 0.0, 5000)      # tolerancia 0: termina en el límite
        self.assertLessEqual(t.size, 5000)
        self.assertTrue(info.limite_alcanzado)

    def test_concentra_muestras_donde_hay_curvatura(self):
        t, _ = sp.adaptativa_vec(curva, -L, L, 3e-5, 0.5, 30001)
        p = curva(t)
        paso = np.hypot(*np.diff(p, axis=0).T)
        h = 1e-4
        d1 = (curva(t + h) - curva(t - h)) / (2 * h)
        d2 = (curva(t + h) - 2 * curva(t) + curva(t - h)) / h ** 2
        kappa = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.hypot(*d1.T) ** 3
        kmed = 0.5 * (kappa[:-1] + kappa[1:])
        self.assertLess(np.median(paso[kmed >= np.quantile(kmed, 0.9)]), 0.6 * np.median(paso[kmed <= np.quantile(kmed, 0.5)]))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            sp.adaptativa_vec(curva, L, -L, 1e-3, 0.5, 1000)
        with self.assertRaises(ValueError):
            sp.adaptativa_vec(curva, -L, L, 0.5, 0.5, 1000)
        with self.assertRaises(ValueError):
            sp.adaptativa_vec(lambda t: np.full((len(t), 2), np.nan), -L, L, 1e-3, 0.5, 1000)

    def test_motor_usa_la_politica_y_el_n_explicito_no_cambia(self):
        m = EpitrocoidalEngine(ParametrosEpitrocoidal())
        sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_UNIFORME, 501))
        r = m.generar_perfil()
        self.assertEqual((r.theta.size, r.muestreo.n_muestras, r.muestreo.estrategia), (501, 501, "uniforme"))
        sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_ADAPTATIVA))
        r = m.generar_perfil()
        self.assertEqual(r.muestreo.estrategia, "adaptativa")
        self.assertTrue(r.muestreo.cumple)
        self.assertEqual((r.theta[0], r.theta[-1], 0.0 in r.theta), (-m.theta_lim, m.theta_lim, True))
        self.assertLess(r.theta.size, 1001, "con la tolerancia por defecto la adaptativa necesita menos muestras")
        e = m.generar_perfil(1001)                              # exportaciones/CAD: malla uniforme explícita
        self.assertIsNone(e.muestreo)
        self.assertTrue(np.array_equal(e.theta, np.linspace(-m.theta_lim, m.theta_lim, 1001)))
        self.assertEqual(len(m.tabular_exportacion()["Theta"]), 1001)

    def test_adaptativa_localiza_el_radio_de_curvatura_minimo_como_la_malla_densa(self):
        m = EpitrocoidalEngine(ParametrosEpitrocoidal())
        sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_ADAPTATIVA))
        ra = m.generar_perfil().radio_curvatura_minimo
        sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_UNIFORME, 20001))
        rd = m.generar_perfil().radio_curvatura_minimo
        self.assertAlmostEqual(ra, rd, delta=0.01 * rd)

    def test_exportacion_no_depende_de_la_discretizacion_de_simulacion(self):
        from exporters.export_manager import exportar
        m = EpitrocoidalEngine(ParametrosEpitrocoidal())
        d = Path(tempfile.mkdtemp())
        textos = []
        for pol in (sp.Politica(sp.ESTRATEGIA_UNIFORME, 301), sp.Politica(sp.ESTRATEGIA_ADAPTATIVA)):
            sp.configurar_politica(pol)
            ruta = d / f"{pol.estrategia}.csv"
            exportar(str(ruta), [("", m, ParametrosEpitrocoidal())], "EPITROCOIDAL")
            textos.append(ruta.read_text(encoding="utf-8"))
        self.assertEqual(textos[0], textos[1])
        self.assertEqual(len(textos[0].strip().splitlines()) - textos[0].count("#") - 1 >= 2001 - 5, True)


class TestCosto(Restaura):
    def test_texto_solo_con_metricas_verificables(self):
        _t, info = sp.adaptativa_vec(curva, -L, L, 3e-4, 0.5, 30001)
        txt, nivel = costo_calculo.resumen([("", info)], 0.0123, False)
        self.assertEqual(nivel, "ok")
        for parte in ("muestras", "adaptativa", "error máx.", "giro máx.", "12.3 ms (medido)"):
            self.assertIn(parte, txt)
        self.assertIn("caché", costo_calculo.resumen([("", info)], 0.0123, True)[0])
        self.assertIsNone(costo_calculo.advertencia([("", info)]))
        _t, mal = sp.adaptativa_vec(curva, -L, L, 1e-7, 0.001, 300)
        self.assertIn("límite de 300", costo_calculo.advertencia([("", mal)]))
        self.assertEqual(costo_calculo.resumen([("", mal)], 0.01, False)[1], "aviso")


class TestVentanas(Restaura):
    def setUp(self):
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["RPS_DATA_DIR"] = self._tmp.name
        self._antes = (runtime.estado, runtime.store, runtime.theme)
        runtime.estado = SettingsState()
        runtime.estado.general.restaurar_sesion = False
        runtime.store = SettingsStore("RPSDesignTest", "C" + uuid.uuid4().hex[:8])
        runtime.theme = ThemeManager(APP)
        runtime._sincronizar_ajustes(runtime.estado)
        self.ventanas = []

    def tearDown(self):
        for w in self.ventanas:
            w._pausar(); w._t_auto.stop(); w.hide()
        runtime.estado, runtime.store, runtime.theme = self._antes
        os.environ.pop("RPS_DATA_DIR", None)
        self._tmp.cleanup()
        super().tearDown()

    def ventana(self, clase=VentanaEpitrocoidal):
        w = clase()
        self.ventanas.append(w)
        return w

    def aplicar(self, **calculo):
        est = copy.deepcopy(runtime.estado)
        for k, v in calculo.items():
            setattr(est.calculo, k, v)
        runtime.aplicar(est)

    def test_los_cuatro_sistemas_con_adaptativa(self):
        self.aplicar(estrategia_muestreo="Adaptativa por tolerancia")
        for clase in (VentanaEpitrocoidal, VentanaHipotrocoidal, VentanaTrocoidal, VentanaPlanetario):
            w = self.ventana(clase)
            self.assertIsNotNone(w.motor_actual, clase.__name__)
            infos = w._infos_muestreo()
            self.assertTrue(infos and all(i.estrategia == "adaptativa" and i.cumple for _e, i in infos), clase.__name__)
        self.assertEqual(len(self.ventanas[-1]._infos_muestreo()), 2)         # planetario: sol + anular

    def test_cambiar_preferencias_recalcula_sin_reiniciar_e_invalida_cache(self):
        self.aplicar(estrategia_muestreo="Adaptativa por tolerancia")
        w = self.ventana()
        n_adapt = w.perfil_actual.muestreo.n_muestras
        llamadas, original = [], w.CLASE_MOTOR
        w.CLASE_MOTOR = lambda p: (llamadas.append(1), original(p))[1]
        self.aplicar(estrategia_muestreo="Uniforme por muestras", muestras_uniformes=501)
        self.assertEqual((w.perfil_actual.muestreo.estrategia, w.perfil_actual.muestreo.n_muestras), ("uniforme", 501))
        self.assertEqual(len(llamadas), 1, "otra discretización = otra geometría")
        self.aplicar(muestras_uniformes=501)                                   # sin cambios: no recalcula
        self.assertEqual(len(llamadas), 1)
        self.aplicar(estrategia_muestreo="Adaptativa por tolerancia")          # vuelta atrás: sale de la caché
        self.assertEqual(len(llamadas), 1)
        self.assertEqual(w.perfil_actual.muestreo.n_muestras, n_adapt)
        self.aplicar(desviacion_lineal_mm=0.0001)                              # otra tolerancia: otra geometría
        self.assertEqual(len(llamadas), 2)
        self.assertEqual(w.perfil_actual.muestreo.tol_mm, 0.0001)

    def test_decimales_repintan_lo_visible_al_aplicar(self):
        w = self.ventana()
        emitido = []
        w.perfilActualizado.connect(lambda *_: emitido.append(1))
        self.aplicar(decimales="4 decimales")
        self.assertEqual((fn.decimales(), len(emitido)), (4, 1))
        self.aplicar(decimales="4 decimales")
        self.assertEqual(len(emitido), 1, "mismo formato: no se repinta")
        w._t = 1.234567891
        w._mostrar_auto() if w._es_auto() else None
        self.aplicar(decimales="Automático")
        self.assertIsNone(fn.decimales())
        self.assertEqual(len(emitido), 2)

    def test_indicador_de_costo(self):
        w = self.ventana()
        self.assertTrue(w._lbl_costo.isHidden())
        self.aplicar(mostrar_estimacion=True)
        self.assertFalse(w._lbl_costo.isHidden())
        self.assertIn("muestras", w._lbl_costo.text())
        self.aplicar(estrategia_muestreo="Adaptativa por tolerancia", desviacion_lineal_mm=0.0002)
        self.assertGreater(w._t_geo, 0.0)
        self.assertIn("(medido)", w._lbl_costo.text())
        w._recalcular()                                  # mismos parámetros y discretización: sale de la caché
        self.assertIn("caché", w._lbl_costo.text())
        self.aplicar(mostrar_estimacion=False)
        self.assertTrue(w._lbl_costo.isHidden())

    def test_advertencia_al_alcanzar_el_limite(self):
        w = self.ventana()
        w.statusBar().clearMessage()
        sp.configurar_politica(sp.Politica(sp.ESTRATEGIA_ADAPTATIVA, max_muestras=100, tol_mm=1e-7, ang_grados=0.001))
        w._recalcular()
        self.assertIn("límite de 100", w.statusBar().currentMessage())
        self.assertFalse(w.perfil_actual.muestreo.cumple)


if __name__ == "__main__":
    unittest.main()
