"""Integración Qt (offscreen) del editor de regímenes y del régimen de contacto en las 4 ventanas."""
import json
import os
import sys
import tempfile
import time
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
from config.settings_model import SettingsState  # noqa: E402

M.localizar_modulos_ui()
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from widgets.pg_helpers import configurar_pyqtgraph  # noqa: E402

configurar_pyqtgraph(False, True)

from engine.estudio_fisico import METODO_DINAMICO, METODO_ESTATICO  # noqa: E402
from engine.motion_engine import FabricaPresets  # noqa: E402
from ui import estudio_qt as eq  # noqa: E402
from ui.ajustes_runtime import runtime  # noqa: E402
from ui.epi_hipo_window import VentanaEpitrocoidal, VentanaHipotrocoidal  # noqa: E402
from ui.planetary_window import VentanaPlanetario  # noqa: E402
from ui.trocoidal_window import VentanaTrocoidal  # noqa: E402
from utils import file_handler  # noqa: E402

VENTANAS = (VentanaEpitrocoidal, VentanaHipotrocoidal, VentanaTrocoidal, VentanaPlanetario)


def esperar(g, s=60.0):
    t0 = time.time()
    while g.calculando() and time.time() - t0 < s:
        APP.processEvents()
        time.sleep(0.005)
    APP.processEvents()


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["RPS_DATA_DIR"] = self._tmp.name
        self._antes = runtime.estado
        runtime.estado = SettingsState()
        runtime.estado.general.restaurar_sesion = False
        runtime.estado.general.confirmar_salir = False
        runtime.estado.simulacion.basada_en_contacto = True
        self.ws = []

    def tearDown(self):
        for w in self.ws:
            w.gestor_estudio.cancelar(); w.gestor_estudio.esperar(5000)
            if w._editor is not None:
                try:
                    w._editor.close()
                except RuntimeError:
                    pass
            w._pausar(); w._t_auto.stop(); w.hide()
        runtime.estado = self._antes
        os.environ.pop("RPS_DATA_DIR", None)
        self._tmp.cleanup()

    def ventana(self, C=VentanaEpitrocoidal):
        w = C()
        self.ws.append(w)
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        return w

    def editor(self, w, k=2e4, carga=0.5, n=21, estatico=True):
        ed = w._editar_linea_tiempo()
        u = ed.ui
        u.comboModeloContacto.setCurrentIndex(1)
        u.spinRigidezNormal.setValue(k)
        u.spinParResistente.setValue(carga)
        u.spinMuestrasEstudio.setValue(n)
        u.comboMuestreoEstudio.setCurrentIndex(1)
        u.comboMetodoSolucion.setCurrentText(METODO_ESTATICO if estatico else METODO_DINAMICO)
        return ed


