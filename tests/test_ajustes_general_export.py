"""Ajustes → General y Exportación con efecto real (Qt offscreen, datos de usuario en carpeta temporal)."""
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PySide6")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from PySide6 import QtGui, QtWidgets  # noqa: E402

import main as M  # noqa: E402
from config.settings_model import SettingsState  # noqa: E402
from config.settings_store import SettingsStore  # noqa: E402

M.localizar_modulos_ui()
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from widgets.pg_helpers import configurar_pyqtgraph  # noqa: E402

configurar_pyqtgraph(False, True)       # foreground/background como tuplas RGB, igual que main.py

from exporters import settings_adapter as ad  # noqa: E402
from exporters.video_recorder import GrabadorVideo, es_vp9  # noqa: E402
from ui.ajustes_runtime import AjustesRuntime, runtime  # noqa: E402
from ui.epi_hipo_window import VentanaEpitrocoidal  # noqa: E402
from ui.main_menu import MenuPrincipal  # noqa: E402
from ui.settings_window import SettingsWindow  # noqa: E402

B = QtWidgets.QMessageBox.StandardButton


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["RPS_DATA_DIR"] = self._tmp.name
        self._antes = runtime.estado
        runtime.estado = SettingsState()
        self.ventanas = []

    def tearDown(self):
        for w in self.ventanas:
            w._t_auto.stop()
            w.hide()
        runtime.estado = self._antes
        os.environ.pop("RPS_DATA_DIR", None)
        self._tmp.cleanup()

    def ventana(self):
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.No):
            w = VentanaEpitrocoidal()
        self.ventanas.append(w)
        return w

    @staticmethod
    def cambiar(w, delta=0.25):
        campo, nombre = w.MAPEO_PARAMETROS[0]
        sp = getattr(w.ui, nombre)
        antes = sp.value()
        sp.setValue(antes + 1)
        if sp.value() == antes:                 # estaba en el máximo
            sp.setValue(antes - 1)
        assert sp.value() != antes
        return campo, sp.value()


