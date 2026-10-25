# -*- coding: utf-8 -*-
"""
ui/settings_window.py  (Settings_window — PROVISIONAL, construida por código)

Archivo → Ajustes. La ventana definitiva sigue "por desarrollar": mientras tanto expone lo que
ya existe (hardware de cálculo, tema, OpenGL) y la conexión/parámetros del MOTOR real.
"""
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from config.app_settings import ajustes
from hardware.motor_controller import guardar_ajustes_motor, obtener_controlador
from ui.errores import manejador_seguro
from ui.style_manager import aplicar_tema


def _puertos() -> list[str]:
    try:
        from serial.tools import list_ports
        return [p.device for p in list_ports.comports()]
    except Exception:
        return []


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustes")
        self.ctrl = obtener_controlador()
        lay = QtWidgets.QVBoxLayout(self)

        g = QtWidgets.QGroupBox("General")
        form = QtWidgets.QFormLayout(g)
        self.combo_hw = QtWidgets.QComboBox(); self.combo_hw.addItems(["CPU", "GPU", "Hibrido"])
        self.combo_hw.setCurrentText(ajustes.modo_hardware)
        self.combo_hw.currentTextChanged.connect(self._hw)
        self.combo_tema = QtWidgets.QComboBox(); self.combo_tema.addItems(["Oscuro", "Claro"])
        self.combo_tema.setCurrentIndex(0 if ajustes.modo_oscuro else 1)
        self.combo_tema.currentIndexChanged.connect(self._tema)
        self.chk_gl = QtWidgets.QCheckBox("Render OpenGL en PyQtGraph (se aplica al instante)")
        self.chk_gl.setChecked(ajustes.render_opengl)
        self.chk_gl.toggled.connect(self._gl)
        form.addRow("Modo de hardware", self.combo_hw)
        form.addRow("Apariencia", self.combo_tema)
        form.addRow(self.chk_gl)
        lay.addWidget(g)

        m = ajustes.motor
        gm = QtWidgets.QGroupBox("Motor (Arduino Mega por serie)")
        fm = QtWidgets.QFormLayout(gm)
        self.chk_hab = QtWidgets.QCheckBox("Ejecutar en el motor al dar Play (modo automático)")
        self.chk_hab.setChecked(m.habilitado)
        self.chk_hab.toggled.connect(lambda v: setattr(ajustes.motor, "habilitado", v))
        self.chk_sim = QtWidgets.QCheckBox("Motor simulado (probar sin hardware)")
        self.chk_sim.setChecked(m.simulado)
        self.chk_sim.toggled.connect(lambda v: setattr(ajustes.motor, "simulado", v))
        self.combo_puerto = QtWidgets.QComboBox(); self.combo_puerto.setEditable(True)
        self.combo_puerto.addItems(_puertos())
        self.combo_puerto.setCurrentText(m.puerto)
        self.combo_puerto.currentTextChanged.connect(lambda t: setattr(ajustes.motor, "puerto", t.strip()))
        b_act = QtWidgets.QPushButton("Actualizar puertos"); b_act.clicked.connect(lambda *_: self._refrescar_puertos())
        fila = QtWidgets.QHBoxLayout(); fila.addWidget(self.combo_puerto, 1); fila.addWidget(b_act)
        fm.addRow(self.chk_hab); fm.addRow(self.chk_sim); fm.addRow("Puerto", fila)

        def spin(campo, minimo, maximo, dec, paso, sufijo=""):
            s = QtWidgets.QDoubleSpinBox(); s.setRange(minimo, maximo); s.setDecimals(dec); s.setSingleStep(paso)
            s.setSuffix(sufijo); s.setValue(getattr(m, campo)); s.setKeyboardTracking(False)
            s.valueChanged.connect(lambda v: setattr(ajustes.motor, campo, v))
            return s
        fm.addRow("Baudios", self._baud())
        fm.addRow("Relación (vueltas motor / vuelta piñón)", spin("relacion", 0.01, 1000, 4, 0.5))
        self.chk_inv = QtWidgets.QCheckBox("Invertir sentido de giro"); self.chk_inv.setChecked(m.invertir)
        self.chk_inv.toggled.connect(lambda v: setattr(ajustes.motor, "invertir", v))
        fm.addRow(self.chk_inv)
        fm.addRow("rpm máximas (seguridad)", spin("rpm_max", 1, 600, 1, 10, " rpm"))
        fm.addRow("rpm al alinear", spin("rpm_alineacion", 1, 600, 1, 5, " rpm"))
        fm.addRow("ACEL del firmware", spin("acel", 100, 1e6, 0, 500, " pasos/s²"))
        fm.addRow("Duración de cada tramo MOVE", spin("dt_segmento", 0.1, 30, 2, 0.1, " s"))
        fm.addRow("Desfase que se absorbe sin preguntar", spin("tolerancia_silenciosa_deg", 0, 360, 1, 1, " °"))
        self.lbl_estado = QtWidgets.QLabel()
        self.btn_con = QtWidgets.QPushButton()
        self.btn_con.clicked.connect(lambda *_: self._conectar_o_desconectar())
        fm.addRow(self.lbl_estado, self.btn_con)
        lay.addWidget(gm)
        lay.addWidget(QtWidgets.QLabel("<i>Ventana en desarrollo: se ampliará más adelante.</i>"))
        self._estado()

    def _baud(self):
        c = QtWidgets.QComboBox(); c.setEditable(True)
        c.addItems(["9600", "57600", "115200", "250000"]); c.setCurrentText(str(ajustes.motor.baud))
        c.currentTextChanged.connect(lambda t: setattr(ajustes.motor, "baud", int(t)) if t.isdigit() else None)
        return c

    def _refrescar_puertos(self):
        actual = self.combo_puerto.currentText()
        self.combo_puerto.clear(); self.combo_puerto.addItems(_puertos()); self.combo_puerto.setCurrentText(actual)

    def _estado(self):
        con = self.ctrl.conectado
        self.lbl_estado.setText("Estado: <b style='color:#1a7f37'>conectado</b>" if con else "Estado: desconectado")
        self.btn_con.setText("Desconectar" if con else "Conectar")

    @manejador_seguro
    def _conectar_o_desconectar(self, *_):
        if self.ctrl.conectado:
            self.ctrl.desconectar()
        else:
            try:
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
                self.ctrl.conectar()          # Motor() espera 2 s: la Mega se reinicia al abrir el puerto
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Motor", f"No se pudo conectar:\n{e}")
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
        guardar_ajustes_motor()
        self._estado()

    def done(self, r):
        guardar_ajustes_motor()
        super().done(r)

    @manejador_seguro
    def _gl(self, activo):
        from widgets.pg_helpers import aplicar_opengl
        ajustes.render_opengl = activo
        if not aplicar_opengl(activo, self):
            ajustes.render_opengl = not activo
            self.chk_gl.blockSignals(True); self.chk_gl.setChecked(not activo); self.chk_gl.blockSignals(False)
            QtWidgets.QMessageBox.warning(self, "OpenGL", "No se pudo cambiar el render (¿driver sin OpenGL?). "
                                          "Se mantiene el modo anterior.")

    @manejador_seguro
    def _hw(self, modo):
        ajustes.modo_hardware = modo

    @manejador_seguro
    def _tema(self, i):
        ajustes.modo_oscuro = i == 0
        aplicar_tema(QtWidgets.QApplication.instance(), ajustes.modo_oscuro)