class Ventanas(Base):
    def test_cuatro_ventanas_dos_regimenes_y_estudio(self):
        for C in VENTANAS:
            w = self.ventana(C)
            self.assertEqual(w.ui.lblEstadoSolucionador.text(), "Estudio físico: Sin estudio")
            self.assertFalse(w.ui.btnVerResultados.isEnabled())
            ed = self.editor(w)
            u = ed.ui
            self.assertEqual(u.tabRegimenes.count(), 2)
            self.assertTrue(u.tabDinamico.isEnabled())
            for i in range(u.listSeccionesEstudio.count()):         # Accionamiento, Cargas, Contacto, Solucionador
                u.listSeccionesEstudio.setCurrentRow(i)
                self.assertEqual(u.stackConfiguracion.currentIndex(), i)
            u.btnEjecutarEstudio.click()
            esperar(w.gestor_estudio)
            g = w.gestor_estudio
            self.assertEqual(g.estado, eq.FINALIZADO, f"{C.__name__}: {g.detalle}")
            self.assertTrue(w.ui.btnVerResultados.isEnabled())
            self.assertGreater(u.tablaTabFuerzasContacto.rowCount(), 0)
            self.assertGreater(u.tablaDiagnosticoEstudio.rowCount(), 0)
            # inspección sobre la geometría: el cursor lleva la ventana al instante calculado
            t = g.resultado.t[7]
            ed.dinamico.cursores[0].setValue(t)
            APP.processEvents()
            self.assertAlmostEqual(w._t, t, places=9)
            self.assertIn("Fn máx", w.sim.lbl_fps.text())

    def test_invalidacion_y_ver_resultados(self):
        w = self.ventana(VentanaEpitrocoidal)
        ed = self.editor(w)
        ed.ui.btnEjecutarEstudio.click()
        esperar(w.gestor_estudio)
        self.assertEqual(w.gestor_estudio.estado, eq.FINALIZADO)
        w.ui.spinBox_numerodedientes.setValue(14)
        w._debounce.stop(); w._recalcular()
        self.assertEqual(w.gestor_estudio.estado, eq.DESACTUALIZADO)
        self.assertFalse(w.ui.btnVerResultados.isEnabled())
        self.assertEqual(w.sim.c_fuerzas.getData()[0] is None or len(w.sim.c_fuerzas.getData()[0]) == 0, True)
        w.ui.spinBox_numerodedientes.setValue(12)
        w._debounce.stop(); w._recalcular()
        self.assertEqual(w.gestor_estudio.estado, eq.FINALIZADO)             # vuelve a ser vigente
        w._ver_resultados_estudio()
        self.assertIs(ed.ui.tabRegimenes.currentWidget(), ed.ui.tabDinamico)

    def test_cancelacion_y_recuperacion(self):
        w = self.ventana(VentanaPlanetario)
        ed = self.editor(w, n=4000)
        ed.ui.btnEjecutarEstudio.click()
        self.assertTrue(w.gestor_estudio.calculando())
        self.assertTrue(ed.ui.btnCancelarEstudio.isEnabled())
        ed.ui.btnCancelarEstudio.click()
        esperar(w.gestor_estudio)
        self.assertEqual(w.gestor_estudio.estado, eq.CANCELADO)
        self.assertTrue(ed.ui.btnEjecutarEstudio.isEnabled())               # interfaz recuperada
        ed.ui.spinMuestrasEstudio.setValue(5)
        ed.ui.btnEjecutarEstudio.click()
        esperar(w.gestor_estudio)
        self.assertEqual(w.gestor_estudio.estado, eq.FINALIZADO)

    def test_activacion_desde_ajustes(self):
        runtime.estado.simulacion.basada_en_contacto = False
        w = self.ventana(VentanaTrocoidal)
        ed = self.editor(w)
        runtime.cambiado.emit(runtime.estado)
        self.assertFalse(ed.ui.btnEjecutarEstudio.isEnabled())
        self.assertFalse(w.gestor_estudio.ejecutar(ed.perfil, ed.dinamico.leer()))
        runtime.estado.simulacion.basada_en_contacto = True
        runtime.cambiado.emit(runtime.estado)
        self.assertTrue(ed.ui.btnEjecutarEstudio.isEnabled())

    def test_hud_velocidades_de_la_linea_de_tiempo_no_de_los_fps(self):
        w = self.ventana(VentanaEpitrocoidal)
        w._t = 10.0
        w._mostrar_auto()
        txt = w.sim.lbl_fps.text()
        self.assertIn("13.333333 rpm", txt)                       # 80 °/s del preset = 13.33 rpm
        w.sim._menu._set_unidad_hud("rad/s", True)
        self.assertIn("rad/s", w.sim.lbl_fps.text())
        w.sim._menu._set_indicador("relacion", True)
        self.assertIn("i = ω_ent/ω_sal = -1", w.sim.lbl_fps.text())
        w.sim._menu._set_indicador("fps", False)
        self.assertNotIn("FPS", w.sim.lbl_fps.text())
        w.ui.comboBox_modo_sim.setCurrentIndex(0)                   # manual: sin velocidad definida
        self.assertIn("—", w.sim.lbl_fps.text())
        w.sim._menu._set_indicador("fps", True)
        w.sim._menu._set_unidad_hud("rpm", True)
        w.sim._menu._set_indicador("relacion", False)
        acciones = [a.text() for a in w.sim._menu._menu.actions()]
        self.assertIn("Opciones de la gráfica", acciones)