class TestGeneral(Base):
    def test_restaurar_sesion(self):
        w = self.ventana()
        campo, valor = self.cambiar(w)
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.Discard):
            self.assertTrue(w.close())
        self.assertTrue((Path(self._tmp.name) / "RPS Design" / "sesion" / "EPITROCOIDAL.json").exists())
        w2 = self.ventana()
        self.assertAlmostEqual(getattr(w2.leer_parametros(), campo), valor, places=6)

    def test_restaurar_sesion_desactivado_no_guarda_ni_restaura(self):
        runtime.estado.general.restaurar_sesion = False
        w = self.ventana()
        _, valor = self.cambiar(w)
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.Discard):
            w.close()
        self.assertFalse((Path(self._tmp.name) / "RPS Design" / "sesion" / "EPITROCOIDAL.json").exists())
        self.assertNotAlmostEqual(getattr(self.ventana().leer_parametros(), self.ventana().MAPEO_PARAMETROS[0][0]), valor, places=6)

    def test_confirmar_salir_con_cambios(self):
        w = self.ventana()
        w.show()
        self.cambiar(w)
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.Cancel) as q:
            w.close()
            self.assertTrue(q.called)
        self.assertTrue(w.isVisible(), "Cancelar debe mantener la ventana abierta")
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.Discard):
            w.close()
        self.assertFalse(w.isVisible())

    def test_confirmar_salir_sin_cambios_no_pregunta(self):
        w = self.ventana()
        w.show()
        with mock.patch.object(QtWidgets.QMessageBox, "question") as q:
            w.close()
            q.assert_not_called()

    def test_confirmar_salir_desactivado_no_pregunta(self):
        runtime.estado.general.confirmar_salir = False
        w = self.ventana()
        self.cambiar(w)
        with mock.patch.object(QtWidgets.QMessageBox, "question") as q:
            w.close()
            q.assert_not_called()

    def test_menu_principal_confirma_cierre(self):
        m = MenuPrincipal()
        for resp, acepta in ((B.No, False), (B.Yes, True)):
            from PySide6.QtGui import QCloseEvent
            e = QCloseEvent()
            with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=resp):
                m.closeEvent(e)
            self.assertEqual(e.isAccepted(), acepta)
        runtime.estado.general.confirmar_salir = False
        e = QCloseEvent()
        m.closeEvent(e)
        self.assertTrue(e.isAccepted())

    def test_autoguardado_y_recuperacion(self):
        runtime.estado.general.guardado_automatico = True
        runtime.estado.general.intervalo_guardado_min = 2
        w = self.ventana()
        self.assertTrue(w._t_auto.isActive())
        self.assertEqual(w._t_auto.interval(), 120_000)
        auto = Path(self._tmp.name) / "RPS Design" / "autoguardado" / "EPITROCOIDAL.json"
        w._autoguardar()
        self.assertFalse(auto.exists(), "sin cambios no se autoguarda")
        campo, valor = self.cambiar(w)
        w._autoguardar()
        self.assertTrue(auto.exists())
        # «corte»: la ventana nunca se cerró -> al abrir otra se ofrece recuperar
        runtime.estado.general.restaurar_sesion = False
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.Yes) as q:
            w2 = VentanaEpitrocoidal(); self.ventanas.append(w2)
            self.assertTrue(q.called)
        self.assertAlmostEqual(getattr(w2.leer_parametros(), campo), valor, places=6)
        self.assertFalse(auto.exists())
        self.assertTrue(w2._hay_cambios(), "lo recuperado sigue sin guardarse")

    def test_autoguardado_desactivado_no_arranca_timer(self):
        runtime.estado.general.guardado_automatico = False
        self.assertFalse(self.ventana()._t_auto.isActive())

    def test_cierre_limpio_borra_autoguardado(self):
        runtime.estado.general.guardado_automatico = True
        w = self.ventana()
        self.cambiar(w)
        w._autoguardar()
        auto = Path(self._tmp.name) / "RPS Design" / "autoguardado" / "EPITROCOIDAL.json"
        self.assertTrue(auto.exists())
        with mock.patch.object(QtWidgets.QMessageBox, "question", return_value=B.Discard):
            w.close()
        self.assertFalse(auto.exists())

    def test_avisos_de_datos(self):
        w = self.ventana()
        with mock.patch.object(QtWidgets.QMessageBox, "information") as info:
            w._aviso_modal("t", "x")
            self.assertTrue(info.called)
        w._aviso("hola")
        self.assertEqual(w.statusBar().currentMessage(), "hola")
        runtime.estado.general.avisos_datos = False
        w.statusBar().clearMessage()
        with mock.patch.object(QtWidgets.QMessageBox, "information") as info:
            w._aviso_modal("t", "x")
            info.assert_not_called()
        w._aviso("silencio")
        self.assertEqual(w.statusBar().currentMessage(), "")

    def test_opciones_de_sobrescritura(self):
        self.assertEqual(runtime.opciones_guardado(), QtWidgets.QFileDialog.Option(0))
        runtime.estado.general.confirmar_sobrescritura = False
        self.assertEqual(runtime.opciones_guardado(), QtWidgets.QFileDialog.Option.DontConfirmOverwrite)