class DinamicaGobierna(Base):
    def test_play_calcula_la_dinamica_y_la_animacion_la_sigue(self):
        for C in (VentanaEpitrocoidal, VentanaTrocoidal, VentanaPlanetario):
            w = self.ventana(C)
            ed = self.editor(w, estatico=False)
            ed.ui.spinInerciaSalida.setValue(50.0)
            ed.close()
            APP.processEvents()
            w._play()                                         # sin estudio vigente: primero calcula
            self.assertTrue(w.gestor_estudio.calculando() or w.gestor_estudio.valido())
            esperar(w.gestor_estudio, 120)
            self.assertEqual(w.gestor_estudio.estado, eq.FINALIZADO, w.gestor_estudio.detalle)
            self.assertEqual(w.gestor_estudio.resultado.meta["modo"], "dinamico")
            self.assertTrue(w._anim.isActive())               # se reproduce al terminar
            w._pausar()
            r = w.gestor_estudio.resultado
            w._t = r.t[len(r.t) // 2]
            self.assertAlmostEqual(w._angulo_motor(), r.theta_in[len(r.t) // 2], places=6)   # θ de la dinámica
            fis = w._estado_fisico(w._angulo_motor())
            self.assertIsNotNone(fis["q"])
            self.assertIn("dinámica", fis["texto"])
            self.assertIn("Simulación por contacto ACTIVA", w.ui.lblEstadoSolucionador.text())

    def test_desviacion_amplificada_sobre_la_geometria(self):
        w = self.ventana(VentanaEpitrocoidal)
        est, _ = w._estado_para(30.0)
        e2 = w._aplicar_desviacion(est, [1e-3], 100.0)
        self.assertAlmostEqual(e2.angulo_patron_rad - est.angulo_patron_rad, 0.1, places=12)

    def test_modo_manual_omega_y_fuerzas_en_vivo(self):
        w = self.ventana(VentanaEpitrocoidal)
        ed = self.editor(w)                                  # rigidez y carga (no se guarda: escenario en edición)
        w.ui.comboBox_modo_sim.setCurrentIndex(0)
        reloj = [100.0]
        with mock.patch("ui.sistema_base.time.perf_counter", side_effect=lambda: reloj[0]):
            for i in range(5):
                w.control.reiniciar(10.0 * i)
                w._control_cambiado()
                reloj[0] += 0.05                              # 10° cada 50 ms = 200 °/s
            reloj[0] -= 0.05
            self.assertAlmostEqual(w._omega_manual(), 200.0, places=6)
            w._emitir_estado()
            self.assertIn("33.333333 rpm", w.sim.lbl_fps.text())
            self.assertIn("manual", w.sim.lbl_fps.text())
            self.assertIn("Contacto (manual", w.sim.lbl_fps.text())
            reloj[0] += 1.0                                   # se suelta el control: ω -> 0
            self.assertEqual(w._omega_manual(), 0.0)
        ed.close()

    def test_opengl_ignora_graficas_destruidas(self):
        from widgets import pg_helpers as ph
        w = self.ventana(VentanaEpitrocoidal)
        ed = w._editar_linea_tiempo()
        ed.close()
        APP.processEvents()
        from PySide6 import QtCore
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        import shiboken6
        self.assertTrue(all(shiboken6.isValid(p) for p in ph.plots_vivos()))


class Escenarios(Base):
    def test_escenario_por_preset_con_cambios_sin_guardar(self):
        w = self.ventana(VentanaEpitrocoidal)
        ed = w._editar_linea_tiempo()                 # formulario sin tocar: nada que preguntar
        d, u = ed.dinamico, ed.ui
        u.comboBox_preset.setCurrentText("Indexer")
        u.comboEscenarioDinamico.setCurrentIndex(1)
        d._escenario_elegido(1)
        self.assertEqual(d._seleccion, "Escenario asociado al preset: Indexer")
        u.spinParResistente.setValue(0.7)
        d._guardar_escenario()
        self.assertEqual(w.gestor_estudio.biblioteca.de_preset("Indexer").carga.constante, 0.7)
        u.spinParResistente.setValue(0.9)                    # sin guardar
        with mock.patch.object(QtWidgets.QMessageBox, "question",
                               return_value=QtWidgets.QMessageBox.StandardButton.Discard) as q:
            u.comboBox_preset.setCurrentText("Lavadora")
            self.assertTrue(q.called)
        self.assertEqual(u.spinParResistente.value(), 0.0)    # Lavadora: escenario sin carga (no se inventa)
        u.comboBox_preset.setCurrentText("Indexer")
        self.assertEqual(u.spinParResistente.value(), 0.7)    # se recupera el asociado
        # duplicar/personalizar sin tocar el preset original
        with mock.patch.object(QtWidgets.QInputDialog, "getText", return_value=("Mi escenario", True)):
            d._escenario_elegido(2)
        u.spinParResistente.setValue(1.5)
        d._guardar_escenario()
        b = w.gestor_estudio.biblioteca
        self.assertEqual(b.personalizados["Mi escenario"].carga.constante, 1.5)
        self.assertEqual(b.de_preset("Indexer").carga.constante, 0.7)
        self.assertEqual(FabricaPresets.crear("Indexer").to_dict(), FabricaPresets.crear("Indexer").to_dict())

    def test_persistencia_en_proyecto_y_compatibilidad(self):
        w = self.ventana(VentanaHipotrocoidal)
        ed = self.editor(w, n=9)
        ed.ui.btnEjecutarEstudio.click()
        esperar(w.gestor_estudio)
        ruta = os.path.join(self._tmp.name, "p.json")
        w._guardar_en(ruta)
        raw = Path(ruta).read_text(encoding="utf-8")
        self.assertIn("estudio_dinamico", raw)
        self.assertNotIn("NaN", raw)
        w2 = self.ventana(VentanaHipotrocoidal)
        w2._aplicar_proyecto(file_handler.abrir_proyecto(ruta, "HIPOTROCOIDAL"))
        self.assertEqual(w2.gestor_estudio.estado, eq.FINALIZADO)
        self.assertEqual(len(w2.gestor_estudio.resultado.t), len(w.gestor_estudio.resultado.t))
        self.assertEqual(w2.gestor_estudio.escenario.contacto.rigidez_n_mm, 2e4)
        # proyecto anterior (sin la sección): abre con «Sin estudio»
        d = json.loads(raw)
        d.pop("estudio_dinamico")
        Path(ruta).write_text(json.dumps(d), encoding="utf-8")
        w2._aplicar_proyecto(file_handler.abrir_proyecto(ruta, "HIPOTROCOIDAL"))
        self.assertEqual(w2.gestor_estudio.estado, eq.SIN_ESTUDIO)
        self.assertIsNone(w2.gestor_estudio.resultado)

    def test_exportar_resultados(self):
        w = self.ventana(VentanaTrocoidal)
        ed = self.editor(w, n=7)
        ed.ui.btnEjecutarEstudio.click()
        esperar(w.gestor_estudio)
        destino = os.path.join(self._tmp.name, "r.csv")
        with mock.patch.object(QtWidgets.QFileDialog, "getSaveFileName", return_value=(destino, "CSV (*.csv)")):
            ed.dinamico._exportar()
        self.assertTrue(Path(destino).exists())
        self.assertTrue(Path(self._tmp.name, "r_contactos.csv").exists())


if __name__ == "__main__":
    unittest.main()


class Tema(Base):
    def test_editor_sigue_el_tema(self):
        from widgets.pg_helpers import color_tecnico
        w = self.ventana(VentanaEpitrocoidal)
        ed = w._editar_linea_tiempo()
        runtime.estado.apariencia.tecnicos_colores["Curva base"] = "#123456"
        ed.plot._retemar()
        self.assertEqual(ed.curvas["Velocidad"].opts["pen"].color().name(), "#123456")
        self.assertEqual(color_tecnico("Curva base"), (0x12, 0x34, 0x56))
        self.assertEqual(ed.rueda.colores["fondo"], color_tecnico("Fondo de gráficas"))


class PresetImponeFisica(Base):
    def test_aplicar_preset_impone_motor_carga_e_inercias(self):
        for seguro in (True, False):
            runtime.estado.simulacion.modo_seguro_banco = seguro
            w = self.ventana(VentanaHipotrocoidal)
            ed = w._editar_linea_tiempo()
            u = ed.ui
            u.comboBox_preset.setCurrentText("Indexer")
            u.pushButton_Aplicar_preset.click()
            e = ed.dinamico.leer()
            self.assertTrue(ed.dinamico._seleccion.endswith("Indexer"))
            if seguro:
                self.assertEqual(e.motor.par_retencion_nm, 0.26)          # PK244-01B
                self.assertEqual(e.carga.constante, 0.0)
                self.assertGreater(e.dinamica.inercia_entrada_kg_mm2, 5.0)
            else:
                self.assertGreater(e.dinamica.inercia_salida, 1e4)        # mesa indexadora real (kg·mm²)
            self.assertIn("Aplicación", u.lblInfoMotor.text())
            ed.close()
        runtime.estado.simulacion.modo_seguro_banco = True

    def test_tipo_de_motor_carga_valores_por_defecto(self):
        w = self.ventana(VentanaEpitrocoidal)
        ed = w._editar_linea_tiempo()
        u = ed.ui
        u.comboTipoMotor.setCurrentIndex(1)                               # AC
        self.assertEqual(u.spinFrecuenciaRed.value(), 50.0)
        self.assertEqual(u.spinNumeroPolos.value(), 4)
        self.assertGreater(u.spinPotenciaNominal.value(), 0)
        self.assertGreater(u.spinParRetencion.value(), 0)                 # par nominal derivado
        u.spinPotenciaNominal.setValue(750.0)
        self.assertAlmostEqual(u.spinParRetencion.value(), 750 / (0.95 * 1500 * 3.141592653589793 / 30), places=3)
        u.comboTipoMotor.setCurrentIndex(0)                               # Stepper = PK244-01B
        self.assertEqual(u.spinParRetencion.value(), 0.26)
        self.assertEqual(u.tablaCurvaMotor.rowCount(), 10)

    def test_hud_queda_encima_del_viewport(self):
        w = self.ventana(VentanaEpitrocoidal)
        w.sim.setViewport(QtWidgets.QWidget())                            # lo que hace el cambio OpenGL ⇄ software
        w._emitir_estado()
        self.assertIs(w.sim.children()[-1], w.sim.lbl_fps)