class TestExportacion(Base):
    def test_campos_de_video_creados_y_persistidos(self):
        rt = AjustesRuntime()
        rt.store = SettingsStore("RPSDesignTest", "T" + uuid.uuid4().hex[:8])
        from ui.theme_manager import ThemeManager
        rt.theme = ThemeManager(APP)
        rt.estado = rt.store.load()
        d = SettingsWindow(None, on_apply=lambda e: rt.aplicar(e), store=rt.store, theme_manager=rt.theme)
        for n in ("comboResolucionVideo", "comboFPSVideo", "spinCRFVideo"):
            self.assertIsNotNone(d.w(n), n)
        self.assertNotIn("por implementar", d.w("comboFormatoVideo", QtWidgets.QComboBox).itemText(1))
        d.w("comboFPSVideo", QtWidgets.QComboBox).setCurrentText("60 FPS")
        d.w("spinCRFVideo").setValue(30)
        d.w("comboResolucionVideo", QtWidgets.QComboBox).setCurrentText("1280 × 720 (HD)")
        d.w("comboFormatoVideo", QtWidgets.QComboBox).setCurrentIndex(1)
        d.w("btnAplicar", QtWidgets.QPushButton).click()
        e = rt.store.load().exportacion
        self.assertEqual((e.video_fps, e.video_crf, e.resolucion_video), (60, 30, "1280 × 720 (HD)"))
        self.assertEqual((e.video_ancho, e.video_alto), (1280, 720))
        pv = ad.parametros_video(e)
        self.assertTrue(pv["vp9"] and pv["extension"] == ".webm" and es_vp9(e.formato_video))

    def test_grabador_vp9_y_h264(self):
        import numpy as np
        from PySide6.QtGui import QImage
        for vp9, ext in ((False, ".mp4"), (True, ".webm")):
            ruta = Path(self._tmp.name) / f"v{ext}"
            g = GrabadorVideo(str(ruta), 24, 30, vp9)
            for k in range(6):
                img = QImage(64, 48, QImage.Format.Format_RGB32); img.fill(k * 30)
                g.agregar(img)
            g.cerrar()
            self.assertGreater(ruta.stat().st_size, 100, ext)

    def test_imagen_con_resolucion_calidad_y_transparencia(self):
        import pyqtgraph as pg
        from exporters.image_exporter import exportar_grafica
        plot = pg.PlotWidget(); plot.resize(500, 300); plot.plot([0, 1, 2], [0, 1, 0]); plot.show()
        op = SettingsState().exportacion
        op.resolucion_imagen = "Personalizada"; op.imagen_ancho, op.imagen_alto = 800, 450
        png = Path(self._tmp.name) / "a.png"
        exportar_grafica(plot, str(png), op=op)
        img = QtGui.QImage(str(png))
        self.assertEqual((img.width(), img.height()), (800, 450))
        op.fondo_transparente = True
        png2 = Path(self._tmp.name) / "b.png"
        exportar_grafica(plot, str(png2), op=op)
        self.assertEqual(QtGui.QImage(str(png2)).pixelColor(0, 0).alpha(), 0)
        tam = []
        for q in (95, 10):
            op.jpeg_calidad = q
            jpg = Path(self._tmp.name) / f"c{q}.jpg"
            exportar_grafica(plot, str(jpg), op=op)
            tam.append(jpg.stat().st_size)
        self.assertGreater(tam[0], tam[1], "calidad 95 debe pesar más que calidad 10")

    def test_grabar_video_desde_la_ventana_con_ajustes(self):
        runtime.estado.exportacion.resolucion_video = "Personalizada"
        runtime.estado.exportacion.video_ancho, runtime.estado.exportacion.video_alto = 320, 180
        runtime.estado.exportacion.video_fps = 24
        runtime.estado.exportacion.formato_video = "WebM — VP9"
        w = self.ventana(); w.show()
        w.ui.comboBox_modo_sim.setCurrentIndex(1)
        APP.processEvents()
        ruta = str(Path(self._tmp.name) / "sim.webm")
        with mock.patch.object(QtWidgets.QFileDialog, "getSaveFileName", return_value=(ruta, "")) as dlg, \
                mock.patch.object(QtWidgets.QMessageBox, "information"):
            w._grabar()
        self.assertEqual(dlg.call_args.args[3], "Video WebM (*.webm)")
        self.assertGreater(Path(ruta).stat().st_size, 500)
        import imageio.v2 as imageio
        r = imageio.get_reader(ruta)
        try:
            self.assertEqual(tuple(r.get_meta_data()["size"]), (320, 180))
            self.assertAlmostEqual(r.get_meta_data()["fps"], 24, delta=1)
        finally:
            r.close()


if __name__ == "__main__":
    unittest.main()
